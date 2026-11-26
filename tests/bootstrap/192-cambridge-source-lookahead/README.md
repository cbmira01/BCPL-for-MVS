# 192 — Cambridge compiler source lookahead

Compile two independent programs through one resident CAMBCOMP invocation. Top-level period must discard the rest of its record (SKIPREC); post-FORMTREE RDCH/UNRDCH must preserve the first character of the second program. Require exactly two complete assembler units, independently assembled, linked with BOOT_OBJ and executed with distinct ordered oracles. First live acceptance pending. No persistent writes.
