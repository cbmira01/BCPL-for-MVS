This directory contains all the files from Martin Richard's "transport"
tape, with the exception of the IBM360 object files, which wouldn't be
much use to anybody anyway.

The first file f01 is the batch job that created the tape and gives you
an idea of what the files contain.

Probably the most interesting files are the code generators for various
machines and the documentation files which suffice as a description of
the language BCPL.

Note that there are some character translation problems because the
tape was read using Unix dd EBCDIC and apparently Cambridge was using a
different dialect of EBCDIC. For instance ] is actually ! and so on. In
fact if you examine the files with a 8-bit clean editor, you will see
that some characters have the 8-th bit on. I haven't taken the trouble
to clean the files, so you'll have to do it yourself.
