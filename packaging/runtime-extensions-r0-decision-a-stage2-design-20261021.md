# Milestone Runtime Extensions — R.0 Decision A stage-2 design review

**Date:** 21 October 2026. **March:** **R.0 — Evidence and contract (open)**.
**Disposition:** **Stage-2 MVS evidence observed**. Calibration **JOB 2217 PASSED** with IEBCOMPR SAME RC=0000, DIFFER RC=0008 and independently reviewed IEB221I inequality. Member comparison **JOB 2218** assembled 18 records and returned IEBCOMPR RC=0008: **strict binary inequality**, caused solely by one EBCDIC day digit in the OBJ END record. The owner approved a *separate, narrow* END run-day exception (columns 50–52 only); the [reproducible report audit and evidence](runtime-extensions-r0-decision-a-jobs-2217-2218-evidence-20261021.md) classifies **object content equivalent except assembler run-day**. This does **not** establish historical build-source provenance. `BOOT_OBJ` remains read-only.

## Question and distinction

Can a freshly assembled **relocatable FB/80 object deck** be shown
identical, record for record and byte for byte, to the currently
installed corresponding `BOOT_OBJ` member? Success would prove
identity of the two **observed logical-record streams at comparison
time**—not their historical source-of-build chain, and not identity
of load modules. The [17 October clean-room acceptance](clean-room-mvs-reconstruction-acceptance-2026-10-17.md)
records baseline `04c74af8b07b5cdc2aaec44d79f020a848cb7e65`
and runtime build JOB 8744; it does **not** include incumbent
binary hashes. Later rebuild/replacement history must be reconciled.

## Recommended candidate: BCPLMEM, then expand only if proved

`BCPLMEM` has Git-tracked source
`bootstrap-toolchain/asm/bcplmem.asm` and a canonical production
IFOX step `ASMMMEM` in
[`bootstrap-toolchain/jcl/bldbmain.jcl`](../bootstrap-toolchain/jcl/bldbmain.jcl).
Reproduce `PARM='OBJECT,NODECK,LIST,XREF(FULL),ESD,RLD'`, the
`SYS1.MACLIB` macro library, and the `SYSGO` temporary
FB/80 dataset (LRECL 80, BLKSIZE 800). **Omit all `PUT*`
installation steps.** The existing `BOOT_OBJ(BCPLMEM)` must
be used solely as a **DISP=SHR input**. No production PDS
member may be written or replaced.

**Preferred utility for testing:** `IEBCOMPR`.
Modern IBM DFSMS documentation describes an 80-byte-record-compatible
logical-record comparison: two sequential inputs match only when
corresponding records and counts match. Documented modern IEBCOMPR
RC=00 means equal; RC=08 means unequal; RC=12 denotes error.
IBM cautions **not** to use IEBCOMPR for *load modules*. Our target
is a **relocatable object deck**, not a load module. Importantly,
none of these current z/OS claims has yet been exercised in the
project's historical **MVS 3.8J/TK5** environment. In particular,
availability, actual return codes and treating `PDS(member)`
as sequential IEBCOMPR input are **still unverified**.

## Staged, read-only verification (implemented for MVS testing)

1. **Record provenance and datasets.** Save Git HEAD, clean/dirty
   status, exact Git source revision and SHA-256, assembler/options,
   resolved `BOOT_OBJ` DSN/volume, PDS member and FB/80 attributes.
   Do not assume today's Git HEAD is the 17 October accepted build.
2. **Calibrate before reading the incumbent.** Compare two known-
   identical **temporary** FB/80 object datasets: require the
   locally observed equal status. Then use a deliberately different
   *valid* temporary FB/80 object: require a detected mismatch and
   identify its observed RC and message. Abort if `IEBCOMPR`
   is unavailable, behaves unexpectedly, or cannot compare
   binary records correctly.
3. **Rebuild BCPLMEM into a disposable FB/80 object dataset**
   using the exact canonical source/options, no PDS output DD;
   require IFOX RC=0000 and zero flagged statements. Capture
   source revision and job/step evidence.
4. **Compare `BOOT_OBJ(BCPLMEM)` and the fresh temporary deck.**
   Use an input-only `SYSUT1` DD with `DISP=SHR`, a second
   input-only DD for the temporary deck, `SYSPRINT` for
   diagnostics and `SYSIN DD DUMMY`, adapting details only after
   utility behavior is verified. Check that both inputs are
   nonempty FB/80 and record counts match; compare **all 80 raw
   bytes of every logical record**, including EBCDIC, zeros,
   control bytes and trailing spaces.
5. **Preserve evidence and do not deploy.** Record actual JCL
   profile, job number, utility report, RC, number of records,
   exact member/source identity, tool options and source hashes.
   An equal result supports current record-byte identity;
   a mismatch is evidence for investigation, **not a reason
   to install replacement objects**.

If `IEBCOMPR` cannot accept the object-PDS member as input,
consider copying the incumbent **read-only** with IEBGENER to
a second disposable FB/80 sequential dataset, then using
IEBCOMPR on two sequential inputs. This fallback needs its
**own binary-copy fidelity calibration**; neither SYSOUT text
nor `dspal cat/get` is acceptable for an object deck.
If the utilities are inadequate, stop and review an IFOX
binary-record comparator design before coding one.

## Proposed acceptance boundary

Positive same/same test, negative known-different test, and actual
BCPLMEM comparison must all have observed results and be interpreted
against the tested utility's RC semantics. Zero-length input or
accidental matching empty datasets must not pass. Confirm *every*
accepted-OBJ DD remains input-only, and the resulting job has no
`PUT*`, no `IEBGENER` target in `BOOT_OBJ`, and no
load-module PDS output there. Preserve binary data on MVS.
Load-module comparison is out of scope.

**Owner decision:** the narrow **BCPLMEM + calibrated IEBCOMPR + temporary rebuild + read-only installed-member comparison** approach was approved for implementation. The probe stages separate `R0BICAL` and `R0BIMEM` jobs. `R0BIMEM` cannot be submitted through the runner until `R0BICAL` has actually run and its IEBCOMPR `SYSPRINT` has been reviewed. Compare equal is expected RC=0000, intentionally different RC=0008; the runner checks the step codes and nonempty punched objects but **does not automatically interpret RC=0008 as proof of unequal bytes**. User-confirmed calibration remains required. No new march number was created; actual MVS acceptance and installed binary identity remain pending.

## External utility references (modern IBM; not evidence of TK5 support)

- [IBM IEBCOMPR compare program](https://www.ibm.com/docs/en/zos/3.2.0?topic=utilities-iebcompr-compare-data-sets-program)
- [IBM IEBCOMPR examples](https://www.ibm.com/docs/en/zos/2.5.0?topic=program-iebcompr-examples)
- [IBM DFSMSdfp utility return codes](https://www.ibm.com/docs/SSLTBW_3.2.0/pdf/idau100_v3r2.pdf)

**R.0 remains open; R.1 has not started.** Strict byte identity remains false for JOB 2218; the narrow date-field content-equivalence decision is independent of binary hashing.
