# System Extensions

Optional MVS/System/370 packages for the Cambridge BCPL Programming System. Packages are selectable at application link-edit time and use the accepted BCEX/BCRG v1 registration model. The canonical source and public headers live with their packages here; GitHub is authoritative.

The existing `EXT_ASM`, `EXT_SOURCE`, `EXT_MAC`, and `EXT_OBJ` MVS datasets retain their approved names and contracts. Their host source mappings are defined in `config/dspal.yaml`. Historical compiler/bootstrap code remains under `bootstrap-toolchain/`.

This directory is distinct from the proposed BCPL Standard Library (`standard-library/`), which contains general-purpose BCPL application facilities. Tests have distinct ownership; formal suite extraction is a separate migration stage.
