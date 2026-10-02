# BCPL Demonstration Suite

This directory contains small BCPL programs that demonstrate the language, classic
algorithms, data structures, mathematical routines, text and data handling, and the
reconstructed BCPL/MVS runtime environment.

The suite is deliberately broader than a regression-test collection.  The programs
should be interesting to read as BCPL, small enough to study without much setup, and
useful as examples of the programming style found in historical BCPL systems.  Where
practical, each program also exercises a meaningful part of the compiler, INTCODE
interpreter, runtime library, or MVS host interface.

Each demonstration directory contains a `README.md` with its `compile-and-run`
invocation.  The core demonstrations below are initial implementations and should be
validated on the local MVS/TK5 environment as they are exercised.

## Shared modules

Some demonstrations benefit from small reusable BCPL modules rather than embedding
all support code in each program.

- **[random](random/)** — seedable Park-Miller pseudo-random number generator for
  reproducible test data, randomized searches, shuffling, randomized sorting choices,
  and similar demonstrations.  This module has already been exercised successfully
  through the multi-module `compile-and-run` path.

Shared modules should have a small documented GLOBAL-vector interface and should be
usable through the existing multi-module `compile-and-run` mechanism.

## Core demonstration programs

The initial suite consists of fifteen representative programs:

1. **[queens](queens/)** — solve the eight-queens problem by recursive backtracking.
2. **[knight](knight/)** — construct a 5x5 knight's tour with Warnsdorff's heuristic.
3. **[hanoi](hanoi/)** — solve the Towers of Hanoi recursively.
4. **[sieve](sieve/)** — generate primes with the Sieve of Eratosthenes.
5. **[gcd](gcd/)** — demonstrate Euclid's algorithm and derive an LCM.
6. **[quicksort](quicksort/)** — recursively sort a vector; pivot selection uses the
   shared `random` module.
7. **[binary-search](binary-search/)** — search a sorted vector by iterative binary
   search.
8. **[linked-list](linked-list/)** — construct, traverse, and reverse a singly linked
   list represented in vector-backed storage.
9. **[binary-tree](binary-tree/)** — build, traverse, and search a binary search tree
   represented in vector-backed storage.
10. **[hash-table](hash-table/)** — demonstrate hashing and chained collision handling
    with vector-backed buckets and nodes.
11. **[word-count](word-count/)** — count characters, words, and lines from a named
    MVS input DD.
12. **[rpn-calculator](rpn-calculator/)** — evaluate a reverse-Polish expression with
    an explicit stack.
13. **[expression-parser](expression-parser/)** — recursively parse and evaluate a
    small arithmetic expression language.
14. **[maze](maze/)** — solve a fixed maze with recursive depth-first search.
15. **[stream-fanout](stream-fanout/)** — open several named MVS streams
    simultaneously, read them, and close them explicitly.

The data-structure examples deliberately use explicit vector-backed storage rather
than assuming a dynamic-allocation interface not yet established as part of the small
MR10 runtime being hosted here.

Collectively these programs exercise recursion, iteration, vectors, `TABLE`
expressions, packed strings, byte access, arithmetic, searching, sorting, linked data
structures, parsing, explicit stacks, stream I/O, multiple open streams, and the
GLOBAL-vector calling model.

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
- `TABLE` expressions;
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

The programs are also useful as progressive integration exercises for the
BCPL-for-MVS reconstruction, but the principal goal of this directory is to provide
readable and interesting examples of BCPL programming.
