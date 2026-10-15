# Milestone Date and Time Services

**Status:** Proposed, not started (2026-10-15). Optional native BCPL runtime service, independent of M4, QSAM and Milestone Decimal Arithmetic.

## Objective and scope

Provide programs compiled with the existing native System/370 BCPL compiler with predictable calendar arithmetic and a small documented interface to MVS 3.8J date/time facilities. The proposed module is `BCPLTIME` (name subject to repository inventory), optionally supported by BCPL-only calendar helpers. This is an **MVS-specific extension**, not a claim of historical Cambridge BCPL support.

**Included:** current date/time; date validation; leap years; ordinal dates; addition/difference of days; weekday; civil date parsing/formatting; time-of-day conversion; simple elapsed-time measurement if supportable.

**Excluded:** modern IANA timezone database, daylight-saving rules/historical conversion, leap-second tables, scheduling/alarms, OS clock setting, high-resolution/monotonic promises not established on TK5, universal POSIX epoch semantics, and cross-address-space synchronization.

## Values and semantics (provisional)

- `DATE` is an ordinary BCPL signed integer `YYYYMMDD`; e.g. `20261015`. Year policy initially `0001..9999`, strictly Gregorian **proleptic** calendar, pending verification of numeric range/word behavior. Calendar arithmetic does not require MVS.
- `TIME` is integer `HHMMSS` (24-hour form, `000000..235959`). Optional hundredths returned separately, never ambiguously embedded in `HHMMSS`.
- `DATENOW(datevec, timevec)` writes date and time components to separate caller-owned output vectors (details pending ABI review). Treat one call as a single snapshot as far as the underlying MVS interface allows.
- The OS clock's **local time** is the default; it may differ from real-world wall time because Hercules/TK5 operator/system configuration controls it. No implied UTC conversion. If GMT service is available in this MVS release, document it separately and test.
- Do not derive four-digit years from the legacy two-digit year returned by some `TIME` forms without an explicit **century policy**. Locate and test contemporary MVS 3.8 `TIME` macro forms, including any `ZONE` and full-year capabilities, before accepting `DATENOW` across century boundaries.
- The MVS `TIME` service is a credible starting point. A fine-resolution clock/interval interface using `STCK` or MVS timing services is a separately verified capability, **not** an assumed monotonic or precise clock. Clock wrap, system clock changes, midnight crossings and timer units need explicit documentation.
- No dynamic storage allocation is required. Parsing/formatting must use actual BCPL string and byte-buffer conventions and EBCDIC, not unverified C-style strings.

## Provisional BCPL interface

| Procedure | Meaning |
| --- | --- |
| `DATENOW(dateout, timeout)` | Read system-local civil date and time into outputs; return status |
| `DATEVALID(ymd)` | True for a supported valid calendar date |
| `DATELEAP(year)` | Gregorian leap-year predicate |
| `DATEORDINAL(ymd)` | Day-of-year 1..365/366, with error handling |
| `DATEADD(ymd, days)` | Add signed number of calendar days; report invalid/range failure |
| `DATEDIFF(first, second)` | Signed day difference (second minus first) |
| `DATEWEEKDAY(ymd)` | 1=Monday through 7=Sunday, or error |
| `TIMEVALID(hhmmss)` | Validate 24-hour time |
| `TIMESECONDS(hhmmss)` | Seconds since midnight; status on invalid input |
| `DATEFORMAT(ymd, buffer, capacity)` | Render ISO `YYYY-MM-DD` |
| `DATEPARSE(text)` | Parse ISO `YYYY-MM-DD` with explicit failure contract |
| `CLOCKREAD(out)` | Optional raw/normalized timer sample; availability decided in T.0 |
| `CLOCKELAPSED(start, end)` | Optional elapsed duration with defined clock assumptions |

Prefer an **output parameter plus status** whenever a numeric return value could be confused with a valid date/day count. Function signatures above are conceptual; T.0 must settle error contracts, outputs, global numbers and exported names consistently. Example signatures `DATEADD` and `DATEDIFF` may change to explicit output parameters.

## Illustrative BCPL (not yet compiled)

```bcpl
// Proposed date API. DATEADD and DATEDIFF use provisional returns.
LET START() BE
$(
    LET TODAY = VEC 0
    LET NOW   = VEC 0
    LET NEXT  = 0
    LET DAYS  = 0

    IF DATENOW(TODAY, NOW) ~= 0 RETURN

    // TODAY!0 holds YYYYMMDD; NOW!0 holds HHMMSS.
    IF ~DATEVALID(TODAY!0) RETURN

    NEXT := DATEADD(TODAY!0, 30)
    DAYS := DATEDIFF(TODAY!0, NEXT)

    // Use the current runtime's integer output convention.
    WRITEF("DATE %N TIME %N*N", TODAY!0, NOW!0)
    WRITEF("PLUS30 %N DAYS %N*N", NEXT, DAYS)
$)
```

This illustrates intended application logic only. The real source must adapt to accepted syntax, integer formatting, global declarations, error semantics, and installed native ABI. Especially do not treat a numeric result of zero as both a valid date and an error without an explicit contract.

## Marches and gates

| March | Scope | Exit gate |
| --- | --- | --- |
| **T.0 — Evidence and contract** | Inspect native ABI and current MVS 3.8 timing macros; settle date representation, century, local/GMT, snapshot, status and optional timer policy | Written API and source-backed MVS capability inventory |
| **T.1 — Pure calendar core** | Leap years, date/time validation, day-of-year, weekday, add/difference of calendar days | Deterministic tests over leap centuries, month/year boundaries and invalid inputs |
| **T.2 — MVS clock adapter** | Separate assembler clock service with actual MVS `TIME` behavior, local date/time extraction and errors | Repeatable MVS job evidence; test around midnight/clock settings where feasible |
| **T.3 — Presentation and optional timing** | ISO formatting/parsing and, only if verified, interval/elapsed-time API | Exact string/buffer tests and documented timer limitations; otherwise timer deferred explicitly |
| **T.4 — Packaging and acceptance** | BCPL demo, global registrations, optional object linkage, full native regression, clean rebuild and examples | Accepted non-invasive release; no new regression failures, independent of M4 |

## Engineering discipline

Pure calendar arithmetic may be written in BCPL; prefer assembler only at the MVS supervisor-service boundary and where justified by the ABI. Keep `BCPLTIME` independently linkable; never replace historical BCPL time or I/O functions without proof and approval. Candidate assembler objects are built into `NATIVE_DEVOBJ` and only promoted with separate acceptance. Track authoritative source via Git; use the live `config/dspal.yaml` dataset manifest and `tools/datasets/dspal`. Record actual tested job IDs, return codes and expected outputs. Document any clock inaccuracies in Hercules/TK5 rather than masking them.

**Primary technical references to verify during T.0:** IBM OS/VS2 MVS *Supervisor Services and Macro Instructions* for the applicable MVS release, particularly `TIME`, `ZONE`, timer units and optional `STCK` forms; actual TK5 behavior. Do not import modern z/OS timing guarantees without evidence.
