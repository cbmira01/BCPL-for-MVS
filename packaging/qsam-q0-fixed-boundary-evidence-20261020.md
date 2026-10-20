# Milestone QSAM — Q.0 F/FB DASD boundary evidence (2026-10-20)

**March:** Q.0 — Reconnaissance & contract. **Status:** Four standalone test profiles PASS on MVS 3.8J/TK5. Q.0 remains open; Q.1 has not started.

**Source:** Owner-supplied full JES reports dated 20 October 2026, including IFOX assembly listings and IEWL outputs. The reports remain available in the owner's JES/printer output. Reproducible source lives in [the boundary probe directory](../bootstrap-toolchain/probes/q0-qsam-boundary-probes/README.md); generated JCL is ignored and must not be committed.

| Profile | JOB / name | RECFM | LRECL | BLKSIZE | Records | ASMWR | ASMRD | LKWR | LKRD | WGO | RGO | QOUT marker |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| F80 | 2163 QS0F080 | F | 80 | 80 | 23 | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | Q0 F80 23 RECORDS PASS |
| F1024 | 2165 QS0F1K | F | 1024 | 1024 | 7 | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | Q0 F1024 7 RECORDS PASS |
| FB8K | 2166 QS0B8K | FB | 80 | 8000 | 105 | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | Q0 FB8K 105 RECORDS PASS |
| FB16K | 2167 QS0B16K | FB | 80 | 16000 | 210 | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | Q0 FB16K 210 RECORDS PASS |

Each separate writer and reader assembled and linked successfully, wrote and read temporary &&Q0DISK, and returned RC=0000. After OPEN the reader verified effective DCB RECFM, LRECL and BLKSIZE, record identifier, sequence byte, 70-byte blank padding for FB80 (or full interior padding for F1024), last-byte marker, count and EODAD. FB8K exercises 100 records in one full block plus five in the next; FB16K exercises 200 plus ten.

**Failed preparatory JOB 2164 / QS0F1K:** ASMWR and ASMRD returned RC=0008, IFOX IFO199 INVALID LENGTH MODIFIER on CL1024 and CL1014 blank constants, respectively. Link/run steps did not execute. This was a probe generator error, *not* a QSAM failure. The correction uses a CL256 blank constant for chunked MVC/CLC, preserves the reader/writer distinction between original blank declarations CL70 and CL80, and replaces the two reader/one writer count comparisons. JOB 2165 passed afterward.

**Observed geometry:** Hercules /tk5/conf/tk5.cnf identifies WORK01–WORK04 as IBM 3390 devices (0290–0293). JOB 2167 allocated &&Q0DISK on WORK01, completed QSAM writes/reads with BLKSIZE=16000, and deleted the temporary dataset. No BOOT_OBJ/BOOT_DEVOBJ or other persistent PDS object was modified.

**Scope limit:** The tests establish only the stated sizes and behaviors, not universal MVS limits, a compiled BCPLQSAM extension, arbitrary binary byte fidelity, V/VB zero payload, exceptional recovery, pending-record retry or Runtime Extensions registrar/finalizer behavior. Q.0 must not be closed from these tests.

Reproduce with the four --check commands documented in the probe README, then submit each through its run-q0-boundary.sh script and review all six step codes and the QOUT PASS line. The fb16k profile requires --allow-large and a device-geometry check. Never commit generated JCL, credentials or original ZIP artifacts.
