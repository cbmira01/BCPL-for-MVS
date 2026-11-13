#!/usr/bin/env python3
"""Host-only verification of the compile-only CO.1 worker-frame oracle."""
import importlib.util
from pathlib import Path
import unittest

FILE = Path(__file__).resolve().parents[1] / 'bootstrap/co1-worker-frame-oracle.py'
spec = importlib.util.spec_from_file_location('co1worker_oracle', FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verify = module.verify_compiler_listing
verify_return = module.verify_runtime_return
model = module.model_return
Error = module.FrameOracleError


NATIVE = '''RETIMPL  L     6,8(5)
         L     5,4(5)
         L     4,0(5)
         BCR   15,6
STKIMPL  LR    5,15
'''


def generated():
    code = []
    for n, mx in enumerate((7, 8, 6), start=90):
        code.extend([f'L{n} EQU *', f'         STM 4,{mx},0(15)',
                     '         BAL 14,60(11)',
                     f'         DC A(L{n+200}) STACK FRAME SIZE',
                     '         LA 15,20(5)'])
        if mx == 8:
            code.append('         BALR 6,4')
        if mx == 6:
            code.extend(['         BALR 6,4', '         BALR 6,4'])
        if mx != 6:
            code.append('         BCR 15,11')
    code.extend([f'L{n+200} EQU 44 STACK FRAME SIZE' for n in (90,91,92)])
    return '\n'.join(code) + '\n'


class WorkerFrameOracleTests(unittest.TestCase):
    def test_valid_three_prologues(self):
        r = verify(generated())
        self.assertEqual((r['checked_entries'],r['one_arg_entry'],r['ordinary_calls']), (3,1,3))

    def test_frame_sizes(self):
        self.assertEqual([x['frame_bytes'] for x in verify(generated())['generated_frame_sizes']], [44]*3)

    def test_no_name_markers_required(self):
        self.assertNotIn('ENTRY TO', generated())
        self.assertEqual(verify(generated())['worker_return_line'],6)

    def test_worker_stored_save_is_r4_to_r7(self):
        self.assertEqual(verify(generated())['generated_frame_sizes'][0]['save_through'],7)

    def test_missing_zero_arg_entry(self):
        with self.assertRaisesRegex(Error,'one each'):
            verify(generated().replace('STM 4,6,0(15)', 'STM 4,8,0(15)'))

    def test_missing_one_arg_entry(self):
        with self.assertRaisesRegex(Error,'one each'):
            verify(generated().replace('STM 4,7,0(15)', 'STM 4,8,0(15)'))

    def test_duplicate_one_arg_entry(self):
        with self.assertRaisesRegex(Error,'one each'):
            verify(generated() + '         STM 4,7,0(15)\n')

    def test_missing_checked_entry(self):
        with self.assertRaisesRegex(Error,'adjacent'):
            verify(generated().replace('STM 4,7,0(15)\n         BAL 14,60(11)',
                                       'STM 4,7,0(15)\n         LR 5,15'))

    def test_missing_inline_frame_size(self):
        with self.assertRaisesRegex(Error,'inline'):
            verify(generated().replace('DC A(L290) STACK FRAME SIZE', "DC F'44'"))

    def test_no_frame_equ(self):
        with self.assertRaisesRegex(Error,'missing/duplicate'):
            verify(generated().replace('L290 EQU 44 STACK FRAME SIZE', ''))

    def test_duplicate_frame_equ(self):
        with self.assertRaisesRegex(Error,'missing/duplicate'):
            verify(generated() + 'L290 EQU 44 STACK FRAME SIZE\n')

    def test_frame_label_reused_by_two_procedures(self):
        with self.assertRaisesRegex(Error, 'reuse one inline'):
            verify(generated().replace('DC A(L291) STACK FRAME SIZE',
                                       'DC A(L290) STACK FRAME SIZE'))

    def test_zero_frame(self):
        with self.assertRaisesRegex(Error,'missing/duplicate'):
            verify(generated().replace('L290 EQU 44', 'L290 EQU 0'))

    def test_misaligned_frame(self):
        with self.assertRaisesRegex(Error,'missing/duplicate'):
            verify(generated().replace('L290 EQU 44', 'L290 EQU 42'))

    def test_extra_checked_entry_rejected(self):
        with self.assertRaisesRegex(Error, 'exactly three'):
            verify(generated() + '         BAL 14,60(11)\n')

    def test_counted_service_rejected(self):
        with self.assertRaisesRegex(Error,'counting'):
            verify(generated() + '         BAL 14,80(11)\n')

    def test_worker_missing_return(self):
        with self.assertRaisesRegex(Error,'worker lacks'):
            verify(generated().replace('         BCR 15,11\nL91', '         LR 7,7\nL91'))

    def test_worker_duplicate_return(self):
        with self.assertRaisesRegex(Error,'worker lacks'):
            verify(generated().replace('         BCR 15,11\nL91',
                                       '         BCR 15,11\n         BCR 15,11\nL91'))

    def test_invoke_missing_call(self):
        with self.assertRaisesRegex(Error,'INVOKE requires'):
            verify(generated().replace('         BALR 6,4\n         BCR 15,11\nL92',
                                       '         LR 6,4\n         BCR 15,11\nL92'))

    def test_invoke_duplicate_call(self):
        with self.assertRaisesRegex(Error,'INVOKE requires'):
            verify(generated().replace('         BALR 6,4\n         BCR 15,11\nL92',
                                       '         BALR 6,4\n         BALR 6,4\n         BCR 15,11\nL92'))

    def test_total_call_count(self):
        with self.assertRaisesRegex(Error,'expected >=3'):
            verify(generated().replace('         BALR 6,4\n         BALR 6,4',
                                       '         BALR 6,4\n         LR 8,8'))

    def test_retimipl_order(self):
        self.assertTrue(verify_return(NATIVE)['tracked_retimpl_order'])

    def test_changed_retimipl_order(self):
        with self.assertRaisesRegex(Error,'RETIMPL'):
            verify_return(NATIVE.replace('L     4,0(5)', 'L     4,0(6)'))

    def test_missing_checked_frame_install(self):
        with self.assertRaisesRegex(Error,'R5'):
            verify_return(NATIVE.replace('STKIMPL  LR    5,15','STKIMPL  LR    5,4'))

    def test_return_loads_callee_continuation(self):
        self.assertEqual(model((0x100,0x200,0x300),0x400),{'R6':0x300,'R5':0x200,'R4':0x400})

    def test_return_never_restores_r4_from_callee(self):
        self.assertNotEqual(model((0x111,0x200,0x300),0x400)['R4'],0x111)

    def test_bad_saved_linkage(self):
        with self.assertRaisesRegex(Error,'three saved'):
            model((0x1,0x2),0x4)


if __name__ == '__main__':
    unittest.main()
