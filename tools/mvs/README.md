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
