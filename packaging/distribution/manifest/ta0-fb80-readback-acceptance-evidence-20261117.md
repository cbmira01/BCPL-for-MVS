# TA.0 — Selected FB80 object readback evidence, 17 November 2026

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone / march:** Tape artifact release / TA.0 — Release Architecture, Inventory, and Manifest  
**State:** Owner-reported MVS readback and saved private panel receipts; **not** independent resident-byte provenance, TA.0 closure, or tape authorization.

## Actual MVS readback results reported by the owner

The owner ran the verified private-evidence collector and decoder on TK5/MVS 3.8J. Three selected FB80 PDS panels completed: `EXT_OBJ` (3 members), `MR10_OBJ` (1), and `BOOT_OBJ` (10). The `EXT_OBJ` panel was recovered **without resubmitting any of its existing JES jobs** after the JOB 9048 pagination decoder fix. Job 9045's earlier two-member output also decoded with the revised parser. Each digest below is the owner's reported SHA-256 of **decoded IEBPTPCH printer output**, not of a raw DASD read or a tape-restored object. The private `job-report.txt`, `printer-window.raw`, per-member `*.fb80`, and SHA-256 receipts remain outside Git and are **not attached to this report**.

| Source | Member | JES job | Observed FB80 records | Decoded print SHA-256 |
| --- | --- | ---: | ---: | --- |
| EXT_OBJ | BCPLDEMO | 9046 | 10 | `a9207bbac0624a34f945630c354b4883f6f6ed526350a0e395e5aa5d99fc49f0` |
| EXT_OBJ | BCPLTIME | 9047 | 12 | `20929a578fe00920e9989f28f9344049aa6f5cb2369515f0c06deab63d4a67cb` |
| EXT_OBJ | BCPLQSAM | 9048 | 159 | `503b026138aacc349beae69a4846a0f3db13f9d979e8dbedf992ffa4310cf4e7` |
| MR10_OBJ | ICINT19 | 9049 | 221 | `995f5795430c9e64d84136c2334f1534cf120060c3788274540c5f91c4e51f03` |
| BOOT_OBJ | BCPLMAIN | 9050 | 76 | `0ca524f7bee2bce45e9fe424da5182dd89812fe08c25fd688b53b5ee24b4a69c` |
| BOOT_OBJ | BCPLMEM | 9051 | 18 | `c18f0546465929d114683c618ea6c272268262fc7394f8db9905799bb6b45e28` |
| BOOT_OBJ | BCPLBYTE | 9052 | 3 | `98c78136f7ef6c1831798ccb1066a83599e18d44b9d57e84b7f847784879670f` |
| BOOT_OBJ | BCPLAPT | 9053 | 7 | `8d8a537c07777953c167d6a5459e6d3d4bebef678e8e7475eb7507d30a8caad4` |
| BOOT_OBJ | BCPLIO | 9054 | 150 | `6a173b93ccf27fffb6c6c4c48f0c6931b1e94449cbf030cfa5bf27d23e24ff1e` |
| BOOT_OBJ | BCPLRGS | 9055 | 57 | `febd6d7de4dceea26e54b48b840457a6524b6c924aec87d754c96d53f9b5c09d` |
| BOOT_OBJ | BCPLREG | 9056 | 3 | `9a6252c021d6ab33ef54f2ee66259c39a797cf46793398154c57fd451935d459` |
| BOOT_OBJ | BLIB | 9057 | 132 | `599b1112ee725eec56edd85f7b7061f873dc4cdb30dbebb92af7afeeb900a860` |
| BOOT_OBJ | BCPLCO | 9058 | 22 | `72148bb90f84ca14b5de143f2e2a1b8b63d792e0cb9f7ab10a03f784a92bd797` |
| BOOT_OBJ | COROUTIN | 9059 | 32 | `cec5f03f8c9f1c46b59151e78a0168cc7cc09471da2d3c70eb9d667d1dc44f93` |

**Total:** 14/14 selected FB80 object members, **902** observed FB80 records and **72,160** decoded printer bytes. `MR10_LOAD(ICINT19)` is the separately selected **15th binary member** and is `PO/U/0/6144`, **not** an FB80 object. No byte readback or load-library restore/execution acceptance is claimed for it.

## Same-member repeat observations and qualifications

- **JOB 9045** (two-member `EXT_OBJ`): `BCPLTIME` = **12** records, `20929a...d4a67cb`; `BCPLQSAM` = **159** records, `503b02...10cf4e7`. Both match separately printed JOB **9047** and JOB **9048** respectively. This is useful cross-job printer-output consistency, not independent DASD provenance.
- **JOB 9044** (single-member `EXT_OBJ(BCPLDEMO)`) saved-report decode produced `a9207bba...9fc49f0`; this agrees with later JOB **9046**, as reported. The old **manually transcribed** hex excerpt produced a different `b74b12ac...f30ee6` SHA-256; its exact erroneous byte(s) have not been isolated. Preserve the discrepancy as a transcription issue under investigation, not a new resident-module conflict.
- **JOB 9048** disclosed `IEBPTPCH` page continuation headings; the page-aware decoder preserved all 159 records, 12,720 bytes. The updated parser is strictly constrained to identical member names following contiguous page numbering; it does not silently merge different members.
- The original receipt attachments, report hashes, source Git builds and `ICINT19` load-library directory remain **outside the assistant's reach**. The table records operator-provided results only. Merely checking the current checkout HEAD cannot establish which Git revision built the resident modules.

## Next read-only MVS verification: MR10_LOAD directory

The canonical TA.0 manifest selects `MR10_LOAD(ICINT19)` as `PO/U/0/6144`, transferred eventually by IEBCOPY unload. FB80 IEBPTPCH decoding must **never** be applied to this library. Before attempting a load-library unload/restore or independent execution test, inspect the actual load-module directory using period MVS `IEHLIST LISTPDS ... FORMAT` and saved `LISTDS LABEL` source/volume evidence. This is a **directory-only** qualification, not load-record bytes or successful fetch/GO.

`tools/distribution/inspect-ta0-mr10-load.py` implements one authorized read-only JES pilot: it validates the canonical inventory and active DCB, checks the SHA-256-pinned `MR10_LOAD.txt` and `MR10_LOAD.stat-raw.txt` already collected outside the checkout, extracts the actual source VOLSER (rather than assuming `TSO003` from an unrelated library), generates the period `IEHLIST` control and a `DISP=SHR` volume DD, and uses the existing authenticated `dspal-core` submission/cursor/report machinery. The private output captures the original printer window, redacted job body, job report, job summary and receipt hashes; it has no tape, IEBCOPY, load-module execution or output dataset DD. It is deliberately a **single MVS experiment** because actual period directory formatting must drive any further parser or verification. A zero return code does not by itself prove that the `ICINT19` entry was listed: review the saved listing before asserting member-directory acceptance.

Period reference: IBM *OS/VS2 MVS Utilities*, Release 3.8, GC26-3902-1, IEHLIST `LISTPDS` and `FORMAT`; the reproduced period example is discussed at https://www.jaymoseley.com/hercules/os_utilities/mvs_utilities.html#IEHLIST .

## Outstanding gates

Separate `RECFM=U` member bytes/directory/IEBCOPY round-trip/executable use; eight build-job receipts; native Core Runtime/BLIB/COROUTIN source-to-MVS revision lineage; full rights/redistribution review; candidate source freeze; release version/VOLSER registry; independent installation and tests; any TA.1 scratch tape operations (owner approval required). **TA.0 remains IN PROGRESS.**
