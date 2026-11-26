# DR.5 — Focused language verification candidate

Baseline: `7e3e977f4feccb528ff259547dce90cee050dca3`. This is an engineering probe, not a numbered regular regression or accepted compiler specification. It uses the same BCPL source in both compiler environments. The owner approved preparation of focused verification and commits; actual JES execution remains operator-controlled.

| Record | Independent expectation / distinguishing observation |
| --- | --- |
| ASSIGN | 20 20 if stores are sequential; 20 10 if RHS values are captured first |
| BOUND | 6 0 if the original upper bound 3 is retained after B is changed to zero |
| STEP | 9, from 5 + 3 + 1 |
| BRANCH | 0: false left operand bypasses BUMP in command condition |
| VALUE | 0 1: word-valued AND evaluates BUMP, but result is false |
| OR | 1 1: true left operand bypasses BUMP in command condition |
| SIGNED | -3 -2: truncation toward zero, remainder has dividend sign |
| SHIFT | 48 1: logical right shift of all-one word by 31 |
| END | Final completion marker |

The golden is an independent source-derived **hypothesis**, not an observation. A different complete result is evidence to reconcile, not permission to adjust the golden silently. No zero-divisor, zero-step, invalid address, stack fault or device tests. Compiler option/GET and negative diagnostic probes remain separate pending this result.

The driver uses installed MR10_LOAD(ICINT19), the tracked MR10 phase decks, installed CAMBCOMP, explicit slash-filled /N/ parameter record, IFOX and IEWL with read-only BOOT_OBJ production linkage. It creates only temporary MVS execution datasets and private host evidence. The helper's private numeric naming parameter 900 selects RG900R; no regular case, registry allocation or march is created. The ordinary regression coordinator and manifests are unchanged. Run serially with JES idle and the accepted development environment installed; do not replay an uncertain submission. The generic driver uses the existing full-printer compiler/MR10 retrieval path and a bounded native GO cursor; combined report evidence is not physical DD attribution.

Host-only `python3 tools/checks/run-dr5-language-verification.py --check` validates fixture format and synthetic oracle parsing. Operator-authorized `--run` submits one MR10 job and at most two native jobs; each path is assessed independently, even if the other fails. It preserves unique private evidence directories under workarea/dr5-language-verification, including generated JCL (may contain credentials), assembler, job summaries/reports and result.json. Return only result.json and, for discrepancies, relevant sanitized JES evidence. Never commit private receipts.

No fresh target execution or installed-image identity is established by preparing this candidate. Exact phase/step and observed record gates must pass before documenting a result. The source/oracle deliberately omit broad compiler certification and pathological inputs.

## First execution and native-only diagnostic follow-up

Owner-reported results, source revision `edabc655d5b4df03b9fe7d686f479c28fe71cc06`, source SHA-256 `d22b33e5f558f6825d99c129e6a96c373631a7340ce574af24a071cefa34a407`, oracle SHA-256 `d078e20ee411412dd25b9690797215f1483ac834e2117c51fccb7cf3e691a7e3`, evidence directory `workarea/dr5-language-verification/run-4lcfzuag`: MR10 job 9489 passed all nine records with all steps RC=0; Cambridge compilation job 9490 passed COMP and SVCODE (RC=0, execution CODE=0); native job 9491 passed ASMAP and LKED (RC=0) but GO returned 12. Seven complete RP records matched ASSIGN through SIGNED, then a partial `RP: DR5` record; no SHIFT or END completion. The original native run and paired result remain FAIL. No installed-image identity is inferred.

The owner provided generated assembly for job 9490. SLL 8,4(0), SRL 7,31(0) and LR 9,7 are consistent with the expected 48 and 1, and the SHIFT format's displacement 156 and counted EBCDIC bytes are consistent with the intended 20-character format. This is not native execution proof. BCPLIO IOWFULL invokes STOP(12), which is consistent with, but does not establish the cause of, GO RC=12.

The separate `native-shift-diagnostic.bcpl` retains the seven preceding probes, computes shifts into independent locals, checks 48 and 1 before formatting (STOP(16) on mismatch), emits the ISO SHIFT OK record with WRITES, checks the counted format length (STOP(20) on mismatch), then uses WRITES to print the format literally and WRITEF to format the values. Its independent 11-record hypothesis is `native-shift-diagnostic.expected`. A pass establishes the modified probe only, not a repair of the original failure. The driver now retains the raw completed report even when a JES return code is nonzero, with job number and step/record evidence in the failure reason. The operator-authorized `--run-native-diagnostic` submits only a fresh Cambridge compile (DR5CISO) and private native run (RG901R); 901 is a naming argument only. Do not repeat the successful MR10 path. Offline source/oracle/parser checks and a synthetic failed GO receipt retention check passed; actual diagnostic MVS execution is pending.
