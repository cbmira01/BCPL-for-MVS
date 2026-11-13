"""Offline source/ABI regression guards for CO.1 CO1INIT R0 correction."""
from pathlib import Path
import re
import unittest

SWITCH = (Path(__file__).resolve().parents[2] /
          'packaging/milestones/coroutines/candidates' /
          'co1-bcpl-switch/co1change.asm')

class R0Contract(unittest.TestCase):
    def setUp(self):
        self.source = SWITCH.read_text('ascii')
        self.init = self.source.split('CO1INIT  STM   4,10,0(15)\n', 1)[1].split('         DROP  10\n', 1)[0]

    def test_cards_and_labels(self):
        for i,line in enumerate(self.source.splitlines(), 1):
            self.assertLessEqual(len(line),71,(i,line))
            self.assertTrue(line.isascii(), (i,line))
            if line and not line.startswith((' ', '*')):
                self.assertRegex(line.split()[0],r'^[A-Z@$#][A-Z0-9@$#]{0,7}$')

    def test_initializer_result_zero_preserved(self):
        # Generated Cambridge instructions compare R7 with R0 (CR 7,0).
        # Only after restoring caller R0 may the initializer clear R7.
        self.assertRegex(self.init,
            r'LR    0,6[^\n]*\n\s*SR    7,7[^\n]*\n\s*BCR   15,11')

    def test_preserve_incoming_r0_in_saved_r6(self):
        self.assertRegex(self.source,
            r'CO1INIT  STM   4,10,0\(15\)\n\s*LR    6,0\b')
        self.assertIn('LR    5,15',self.init)
        self.assertNotIn('LR    6,0', self.init.split('BALR  10,0',1)[1])

    def test_initialize_worker_r0_and_restore_caller_r0(self):
        snapshot = self.init.index('STM   0,15,0(4)')
        worker = self.init.index('ST    6,0(4)')
        restore = self.init.index('LR    0,6')
        return_zero = self.init.index('SR    7,7')
        ret = self.init.index('BCR   15,11')
        self.assertLess(snapshot,worker)
        self.assertLess(worker,restore)
        self.assertLess(restore,return_zero)
        self.assertLess(return_zero,ret)
        self.assertEqual(self.init.count('LR    0,6'),1)
        self.assertEqual(self.init.count('ST    6,0(4)'),1)

    def test_switch_restores_zero_register_image(self):
        self.assertIn('CO1SW    STM   0,15,0(15)',self.source)
        self.assertIn('MVC   32(64,2),0(5)',self.source)
        self.assertIn('LM    0,15,0(1)',self.source)

    def test_saved_r6_original_continuation_retimpl_not_clobbered(self):
        # STM 4..10 at 0(15) stores original R6 in word 2, 8(15).
        registers = list(range(4,11))
        offset_by_register={register:4*(register-4) for register in registers}
        self.assertEqual(offset_by_register[6],8)
        self.assertRegex(self.source,r'STM   4,10,0\(15\)\n\s*LR    6,0')

    def test_no_hidden_r6_overwrite_during_init(self):
        # R6 is scratch only inside CO1INIT; original R6 is in its frame.
        lines = self.init.splitlines()
        writers = [line.strip() for line in lines
                   if re.match(r'^\s*(?:L|LR|LA|SR|AR|LH|SLL|SRL|BASR|BALR)\s+6,',line)]
        self.assertEqual(writers,['LR    6,0              SAVE CG370 R0; R6 SAVED IN FRAME'])

if __name__=='__main__':
    unittest.main()
