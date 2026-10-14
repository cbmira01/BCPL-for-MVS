# Reconstructed library GLOBAL assignments

BCPL modules rendezvous through the shared global vector, so independently compiled library modules must use stable, non-conflicting GLOBAL numbers.

This project currently uses three ranges:

- historical/bootstrap runtime assignments through slot 86, including `WRITEF:76`, `GETBYTE:85`, and `PUTBYTE:86`;
- reconstruction runtime assignments 87..95 for allocation and coroutines;
- reconstruction general-library assignments 96..159.

The general-library range is intentionally larger than the current set so new portable routines can be added without disturbing existing ABI assignments.  These numbers are reconstruction-local until a final consolidated runtime/library header is established.

## Current map

```text
87  GETVEC
88  FREEVEC
89  HEAPINIT
90  FREEHEAD

91  CREATECO
92  DELETECO
93  CALLCO
94  COWAIT
95  RESUMECO

96  SRAND
97  RAND
98  RANDRANGE
99  RANDSTATE        private state used by random.bcpl
100 RANDSEED         compatibility spelling for SRAND

101 ABS
102 MIN
103 MAX
104 SIGN
105 GCD
106 IPOW

107 STRLEN
108 STRCMP
109 STRCPY
110 STRCAT
111 STRCHR

112 MEMCPY
113 MEMSET
114 MEMCMP
115 VECCOPY
116 VECCLEAR

117 ATOI
118 ITOA
119 HEXTOI
120 ITOHEX

121 ISDIGIT
122 ISALPHA
123 ISSPACE
124 TOUPPER
125 TOLOWER

126 READLINE
127 WRITELINE
```

## Convention

A program that uses one of these routines declares the same GLOBAL number locally and compiles the corresponding library source as an additional compilation unit.  For example:

```bcpl
GLOBAL $(
START:1
WRITEF:76
SRAND:96
RAND:97
$)
```

and:

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    my-program.bcpl \
    +library/random.bcpl
```

Do not allocate a new slot ad hoc in a demonstration or test.  Add it to this map when promoting a reusable routine into `library/`.
