# JOB 893: Cambridge master bootstrap and ICINT global capacity

JOB 893 compiled `demoted/bcpl` successfully through the MR10 bootstrap path and
saved nonempty `workarea/bcpl.ocode`. CGI converted the OCODE to an INTCODE unit
with loaded program size 2,953 words.

Unlike SYN/LEX/TRNA/TRNB, the Cambridge BCPL master defines global 1 and is a
real START unit, so the final RUN entered the master rather than merely failing
because an isolated section lacked an entry point.

Execution reached the V17/V18 OP1 address guard after 19 cycles:

```text
*** V17 OP1 ADDRESS TRAP ***
A=0 B=175911 D=168735
C=173273 P=175945 W=9728
...
EXECUTION CYCLES = 19, CODE = -2
```

The failure is a global-vector capacity boundary. ICINT V18 still has:

```text
GLOBCNT = 401
valid globals G!0 .. G!400
OP1 global upper bound G+400
GUSED size 401
```

The Cambridge master declares `TOPGLOB:699`, and the System/370 `CGHDR` uses
global numbers into the 690s. The master explicitly assigns `TOPGLOB := 0` with
the historical comment `ENSURE ENOUGH GLOBAL VECTOR`.

Therefore the next interpreter revision must enlarge the global vector to 700
entries, G!0 through G!699, and move all capacity-dependent diagnostics and
tracking structures with it. `make-icintv19.py` performs exactly that mechanical
capacity change from the proven V18 candidate; no INTCODE, stream, or PROGVEC
semantics are intentionally changed.

The next probe is to generate `asm/icintv19.asm` and rerun the same isolated
Cambridge master compile-and-run. The compile side should remain unchanged; the
RUN should progress beyond the old G+400 guard and expose the next actual
integration dependency.
