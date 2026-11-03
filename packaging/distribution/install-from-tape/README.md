# Install from tape

Consumer-side source intended to be carried on distribution media.

- `jcl/`: MVS dataset allocation, IEBCOPY restore, and verification jobs.
- `scripts/`: installation-support source, if needed; any tape-resident executable dependency must be available on the target MVS installation.
- `tests/`: clean-target restoration and verification cases.

The installer must be usable without GitHub, WSL, Python, or project development utilities. The tape bootstrap arrangement must make installation instructions and JCL accessible before BCPL is installed. No executable installation procedure or overwrite policy is approved yet.
