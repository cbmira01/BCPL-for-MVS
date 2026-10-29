# Milestone QSAM — Q.2 closure (29 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** **Q.2 — Fixed logical records**
**Disposition:** **CLOSED — 29 October 2026**, on the project owner's
explicit direction to add the regressions to the established panel and
close Q.2. **Q.3 has not been opened by this closure.**
**Implementation baseline:** GitHub `main`, Q2MIX commit
[`0ed178091764`](https://github.com/cbmira01/BCPL-for-MVS/commit/0ed17809176422e97a1beae976874e54c9e576ea),
including QUERY bitmap `X'1F'`, `QS_CAP_FIXED=1` and Q2MIX.
The subsequent numbered-regression integration commit changes no
BCPLQSAM implementation contract.

## Native acceptance evidence already observed on the resident target

These are the operator's actual MVS 3.8J / Hercules JES results, not
synthetic source checks. Generated JCL and object decks were temporary.

| JES job(s) | Native evidence | Result |
| --- | --- | --- |
| 6640 Q2FULL | F80/FB80 write, read/copy, private short-buffer retry, EOF, 23 record independent binary verifier | All 13 steps RC=0000; PASS |
| 6641 Q2SCOMP / 6642 Q2STOP | BCPL STOP(8), FB80 flush and independent assembler exact record/EOF verification | BGO RC=0008, VGO RC=0000; PASS |
| 6643 Q1NCOMP / 6644 Q1NEG | Native ordinary negative requests | Seven steps RC=0000; negative evidence checker PASS |
| 6645–6646 Q16FIN | Sixteen-handle FINISH lifecycle | Ten steps RC=0000; PASS |
| 6647–6648 Q16STP | Sixteen-handle STOP lifecycle | Nine steps RC=0000, GO RC=0008; PASS |
| 6973–6974 Q2QUERY | Six-word QUERY v1, supported opcode mask 31, fixed capability 1, vector boundaries | Seven steps RC=0000; PASS |
| 6975–6976 Q1OUT | Output OPEN/INFO/CLOSE and invalid WRITE semantics | Seven steps RC=0000; PASS |
| 6977–6978 Q2MIX | Required BCPLQSAM + installed read-only BCPLDEMO in a single BCPL application, interleaved dispatch and independent FB80 readback | BGO RC=0008, VGO RC=0000; BCPLREG 60 bytes; PASS |
| Production 00–162 | Native production runtime baseline | 162 PASS, 0 FAIL, 1 expected SKIP 083; RC=0 |

The Q2MIX source was committed at the baseline above. In the later
operator run, all six IFOX assemblies and two IEWL steps returned RC=0,
the native checker reported both BCEX descriptors and 60-byte BCRG,
and the independent FB80 verifier returned RC=0.

The ordinary Q.2 acceptance requirements—byte-accurate F/FB READ and
WRITE, sticky EOF, private undersized READ retry, fixed WRITE length
rejection, invalid handles, lifecycle and no regressions against the
accepted production runtime—were therefore evidenced before closure.

## Permanent numbered regressions added at closure

The existing numbered native regression framework is extended with:

- 163 QUERY fixed capability
- 164 negative caller
- 165 output lifecycle
- 166 sixteen-handle FINISH
- 167 sixteen-handle STOP
- 168 Q2FULL writer/reader/independent verifier
- 169 Q2STOP finalizer flush and independent verifier
- 170 Q2MIX interoperability with installed BCPLDEMO

The numbered runner uses the **same native Cambridge compiler, IFOX,
IEWL, JES2 and real QSAM operations**, not host-simulated results.
The original 00–162 execution path remains unchanged.

**Post-closure native regression verification — 29 October 2026:**
The operator executed the numbered **163–170** panel on MVS with
**8 PASS, 0 FAIL, 0 SKIP, runner RC=0**, including BCPLQSAM and
BCPLDEMO interoperability in case 170.

The operator subsequently executed the entire contiguous
**00–170 production regression panel**, reporting:

| Panel | PASS | FAIL | SKIP | TOTAL | Runner RC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Q.2 numbered 163–170 | 8 | 0 | 0 | 8 | 0 |
| Full production 00–170 | **170** | **0** | **1 (083)** | **171** | **0** |

The operator preserved the full-panel log at
`workarea/bcplqsam-q2/full-00-170/panel.log`, and the
focused numbered-panel log at
`workarea/bcplqsam-q2/numbered-163-170/panel.log`.
These are ignored local evidence artifacts, **not Git-tracked files**.
The recorded outcome comes from the operator's reported console output
(eight individual PASS lines and the full-panel totals), not an
independent per-case JES audit by the documentation author.

The regression integration is committed at
[`3bd532be3d39`](https://github.com/cbmira01/BCPL-for-MVS/commit/3bd532be3d39489b652b4c8713b4027eb9d7a8c1).
The expanded panel is no longer pending. Its actual result is
**170 PASS, 0 FAIL, 1 expected SKIP**, correcting the earlier
estimate of 169 PASS.

## Explicitly retained limits and deferrals

- No independent complete 16-CLOSE counter/WTO observation for STOP
  is claimed; a physical STOP flush was independently verified.
- Rare failed-OPEN/returned-CLOSE failure-injection behavior and
  cleanup-error precedence remain for hardening.
- Optional omitted-DCB geometry recovery, console-log normalization
  and broader period MVS size boundaries are not new Q.2 claims.
- RECFM V/VB and RDW handling belong to **Q.3 — Variable logical
  records**; FBA/SYSOUT and carriage control belong to Q.4.
- Production object promotion, packaging/reconstruction and broader
  hardening belong to Q.5; no BCPLQSAM MVS object was installed.
- The original 00–162 baseline validates accepted Core Runtime and
  installed optional extensions, not automatic BCPLQSAM installation.

## Owner decision

On 29 October 2026 the owner explicitly directed:

> I want regressions tests added to the panel, and Q.2 closed.

Accordingly **Q.2 — Fixed logical records is CLOSED** based on the
completed native acceptance evidence above, with subsequent numbered
and full-panel MVS verification also PASS. No additional milestone
or march identifier is introduced. The next march is still
**Q.3 — Variable logical records**, requiring its own authorization
before implementation.
