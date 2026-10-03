#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

set -u
set -o pipefail

COMPILE="tools/compile-and-run"
ICINT="asm/icintv17.asm"
SUITE="suite"

FAILURES=0

run_demo()
{
    name="$1"
    shift

    echo
    echo "================================================================"
    echo "DEMO: $name"
    echo "================================================================"

    if "$@"
    then
        echo
        echo "PASS: $name"
    else
        rc=$?
        echo
        echo "FAIL: $name (rc=$rc)"
        FAILURES=$((FAILURES + 1))
    fi
}

run_demo "queens" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/queens/queens.bcpl"

run_demo "knight" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/knight/knight.bcpl"

run_demo "hanoi" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/hanoi/hanoi.bcpl"

run_demo "sieve" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/sieve/sieve.bcpl"

run_demo "gcd" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/gcd/gcd.bcpl"

run_demo "quicksort" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/quicksort/quicksort.bcpl" \
    +"$SUITE/random/random.bcpl"

run_demo "binary-search" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/binary-search/binary-search.bcpl"

run_demo "linked-list" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/linked-list/linked-list.bcpl"

run_demo "binary-tree" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/binary-tree/binary-tree.bcpl"

run_demo "hash-table" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/hash-table/hash-table.bcpl"

run_demo "word-count" \
    "$COMPILE" --results \
    --dd TEXT="$SUITE/word-count/input.txt" \
    "$ICINT" \
    "$SUITE/word-count/word-count.bcpl"

run_demo "rpn-calculator" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/rpn-calculator/rpn-calculator.bcpl"

run_demo "expression-parser" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/expression-parser/expression-parser.bcpl"

run_demo "maze" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/maze/maze.bcpl"

run_demo "stream-fanout" \
    "$COMPILE" --results \
    --dd AIN="$SUITE/stream-fanout/ain.txt" \
    --dd BIN="$SUITE/stream-fanout/bin.txt" \
    --dd CIN="$SUITE/stream-fanout/cin.txt" \
    "$ICINT" \
    "$SUITE/stream-fanout/stream-fanout.bcpl"

echo
echo "================================================================"
echo "SUITE COMPLETE"
echo "================================================================"

if [ "$FAILURES" -eq 0 ]
then
    echo "All 15 demos passed."
    exit 0
else
    echo "$FAILURES demo(s) failed."
    exit 1
fi

