# Native suite coordinator (Stage 2B/2C)

`run-suite` reads `tests/suites/*.tsv`, validates their static case ownership,
and invokes existing `tools/bootstrap/run-production-regression` or
`tools/bootstrap/run-installed-r5-t1-regression` per selected native case.
It is a host-side selection/accounting adapter, not a replacement compiler,
JCL generator, MVS backend or MR10 runner. See [suite contract](../../tests/README.md).

Check offline with:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_stage2b_suite.py' -v
tools/tests/run-suite --check
tools/tests/run-suite --list
```

**`--run` submits JES jobs and requires separate authorization.**
