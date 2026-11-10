# MVS tools

Common Hercules/TK5 and MVS operational tools: start/shutdown, JCL submission, JES reporting, and IFOX job generation.

The root `tools/` commands are compatibility launchers; the underlying `make-asm-job.py` helper remains accessible from its original path for callers importing it explicitly.

Use [`mvs-console`](mvs-console) for one-shot and interactive Hercules/MVS/JES2 console commands, contextual help and tape-device handling. See its [user guide](mvs-console-README.md). The console interface operates on the live system; it is not a substitute for the 3270 operator terminal.

Use [`tape-map`](tape-map) to display the labels of an existing AWS/HET
image under `mvs-state/tape/` without mounting media or submitting JES.
For example, from the repository root:

```sh
tools/mvs/tape-map bcpl-pdstest-20261108-01.aws
tools/mvs/tape-map --all bcpl-pdstest-20261108-01.aws
tools/mvs/tape-map --files bcpl-pdstest-20261108-01.aws
tools/mvs/tape-map --datasets bcpl-pdstest-20261108-01.aws
```

The default `--labels` option delegates to `docker exec mvs38j hetmap -l`
and reports `VOL1`, `HDR1`, `HDR2`, `EOF1`, `EOF2` where present.
The wrapper refuses missing files, paths outside the tape directory and
symlinks. It is a read-only host tool; see [tape-inspection notes](../../packaging/distribution/tape-inspection-capabilities-20261108.md).
Offline tests: `python3 -B -m unittest discover -s tools/mvs -p 'test_tape_map.py' -v`.

## Guarded JES printer window — opt-in trial

`printer-window.py` is an offline-capable byte cursor helper. Capture
before a job is submitted, then read only newly appended output while
validating printer identity, size and a short end-of-prefix digest.
An invalid cursor **fails closed**, never falling back to historical
jobs with reused JES numbers.

`submit-jcl`, `job-summary` and `dump-report-for-job` accept optional
`--cursor-file FILE`. Without it, the established full-printer
behavior is unchanged. The ordinary native regression harness and
the Cambridge compiler use this path **only** if the operator
explicitly sets `BCPL_PRINTER_WINDOW_TRIAL=1`; no JES is launched
by the cursor tool itself. See the
[trial design and authorization boundaries](../../packaging/operations/maintenance/jes-printer-window-opt-in-trial-20261110.md).

Offline tests:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_printer_window*.py' -v
```
