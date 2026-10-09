# BCPLMAIN stack-clearance march

Status: **SOURCE CHANGE COMMITTED — TK5 VALIDATION PENDING**

Historical source: `richards-bcpltape/km10/bcplmac`, macros `INITSAVE` and the user save-area definition.

Recovered facts:
- `INITSAVE` includes `STKMAIN` for the allocation containing the global vector and stack.
- `INUM` is identified as stack-clearance extent; the historical default, units, and calculation are not recovered.
- The historical user save area has consecutive byte addresses `STKBASE`, `STKLIM` (safe limit), and `STKHIGH` (one byte beyond stack).
- The exact historical STKCK machine-code body is not in the surviving evidence.

## Proposed reconstruction implemented

In `asm/bcplmain-wip.asm`, preserve **16,384 bytes usable workspace** after the 804-byte global vector; acquire another **256 bytes of explicitly provisional clearance** in the same GETMAIN block:

```text
G vector: 804 bytes
Stack base: allocation base + 804
Safe limit (STKLIM): stack base + 16,384
High boundary (DYNEND; published G!55): STKLIM + 256
Total allocation: 17,444 bytes
```

This deliberately preserves the existing 16K checked-entry threshold; the 256-byte reservation is a reconstruction choice, **not a recovered historical default**. The overflow path is unchanged. G!54/G!55 are word pointers, while STKLIM and DYNEND are byte addresses.

## Operator acceptance

1. Pull `main`, run `tools/run-native-regression 0 --show-output` and `tools/run-native-regression 52 --show-output`.
2. If both pass, run `tools/run-native-regression --show-output`.
3. Record operator results only after real TK5 execution.

Baseline **before** this change: 82 PASS, 0 FAIL, observed after commit `f58b9d0` and recorded at `64d4828`. The modified layout is not yet validated under TK5.

## Future work

Confirm the historical INUM grammar and units, decide whether STACKEND denotes full allocated extent or safe limit from BLIB usage, initialize historical stack markers, and reconcile the error/ABORT path. Do not claim the provisional 256-byte clearance is historically exact.
