# Native Cambridge BLIB

`blib.bcpl` is the complete historical source from
`richards-bcpltape/bcplib/bcpl/blib` with exactly one bootstrap
demotion: the initial `SECTION "BLIB"` directive is replaced by a
comment. Every remaining source record is unchanged; `GET "LIBHDR"`
continues to use the resident MVS library header.

The whole-library regression is
`native-compiler/regression/067-full-historical-blib-link`.
It references this file instead of carrying yet another copy.

Do not edit this derivative to make individual tests pass. Changes
needed for Cambridge or MVS compatibility must be explained, separately
tracked, and preferably generated from the historical source.
