# CO.1 — CG370 checked-entry option matrix and native stack-bound gap

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Date:** 12 November 2026
**Source revision:** `d7ad5a0bce3691e3b32646637203f2059c3295f8`
**Status:** CO.1 IN PROGRESS; design gate OPEN
**Evidence:** SOURCE-OBSERVED, not new native execution

## Scope

Extend [CO.1 checkpoint 1](co1-native-abi-and-stack-source-investigation-20261112.md) and [checkpoint 2](co1-historical-native-control-block-and-abi-discrepancies-20261112.md) with a source-derived check of CG370's **four compiler-option-dependent procedure-entry paths**. The governing [milestone](milestone-implement-coroutine-support-for-native-compiler.md) requires owner-reviewed ABI and probes before native switch implementation. Owner-selected Approach A valid/live pointer descriptors and S1 active stack limits are unchanged. No Core Runtime, compiler, test or MVS installation changes are implied.

## 1. The actual entry options

Source anchors:
- `richards-bcpltape/bcplib/bcpl/bcpl`, option initialization/parsing near lines 129–137 and 177–212;
- `richards-bcpltape/bcplib/bcpl/cghdr`, `S.COUNT=20`, `S.STKCK=60` and `S.STKCKCOUNT=80` near lines 161–173;
- `richards-bcpltape/bcplib/bcpl/cg`, `CGSAVE` lines 652–675, `CGAPPLY` lines 688–731, `GENDCF` 2186–2191, `GENSTKCK1` 2238–2246, `GENSTKCK2` 2248–2255.

| Generator switches | Post-`STM` entry path | Inline metadata | Next valid action |
| --- | --- | --- | --- |
| Neither `C` nor `K` | `LR 5,15` | None | Start callee body |
| `K`, no `C` | `BAL 14,20(11)` | 4-byte zero counter | Set `R5=R15` |
| `C`, no `K` | `BAL 14,60(11)` | 4-byte full required frame size | Checked service installs frame and skips metadata |
| `C` plus `K` | `BAL 14,80(11)` | **8 bytes: counter then full frame size** | Combined counted + checked service required |

In the code-generator option phase, `C` sets `STKCKING`, `K` sets `CALLCOUNTING`, and `P` sets both `CALLCOUNTING` and `COUNTING`. Consequently `C` + `P` also selects the combined +80 entry path (with further counting behavior outside this table).

The combined metadata are two distinct fullwords: `GENDCF(0)` emits a zero-initialized counter and advances `TXTP` by four bytes, then `GENSTKCK1` emits the separately patched required-frame-size word and advances `TXTP` by another four bytes. `CGSAVE`'s initial `STM` saves R4–R6 and the number of R7–R10 argument registers needed by that callee; the precise save range depends on the formal-argument count. `CGAPPLY` computes the incoming R15 workspace, reserves its caller-side frame (`SAFEFRAME=K+7` when checked), and calls with `BALR 6,4`.

Schematic for a no-argument callee with `C` + `K` (derived from source, **not** a captured assembler listing):

```asm
         STM   4,6,0(15)
         BAL   14,80(11)
         DC    F'0'            COUNTER
         DC    A(Lnnn)         STACK FRAME SIZE
         ...                   CALLEE BODY
Lnnn     EQU   nn
```

## 2. Mismatch in the reconstructed Core Runtime

Source: `bootstrap-toolchain/asm/bcplmain.asm`, system vector +20/+60/+80 at lines 430–453, `CNTIMPL` around 478–484, `STKIMPL` around 564–575 and `STKCIMP` around 591–598.

- `CNTIMPL` (+20) advances R14 by four bytes to consume its one counter, after which generated code establishes R5.
- `STKIMPL` (+60) establishes `R5=R15`, loads and validates the one inline frame-size word, compares `R15+size` against the active `STKLIM`, restores R4 and advances R14 by four bytes.
- `STKCIMP` (+80) currently executes only `LA 14,4(14)` and `BR 14`.

