# Milestone QSAM — Q.5 packaging review and consolidated native campaign

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release** (historical campaign; CLOSED by owner 1 November 2026)  
**Status (31 October design):** Non-destructive campaign prepared, not yet MVS-executed at the time of that design. **Update (1 November):** Direct native `Q5PKG` JOB 8155 completed 17 steps RC=0000; the owner reported the production 00–176 panel at 176 PASS / 0 FAIL / 1 expected SKIP 083 on prior revision `72a5da31`. These results do **not** constitute installed-object proof, clean-room proof, or Q.5 closure. The subsequent [installed reconstruction/verification design](qsam-q5-installed-reconstruction-20261101.md) now stages Git manifest, installation JCL, and read-only installed linkage JCL for a separately authorized future MVS run.  
**Baseline:** GitHub main through JOB 8154 real GETMAIN acceptance, revision 6e0d38bce06f10848c9bf7e82f23039371532039.  
**Owner authority:** Commit reviewed project files and request native MVS job runs. No permission to overwrite or purge installed MVS datasets is inferred.

**Later owner disposition (1 November 2026):** Q.5 and Milestone QSAM were [closed with explicit qualifications](../../qsam-q5-closure-20261101.md) after the [later full-panel failure and focused rerun](qsam-q5-regression-evidence-20261101.md). All statements below that Q.5 remained open or that installation was a future gate describe this **earlier design stage**, not a later successful installed-mode verification. The closure does not certify Q5QVFY or permanent BCPLQSAM promotion.

## Packaging decisions

1. **Public identity.** BCPLQSAM remains the optional System Extension at QSAMSVC/G!200, using the accepted BCEX/BCRG v1 registrar, dispatcher and finalizer. Preserve the source and ABI of the accepted Core Runtime, Base Library, Cambridge bootstrap compiler and BCPLQSAM.
2. **Source and binary.** The authoritative assembler is bootstrap-toolchain/extensions/bcplqsam/bcplqsam.asm; its public BCPL declarations are in bcplqsam.h. IFOX must produce relocatable FB80 object records on MVS. No binary build artifact is authoritative in GitHub or on the host.
3. **Installed destination (future gate).** Use the existing manifest-managed R.5 optional package convention, EXT_OBJ (HERC02.BCPL.EXT.OBJ at TK5), with Git-backed EXT_ASM and EXT_SOURCE text mirrors. Preserve installed EXT_OBJ(BCPLDEMO). The accepted EXT_MAC catalog currently knows BCPLDEMO; update EXT_MAC(BCXCAT) for BCPLQSAM only after separate review of the exact member bytes and recovery procedure.
4. **Package selection.** The temporary Q.1 catalog uses QSMOBJ. A true PDS member link requires a catalog entry naming EXTLIB, which is the selected IEWL object-library DD. The first campaign therefore substitutes a **test-only BCXCAT entry** for BCPLQSAM; it does not modify installed EXT_MAC.
5. **No-destructive-test boundary.** Prepare the complete campaign from source-controlled files and the resident demoted Cambridge compiler, using an MVS **temporary** PDS, temporary relocatable records and temporary load modules. Do not catalog permanent datasets, alter BOOT_OBJ/BOOT_DEVOBJ/EXT_OBJ/EXT_MAC, or purge the 28 managed PDSes merely to run Q5PKG.
6. **Native acceptance authority.** Real JES/IFOX/IEWL/IEBGENER/IEBCOMPR/GO reports, exact source Git revision and output records are required; Python deck construction is not MVS proof.

## The consolidated candidate job: Q5PKG

The preserved direct native JOB deck is
[`bootstrap-toolchain/jcl/history/q5pkg-native.jcl`](../../../bootstrap-toolchain/jcl/history/q5pkg-native.jcl).
It is a historical Q.5 acceptance artifact, not a manifest-managed
`BOOT_JCL` production installation job. Moving it into `history/`
does not change the recorded JOB 8155 evidence or authorize a rerun.

One Q5PKG payload executes the following in order, after two resident compiler jobs produce the native application CODE:

| Native step group | Purpose |
| --- | --- |
| SASMA, SASMN, SASMR, SASMQ | IFOX selected application, native BCPLMAIN, BCPLRGS and Git-controlled BCPLQSAM |
| SALLOC, SPUTQ, SREADQ, SVERIFY | Allocate temporary PDS; binary-install &&Q5QOBJ(BCPLQSAM); read back; IEBCOMPR exact records |
| SASMG, SLKED, SGO | Test-only BCXREQ BCPLQSAM, selected IEWL INCLUDE EXTLIB(BCPLQSAM), native QUERY |
| NASMA, NASMN, NASMR, NASMG, NLKED, NGO | Independent native BCPL application with empty extension selection, IEWL and GO |

**17 named native steps** in a **single** Q5PKG job. No unit/probe proliferation.

The selected application is existing numbered regression **163 — Q.4 QUERY capabilities**, whose current expected output is:

    BCPLQSAM Q4 QUERY CARRIAGE PASS

The unselected application is existing numbered regression **146 — empty optional-extension selection**, whose current expected output is:

    R5 EXT 146 PASS

These are deliberately current accepted fixtures. Do not use the older Q.1 or Q.2 QUERY tests: they contain superseded opcode/capability expectations.

