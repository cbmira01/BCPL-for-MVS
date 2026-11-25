# DR.1 — Manual catalog: owner decisions

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.1 — Architecture and Outlines (IN PROGRESS)  
**Date:** 25 November 2026 EST  
**Basis:** [Architecture and outlines proposal](dr1-architecture-and-outlines-proposal-20261124.md), followed by owner discussion.

## Agreed catalog direction

The owner agreed to the language documentation approach, common compiler manuals and common runtime/library reference. The owner also directed that the MVS educational background remain one large explanation, development and testing remain chapters in one how-to, and operation receive its own distinct how-to.

| Subject | Owner decision |
| --- | --- |
| BCPL language | Add an implementation-specific language reference and a progressive language tutorial; absorb the first-program tutorial into the latter |
| Compilers | Common manuals with distinct MR10 Kit Compiler, interpreter-hosted demoted Cambridge Compiler and unfinished native-running Cambridge Compiler chapters |
| Cambridge Runtime and Libraries | Common reference with distinct Core Runtime, Base Library (BLIB) and Coroutine Support Library chapters |
| MVS programming environment | One coherent explanation covering System/370, MVS, JCL, Hercules and the assembler/linkage toolchain |
| Development and testing | One how-to, with development and testing as distinct chapters |
| Product operation | A distinct how-to, separate from installation, programming and project maintenance |

## Agreed BCPL language documentation approach

Describe BCPL as implemented by this programming system, grounded in historical primary sources and actual compiler behavior. Explicitly distinguish MR10 and Cambridge language capabilities where necessary; do not assume modern BCPL dialect features are supported. Use actual compiler and MVS results to verify material. Historical sources establish provenance and intended behavior; implementation-specific claims require corresponding evidence. Do not infer language support solely from a successful example in another compiler.

### Tutorial on BCPL Programming

**Filename:** Tutorial-on-BCPL-Programming.md  
**Audience:** New BCPL programmers.  
**Purpose:** Learn through progressive, executable examples rather than read an exhaustive language specification.

Agreed outline direction:

1. Your first BCPL program
2. Constants, variables and declarations
3. Expressions and operators
4. Conditional execution and iteration
5. Functions and routines
6. Vectors, pointers and indirection
7. Strings and character manipulation
8. Global variables and separate compilation
9. Dynamic memory management
10. Data structures and algorithms
11. Coroutines
12. Writing a substantial BCPL application

Use the existing MR10 language and BCPL demonstrations as starting points, with verified source examples. The tutorial links to compile/run procedures and library references rather than duplicating them. Identify library-dependent material, compiler/profile prerequisites and unverified features. The detailed chapter sequence and examples remain subject to review.

### Reference for the BCPL Language

**Filename:** Reference-for-the-BCPL-Language.md  
**Audience:** Programmers and compiler developers.  
**Purpose:** Consult precise syntax and language semantics for the implemented dialects.

Agreed outline direction:

1. Lexical structure
2. Syntax and grammar
3. Data representation
4. Declarations and scope
5. Expressions and operator precedence
6. Commands and control structures
7. Functions and routines
8. Storage and addressing
9. Program structure and separate compilation
10. Language dialects and implementation differences

Distinguish core language semantics from compiler options, library APIs, runtime ABI, MVS procedures and historical/modern dialect features. Link to their respective authorities. Mark differences and verification limits without implying that the native-running Cambridge Compiler is available. A comparative compiler feature matrix may be useful; its contents must be source-grounded and verified, not invented.

## Revised candidate catalog

The earlier proposal contained 15 manuals plus the optional MVS explanation. The decisions above replace one tutorial, add one language reference, add one operating how-to and retain the MVS explanation, yielding 18 candidate manuals.

### Product (13)

| Type | Title |
| --- | --- |
| Tutorial | Tutorial on BCPL Programming |
| Tutorial | Tutorial on System Extensions |
| How-to | How to Install BCPL from Tape |
| How-to | How to Operate the BCPL Programming System |
| How-to | How to Compile and Run BCPL Programs |
| How-to | How to Use System Extensions |
| Explanation | Explanation of BCPL Compilers |
| Explanation | Explanation of the Cambridge Runtime and Libraries |
| Explanation | Explanation of System Extensions |
| Reference | Reference for the BCPL Language |
| Reference | Reference for BCPL Compilers |
| Reference | Reference for the Cambridge Runtime and Libraries |
| Reference | Reference for System Extensions |

### Project and shared background (5)

| Type | Title |
| --- | --- |
| How-to | How to Reconstruct BCPL from Source |
| How-to | How to Develop and Test BCPL for MVS |
| How-to | How to Create a Release Candidate |
| Reference | Reference for Project Tools |
| Explanation | Explanation of the MVS Programming Environment |

The exact title and outline of the operating how-to, the placement of shared background, detailed outlines, authority boundaries, directory organization, navigation and overall DR.1 acceptance remain open for owner review. The catalog grouping follows the earlier proposal; it is not permission to move existing files. No implementation, relocation, deletion or MVS operation was performed. The DR.0 dependency qualification remains in force.
