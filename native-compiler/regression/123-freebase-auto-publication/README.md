# Regression 123 — automatic G6!48 publication

Source-mode only until production installation is accepted. Uses real historical BLIB VALIDPOINTER and external BCPLMEM object. Unlike regression 122, this BCPL program does **not** write G6!48. BCPLMAIN binds the storage slot to MEMBIND, and BCPLMEM publishes its list-head on GETVEC, head FREEVEC and MEMDRAIN. STACKEND is temporarily set to SAVEAREA to exclude historical broad-address predicate. Expect `V`; a diagnostic character identifies the failed assertion.

```sh
BCPL_RUNTIME_PDS=0 BCPLMEM_OBJECT=1 tools/run-native-regression 123 --show-output
```

PDS mode must not be used before coordinated installation of new BCPLMAIN and BCPLMEM.
