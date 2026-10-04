# Third-party notices and provenance

The MIT license in this repository covers original project work unless a file says otherwise. It does **not** relicense historical BCPL material or external software used by the build and test environment.

## Historical BCPL transport tape

`richards-bcpltape/` is third-party archival material associated with Martin Richards' BCPL system.

The provenance retained with the archive is:

- Martin Richards' "transport" tape is the original source described by the surviving archive notes;
- Ken Yap made an early tar archive available;
- Robert Nordier corrected character-mapping problems, assigned descriptive filenames, organized the files, and published the result as `bcpltape`;
- Nordier's account is retained verbatim as `richards-bcpltape/README.Nordier`;
- Yap's earlier note is retained verbatim as `richards-bcpltape/README.orig.Yap`;
- `richards-bcpltape/INDEX` records the mapping from the original numbered tape entries to the curated paths.

Nordier publicly distributes `bcpltape`, and Martin Richards' archive and the Computer History Museum Software Preservation Group identify the same material as part of the historical BCPL collection. That establishes a strong provenance trail. It does not, by itself, create a new open-source license.

No blanket conventional open-source license for every historical tape file was located during the October 2026 public-release audit. The historical files therefore remain the work of their respective authors and rights holders. The project's MIT license must not be read as applying to them.

Martin Richards' current BCPL page describes terms for a present-day BCPL distribution. Those terms should not automatically be extended to unrelated or older files on the transport tape.

## Historical working copies under `intcode/`

The interpreted bootstrap uses convenient working copies of several files from `richards-bcpltape/mr10/bcplkit/`:

| Project path | Historical source |
| --- | --- |
| `intcode/blibi.int` | `richards-bcpltape/mr10/bcplkit/blibi` |
| `intcode/cgi.int` | `richards-bcpltape/mr10/bcplkit/cgi` |
| `intcode/syni.int` | `richards-bcpltape/mr10/bcplkit/syni` |
| `intcode/trni.int` | `richards-bcpltape/mr10/bcplkit/trni` |

At the time of the public-release audit these pairs are byte-for-byte identical in Git. They retain the provenance and rights status of the historical files.

`intcode/iclib.int` is project-side runtime support for the hosted interpreter and is not one of those byte-for-byte tape copies.

## Reconstructed ICINT

The System/370 ICINT implementations under `asm/` are project reconstruction work based closely on the historical BCPL implementation in `richards-bcpltape/mr10/bcplkit/icint`. The reconstruction intentionally follows the historical operation and data model where practical, while adding the MVS-specific hosting, stream handling, character translation, diagnostics, and safeguards needed by this project.

This is derivative/reconstruction work with historical source provenance; the presence of project-written assembler does not erase the provenance of the original design and implementation.

## Hercules

The project uses [Hercules](https://github.com/SDL-Hercules-390/hyperion), originally created by Roger Bowler and maintained by its contributors. Hercules has its own copyright and license terms. Those terms are not replaced by this repository's MIT license.

## MVS Turnkey 5 / TK5

The Docker environment downloads [MVS Turnkey 5 (TK5)](https://www.prince-webdesign.nl/tk5). TK5 contains IBM OS/VS2 MVS Release 3.8J and software from multiple contributors and projects. The archive and DASD images are not committed to this repository, but they are present in a locally built container image.

This repository does not grant rights to TK5 or its contents.

## Ubuntu and packaged software

The container uses the Ubuntu Official Image and distribution packages. Ubuntu and those packages retain their respective licenses and notices.

## Related container work

The container setup was informed by public Hercules/TK projects including `tk5-hercules` by Joerg Schultze-Lutter and `tk4-hercules` by Ken Godoy / skunklabz. The repository does not claim authorship of those projects.

## AI assistance

ChatGPT and Claude have been used during parts of the reconstruction for research, code review, drafting, and editing. The checked-in work has been selected and revised as part of the project; AI assistance is not a provenance claim for the historical material.