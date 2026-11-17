# TA.0 read-only manifest validator

Run from the repository root (development host, PyYAML required):

```sh
python3 -B tools/distribution/validate-manifest.py
python3 -B -m unittest discover -s packaging/distribution/manifest/tests -p 'test_*.py' -v
```

The TA.0 prototype is read-only and has no JES, MVS dataset, tape or Git write operations.
It validates the approved design selection against `config/dspal.yaml` without
making that development dataset map the release selection authority.

Expected result: 20 logical tape datasets, 127 selected PDS members
(79 MR10), last proposed alias `BCPL.BT0020`, `native_compiler: absent`.

The following check MUST fail on this non-candidate design inventory:

```sh
python3 -B tools/distribution/validate-manifest.py --release
```

The design contains no candidate version, source Git SHA, VOLSER registry reservation,
actual tape unload DCB, MVS binary readback receipts, complete member provenance
or redistribution approvals. The validator cannot itself demonstrate TA.1–TA.8
acceptance, producer/installer correctness or legal redistribution.

TA.0 is in progress; TA.1 is separately gated.
