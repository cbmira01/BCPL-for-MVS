# BCPL Demonstration Suite

This directory is intended for small BCPL programs that demonstrate the language,
classic algorithms, data structures, mathematical routines, text and data handling,
and the reconstructed BCPL/MVS runtime environment.

The suite is deliberately broader than a regression-test collection.  The programs
should be interesting to read as BCPL, small enough to study without much setup,
and useful as examples of the programming style found in historical BCPL systems.
Where practical, each program should also exercise some meaningful part of the
compiler, INTCODE interpreter, runtime library, or MVS host interface.

## Shared modules

Some demonstrations benefit from small reusable BCPL modules rather than embedding
all support code in each program.

- **random** — a seedable pseudo-random number generator for reproducible test data,
  randomized searches, shuffling, maze work, randomized sorting choices, and similar
  demonstrations.  See `random/README.md`.

Shared modules should have a small documented GLOBAL-vector interface and should be
usable through the existing multi-module `compile-and-run` mechanism.

## Core demonstration programs

The initial suite consists of fifteen representative programs:

1. **queens** — solve the N-Queens problem by backtracking.
2. **knight** — find or explore a knight's tour on a chessboard.
3. **hanoi** — solve the Towers of Hanoi recursively.
4. **sieve** — generate primes with the Sieve of Eratosthenes.
5. **gcd** — demonstrate Euclid's algorithm and related integer arithmetic.
6. **quicksort** — sort a vector using recursive partitioning.
7. **binary-search** — search a sorted vector and demonstrate indexed data access.
8. **linked-list** — construct, traverse, modify, and destroy a linked structure.
9. **binary-tree** — build and traverse a binary search tree.
10. **hash-table** — demonstrate hashing and collision handling.
11. **word-count** — perform simple stream-oriented text processing and statistics.
12. **rpn-calculator** — evaluate reverse-Polish expressions with an explicit stack.
13. **expression-parser** — parse and evaluate a small arithmetic expression language.
14. **maze** — solve a small maze using search and explicit data structures.
15. **stream-fanout** — work with several named streams and demonstrate BCPL/MVS I/O.

These programs should collectively exercise recursion, iteration, vectors, packed
strings, arithmetic, searching, sorting, dynamic data structures, parsing, explicit
stacks, stream I/O, and the GLOBAL-vector calling model.

## BCPL idioms

A separate set of small examples should demonstrate BCPL itself rather than merely
implementing familiar algorithms.  Topics should include, as suitable examples are
developed:

- `LET`, `AND`, and simultaneous declarations;
- `VALOF` and `RESULTIS`;
- `TEST ... THEN ... OR`;
- `SWITCHON`, `CASE`, and `DEFAULT`;
- `REPEAT`, `REPEATWHILE`, and `REPEATUNTIL`;
- vectors and vector indexing;
- `MANIFEST` constants;
- `GLOBAL` declarations and the global vector;
- functions used as values;
- packed strings and byte access;
- pointer-oriented BCPL programming;
- explicit input and output stream selection;
- multiple simultaneously open streams;
- recursion and non-local control mechanisms where historically appropriate.

The idiom examples may be independent programs or particularly clear programs from
the core suite.  Their purpose is to make characteristic BCPL constructs easy to
find and understand.

## Coroutines

Coroutine support is an advanced part of the suite and should be treated separately
until the historical BCPL interface and runtime implementation have been researched.
The Richards distributions and other surviving BCPL material should be examined
before choosing names, calling conventions, or semantics for coroutine primitives.

Once the historical mechanism is understood and supported by the reconstructed
runtime, the suite should contain at least one small coroutine demonstration.  A
producer/consumer example, or cooperating generators that exchange values, would be
a suitable first program.

## Style of the suite

Programs should favor clarity over cleverness.  They should use ordinary BCPL idioms,
contain enough commentary to explain the algorithm and any unusual language feature,
and avoid unnecessary dependencies on host-specific facilities.  MVS-specific I/O
examples are appropriate where the host interface itself is the subject of the demo.

The programs are also useful as progressive integration exercises for the BCPL-for-MVS
reconstruction, but the principal goal of this directory is to provide readable and
interesting examples of BCPL programming.