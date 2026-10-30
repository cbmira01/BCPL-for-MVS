# Milestone QSAM — Q.4 closure (30 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** **Q.4 — SYSOUT devices**
**Disposition:** **CLOSED — 30 October 2026**, by the project owner's explicit instruction: **"Close out Q.4. Give me a handoff prompt for Q.5."**
**Accepted native source/regression baseline:** GitHub `main` [`51ed022eeea69af2b8453a766b43769abbdbf826`](https://github.com/cbmira01/BCPL-for-MVS/commit/51ed022eeea69af2b8453a766b43769abbdbf826).
**Technical gate evidence:** [Q.4 native regression acceptance](qsam-q4-native-regression-evidence-20261030.md).

## Accepted native operation

The owner ran the resident **demoted Cambridge compiler**, IFOX, IEWL, native BCPL/BCPLQSAM and an independent IFOX verifier on Hercules/TK5 MVS 3.8J. The optional System Extension remained **source-selected** using the established BCEX/BCRG v1 mechanism; production `BOOT_OBJ` Core Runtime members were read-only.

- **FB80 SYSOUT punch**: BCPL writes three exact EBCDIC FB80 logical records to a passed temporary dataset and `SYSPUNCH DD SYSOUT=B`. Independent IFOX verified the 80-byte payloads, final-column data and exact EOF; JES2 produced the three expected class-B ASCII card images and a blank separator.
- **FBA133 SYSOUT printer**: BCPL writes three full FBA133 logical records to temporary QSAM and `Q4PRINT DD SYSOUT=A`; an independent IFOX verifier established exact EBCDIC 133-byte records/EOF, and JES2/Hercules showed ASA blank, `0` and `1` spacing/page-control presentation. This test does **not** change Core Runtime `SYSPRINT`.
- **QUERY capability**: `QSAMSVC:200` `info!5=7` represents `QS_CAP_FIXED | QS_CAP_VARIABLE | QS_CAP_CARRIAGE`; the supported-opcode bitmap remains 31. F/FB, V/VB and **FBA** support is verified; **VBA remains unimplemented and unverified**.
- Existing QSAM lifecycle, negative, F/FB, V/VB and optional BCPLDEMO interoperability tests remained green.

Standalone FB80 [JOBs 7725/7726](qsam-q4-punch-evidence-20261030.md) and FBA133 [JOBs 7727/7728](qsam-q4-fba-evidence-20261030.md) passed, independently of the subsequent numbered regression runs.

## Numbered native regression closure gate

On the accepted source revision `51ed022e`, the owner executed:

| Native MVS panel | PASS | FAIL | SKIP | TOTAL | Runner RC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Focused `163..176` | **14** | **0** | **0** | **14** | **0** |
| Full production `00..176` | **176** | **0** | **1 (expected case 083)** | **177** | **0** |

Both panel log-capture steps returned RC=0. Cases **175 — qsam-fb80-sysout-punch** and **176 — qsam-fba133-sysout-printer** passed both panels, as did updated QUERY/interop cases 163/170. The final owner-supplied workflow reported `Q.4 FOCUSED AND FULL NATIVE ACCEPTANCE PASSED` and `Q.4 acceptance workflow RC=0`.

The first focused run had reported **13 PASS / 1 FAIL** because `PUNCH1` was paused with `P=Y` after native JOB 7755 completed successfully. The owner verified JES2 device status and used `$S PUN1` to release its queued three-card output, obtaining exactly 172 expected new ASCII capture bytes. That failure and its actual MVS recovery are preserved in the [numbered punch incident](qsam-q4-numbered-punch-incident-20261030.md). The accepted fresh reruns used the explicit `Q4_PUNCH_RESUME=1` opt-in and both panels passed; this closure does **not** relabel the earlier failed run as successful.

## Evidence scope and retained work

The operator's complete consolidated PASS/SKIP counts and return codes were supplied; a separate audit of every underlying JES listing was **not** provided. Generated decks, JES reports, device captures and individual native job metadata remain local under `workarea/bcplqsam-q4/` and `workarea/native-regression/`, not tracked in Git.

The accepted tests **do not** prove permanent BCPLQSAM installation, arbitrary device/record geometries, VBA, unrestricted reentrancy, the future native/self-hosted Cambridge compiler, or every exceptional resource-failure path. No MVS dataset installation/promotion, Hercules configuration change or new JES submission is authorized or undertaken by this documentation closure.

## Q.5 handoff: bounded hardening obligations

**Milestone QSAM remains ACTIVE. Q.4 — SYSOUT devices is CLOSED. Q.5 — Hardening & release is NOT STARTED.** Its official scope is documented in [Milestone QSAM](milestone-qsam.md): regression subset/negative tests, reproducible build/clean/rebuild, examples/docs, optional System Extension object-promotion decision, clean-from-Git reconstruction and full native production regression.

Previously deferred Q.1 matters remain explicit rather than silently accepted: exceptional/returned CLOSE handling and ownership/quarantine, failed/partial OPEN rollback and resource accounting, sixteen-handle STOP(8) finalizer CLOSE accounting, broader geometry/resource failure paths and relevant source-to-installed-object packaging questions. These require bounded Q.5 design and native tests, not assumptions of completion. Preserve `BCPLIO` character streams, `BCPLMAIN`, and the accepted `BOOT_OBJ` Core Runtime unless separately authorized.

**Owner decision:** Q.4 was explicitly ordered closed following successful native technical acceptance. This closure authorizes neither Q.5 implementation nor permanent dataset changes; plan and review Q.5 before executing tests or making changes.
