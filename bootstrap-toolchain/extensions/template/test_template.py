"""Offline R.3 template checks. No Git, credentials, JES, or MVS writes."""
from pathlib import Path
import re
import unittest

HERE = Path(__file__).resolve().parent
REPLACEMENTS = {'@PACKAGE@': 'TSTPKG', '@GLOBAL@': '299',
                '@SERVICE@': 'TMSVC'}


def render(name: str, *, finalizer: bool = False) -> str:
    data = (HERE / name).read_text('ascii')
    for token, value in REPLACEMENTS.items():
        data = data.replace(token, value)
    data = data.replace('@FINEX@', '         EXTRN TMFIN' if finalizer else '*')
    data = data.replace('@FINADR@', 'A(TMFIN)' if finalizer else "F'0'")
    # Exclude comment lines: source commentary may deliberately mention tokens.
    assert not re.search(r'@(?:PACKAGE|GLOBAL|SERVICE|FINEX|FINADR)@', data)
    return data


class TemplateTests(unittest.TestCase):
    def test_instantiated_asm_is_ifox_card_safe(self):
        for item in ('descriptor.asm.in', 'registry.asm.in',
                     'dispatcher.asm.in', 'finalizer.asm.in'):
            for mode in (False, True):
                data = render(item, finalizer=mode)
                self.assertTrue(all(len(line) <= 71 and line.isascii()
                                    and '\t' not in line
                                    for line in data.splitlines()), item)

    def test_registered_extents_and_relocation(self):
        reg = render('registry.asm.in')
        desc = render('descriptor.asm.in')
        self.assertIn("F'1',F'28',F'44',F'1',F'1',F'0'", reg)
        self.assertIn('DC    A(TMBEG),A(TMEND)', reg)
        self.assertIn("CL8'TSTPKG'", reg)
        self.assertIn("F'1',F'48',F'56'", desc)
        self.assertIn("F'299',A(TMDISP)", desc)
        self.assertIn('ENTRY TMBEG,TMEND', desc)
        self.assertIn('EXTRN TMDISP', desc)
        self.assertNotIn('BCPLQSAM', desc)
        self.assertNotIn('BCPLTIME', desc)
        self.assertNotIn('BCPLDEC', desc)

    def test_declared_byte_lengths_match_data(self):
        def width(source, start, end):
            lines = source.splitlines()
            body = lines[lines.index(start)+1:lines.index(end)]
            size = 0
            for line in body:
                stripped = line.strip()
                if not stripped.startswith('DC    '):
                    continue
                for part in stripped[6:].split(','):
                    part = part.strip()
                    if re.fullmatch(r"F'-?\d+'", part) or re.fullmatch(
                            r'A\([A-Z][A-Z0-9]{0,7}\)', part):
                        size += 4
                    elif re.fullmatch(r"CL[48]'[^']*'", part):
                        size += int(part[2])
                    else:
                        self.fail(f'unknown assembler DC field {part!r}')
            return size
        reg = render('registry.asm.in')
        self.assertEqual(width(reg, 'BCRGBEG  DS    0F',
                               'BCRGEND  EQU   *'), 44)
        for final in (False, True):
            desc = render('descriptor.asm.in', finalizer=final)
            self.assertEqual(width(desc, 'TMBEG    DS    0F',
                                         'TMEND    EQU   *'), 56)

    def test_optional_finalizer_uses_linker_address(self):
        empty = render('descriptor.asm.in')
        hook = render('descriptor.asm.in', finalizer=True)
        fin = render('finalizer.asm.in')
        self.assertIn("F'1',F'0',F'1',F'0',F'0',F'0'", empty)
        self.assertIn("F'1',F'0',F'1',A(TMFIN),F'0',F'0'", hook)
        self.assertIn('EXTRN TMFIN', hook)
        self.assertIn('ENTRY TMFIN', fin)
        self.assertIn('STM   14,12,12(13)', fin)
        self.assertIn('LM    0,12,20(13)', fin)
        self.assertIn('SR    15,15', fin)

    def test_query_before_pointer_conversion(self):
        disp = render('dispatcher.asm.in')
        self.assertLess(disp.index("C     9,=F'6'"),
                        disp.index('SLL   8,2'))
        self.assertIn("QDATA    DC    F'1',F'1',F'0',F'6',F'1',F'0'", disp)
        self.assertIn("VDATA    DC    F'10',F'20',F'30'", disp)
        for pair in (('BADOP', "=F'-2'"), ('SHORT', "=F'-1'"),
                     ('BADARG', "=F'-3'")):
            self.assertIn(pair[0], disp)
            self.assertIn(pair[1], disp)

    def test_public_declarations_are_distinct_from_linking(self):
        head = render('public.h.in')
        self.assertIn('TMSVC:299', head)
        self.assertIn('TEMPLATE_QUERY=0', head)
        self.assertIn('TEMPLATE_GETVALUES=1', head)
        self.assertNotIn('BCPLREG', head)
        self.assertNotIn('DMODISP', head)

    def test_client_checks_query_version_and_unsupported_opcode(self):
        src = render('client.bcpl.in')
        self.assertIn('TMSVC:299', src)
        self.assertIn('TM_QUERY_WORDS', src)
        self.assertIn('INFO!1 NE TM_MAJOR', src)
        self.assertIn('INFO!3 NE 6', src)
        self.assertIn('TMSVC(2,0,0) NE -2', src)
        self.assertNotIn('R2BSVC', src)

    def test_linkage_selection_matrix_is_explicit(self):
        guide = (HERE.parents[2] / 'packaging' /
                 'runtime-extensions-r3-linkage-guide.md').read_text()
        for name in ('DMODESC', 'DMODISP', 'R2BDSC', 'R2BDISP',
                     'RGINIT', 'BCPLREG', 'BCPLMAIN', 'BLIB'):
            self.assertIn(name, guide)
        self.assertIn('145 PASS / 0 FAIL / 1 expected SKIP 083', guide)
        self.assertIn('BOOT_DEVOBJ', guide)


if __name__ == '__main__':
    unittest.main()
