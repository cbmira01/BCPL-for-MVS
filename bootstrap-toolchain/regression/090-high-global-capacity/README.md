# 090 — high global index and expanded runtime allocation

Status: **PENDING TK5**.

This program defines a callable global at G!699 (byte offset 2796),
calls it through the global vector and reports 42. It exercises
the raised module-trailer bound and the expanded initialization of
the global vector without involving APTOVEC.

Expected native output is `42`, with successful compile, assemble,
link and GO (RC=0000). Previous BCPLMAIN rejected module trailers
requiring offsets above 800, so this probes the new capacity path.
It does **not** independently prove that the full Cambridge compiler
fits, that the new workspace is sufficient, or that APTOVEC works.
