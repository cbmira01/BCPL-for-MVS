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
