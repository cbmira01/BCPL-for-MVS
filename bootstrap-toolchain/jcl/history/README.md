# Historical native JCL — not in dspal.yaml

These decks document earlier BCPLMAIN, BCPLIO and BCPLQSAM development stages.
They are preserved for engineering provenance, **not** populated by
`dspal populate BOOT_JCL`.

- `build-dev-bcplm6.jcl` rebuilds the accepted M5.5 D6 object from
  canonical `BOOT_ASM(BCPLMAIN)` into **BOOT_DEVOBJ(BCPLM6)** only.
  To reproduce the accepted historical DEVOBJ profile, explicitly
  install as `BOOT_JCL(BLDDEVM6)` and submit after review.
- `build-native-bcplm7-for-dynamic.jcl` rebuilds the M2.1 D7
  object when historical D7 source has been explicitly staged as
  `BOOT_ASM(BCPLM7)`; it is not the current source mapping.
- `bcplio-d6-integration-link.jcl` and
  `bcplio-d7-integration-link.jcl` are stage-specific historical
  linkage experiments, not maintained builds.
- `build-gate-f1-bcplmem.jcl` is a historical single-member
  BCPLMEM production installation, not a current build entry point.
- `q5pkg-native.jcl` preserves the direct, 17-step Q.5 native
  temporary-PDS packaging and selected/unselected linkage campaign
  accepted as JOB 8155; it is not a canonical extension installation
  job or an installed-object verification.

Obsolete D3–D5 candidate, linkage and probe decks, the unneeded
BLIBLINK consumer and the hazardous SEEDDEV binary-copy job have been
retired from the working tree; Git history preserves them.
Some retained decks refer to **historical DSNs or PDS members**.
Inspect them before manually staging or submitting.

Current maintained JCL lives one directory above, with lowercase
filenames matching their uppercase `BOOT_JCL` member names.
