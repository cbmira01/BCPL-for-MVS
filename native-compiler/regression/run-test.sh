#!/usr/bin/env bash
set -u
set -o pipefail

usage() {
    echo "Usage: bash native-compiler/regression/run-test.sh NN" >&2
    exit 64
}

[[ $# -eq 1 && $1 =~ ^[0-9][0-9]$ ]] || usage

test_no=$1
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd -- "$script_dir/../.." && pwd)"

shopt -s nullglob
matches=("$script_dir/${test_no}-"*)
shopt -u nullglob

if (( ${#matches[@]} != 1 )); then
    echo "run-test: expected exactly one ${test_no}-* test directory" >&2
    exit 65
fi

case_dir=${matches[0]}
case_name=$(basename "$case_dir")
source="$case_dir/source.bcpl"

[[ -f "$source" ]] || {
    echo "run-test: missing $source" >&2
    exit 66
}

work="$root/workarea/native-regression/$case_name"
mkdir -p "$work"

source_copy="$work/$case_name.bcpl"
cp "$source" "$source_copy"

compiler_job="RG${test_no}COMP"

echo "=== Cambridge compile: $case_name ==="
python3 "$root/tools/cambridge-compile"     "$source_copy"     --job-name "$compiler_job"     --listing light || exit $?

generated_root="$root/workarea/$case_name.s370.asm"
generated="$work/generated.s370.asm"

[[ -f "$generated_root" ]] || {
    echo "run-test: Cambridge CODE was not recovered: $generated_root" >&2
    exit 66
}

mv -f "$generated_root" "$generated"

combined="$work/native-test.asm"
entry="BCRG00${test_no}"

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

echo
echo "=== Assembler preflight ==="
python3 "$root/tools/checks/check-asm-source.py" "$combined" || exit $?

echo
echo "=== Build native assemble/link/go job ==="
python3 "$root/tools/make-asm-job"     "$combined"     --output-dir "$work"     --entry "$entry"     --job-name "RG${test_no}RUN"     --listing heavy     --force || exit $?

jcl="$work/native-test-heavy.jcl"

echo
echo "=== Submit native run ==="
submit=$(
    bash "$root/tools/submit-jcl" --timeout 120 "$jcl"
) || exit $?

echo "$submit"

job=$(awk '/^JOB [0-9]+$/ {print $2}' <<<"$submit" | tail -1)

[[ -n "$job" ]] || {
    echo "run-test: could not obtain JES job number" >&2
    exit 65
}

echo
echo "=== Wait for complete job report ==="

deadline=$((SECONDS + 180))
while (( SECONDS <= deadline )); do
    if summary=$("$root/tools/job-summary" "$job" 2>&1); then
        echo "$summary"
        exit 0
    fi

    if grep -a -q "END JOB[[:space:]]\+$job"         "$root/mvs-state/prt/prt00e.txt" 2>/dev/null; then
        echo "$summary"
        echo
        echo "Full report:"
        bash "$root/tools/dump-report-for-job" "$job"
        exit 1
    fi

    sleep 1
done

echo "run-test: timed out waiting for JOB $job to finish" >&2
exit 75
