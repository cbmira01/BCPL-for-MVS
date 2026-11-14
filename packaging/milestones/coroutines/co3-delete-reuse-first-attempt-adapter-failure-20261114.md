# CO.3 — First DELETECO integration attempt: adapter mismatch

**Milestone:** Implement coroutine support for native compiler  
**March:** CO.3 — Coroutine Library and Lifecycle (**IN PROGRESS**)  
**Date:** 14 November 2026  
**GitHub revision:** `4565e9f6aca065fc3193ec7e044dc06055531a08`  
**Evidence classification:** OWNER-REPORTED HOST-ADAPTER FAILURE; native execution not reached

The owner executed `tools/coroutines/run-co3-delete-reuse.py --run`
and reported:

    CO.3 first lifecycle FAIL: BCPL library imports changed
    CO.3 first lifecycle evidence:
      workarea/co3-delete-reuse/20261114T235000Z-zvui6mmb
    CO.3 deletion/reuse verification RC=1

The base CO.3 adapter uses mutable `EXPORTS` for registration
trailer additions and symbolic procedure aliases, but it emits
hard-coded five-symbol `EXTRN` and `ENTRY` cards. The deletion
extension added G!291 `C3DELETE` as a sixth BCPL procedure. Its
application adapter wrongly expected the base runner to produce
an expanded six-symbol `EXTRN` card. It raised before the IFOX deck
could be written or submitted. Independently, the library's fixed
five-symbol `ENTRY` card would have omitted `C3DELETE` from IEWL
external references even if the application check had been bypassed.

The correction is confined to the private deletion/reuse adapter:
accept the known five-symbol baseline, expand the application
`EXTRN` and library `ENTRY` to include `C3DELETE`, validate
the unique generated alias and preserve the separate compilation
and link-edit model. A candidate-only `CO3DROP` remains the
native unregister mechanism.

The failed attempt does **not** establish any MVS IFOX, IEWL, GO
or `DELETECO` behavior. The strict 21-record native oracle remains
pending.

**Disposition:** CO.3 IN PROGRESS; CO.4–CO.5 NOT STARTED.
