# TA.0 read-only manifest validator

Run from the repository root (development host, PyYAML required):

```sh
python3 -B tools/distribution/validate-manifest.py
python3 -B tools/distribution/validate-manifest.py --audit-json
python3 -B -m unittest discover -s packaging/distribution/manifest/tests -p 'test_*.py' -v
```

The TA.0 prototype is read-only and has no JES, MVS dataset, tape or Git write operations.
The new `--audit-json` option derives a 127-member provenance worksheet: 110 Git-backed sources, 2 generated members, 15 resident binary members, and **all 127 redistribution reviews unreviewed**. No MVS build receipt is inferred. See the [recipient-JCL and provenance audit](../../packaging/distribution/manifest/ta0-provenance-and-dependency-audit.md).
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

## Selected release JCL dependency audit (TA.0)

```sh
python3 -B tools/distribution/audit-jcl-dependencies.py
python3 -B tools/distribution/audit-jcl-dependencies.py --json
python3 -B tools/distribution/audit-jcl-dependencies.py --strict
```

The default read-only scan checks the **ten selected Git JCL source members** against the proposed TA.0 inventory and `dspal` Git paths. It rejects undeclared datasets, members, program dependencies and MR10/native cross-profile references. Original jobs have no standalone `JOB` cards and hard-code development `HERC02`; consequently the `--strict` command **must fail** until release JCL is separately adapted.

For an inspection of site-adapted *files*, use `--hlq SITEABC --strict --dspal <stage-map.yaml> --root <stage-root>`; the specified development-host map must identify the corresponding staged JCL paths and other selected source inputs. The scanner does **not** create, adapt, submit or validate execution of an MVS job. Program availability, full JCL semantics, site allocation/no-overwrite safety and target MVS verification remain acceptance gates.

The 17 November GitHub review found 260 selected permanent-dataset references, zero unselected or cross-profile references, and seven `SYS1.MACLIB` dependencies. The two offline TA.0 test modules contain **40 passing synthetic-fixture cases**; see [audit details](../../packaging/distribution/manifest/ta0-provenance-and-dependency-audit.md).

## Exact selected binary build-chain review (TA.0)

```sh
python3 -B tools/distribution/audit-binary-build-chain.py
python3 -B tools/distribution/audit-binary-build-chain.py --json
python3 -B tools/distribution/audit-binary-build-chain.py --strict
```

The first two commands audit the fifteen selected object/load members against the reconstructed Git-backed source/build JCL and `tools/reconstruction/verify.py` (AST inspection; no code execution). The last intentionally **fails closed** because candidate-specific IFOX/IEWL/JES, accepted object readback, load-library execution and redistribution records have not been supplied.

To additionally check the exact **member names** in *saved read-only MVS listing outputs*, supply `--inventory-dir <directory>`; that directory must contain `MR10_OBJ.txt`, `MR10_LOAD.txt`, `BOOT_OBJ.txt`, `EXT_OBJ.txt` as unmodified output from `dspal ls <key>` on the intended MVS system. This tool does not contact MVS, collect those outputs, or equate a matching directory with binary-byte acceptance.

The [TA.0 binary provenance review](../../packaging/distribution/manifest/ta0-provenance-and-dependency-audit.md) documents the limitations. The offline TA.0 suite contains **55 synthetic-fixture cases**. There is no license/rights sign-off, no tape producer or installation approval, and no TA.0 formal closure.
