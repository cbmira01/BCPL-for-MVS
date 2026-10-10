# Regression 097: UNRDCH single-character pushback

Status: PENDING TK5.

The historical System/370 manual specifies UNRDCH() with no arguments: the next RDCH() on the current input stream repeats its previous result. This test exercises pushback of A, the logical newline (displayed as slash), and B from two physical QSAM records. The expected output is AA//BB. Unexpected values produce question marks.

The provisional native adapter supports one selected BCPIN stream and one saved character. This does not establish arbitrary rewind or independently managed multiple streams.
