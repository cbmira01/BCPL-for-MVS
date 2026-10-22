# Milestone Runtime Extensions — R.2 interoperability probes

**Status:** R.2 development, not accepted. **First increment:** BCPLDEMO
as a real, project-assigned G!203 extension; second independent extension
and 0/A/B/A+B acceptance matrix are **not implemented in this increment**.

The first test uses `demo.bcpl` (a separately compiled BCPL caller),
`registry-demo.asm` (real BCRG selection and required-package declaration),
and the [BCPLDEMO maintained example](../../extensions/bcpldemo/README.md).
The single resulting link uses the same R.1 `RGINIT` and temporary
`BCPLMAIN` adaptation proved in the completed R.1 campaign.

To inspect the generated in-memory test deck, run:

```sh
python3 -m unittest discover -s \
  bootstrap-toolchain/probes/r2-interoperability -p 'test_*.py' -v
python3 bootstrap-toolchain/probes/r2-interoperability/make-job.py --check
```

For the end-to-end MVS candidate procedure, expected GO marker, and
resource guarantees, see the BCPLDEMO README. **No evidence is claimed
until actual MVS JES and IEWL results are reviewed.** Do not reuse G!203
for the second test extension; it remains BCPLDEMO's permanent assignment.
