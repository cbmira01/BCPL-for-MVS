# DR.5 — Registrar contract probe

Owner-approved correction to BCPLRGS dependency validation. This direct
MVS assembler probe exercises the real RGINIT and RGFINI entry points with
three private, linked BCEX descriptors, a BCRG table and a private global
vector/owner ledger. It uses test-only slots 10–12 in that private vector
and never calls the dummy export entries as BCPL. No package allocation or
production G-slot ownership changes. The probe is not a BCPL application
and does not replace integrated R.1/R.2 or regular project regressions.

| Case | Expected RGINIT status | Assertion |
| ---: | ---: | --- |
| 1 | 0 | Two distinct earlier dependencies; exact publication |
| 2 | 1014 | Duplicate second dependency |
| 3 | 1010 | Missing second dependency |
| 4 | 1012 | Forward dependency |
| 5 | 1004 | Invalid later extent before dependency lookup |
| 6 | 1004 | Later invalid extent before earlier bad magic |
| 7 | 1005 | Bad fixed header |
| 8 | 1005 | Later bad header before earlier bad count |
| 9 | 1006 | Invalid count |
| 10 | 1014 | Zero required major |
| 11 | 1014 | Negative required major |
| 12 | 1014 | Negative minimum minor |
| 13 | 1011 | Incompatible minimum minor |
| 14 | 1011 | Incompatible major |
| 15 | 1014 | Self dependency |
| 16 | 1014 | Blank dependency |
| 17 | 1009 | Prior-owner ledger collision |
| 18 | 0 | Repeat valid case after rejection sequence |

Every rejection requires REGCOUNT=0 and all three G slots unchanged.
Both successful cases require exactly the three relocated export addresses,
REGCOUNT=3, reverse finalizer order C/B/A and no repeat on a second RGFINI.
Invalid extent uses equal real linked begin/end addresses, not an arbitrary
address. The test does not certify malicious descriptors, register
preservation exhaustively, all legal dependency counts or arbitrary
multi-fault precedence. Private JOB 798, installation/IEBCOMPR JOB 801 and installed JOB 802 passed on 26 November 2026.

Run from repository root with explicit operator authorization:

```sh
python3 tools/checks/run-dr5-registrar-fix.py --candidate-only
python3 tools/checks/run-dr5-registrar-fix.py --installed-only
```

The first uses privately assembled canonical source and no production
object; the second consumes only the installed registrar. Explicit
`--rebuild-and-verify` first proves the private candidate, checks JES idle,
stages/readbacks BOOT_ASM(BCPLRGS), installs and independently compares
BOOT_OBJ(BCPLRGS), then runs the installed probe. Do not run the installed
probe against an uncorrected registrar as an acceptance campaign. The
driver preserves receipts under workarea/dr5-registrar-fix; if a write
has begun and a failure occurs, do not blindly replay. The credential-free
`--check` mode generates/checks deck shape without submitting JES.

Each GO must finish RC0 after all 18 assertions. Assertion failure returns
8 plus the failing case number (9–26); unexpected abend or nonzero IFOX/
IEWL/GO RC also fails the receipt. Expected registrar WTO diagnostics
on negative cases do not themselves constitute a test failure. This
standalone permanent probe is not counted in the regular eight-suite
regression baseline. The regular Runtime Extensions cases 194–197 derive
separate bodies from this verified shared source, including independent
single-dependency ordinal and version variants. They count as four
numbered cases and link installed BCPLRGS in both profiles. First numbered
execution pending.
