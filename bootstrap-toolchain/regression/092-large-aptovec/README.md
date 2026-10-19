# 092 — large APTOVEC workspace

Status: **PENDING TK5**.

Invoke G!40 APTOVEC with N=9000, allocating a temporary vector of
9001 32-bit BCPL words (36,004 bytes) on the native execution stack.
The nested function checks the passed size, writes to the first, middle,
and last elements, and returns their sum (10+12+20=42).

This is considerably larger than regression 091's VEC 3 and exceeds
the compiler master's 5,000-word minimum workspace. It verifies
that APTOVEC can place a large vector on the stack without corrupting
the nested function's linkage, but it does not measure full compiler
workspace use or exercise stack exhaustion.

Acceptance: Cambridge compile, IFOX assembly and IEWL link-edit
succeed; native GO returns RC=0000 and BCPL output is `42`.
