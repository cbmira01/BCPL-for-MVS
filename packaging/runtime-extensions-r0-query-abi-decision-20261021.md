# Milestone Runtime Extensions — R.0 shared QUERY ABI decision

**Owner approval:** 21 October 2026. **March:** **R.0 — Evidence and contract (open)**.
**Next march:** **R.1 — Generic registration foundation (not started)**.
**Authority:** [Milestone Runtime Extensions](milestone-runtime-extensions.md),
[owner ABI decisions A–H](runtime-extensions-r0-owner-abi-decisions.md),
[Global Number Registry](global-number-registry.md), and
[Cambridge runtime/library nomenclature](runtime-and-library-nomenclature.md).

The owner **approved the six-word shared `QUERY` prefix, three common
negative results, all-or-nothing writes, version/opcode rules, and
append-only extended descriptors**. This records a version-1 API
**contract**, not working optional-module startup registration. It does
not allocate any new G! number or revise package-specific API opcodes.

## Common dispatcher calling convention

Every participating optional System Extension, Standard Library, or
User/Site Library normally exposes **one dispatcher global** (a package
with multiple exports requires the existing Decision C exception).
Its package-specific operation numbers include reserved **opcode 0**:

```text
PACKAGE_SVC(0, info_vector, capacity_words) -> required_word_count | error
PACKAGE_SVC(0, 0, 0)                       -> required_word_count
```

- The native BCPL ABI passes arguments in **R7, R8, R9** and returns the
  signed 32-bit result in **R7**. `info_vector` is a **BCPL word pointer**,
  not an MVS byte address; `capacity_words` counts **32-bit words**.
  Machine-code adapters must perform the proven word-to-byte conversion.
- `QUERY` operates on **an already linked and registered** package. It
  does not discover absent packages. A `GLOBAL` declaration does not
  establish availability; the approved `BCPLREG` preflight must check
  required packages before `START` when R.1 implements it.
- `QUERY` is **side-effect-free** apart from a successful write into the
  caller's supplied vector. No dataset OPEN/I/O, clock read, state
  mutation, new package resource, buffer allocation, or hidden init.
- The caller must pass genuinely accessible storage. The dispatcher
  cannot generally validate arbitrary fabricated nonnull BCPL pointers
  or a dishonest accessible-capacity claim. This is a normal native ABI
  caller obligation, **not** a promise of memory protection.

## Six-word version-1 prefix

| BCPL word | Common meaning |
| --- | --- |
| `info!0` | Shared QUERY descriptor format = **1** |
| `info!1` | Package API **major** version |
| `info!2` | Package API **minor** version |
| `info!3` | Entire descriptor length in 32-bit words, **at least 6** |
| `info!4` | Supported-operation bitmap: bit 0 means opcode **1**; bit 31 means opcode **32** |
| `info!5` | Package-owned capability flags; their meanings are **not shared** |

API major and minor reported by QUERY must match the selected package's
linked `BCEX` descriptor. A client accepts a compatible major version
and required minor version and consults the bitmap for functions it
actually intends to call. A bit means the opcode is **implemented**, not
that a DD allocation or environmental operation is guaranteed to work.
Unassigned bitmap bits and package capability-flag bits are zero.
Bits for opcodes above 32 require a separately documented appended
capability-map extension before any package advertises such operations.

Future compatible descriptors preserve these six fields and append
additional words. A six-word caller may inspect the prefix **only when
the full descriptor length returned by the size inquiry fits its buffer**;
there is no partial-prefix success. Format-1 extensions keep the same
field meanings. Any incompatible reinterpretation requires a new shared
format version.

## Required return and buffer rules

| Case | Result | Memory write |
| --- | ---: | --- |
| `(0,0,0)` | Positive entire length in words | None |
| Valid nonnull vector and capacity at least entire length | Positive entire length | **All** descriptor words, exactly |
| Valid nonnull vector and capacity shorter than entire length (including 0) | **-1** (`QUERY_ERR_CAPACITY`) | **None** |
| Unsupported nonzero opcode | **-2** (`QUERY_ERR_OPCODE`) | No QUERY vector write required |
| Null vector with nonzero capacity | **-3** (`QUERY_ERR_ARGUMENT`) | None |
| Any negative capacity | **-3** (`QUERY_ERR_ARGUMENT`) | None |

Argument errors take precedence over insufficient capacity for
negative counts. `(0,0,0)` is the **only** valid null-vector QUERY
form. A nonnull vector with zero capacity returns `-1` without a write.
On insufficient capacity, the vector is **not partially modified**.
When capacity exceeds required length, trailing caller words are left
unchanged. All valid positive-size results are word counts, **not
success status zero**.

The shared negative meanings match the reviewed
[BCPLQSAM public specification](bcplqsam-public-interface.md), but
package-specific non-QUERY opcodes own their own arguments and status
semantics; this contract does not impose an ordinary-operation result
vector on every package.

## Evidence, scope and outstanding test

[Q.0 JOB 2157](qsam-q0-dispatcher-abi-evidence-20261019.md)
**passed** test-only native G!200 caller/dispatcher linkage, R7/R8/R9
transmission, six-word QUERY, capacity `-1` with no partial write,
unsupported opcode `-2`, and normal BCPL return. It used a synthetic
application-trailer binding, not production `BCPLREG` registration.
It did not exercise the common rules on **two** independent packages
or extended descriptors.

The [R.0 isolated shared QUERY probe](../bootstrap-toolchain/probes/r0-query-probe/README.md)
adds two separately assembled test dispatchers, a native BCPL caller,
short-buffer sentinels and an eight-word descriptor. **Local offline
checks passed; an actual MVS execution has not yet been observed.**
The probe's **G!298/G!299 are local fixture bindings**, not Global
Number Registry assignments, and it does not implement BCPLQSAM,
BCPLTIME, BCPLDEC, or the `BCPLREG` registrar. IEWL resolves their
addresses in the temporary test load module. MVS test results must be
recorded separately before being claimed verified.

**R.0 remains open; R.1 has not started.** The remaining gate items
are listed in the [R.0 gate review](runtime-extensions-r0-gate-review-20261021.md).
