#!/usr/bin/env bash
set -u
set -o pipefail

usage() {
    echo "Usage: bash native-compiler/regression/run-test.sh N" >&2
    exit 64
}

[[ $# -eq 1 && $1 =~ ^[0-9]{1,3}$ ]] || usage

test_num=$((10#$1))
(( test_num <= 999 )) || usage

if (( test_num <= 52 )); then
    printf -v test_id '%02d' "$test_num"
else
    printf -v test_id '%03d' "$test_num"
fi

# Keep MVS names within their eight-character limit independently of the
# directory ID width. These remain unique for test numbers 0..999.
printf -v job_base 'RG%03d' "$test_num"
printf -v entry 'BCRG%04d' "$test_num"
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd -- "$script_dir/../.." && pwd)"

shopt -s nullglob
matches=("$script_dir/${test_id}-"*)
shopt -u nullglob

if (( ${#matches[@]} != 1 )); then
    echo "run-test: expected exactly one ${test_id}-* test directory" >&2
    exit 65
fi

case_dir=${matches[0]}
case_name=$(basename "$case_dir")
source="$case_dir/source.bcpl"
library="$case_dir/library.bcpl"
# Whole-library tests may reference the shared canonical native BLIB unit.
library_ref="$case_dir/library-source.txt"
if [[ -f "$library_ref" ]]; then
    [[ ! -f "$library" ]] || {
        echo "run-test: library.bcpl and library-source.txt conflict" >&2
        exit 65
    }
    library_name="$(tr -d '\r\n' < "$library_ref")"
    if [[ "$library_name" != "blib" ]]; then
        echo "run-test: unsupported shared library $library_name" >&2
        exit 65
    fi
    python3 "$root/native-compiler/bootstrap-cambridge/make-demoted.py" --blib-only || exit $?
    library="$root/workarea/bootstrap-cambridge/demoted/blib"
fi
native="$case_dir/native.asm"
cambridge_parm="$case_dir/cambridge-parm.txt"
generated_regex="$case_dir/generated-regex.txt"
compile_only="$case_dir/compile-only.txt"

[[ -f "$source" ]] || {
    echo "run-test: missing $source" >&2
    exit 66
}

work="$root/workarea/native-regression/$case_name"
mkdir -p "$work"

source_copy="$work/$case_name.bcpl"
cp "$source" "$source_copy"

compiler_job="${job_base}C"

compiler_driver="${CAMBRIDGE_COMPILE:-$root/tools/cambridge-compile}"

echo "=== Cambridge compile: $case_name ==="
compile_args=(
    "$source_copy"
    --job-name "$compiler_job"
    --listing light
    --timeout 180
)
if [[ -f "$cambridge_parm" ]]; then
    compile_args+=(--cambridge-parm "$cambridge_parm")
fi
python3 "$compiler_driver" "${compile_args[@]}" || exit $?

generated_root="$root/workarea/$case_name.s370.asm"
generated="$work/generated.s370.asm"

[[ -f "$generated_root" ]] || {
    echo "run-test: Cambridge CODE was not recovered: $generated_root" >&2
    exit 66
}

mv -f "$generated_root" "$generated"

if [[ -f "$generated_regex" ]]; then
    echo
    echo "=== Generated-code assertions ==="
    python3 - "$generated" "$generated_regex" <<'PY' || exit $?
from pathlib import Path
import re
import sys

generated_path = Path(sys.argv[1])
patterns_path = Path(sys.argv[2])
text = generated_path.read_text(encoding="latin-1")
patterns = [
    line.strip()
    for line in patterns_path.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.lstrip().startswith("#")
]
if not patterns:
    raise SystemExit(f"{patterns_path}: no regex assertions found")
for pattern in patterns:
    if re.search(pattern, text, re.MULTILINE) is None:
        print(f"missing generated-code pattern: {pattern}", file=sys.stderr)
        raise SystemExit(1)
    print(f"MATCH {pattern}")
PY
fi

if [[ -f "$compile_only" ]]; then
    echo
    echo "=== Regression result ==="
    echo "TEST:        $case_name"
    echo "OBJECTIVE:   PASS"
    echo "TERMINATION: COMPILE-ONLY"
    echo "RESULT:      PASS"
    exit 0
fi

# 069 must use the separately assembled object-library path. This
# bypasses the static source combiner without changing any older test.
if (( test_num == 69 )); then
    echo
    echo "=== Build independently linked BLIB object GO job ==="
    jcl="$work/069-object-go.jcl"
    rm -f "$jcl"
    python3 "$case_dir/prepare-stage2.py" "$generated" "$jcl" || exit $?
    [[ -s "$jcl" ]] || {
        echo "run-test: 069 JCL generator produced no deck" >&2
        exit 66
    }
else
library_generated=""
if [[ -f "$library" ]]; then
    library_copy="$work/$case_name-library.bcpl"
    cp "$library" "$library_copy"

    library_job="${job_base}L"

    echo
    echo "=== Cambridge library compile: $case_name ==="
    library_args=(
        "$library_copy"
        --job-name "$library_job"
        --listing light
        --timeout 180
    )
    if [[ -f "$cambridge_parm" ]]; then
        library_args+=(--cambridge-parm "$cambridge_parm")
    fi
    python3 "$compiler_driver" "${library_args[@]}" || exit $?

    library_generated_root="$root/workarea/$case_name-library.s370.asm"
    library_generated="$work/library-generated.s370.asm"

    [[ -f "$library_generated_root" ]] || {
        echo "run-test: library Cambridge CODE was not recovered: $library_generated_root" >&2
        exit 66
    }

    mv -f "$library_generated_root" "$library_generated"
fi

combined="$work/native-test.asm"
# entry is precomputed above as an eight-character assembler symbol.

if [[ -f "$native" ]]; then
    echo
    echo "=== Prepare external native global ==="
    python3 "$script_dir/prepare-native-global.py" \
        "$generated" \
        "$root/asm/bcplmain-wip.asm" \
        "$combined" \
        "$entry" \
        NATIVEAD \
        151 || exit $?
elif [[ -n "$library_generated" ]]; then
    echo
    echo "=== Combine separately compiled BCPL units ==="
    python3 "$script_dir/combine-separate-bcpl.py" \
        "$generated" \
        "$library_generated" \
        "$root/asm/bcplmain-wip.asm" \
        "$combined" \
        "$entry" || exit $?
else
python3 - "$generated" "$root/asm/bcplmain-wip.asm"     "$combined" "$entry" <<'PY'
from pathlib import Path
import re
import sys

generated_path = Path(sys.argv[1])
runtime_path = Path(sys.argv[2])
output_path = Path(sys.argv[3])
entry = sys.argv[4]

raw = generated_path.read_bytes()
text = raw.decode("latin-1")

# The recovered printer stream can contain non-ASCII bytes in generated
# comments.  Native constants themselves are emitted as assembler hex data.
# Replace transport-only non-ASCII text so the card deck remains ASCII.
text = "".join(ch if ord(ch) < 128 else "?" for ch in text)

lines = text.splitlines()

# The generated module normally declares BCPLMAIN external.  In this
# regression deck BCPLMAIN is assembled later in the same source, so
# remove that external declaration and resolve A(BCPLMAIN) locally.
extern_indexes = [
    i for i, line in enumerate(lines)
    if re.fullmatch(r"\s*EXTRN\s+BCPLMAIN\s*", line)
]
if len(extern_indexes) != 1:
    raise SystemExit(
        f"expected one EXTRN BCPLMAIN, found {len(extern_indexes)}"
    )
del lines[extern_indexes[0]]

csect_indexes = [
    i for i, line in enumerate(lines)
    if re.fullmatch(r"\s*CSECT\s*", line)
]
if len(csect_indexes) != 1:
    raise SystemExit(
        f"expected one unnamed generated CSECT, found {len(csect_indexes)}"
    )
lines[csect_indexes[0]] = f"{entry} CSECT"

end_indexes = [
    i for i, line in enumerate(lines)
    if re.fullmatch(r"\s*END(?:\s+.*)?", line)
]
if len(end_indexes) != 1:
    raise SystemExit(
        f"expected one generated END statement, found {len(end_indexes)}"
    )
del lines[end_indexes[0]]

generated = "\n".join(lines).rstrip() + "\n"
runtime = runtime_path.read_text(encoding="ascii")

combined = (
    generated
    + "*\n"
    + "* BCPLMAIN WIP FOLLOWS\n"
    + "*\n"
    + runtime.rstrip("\n")
    + "\n"
)

for number, line in enumerate(combined.splitlines(), 1):
    if len(line) > 71:
        raise SystemExit(
            f"{output_path}:{number}: source exceeds column 71 "
            f"(length {len(line)})"
        )

output_path.write_text(combined, encoding="ascii", newline="\n")
PY
fi

echo
echo "=== Assembler preflight ==="
python3 "$root/tools/checks/check-asm-source.py" "$combined" || exit $?
if [[ -f "$native" ]]; then
    python3 "$root/tools/checks/check-asm-source.py" "$native" || exit $?
fi

echo
echo "=== Build native assemble/link/go job ==="
if [[ -f "$native" ]]; then
    jcl="$work/native-test-heavy.jcl"
    python3 "$script_dir/make-two-object-job.py" \
        "$combined" \
        "$native" \
        "$jcl" \
        --entry "$entry" \
        --job-name "${job_base}R" || exit $?
else
    python3 "$root/tools/make-asm-job" \
        "$combined" \
        --output-dir "$work" \
        --entry "$entry" \
        --job-name "${job_base}R" \
        --listing heavy \
        --force || exit $?

    jcl="$work/native-test-heavy.jcl"
fi

if [[ ! -f "$native" ]]; then
python3 - "$jcl" "$test_num" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
test_no = sys.argv[2]
text = path.read_text(encoding="ascii")
old = "//GO       EXEC PGM=*.LKED.SYSLMOD,\n"
seconds = 3 if test_no == "3" else 1
new = f"//GO       EXEC PGM=*.LKED.SYSLMOD,TIME=(,{seconds}),\n"
if text.count(old) != 1:
    raise SystemExit("cannot locate final GO EXEC statement")
path.write_text(text.replace(old, new, 1), encoding="ascii", newline="\n")
PY
fi

fi # end regular static/native assembly strategy

echo
echo "=== Submit native run ==="
submit=$(
    bash "$root/tools/submit-jcl" --timeout 30 "$jcl"
) || exit $?

echo "$submit"

job=$(awk '/^JOB [0-9]+$/ {print $2}' <<<"$submit" | tail -1)

[[ -n "$job" ]] || {
    echo "run-test: could not obtain JES job number" >&2
    exit 65
}

echo
echo "=== Wait for complete job report ==="

expected_file="$case_dir/expected.txt"

[[ -f "$expected_file" ]] || {
    echo "run-test: missing $expected_file" >&2
    exit 66
}

expected_output() {
    [[ -s "$expected_file" ]] || return 1
    cat "$expected_file"
}


show_bcpl_output() {
    local report emitted

    report=$(bash "$root/tools/dump-report-for-job" "$job" 2>/dev/null)
    printf '%s\n' "$report" >"$work/job-report.txt"

    emitted=$(
        python3 - "$expected_file" "$work/job-report.txt" <<'PY'
from pathlib import Path
import sys

expected_path = Path(sys.argv[1])
report_path = Path(sys.argv[2])

expected = [
    line.strip()
    for line in expected_path.read_text(encoding="utf-8").splitlines()
]
report = report_path.read_text(encoding="utf-8", errors="replace").splitlines()

if not expected:
    raise SystemExit(1)

# Native program output follows the linkage editor report.  Restrict matching
# to the suffix after the final linker authorization line so source/JCL,
# assembler listings, and link-edit listings cannot satisfy an expectation.
linker_ends = [
    index
    for index, line in enumerate(report)
    if "AUTHORIZATION CODE IS" in line
]
if not linker_ends:
    raise SystemExit(1)

runtime_report = report[linker_ends[-1] + 1:]
trimmed = [line.strip() for line in runtime_report]
width = len(expected)

for start in range(0, len(trimmed) - width + 1):
    if trimmed[start:start + width] == expected:
        print("\n".join(expected))
        raise SystemExit(0)

raise SystemExit(1)
PY
    ) || return 1

    [[ -n "$emitted" ]] || return 1

    echo
    echo "=== BCPL output ==="
    printf '%s\n' "$emitted"
}

show_result() {
    local objective=$1
    local termination=$2
    local overall=$3

    echo
    echo "=== Regression result ==="
    echo "TEST:        $case_name"
    echo "OBJECTIVE:   $objective"
    echo "TERMINATION: $termination"
    echo "RESULT:      $overall"
}

deadline=$((SECONDS + 30))
while (( SECONDS <= deadline )); do
    summary=$("$root/tools/job-summary" "$job" 2>&1)
    rc=$?

    if (( rc == 0 )); then
        echo "$summary"

        if expected_output >/dev/null 2>&1; then
            if ! show_bcpl_output; then
                echo
                echo "=== Output mismatch ==="
                echo "EXPECTED:"
                sed 's/^/  /' "$expected_file"
                echo "ACTUAL:"
                echo "  expected text was not found in the native job report"
                echo "  full report: ${work#$root/}/job-report.txt"
                if [[ ${NATIVE_REGRESSION_SHOW_OUTPUT:-0} == 1 ]]; then
                    echo
                    echo "=== Native job report ==="
                    cat "$work/job-report.txt"
                fi
                show_result "FAIL" "NORMAL" "FAIL"
                exit 1
            fi
        fi

        show_result "PASS" "NORMAL" "PASS"
        exit 0
    fi

    # job-summary returns 1 for a completed failing job and 2 while the
    # complete report is not yet available.
    if (( rc == 1 )); then
        echo "$summary"

        report=$(
            bash "$root/tools/dump-report-for-job" "$job" 2>/dev/null
        )
        printf '%s\n' "$report" >"$work/job-report.txt"

        if [[ ${NATIVE_REGRESSION_SHOW_OUTPUT:-0} == 1 ]]; then
            echo
            echo "=== Native job report ==="
            cat "$work/job-report.txt"
        fi

        if expected_output >/dev/null 2>&1 &&
           show_bcpl_output &&
           grep -a -q 'ABEND S322' <<<"$report"; then
            show_result \
                "PASS" \
                "S322 (known runtime defect)" \
                "PASS WITH KNOWN RUNTIME DEFECT"
            exit 0
        fi

        show_result "FAIL" "ABNORMAL" "FAIL"
        exit 1
    fi

    sleep 1
done

echo "run-test: timed out waiting for JOB $job to finish" >&2
show_result "UNKNOWN" "HOST WAIT TIMEOUT" "FAIL"
exit 75
