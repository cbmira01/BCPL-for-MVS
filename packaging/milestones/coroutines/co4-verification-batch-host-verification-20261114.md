# CO.4 — Three-case verification batch: host evidence

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)  
**Classification:** HOST-CHECKED / NATIVE MVS PENDING  
**Scope:** `stack`, `churn`, `busy` isolated native application cases

The host review workspace prepared three ASCII FB80-compatible BCPL
sources with separate complete-record oracles (six, seven and ten
records), a thin inherited native runner adapter, and a 12-case Python
unit suite. Unit checks validate source identity contracts, literal
marker uniqueness, rejection of malformed records and unsafe scalar
CALLCO/RESUMECO targets, exact case order, synthetic case receipts and
batch fail-fast operation. Python syntax compilation is checked.

**Verified in the assistant's isolated workspace:**

- `python3 -B -m unittest discover -s tools/coroutines -p
  'test_run_co4_verification_batch.py' -q`: **12 PASS / 0 FAIL**.
- Python bytecode syntax compilation of runner and unit tests: **PASS**.
- All three application files: **ASCII and no record exceeds 80
  columns**; expected output markers occur once at source level.
- Synthetic per-case PASS and batch failure after case 2 preserve
  strict distinct result records: **PASS**.

The host review is **not** a Cambridge compiler parse, a complete
S/370 IFOX/IEWL linkage, or native MVS GO execution. The inherited
baseline's existing exact Git blob pins guard its accepted CO.3
library/CO3DROP/compiler parameter before native execution. The
three complete source programs still require the native evidence gate.
The MVS-facing batch runs all cases sequentially and fails closed;
receipts are not interpreted as production runtime installations.

No historical case IDs are assigned or renumbered; no installed
`BOOT_OBJ` is modified; no permanent globals are allocated; and
CO.5 is NOT STARTED.
