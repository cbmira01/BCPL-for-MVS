# Regression 121 — G6 extended save-area BLIB consumer probe

Tests canonical BCPLMAIN's G6 pointer and historical BLIB's real
`INPROGRAM` (G58) and `VALIDPOINTER` (G59) procedures. The test
asserts that historical byte-address list heads `SAVEAREA!29` (LOADLIST)
and `SAVEAREA!48` (FREEBASE) are initially zero, and that both
historical procedures reject the word address zero without traversing
either absent list. Output is exactly `G`.

This tests only the empty-list behavior. It does **not** validate
nonempty loader/vector region lists, allocator membership, or complete
historical USERSAVE fidelity. It links the historical BLIB object,
not replacement stubs.

## Validation gates

```sh
git pull --ff-only
BCPL_RUNTIME_PDS=0 tools/run-native-regression 121 --show-output
```

**Do not run the PDS-default regression before production promotion**:
the currently installed BCPLMAIN does not contain the extended G6
backing and could perform out-of-bounds loads.

After source-mode 121 passes, full source-mode regression may be run.
Promote BCPLMAIN only after review and then run installed regression
121 and installed-object acceptance. Record actual JES job numbers
and return codes; no TK5 result was available when this test was added.
