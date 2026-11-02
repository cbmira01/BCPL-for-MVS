# MVS tools

Common Hercules/TK5 and MVS operational tools: start/shutdown, JCL submission, JES reporting, and IFOX job generation.

The root `tools/` commands are compatibility launchers; the underlying `make-asm-job.py` helper remains accessible from its original path for callers importing it explicitly.

Use [`mvs-console`](mvs-console) for one-shot and interactive Hercules/MVS/JES2 console commands, contextual help and tape-device handling. See its [user guide](mvs-console-README.md). The console interface operates on the live system; it is not a substitute for the 3270 operator terminal.
