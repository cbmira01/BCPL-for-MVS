# M2.1 — Runtime Completion-Code Register

**D7 DEVOBJ(BCPLM7), 14 October 2026.** These are **MVS GO-step completion codes in R15**, not assembler/IEWL diagnostic RCs, JES job-status classifications, or MVS ABEND codes. `STOP(N)` intentionally allows application-defined values; no unique global allocation of RCs is implied.

| RC (decimal) | Producer / condition | Output or observable consequence | Cleanup / evidence |
| --- | --- | --- | --- |
| 0 | FINISH, or STOP(0) | Normal BCPL application exit | FINEXIT, IOFIN and memory drain/release. Focused 084–086, 119, full suite. |
| N (chosen by app) | STOP(N) | Program-specific result | STOPENT → FINEXIT. 087 tests 100 and 089 tests 8. These values **are not reserved runtime errors**. |
| 12 | STKOVFL: checked-entry frame or APTOVEC stack exhaustion | `STACK OVERFLOW`, unflushed primary record replaced | IOREPL then STOPENT → FINEXIT; **052/093 targeted PASS, GO RC=0012**. |
| 12 | BCPLIO output buffer full | Record-capacity failure; not necessarily same output as stack overflow | IOSTOP → STOPENT → FINEXIT; test 113 covers rejection; inspect actual message rather than infer from RC. |
| 16 | GTOOBIG, exported global capacity exceeded | No standard diagnostic asserted | Source path RELMEM; not focused GO-tested. |
| 20 | NOSTART, missing application START | No standard diagnostic asserted | Source path RELMEM; not focused GO-tested. |
| 24 | GNOCORE, startup GETMAIN failure | No initial block acquired | Direct MVS return; not fault-injection-tested. |
| 36 | STKFORM, invalid checked-frame metadata | No reliable buffered-output guarantee | Direct abnormal completion bypasses FINEXIT; source evidence only. |
| 36 | BADRETN, unexpected START return | No standard diagnostic asserted | RELMEM path; source evidence only. |

**Evidence levels:** executable (targeted named test), integrated (full native candidate panel), or source-only (not exercised under an induced failure). Source-derived RC numbers are not a claim of observed execution.

**Historical comparison:** documented historical BLIB stack-overflow system code X'0D3' and eventual STOP(100) do not establish that the D7 runtime implements historical ABORT behavior. D7's **approved** policy is GO RC=12. MVS ABEND labels (such as S0C4/S322) are different mechanisms, not entries in the runtime RC register.

**Future maintenance:** add an entry or update existing entry when a runtime-generated exit is changed, document the producing source routine, observed output, exact cleanup path and executable evidence. Keep user-defined STOP(N) separate. This register fulfills the M2.1 Gate B commitment to consolidate RCs by Gate F.
