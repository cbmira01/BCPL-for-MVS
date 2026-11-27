# DR.5 — First clean-room reconstruction attempt stopped at BLIBBLD

**March:** DR.5 — Validation and Reconciliation (IN PROGRESS)  
**Date:** 27 November 2026 EST  
**Source revision:** `7b335e2932a82734113c60f62bffb9bd8df1ec6b`  
**Evidence:** `mvs-state/dr5-clean-room/rebuild.log`

Owner authorized the unattended batch clean-room reconstruction as the first of three distinct remaining target gates. The owner-reported shell transcript establishes two fresh JES2 idle responses before the rebuild, presence of both previously preserved DEBUGINT result files, and execution of `tools/reconstruction/rebuild-from-source --unattended --batch-populate`. Guide Step 7 completed RC0. Guide Step 8 stopped at the first job, BLIBBLD, launcher JOB 1378 / payload JOB 1379, because the submit helper reported JOB RESULT: FAILURE despite HIGHEST RC: 0000.

| Observed step | Program | RC |
| --- | --- | --- |
| COMP | ICINT19 | 0000 |
| PREPASM | IFOX00 | 0000 |
| PREPLK | IEWL | 0000 |

The summary reported ABEND detected and one or more bypassed steps, no assembler flags, highest assembler severity zero. The next step in the tracked [BLIBBLD job](../../../bootstrap-toolchain/jcl/blibbld.jcl) is FIXASM, which executes the temporary BLIBPREP load module. The later steps are ASMBLIB and INSTALL. The exact failing step, completion code, and cause require the retained JES report; do not infer a particular ABEND from the summary alone. The driver stopped at Step 8 RC1; total elapsed 6m 34s, rebuild RC1. No successful clean-room acceptance, independent installed inventory or consolidated regression is claimed. The previously accepted focused DEBUGINT verification remains historical evidence, not verification of the newly reconstructed target.

Preserve JOB 1379's report under the existing evidence directory, review its actual JES/system diagnostics and the tracked JCL before proposing a correction. Do not replay the rebuild or submit later steps as an unapproved resume. Any further destructive reconstruction requires a reviewed disposition and fresh authorization. No production code or JCL changed by this evidence record.

## Actual JES diagnostic and narrowed investigation

Owner supplied the retained JOB 1379 report extracts: IEC020I 001-4 in BLIBBLD FIXASM RAW, device 292, volume WORK03, temporary dataset SYS26331.T222221.RA000.BLIBBLD.CODE. IEC020I reports DCB EROPT=ABE or invalid code and/or missing SYNAD exit; IEF450I and IEF472I confirm S001 U0000. ASMBLIB and INSTALL were flushed. The dataset was subsequently deleted; no BLIB installation occurred in this payload. The report is retained at mvs-state/dr5-clean-room/job-1379-BLIBBLD.log.

The tracked BLIBBLD JCL is byte-identical (Git blob 01eb17f93b3ae5e08d8ac81a455325d1e50f6e9e) to the accepted CO.5 clean-room revision 788616e6d34325cbe6a9473edcc6be340da3e577. The ICINT19 assembler source also matches that revision. The bootstrap host and demotion generator have changed for DR.5's accepted compiler stream and newline work; this does not by itself establish a causal relationship. The compiler writes temporary FB80 CODE with BLKSIZE=80; FIXASM uses QSAM GET with the inherited dataset DCB attributes. S001-4 identifies the error disposition, not the underlying physical or record-format cause. Do not suppress the failure by changing EROPT to ACC or SKP. Obtain console evidence around JOB 1379 and the affected device/volume, and the compiler completion/allocation messages from the saved report before deciding on any new JCL, diagnostic or rerun. No code change or new submission is authorized by this record.
