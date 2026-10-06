# MVS-resident Cambridge compiler path

The Cambridge compiler used by the native-code regressions is still an
INTCODE program executed by ICINT V19.  It is not yet a native System/370
compiler load module.

The original bootstrap runner intentionally rebuilds that interpreted image
from the demoted Cambridge BCPL sources for every regression.  That is useful
as a bootstrap proof, but it is unnecessarily expensive once the image is
known to work.

The resident path makes the bootstrap products persistent on MVS.

## Persistent state

The installation uses the managed HERC02 libraries:

```text
HERC02.BCPL.SOURCE
    BCPL SYN LEX TRNA TRNB
    CGA CGB CGC CGD CGE
    BOOTHOST
    OPTIONS CAMBPARM
    LIBHDR SYNHDR TRNHDR CGHDR

HERC02.BCPL.ASM
    ICINT19

HERC02.BCPL.LOAD
    ICINT19

HERC02.BCPL.INTCODE
    SYNI TRNILRG CGI BLIBI ICLIB
    BCPL SYN LEX TRNA TRNB
    CGA CGB CGC CGD CGE
    BOOTHOST
```

The Cambridge members in `INTCODE` are build products.  The corresponding
demoted BCPL text remains in `SOURCE`.

## One-time installation

Run:

```sh
python3 tools/install-cambridge-mvs
```

The tool generates and submits one authenticated JCL job.  That job:

1. copies the demoted Cambridge source, headers, options, ICINT V19 source,
   and bootstrap INTCODE inputs into the managed HERC02 PDSes;
2. assembles ICINT V19 with IFOX;
3. link-edits it as `HERC02.BCPL.LOAD(ICINT19)`;
4. compiles each Cambridge BCPL unit with the MR10 bootstrap compiler;
5. converts each OCODE unit with CGI;
6. writes the resulting Cambridge compiler INTCODE modules permanently to
   `HERC02.BCPL.INTCODE`.

The installer verifies that every interpreted compile/code-generation
execution returns BCPL execution code zero.

The complete generated JCL can be inspected without submission:

```sh
python3 tools/install-cambridge-mvs --show-jcl
```

The displayed JOB card has the password redacted.  Actual submission obtains
the HERC02 batch credentials from the gitignored `config/dspal.local.yaml`.

## Fast compile path

After installation:

```sh
python3 tools/cambridge-compile-mvs program.bcpl
```

runs only the already-compiled Cambridge image:

```text
HERC02.BCPL.LOAD(ICINT19)
        +
persistent Cambridge INTCODE modules
        +
BLIBI + ICLIB
        |
        v
input BCPL source -> System/370 CODE
```

The resulting textual assembler stream is recovered to
`workarea/<source>.s370.asm`.

This removes the repeated ICINT assembly/link and the eleven
MR10-compile-plus-CGI bootstrap pairs from an ordinary native regression.

## Regression comparison

The historical/bootstrap path remains:

```sh
bash native-compiler/regression/run-test.sh 24
```

The resident path is:

```sh
bash native-compiler/regression/run-test-mvs.sh 24
```

Both feed the same downstream assembler/runtime regression machinery.  Test
24 is therefore a direct equivalence check for the change in compiler
delivery method.

## ICINT promotion policy

This workflow does not change `config/CURRENT`.  ICINT V19 remains the
specific interpreter required by the Cambridge resident compiler image until
separate project-wide promotion work says otherwise.