The combined +80 service is therefore missing **three mandatory operations**: (1) establishing R5 from R15, (2) validating the required full frame against `STKLIM`, and (3) consuming **both** inline fullwords. It advances past the first word only and leaves the frame-size word in the instruction path. Source strongly indicates incorrect execution for checked + counted entry, but **no fresh MVS JES run has established its actual failure mode**. Do not claim a particular ABEND or MVS return code.

**S1 consequence:** Correctly switching `STKLIM` and external `BCPLAPT APLIMIT` cannot protect a generated entry path that fails to perform its bound check. The +80 service must be a separate CO.1 compatibility decision, not silently treated as the already verified +60 service. Do not suppress standard checked entry to avoid the discrepancy.

## 3. Historical defaults and bounded regression evidence

The historical MVS procedure `richards-bcpltape/sys1/userproc/bcplclg` sets `PARMC='/CK'`. Its slash begins generator-option parsing: `C` means checked entry and `K` means call counting. This is the *historical compile default*, **not** a successful assertion about the reconstructed +80 path. The bootstrap standard option file is `/N`, which does not enable either feature.

Existing native Bootstrap 48–51 documentation explicitly identifies `/CN` and the +60 stack-check path. Test 52's README and generated-regex fixture show the +60 entry and a controlled-stack-overflow observation; its README **does not explicitly state** `/CN`. None of these fixtures demonstrates +80 operation. Test 52 records a 1044-byte recursive call-frame displacement versus the callee's complete 1072-byte requirement: checked entry must use **the inline full-frame size**, not the caller's advancement alone.

Maintain the established profile-specific overflow expectations from checkpoint 2: D6/BCPLM6 may expect GO RC0000; D7/BCPLM7 expects RC0012. A new combined-mode investigation must name its linked candidate/runtime and independently obtain GO/JES outcomes. Do not change accepted fixtures or reinterpret historical results as current native verification.

## 4. Isolated evidence and decision gates

| Probe | Action | Limits |
| --- | --- | --- |
| CK-A | Source-assert the four paths, exact metadata lengths, `CGAPPLY` frame reservation, and the +20/+60/+80 runtime services | Host-only source verification |
| CK-B | Re-run existing native Bootstrap cases 49–52 against one explicit current production profile | MVS-facing baseline of the **+60 path only**, no installed overwrite |
| CK-C | Use an isolated **compile-only** `/CKN` candidate to verify the emitted +80 branch, counter and full-frame-size word | **Do not GO** with the current +80 stub; requires separately authorized JES operation |
| CK-D | Owner review of corrected +80 contract: frame setup, required size, 8-byte metadata advance, counter meaning, active limit | Architecture decision before implementation |
| CK-E | Isolated IFOX/IEWL/GO/JES candidate for +80 after design approval; later extend to coroutine S1 contexts and `APTOVEC` | Separate native implementation and MVS authorization |

**Owner decisions still open:** Whether `/CK` (historically the default) must be supported for the initial native coroutine release; which Core Runtime module owns the counted checked-entry fix; preservation of counter semantics; and exact verification to close this gap. This source analysis alone authorizes none of those choices.

## 5. Checks and status

Source checks inspect actual GitHub file contents at the revision above, not reconstructed examples: compiler option dispatch, generator `CGSAVE` and `GENDCF/GENSTKCK1` length accounting, runtime `STKCIMP/STKIMPL/CNTIMPL` bodies, historical `PARMC`, and Bootstrap manifest/fixture boundaries. The initial check incorrectly required test 52's README to literally mention `/CN`; investigation confirmed it documents +60 but not that exact option spelling. The audit constraint was corrected, rather than altering historical source evidence.

**CO.1 remains IN PROGRESS; its owner-reviewed design gate is OPEN; CO.2–CO.5 remain NOT STARTED.** No native code or MVS dataset is changed.
