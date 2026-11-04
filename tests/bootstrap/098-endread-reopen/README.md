# Regression 098 — ENDREAD and input reopen

Status: PENDING TK5.

Richards' 1974 System/370 BCPL manual defines ENDREAD() as the
zero-argument routine closing the currently selected input stream;
the corresponding global is G!46.

The program opens and selects BCPIN, reads A, explicitly calls
ENDREAD, and expects RDCH without a selected stream to return -1
(the narrow bootstrap adapter's provisional no-selection policy).
It reopens and reselects the same DD and expects reading to restart
at A, followed by the logical newline 10 (rendered as slash).
FINISH closes the second OPEN. Output: AEA/.

This test does not establish independent multiple-input-stream support,
general QSAM RECFM handling, or historical behavior when RDCH is
invoked with no selected stream. It verifies the provisional policy.
