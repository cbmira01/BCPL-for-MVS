# M2.1 — Native Runtime Regression Coverage Matrix

**Candidate:** DEVOBJ(BCPLM7). **Accepted execution set:** native 00–123, **123 PASS / 0 FAIL / 1 expected SKIP (083)**, including new Gate E rerun and separate JOB 3646 IEWL MAP/GO. These mappings identify *asserted behavior*, not percent source coverage, exhaustive combinations, or undocumented historical equivalence.

| Area / interface | Principal tests | What is established | Explicit limit |
| --- | --- | --- | --- |
| START, global registration, basic arithmetic/control | 000–024, 034–047 | Generated application entry, locals, pointers, control flow, globals | Not every language syntax or global export |
| Separate BCPL/native linkage | 025–026, 037 | BCPL routines, native procedure calling through global vector | Not arbitrary user-library loader |
| Stack frame/linkage | 013–019, 048–052 | Multiarg, recursion, checked frames and controlled exhaustion | Invalid-metadata RC36 not fault-injection tested |
| Dynamic BCPL vectors, BCPLMEM G87/G88 | 027–032, 039, 082, 122–123 | Allocation, invalid/failed request handling in tested cases, outstanding vectors and FREEBASE registration | No quantitative FREEMAIN leak meter; 083 SKIP |
| Byte operations, BCPLBYTE G85/G86 | 038, 070–071 | Word/byte roundtrip and BLIB byte consumers | Limited boundary-space testing |
| BLIB independent object and formatting G60–77 subset | 053–081; especially 067–069 and 075 | Formatting/string use, independent library binding, G76 WRITEF behavior | Not comprehensive postmortem or all BLIB exports |
| FINISH and STOP G30 | 082, 084–089, 119 | Normal/nonzero return paths, buffered streams and termination | Unusual startup exception cleanup unverified |
| G40 APTOVEC from BCPLAPT | 091–093 | Nested/large temporary vectors and overflow RC12 | Not every stack-boundary adjacency |
| G11–17 G33 G39 G41–42 G46–47, BCPLIO | 094–119, 101, 108–109 | Selection, RDCH/UNRDCH, EOF, reopen, two outputs, PARM, WRAPOUTPUT, record capacity/closure | Fixed MVS names/record formats; not arbitrary DDNAME manager |
| STACKHWM G56 and G6 SAVEAREA | 120–123 | Sentinel-pattern initialization and in-range high-water, selected BLIB pointer/list consumers | Exact stack high-water usage and complete SAVEAREA unverified |
| STKOVFL, runtime RC12 | 052, 093 | Both checked-entry and APTOVEC output + GO RC0012 | Not historical ABORT system code |
| Application-independent object link and GO | 025,026,069,075,091,101,119,121; **JOB 3646** | Separate application, BCPLMAIN, BCPLIO, BCPLBYTE, BCPLAPT, BCPLMEM, BLIB CSECTs; IEWL XREF and successful `BLIB 42` | Does not mean Cambridge compiler itself is native |
| Storage-reclamation instrumentation | 083 **SKIP** | Test exists but is explicitly source-only instrumentation | No executable proof of quantitative reclamation |
| G29 DATE, G31 LEVEL/G32 LONGJUMP, overlays/postmortem | **No accepted native test** | Historically identified only | Deliberately unsupported/deferred |

**Gate F use:** any change to native code, member packaging, test contract or JCL must be assessed against this matrix; add focused evidence before reasserting acceptance. Preserve the four env selectors to avoid accidental fallback to production `OBJ`.
