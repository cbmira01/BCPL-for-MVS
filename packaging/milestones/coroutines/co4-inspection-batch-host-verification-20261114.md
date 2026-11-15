# CO.4 — Live limit/allocator inspection: host verification

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.4 — Robustness and Edge-Case Verification (IN PROGRESS)
**Authority:** GitHub `main` after owner-reported three-case CO.4 PASS at
`976c20da29943a72867195a24e010afe4e395e1a`
**Evidence classification:** **HOST-CHECKED / NATIVE MVS PENDING**.

## Prepared candidate

The three independent BCPL fixtures in
`candidates/co4-inspection-batch/` are compiled with the accepted
Cambridge `/CN` options and accepted CO.3 BCPL library. A private IFOX
`CO4PROB` reader observes active STKLIM/APLIMIT, G54/G55, private
CURPTR, and the BCPLMEM `MEMSTAT` vector/byte counters; it is injected
into an ephemeral BCPLCO assembly deck along with the existing CO3DROP
extension and bound to **test-local G301**.

Only the third fixture temporarily redirects test-local G87 to a BCPL
proxy that simulates two recoverable GETVEC refusals, restoring G87
before checking accounting and continuity. This is **not** a native
GETMAIN refusal, nor a change to the accepted BCPLMEM allocator.

## Assistant host checks

- Python syntax compilation for the new runner and unit tests: PASS.
- Candidate `--check` source/card, accepted CO.3 identity and oracle
  validation in an isolated assistant workspace: PASS.
- `python3 -B -m unittest discover -s tools/coroutines -p
  'test_run_co4_inspection_batch.py' -v`: **17 PASS, 0 FAIL**.
- Tests cover exact per-case oracles, malformed record rejection,
  source-contract drift rejection, fault-injection pair balancing,
  read-only IFOX entry shape, synthetic BCPLCO/CG370 insertion/binding,
  G301 collision refusal, simulated PASS receipt and fail-fast receipt.
- Git tree/whitespace/byte-identity checks of new files before commit:
  PASS; no owner WSL checkout was touched.

## Evidence limitations

Offline unit tests use **synthetic CG370 trailer and BCPLCO anchors**
for insertion/binding; they do not run IFOX, IEWL, the Cambridge
compiler or JES. The actual inherited source interfaces and private
entry/registry/allocator semantics were reviewed directly from the
GitHub `main` source. The validator also pins accepted CO.3 source
blobs through the prior runner.

This record makes no native PASS claim for the new fixtures. A real
MVS run is required to confirm the IFOX observer's ABI, symbol
resolution, each BCPL fixture's compilation, all JES/IEWL/GO return
codes and exact application oracles. Any first native FAIL must be
retained and investigated rather than silently replaced.

**CO.4 IN PROGRESS; CO.5 NOT STARTED.**
