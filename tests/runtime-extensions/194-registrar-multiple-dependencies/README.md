# 194 — registrar-multiple-dependencies

Two distinct earlier dependencies, duplicate and missing second dependency, prior-owner collision, repeated registration and reverse exactly-once finalization. Reuses full probe cases 1–3 and 17–18.

The installed BCPLRGS object is linked with a private assembler probe. The [shared contract fixture](../../../bootstrap-toolchain/probes/dr5-registrar/README.md) supplies checked exact return codes, G-vector publication, REGCOUNT and finalization assertions. No production writes or compiler invocation. Both regular native profiles use installed BOOT_OBJ(BCPLRGS). First numbered execution pending.
