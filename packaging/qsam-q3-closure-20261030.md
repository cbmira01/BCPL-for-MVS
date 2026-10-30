# Milestone QSAM — Q.3 closure (30 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.3 — Variable logical records**  
**Disposition:** **CLOSED — 30 October 2026**, following the project owner's explicit approval to integrate the Q.3 regressions and close the march after verification.  
**Accepted implementation and regression baseline:** GitHub `main` commit [`5864fdc4490e4555e78b6099e1f7ed280bf3f8ac`](https://github.com/cbmira01/BCPL-for-MVS/commit/5864fdc4490e4555e78b6099e1f7ed280bf3f8ac).

## Native MVS 3.8J evidence

The owner supplied source-mode IFOX, IEWL, JES2, native BCPL and QSAM results from the resident MVS system. The following jobs operated on temporary MVS datasets, not installed BCPLQSAM objects.

| JOB | Test | Observed native evidence |
| --- | --- | --- |
| 7340 | V READ, LRECL=100 | Six records; RDW isolation, short-buffer retry, zero-payload record, EOF; native PASS |
| 7344 | V WRITE, LRECL=100 | Six records; independent IFOX RDW and binary verification; all ten steps RC=0000 |
| 7347 Q3VLRED | V READ, LRECL=1024 / BLKSIZE=1028 | Seven records including two successive 1020-byte payloads; IFOX writer/BCPL reader; ten steps RC=0000 |
| 7348 Q3VLWRT | V WRITE, LRECL=1024 / BLKSIZE=1028 | BCPL writer/independent IFOX RDW and binary verifier; ten steps RC=0000 |
| 7349 Q3VBRED | VB READ, LRECL=1024 / BLKSIZE=2052 | QSAM deblocking, payload-only BCPL READ; ten steps RC=0000 |
| 7350 Q3VBWRT | VB WRITE, LRECL=1024 / BLKSIZE=2052 | QSAM blocking, BCPL writer and independent IFOX RDW/binary verification; ten steps RC=0000 |

The supplied JOB 7347–7350 results each reported zero assembler severity and flagged statements and the required native PASS markers. The 1024-byte private-stage ceiling is an implementation policy, not a system-wide MVS limit.

## Numbered production regression acceptance

The owner-approved integration commit `5864fdc4` added:
- 171 — QSAM V READ: RDW stripping, 0/1/12/1020-byte payloads, binary fidelity, short-buffer retries, EOF.
- 172 — QSAM V WRITE: length validation and independent IFOX RDW/binary/EOF readback.
- 173 — QSAM VB READ: MVS deblocking and the same logical-record boundary/retry/EOF contract.
- 174 — QSAM VB WRITE: MVS blocking and independent IFOX RDW/binary/EOF readback.

Existing case 163 QUERY and case 170 BCPLQSAM/BCPLDEMO were updated for `QS_CAP_FIXED | QS_CAP_VARIABLE = 3`. Supported opcode bitmap remains 31. Historical Q.2 standalone BCPL source and closure evidence were preserved.

**30 October 2026 — owner-run actual MVS production panel results:**

| Panel | PASS | FAIL | SKIP | TOTAL | Runner RC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Focused 163–174 | **12** | **0** | **0** | **12** | **0** |
| Full 00–174 | **174** | **0** | **1 (083)** | **175** | **0** |

All four newly numbered V/VB cases, plus the updated 163 and 170, passed in both runs. The full-panel command reported `FULL Q.3 ACCEPTANCE PANEL VERIFIED`.

Evidence is retained by the operator, not tracked in Git: `workarea/bcplqsam-q3/q3-numbered-163-174-panel.log`, `q3-numbered-163-174.rc`, `q3-full-00-174-panel.log`, `q3-full-00-174.rc`, individual runner outputs under `workarea/native-regression/`, and the earlier standalone job reports under `workarea/bcplqsam-q3/`.

These are the **owner's reported MVS results**: the focused panel's complete PASS lines and totals and the full panel's trailing PASS lines, totals and runner RC were supplied in console output. This closure does **not** assert an independent per-JES audit of every individual job identifier or spool listing, which was not supplied.

## Accepted Q.3 behavior and boundaries

- `BCPLQSAM` remains an **optional, source-controlled System Extension**, explicitly selected through BCEX/BCRG v1, at `QSAMSVC:200`. The dispatcher opcodes 0–5, four-word request/eight-word result vectors, error values and handle contract remain unchanged.
- Fixed F/FB behavior accepted in Q.2 remains supported. Q.3 adds variable V/VB READ and WRITE with effective LRECL 4–1024 bytes, including private four-byte RDW. The maximum BCPL data payload is **1020 bytes**. A zero-byte payload is a valid logical record, not EOF; RDW and physical BDW are not exposed to BCPL.
- Insufficient READ capacity returns `QS_ERR_CAPACITY=-1` and exact required payload length, retains the staged record for retry, and does not overwrite the caller's buffer. The native tests cover repeated EOF, binary fidelity and defined negative paths.
- QSAM performs physical blocking and deblocking. QUERY capability flags now advertise fixed plus variable (`info!5=3`), **not** carriage-control support.
- The full panel exercised the accepted production `BOOT_OBJ` Core Runtime and a **temporary source-mode BCPLQSAM**; no permanent MVS PDS object was installed, no package promoted, and no untested geometry/device behavior is claimed.

## Deferrals and next march

Previously recorded Q.1 deferrals (exceptional/returned CLOSE, incomplete STOP/finalizer accounting, exceptional OPEN behavior) and broader geometry, resource, clean-room rebuild and release-hardening obligations remain with **Q.5 — Hardening & release**, where applicable. Q.3 closure does not certify them.

**Milestone QSAM remains ACTIVE. Q.4 — SYSOUT devices is NOT STARTED.** SYSPRINT/FBA carriage-control and SYSPUNCH 80-column card-image testing require separate approval and native MVS evidence. Q.5 remains future work. No new JES execution, MVS dataset modification or package installation is authorized by this closure.

## Owner decision

The owner approved Q.3 numbered regression integration, fixing regression 163, and closing Q.3. Both stipulated focused and full native regression gates subsequently passed. **Q.3 — Variable logical records is formally CLOSED on 30 October 2026.**
