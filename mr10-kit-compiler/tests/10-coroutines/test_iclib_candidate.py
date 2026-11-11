"""Small offline model of the CO.0 candidate CHANGECO instruction sequence.

Not an ICINT19 run, compiler run, native ABI test, or MVS acceptance.
Opcode semantics are taken from richards-bcpltape/mr10/bcplkit/icint.
"""
from pathlib import Path
import unittest

KIT = Path(__file__).resolve().parents[2]
CANDIDATE = KIT / "source" / "iclib-co0-candidate.int"
COBOOT = KIT / "library" / "coroutines-co0-candidate.bcpl"


def bridge_instructions():
    records = CANDIDATE.read_text(encoding="ascii").splitlines()
    tokens = []
    collecting = False
    for record in records:
        parts = record.split()
        if not parts:
            continue
        if parts[0] == "6":
            collecting = True
            parts = parts[1:]
        elif parts[0] == "498":
            parts = parts[1:]
        elif collecting and parts[0].isdigit():
            break
        if collecting:
            tokens.extend(p for p in parts if p != "G6L6")
    return tokens


def switch(memory, globals_, call_frame):
    """Execute only the switch subset: F0, F1, F2, F3, X1 and X32."""
    a = b = 0
    p, c = call_frame, -1
    for op in bridge_instructions():
        if op.startswith("LIP"):
            b, a = a, memory[p + int(op[3:])]
        elif op.startswith("LP"):
            b, a = a, p + int(op[2:])
        elif op.startswith("LIG"):
            b, a = a, globals_[int(op[3:])]
        elif op.startswith("LL"):
            b, a = a, int(op[2:])
        elif op.startswith("SG"):
            globals_[int(op[2:])] = a
        elif op.startswith("SIG"):
            memory[globals_[int(op[3:])]] = a
        elif op.startswith("A"):
            a += int(op[1:])
        elif op == "X1":
            a = memory[a]
        elif op == "X32":
            p, c = a, b
        elif op.startswith("JIG"):
            c = globals_[int(op[3:])]
        else:
            raise AssertionError("Unsupported instruction: " + op)
    return p, c, a


class TestCandidateChangeCo(unittest.TestCase):
    def test_switch_preserves_independent_continuations(self):
        # ROOT descriptor=9000, CHILD descriptor=3000.
        # C!0 points at each context's suspended CHANGECO call frame.
        memory = {
            9000: 0, 3000: 2000,
            2000: 700, 2001: 202,
            1000: 500, 1001: 101, 1002: 20, 1003: 3000,
        }
        g = {7: 9000, 9: 0, 10: 0}
        self.assertEqual(switch(memory, g, 1000), (700, 202, 20))
        self.assertEqual(memory[9000], 1000)
        self.assertEqual(g[7], 3000)

        # CHILD yields from STAGEDWAIT site 303, ROOT resumes site 101.
        memory.update({1100: 800, 1101: 303, 1102: 201, 1103: 9000})
        self.assertEqual(switch(memory, g, 1100), (500, 101, 201))
        self.assertEqual(memory[3000], 1100)

        # ROOT later resumes CHILD, using 303 with new value 27.
        memory.update({1200: 500, 1201: 102, 1202: 27, 1203: 3000})
        self.assertEqual(switch(memory, g, 1200), (800, 303, 27))
        self.assertEqual(memory[9000], 1200)

    def test_explicit_bootstrap_entry(self):
        memory = {
            9000: 0, 3000: 4000,
            2000: 600, 2001: 501, 2002: 0, 2003: 3000,
            4000: 4000, 4001: 777, 4002: 900, 4003: 100,
        }
        g = {7: 9000, 9: 0, 10: 0}
        self.assertEqual(switch(memory, g, 2000), (4000, 777, 0))
        self.assertEqual(memory[9000], 2000)

        # Initial COWAIT yields the descriptor to CREATECO.
        memory.update({2100: 4000, 2101: 888, 2102: 3000, 2103: 9000})
        self.assertEqual(switch(memory, g, 2100), (600, 501, 3000))
        self.assertEqual(memory[3000], 2100)

    def test_library_uses_matching_startup_layout(self):
        bcpl = COBOOT.read_text(encoding="ascii")
        for required in (
            "LET COBOOT(FN, SIZE, C) = VALOF",
            "C := FN(COWAIT(C)) REPEAT",
            "P := C+3",
            "P!0 := P",
            "P!1 := COBOOT",
            "RESULTIS CHANGECO(0, C)",
        ):
            self.assertIn(required, bcpl)

    def test_only_existing_intcode_ops(self):
        self.assertEqual(
            bridge_instructions(),
            ["LIP2", "SG9", "LP0", "SIG7", "LIP3", "SG7",
             "LIG7", "X1", "A1", "X1", "SG10",
             "LL498", "LIG7", "X1", "X1", "X32",
             "LIG9", "JIG10"],
        )


if __name__ == "__main__":
    unittest.main()
