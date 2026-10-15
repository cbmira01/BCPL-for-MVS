# Twelve input streams

This probe opens `DD01` through `DD12` at the same time. It reads one record from each and closes each stream. Every fixture contains its stream number (for example, `DD01` contains `STREAM 01`).

| Check | Expected |
| --- | --- |
| Open | `OPENED 12 STREAMS` |
| Read | Each DD reports its own `STREAM NN` text |
| Close | `ALL 12 STREAMS READ AND CLOSED` |

Run with `tools/mr10/compile-and-run` and twelve `--dd DDNN=mr10-kit-compiler/tests/07-many-streams/ddNN.txt` arguments. This is a historical ICINT dynamic-stream stress test rather than one of the 12 default regression-panel cases.
