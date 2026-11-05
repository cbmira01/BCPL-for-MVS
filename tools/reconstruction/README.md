# Clean-room reconstruction — Step 1 (read-only)

`tools/reconstruction/plan` is the first stage of the approved [clean-room automation decision](../../packaging/distribution/clean-room-reconstruction-automation-decision-20261104.md).
It is a **planner only**. It does not request approval, start TK5, write files, submit JES jobs, purge datasets, or run regression tests.

From a clean `main` checkout:

```sh
tools/reconstruction/plan
tools/reconstruction/plan --dry-run
tools/reconstruction/plan --probe
```

The default and `--dry-run` are equivalent. `--probe` additionally performs read-only Docker-container and TCP endpoint checks; it does not submit an MVS job or establish an authenticated MVS session. A successful probe is **not** evidence that a destructive reconstruction is safe to start: active JES writers and dataset state will need separate protection when the execution stage is implemented.

The output identifies the exact Git revision and source-dirty status, managed MVS dataset names derived from the effective `dspal` configuration, tracked and generated source counts, host workarea cleanup entries, rebuild order, and blocked prerequisites. Secrets are never printed. Use the independently executable `dspal purgebcpl --show-jcl` and `dspal initbcpl --show-jcl` commands to inspect redacted JCL.

**Error status:** 0 means read-only preflight passed; 2 means it is blocked. No status authorizes reconstruction. The tool never changes managed datasets or accepts a confirmation flag.

## Offline tests

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_reconstruction_plan.py' -v
```

The test fixtures use isolated Git repositories and fake `dspal` configuration. They do not contact Hercules or MVS. The [manual reconstruction guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md) remains authoritative until execution automation is separately implemented, tested, and accepted.
