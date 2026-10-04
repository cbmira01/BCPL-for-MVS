# Richards BCPL transport-tape archive

This directory is preserved historical material used as primary evidence by the reconstruction. It is not original BCPL-for-MVS project code.

## Provenance

The surviving provenance chain is unusually good:

1. the files are described as coming from Martin Richards' BCPL "transport" tape;
2. Ken Yap made a tar archive of the tape files available;
3. Robert Nordier corrected character-mapping problems, assigned descriptive filenames, and organized the files into directories;
4. Nordier published the curated result as `bcpltape`;
5. Martin Richards' archive and the Computer History Museum Software Preservation Group point to the Nordier-curated material.

The original evidence is retained here:

- `README.orig.Yap` — Yap's note about the transport tape and its character-translation problems;
- `README.Nordier` — Nordier's note describing his cleanup and renaming;
- `INDEX` — mapping and comments for the original numbered tape entries.

Do not rewrite those three files merely to modernize their prose; they are provenance artifacts.

Nordier reports 55 surviving files from an original sequence of 75 entries. The missing entries are represented in `INDEX`.

## Areas used by this project

`mr10/bcplkit/` contains the portable kit that currently drives the interpreted bootstrap: `syn`, `trn`, `cg`, their INTCODE forms, `blib`/`blibi`, and the historical BCPL `icint` implementation.

`mr10/print/manual`, `mr10/text/bstrbcpl`, and `mr10/text/intcode` provide contemporary documentation for the language, bootstrap, and INTCODE system.

`bcplib/` contains later compiler/library source and remains useful comparative evidence.

The archive also contains target-specific material and code generators. A historical System/370 code generator has now been identified as relevant to the native-target work. The project is therefore concentrating on hosting and integrating surviving S/370 code-generation material with the runnable kit compiler rather than designing a new backend without reference to the historical implementation.

## Working copies

For convenience the runnable bootstrap keeps byte-for-byte copies of several kit files under `intcode/`:

```text
mr10/bcplkit/blibi -> intcode/blibi.int
mr10/bcplkit/cgi   -> intcode/cgi.int
mr10/bcplkit/syni  -> intcode/syni.int
mr10/bcplkit/trni  -> intcode/trni.int
```

Those copies remain historical third-party material.

## Copyright and redistribution

The repository's MIT license does not apply to this directory merely because the files are checked in here.

Public archival redistribution of this material is well established through Nordier and Richards' archive, but the October 2026 release audit did not locate a blanket conventional open-source license covering every historical file. See `../THIRD-PARTY-NOTICES.md` and `../PUBLIC-RELEASE-AUDIT.md` before redistributing the archive.