The preparer is bootstrap-toolchain/extensions/bcplqsam/prepare-q5-release-campaign.py. It builds JCL from the established Q.1 and R.5 job generators, preserves the independent BCPL compiler images, validates fixed-column cards, and refuses to overwrite an existing deck. Its output is workarea/bcplqsam-q5/q5pkg.jcl. The executable campaign uses only temporary object/library data sets; it does not install EXT_OBJ.

## Operator workflow and evidence

From the correct GitHub main checkout, first run its non-submitting syntax/template check:

    python3 bootstrap-toolchain/extensions/bcplqsam/prepare-q5-release-campaign.py --check

Use the resident **demoted Cambridge compiler** to compile both tracked BCPL application sources (two native compiler jobs, not test probes). Each must pass before proceeding:

    python3 tools/bootstrap/compile-mvs bootstrap-toolchain/regression/163-qsam-query-capabilities/source.bcpl --job-name Q5SCOMP --output workarea/bcplqsam-q5/release-selected.asm

    python3 tools/bootstrap/compile-mvs bootstrap-toolchain/regression/146-optional-empty/source.bcpl --job-name Q5NCOMP --output workarea/bcplqsam-q5/release-unselected.asm

Then generate the single native Q5PKG deck:

    python3 bootstrap-toolchain/extensions/bcplqsam/prepare-q5-release-campaign.py --prepare --selected workarea/bcplqsam-q5/release-selected.asm --unselected workarea/bcplqsam-q5/release-unselected.asm

Submit the generated deck **once** via tools/mvs/submit-jcl, retaining the printed job number, SHA-256, full job report, JES summary, and raw console/hardcopy logs. A compilation error, JCL error, abnormal completion or missing BCPL output is failure evidence, never permission for an automatic retry.

### Q5PKG acceptance

- Q5SCOMP and Q5NCOMP each report successful ICINT19 compilation and CODE recovery, with source hash, native CODE SHA-256 and real compiler job IDs.
- All 17 Q5PKG steps execute with RC=0000, including the four temporary-PDS packing/verification steps. All IFOX assemblies report zero flagged statements and highest severity zero.
- SGO and NGO each emit their own exact standalone PASS record, once, and both normal FINISH paths succeed.
- Review actual IEWL MAP/XREF and the macro/PUNCH result: selected SLKED includes the BCPLQSAM descriptor/dispatcher using EXTLIB(BCPLQSAM) from the temporary binary PDS; NLKED has no BCPLQSAM include, descriptor, dispatcher or G!200 registration.
- Report any unexpected IEWL warning, binder unresolved external, IEBGENER/IEBCOMPR discrepancy or MVS resource failure separately. No installed PDS is changed.

**If Q5PKG passes:** claim only a reproducible **temporary-PDS optional binary packaging and link-edit** candidate, not permanent installation, full native regression, or Q.5 release.

## Subsequent release gates

1. **Specific permanent installation decision**: owner review of manifest changes and exact EXT_ASM(BCPLQSAM), EXT_SOURCE header, EXT_OBJ(BCPLQSAM) and EXT_MAC(BCXCAT) member updates, their ordering, readback and failed-install recovery. BCPLDEMO and existing Core Runtime/Base Library members must remain intact. No existing permission to request JES is a blanket authorization for this write.
2. **Installed-mode MVS gate**: install only after approval; independently link selected and unselected native clients from read-only EXT_OBJ and resident EXT_MAC macro sources. Inspect IEWL MAP/XREF and actual RUN output.
3. **Clean-from-Git reproduction**: perform a separately reviewed clean rebuild of the optional package and dependencies, noting the exact revision, temporary and permanent objects and all JES IDs. Do not run the older destructive 28-PDS purge unapproved.
4. **Fresh regression**: run QSAM-focused **163–176**, then the full numbered **00–176** native panel on the accepted revision/configuration. The previously documented expected SKIP 083 remains the only planned skip. The 30 October results are historical baseline, not this Q.5 release panel.
5. **Closure**: record all evidence, retained error-path limitations (in particular genuine exceptional CLOSE and unrecovered abends), the installed-object disposition and explicit owner acceptance. Q.5 and Milestone QSAM remain open until that decision.

## Authority references

- [Milestone QSAM](../../milestone-qsam.md)
- [Runtime Extensions R.5 packaging](../runtime-extensions/runtime-extensions-r5-packaging-and-regression.md)
- [R.5 installation design](../runtime-extensions/runtime-extensions-r5-installation-design.md)
- [Git and MVS authority](../../git-mvs-authority.md)
- [Q.5 resource-exhaustion acceptance](qsam-q5-real-getmain-acceptance-20261031.md)

## One-shot campaign runner

The tracked tools/mvs/run-q5-release-campaign script implements the operator sequence above. Invoke it using Bash, not by sourcing it into an interactive shell. It reserves workarea/bcplqsam-q5/q5pkg-attempt once, records Git HEAD and source hashes, performs the non-submitting JCL check, invokes two independently named resident compiler jobs, prepares and submits Q5PKG only if both compile successfully, and stores the native job summary, complete printer report and compilation evidence. It never retries an uncertain JES submission or overwrites an earlier attempt. It prints only a preliminary native PASS: IEWL MAP/XREF must still be reviewed before acceptance.

Do not invoke the runner for a second attempt after any failure; first preserve and analyze the complete original evidence. Changes and a new job attempt require a separate uniquely identified continuation.
