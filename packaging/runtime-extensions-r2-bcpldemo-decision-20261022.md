# Milestone Runtime Extensions — R.2 BCPLDEMO owner design decision

**Owner decision (22 October 2026): APPROVED.** Allocate permanent G!203
with public BCPL dispatcher name `DEMOSVC` to the project-maintained
reference optional extension **BCPLDEMO**. This is a **global-number
allocation**, not automatic inclusion, successful MVS registration, or
promotion of an accepted object module.

## Purpose and scope

BCPLDEMO is an instructive, fully optional extension that uses the **same
`BCEX`, `BCRG`/`BCPLREG`, IEWL relocation and native BCPL call path** as
real extensions such as BCPLQSAM. Its permanent global number lets readers
see how `GLOBAL $( DEMOSVC:203 $)` turns into a dispatcher call through
G!203 only after an application-specific link/edit selects the extension.
It is a project-owned reference example, not a claim of historical Cambridge
BCPL functionality and not a substitute for site/library slot policy.

**Initial version-1.0 API** (approved candidate, first exercised in MVS JOB 3075; not yet R.2-accepted):

| Opcode | Behavior | Return |
| --- | --- | --- |
| 0 | Approved side-effect-free six-word shared `QUERY` | 6 or common `-1`/`-3` |
| 1 | `GETVALUES`, copy three fullwords 10/20/30 to caller-owned vector | 3, `-1` short, `-3` bad argument |
| Other | No action | `-2` unsupported |

The opcode-0 bitmap is 1 (only opcode 1 advertised), API version 1.0,
format 1, length 6, capability flags 0. The package has **no dependencies
and no finalizer**. No new public QUERY format or shared error meaning is
created. Extension A uses permanently allocated **G!203**; an eventual
second independent test extension remains test-local until separately
approved. Never reuse G!203 for the second test package.

## R.2 gate relationship

The approved [R.2 — Selective interoperability](milestone-runtime-extensions.md)
requires two independent optional extension probes and the 0/A/B/A+B
matrix, QUERY/version/capability checks, rejection of collisions and malformed
or absent dependencies, and real IEWL MAP evidence. The initial
[BCPLDEMO source](../bootstrap-toolchain/extensions/bcpldemo/README.md)
and [R.2 one-extension probe](../bootstrap-toolchain/probes/r2-interoperability/README.md)
are **only the first increment** of that work. The first real MVS run of extension A **passed JOB 3075**; see [the reviewed execution evidence](runtime-extensions-r2-bcpldemo-job-3075-evidence-20261022.md). R.2 will remain ACTIVE until
all exit criteria pass and the owner authorizes closure.

R.3 — Packaging and acceptance will turn the validated implementation into
a polished copying/adaptation tutorial and reproducible link-edit recipe.
No BOOT_OBJ/BOOT_DEVOBJ deployment or acceptance decision is implied.
G!150 FORMTREE/DEBUGINT remains separately unresolved.
