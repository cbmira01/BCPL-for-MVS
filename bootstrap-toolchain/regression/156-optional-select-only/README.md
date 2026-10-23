# 156 - optional-select-only

R.5 candidate: NOT YET TESTED ON MVS.

Compile the BCPL source using the resident demoted Cambridge compiler
under MVS. Assemble the selection with IFOX, link BCPLMAIN, BCPLRGS,
the BCRG and selected extension under IEWL, then execute the client.
The expected GO return code is 0000 and the expected output is
R5 EXT 156 PASS. Verify BCRG length and optional CSECT presence
in the IEWL MAP independently of the program output.

Run with tools/bootstrap/run-regression 156 when integrated.
