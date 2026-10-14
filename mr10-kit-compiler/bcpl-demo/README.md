# BCPL programs

These 17 programs show what BCPL can do. Each prints a short `DEMO:` line when run.

| Program | What it does |
| --- | --- |
| richards-factorial | Computes factorials by recursion |
| queens | Solves the eight-queens puzzle |
| knight | Finds a knight's tour |
| hanoi | Moves the Towers of Hanoi |
| sieve | Finds prime numbers |
| gcd | Finds greatest common divisors and least common multiples |
| quicksort | Sorts values with a shared random-number module |
| binary-search | Searches a sorted vector |
| linked-list | Walks and reverses a linked list |
| binary-tree | Builds and searches a binary tree |
| hash-table | Stores and finds keyed values |
| word-count | Counts text read from a named DD |
| rpn-calculator | Evaluates stack-based expressions |
| expression-parser | Parses arithmetic expressions |
| maze | Finds a path through a maze |
| stream-fanout | Reads three named input streams |
| coroutines | Runs a coroutine-based generator |

## Run

From the repository root:

```sh
tools/run-mr10kit-demo-suite
```

On MVS, first install the mapped BCPLDEMO and LIBRARY members. Then submit stored `MR10_JCL(MRBCDEMO)` with `tools/dspal submit MR10_JCL MRBCDEMO`. See [suite jobs](../jcl/README-SUITES.md).

Some programs need extra modules or input DDs. The suite runner and stored JCL provide those details. These are demonstrations; exact-output checks are in [the regression panel](../tests/00-regression-panel/README.md).
