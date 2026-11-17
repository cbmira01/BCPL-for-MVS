# Install from tape

Consumer-side source intended to be carried on distribution media.

- `jcl/`: MVS dataset allocation, IEBCOPY restore, and verification jobs.
- `scripts/`: installation-support source, if needed; any tape-resident executable dependency must be available on the target MVS installation.
- `tests/`: clean-target restoration and verification cases.

The installer must be usable without GitHub, WSL, Python, TSO or project development utilities. The tape bootstrap arrangement must make installation instructions and JCL accessible before BCPL is installed. Per the [approved distribution direction](../native-cambridge-compiler-distribution-decisions-20261108.md), the recipient supplies a site-specific HLQ and the installation uses the same position-based `BCPL.BTnnnn` mapping as the producer. The initial read-only bootstrap and all installation procedures remain to be implemented and verified. No executable installation procedure or overwrite policy is approved yet.

The [expanded release scope](../release-payload-scope-decision-20261116.md) requires **independent MVS-only installation and verification** for both the native Cambridge Compiler and the MR10 Kit Compiler. MR10 must ship with its 11 language demonstrations, 17 BCPL demonstrations, and 12-case regression panel. Its existing `MRREGRES` job runs on MVS. The [subsequent owner decision](../mr10-regression-exp-manual-verification-decision-20261116.md) requires fixed `EXP:` and actual `RP:` report records and **human per-case review of all 12 plus interpreted `CODE=`** on MVS, with recorded PASS/FAIL and sign-off; an automatic MVS semantic comparator is **not** required. This report format and manual acceptance procedure remain to be implemented and proven. Host-side `dspal` and Python verification are not acceptable recipient dependencies.

