# DR.1 — Directory organization: owner decision

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.1 — Architecture and Outlines (IN PROGRESS)  
**Date:** 25 November 2026 EST  
**Status:** Owner-approved directory scheme; implementation not yet authorized.

The owner agreed to the proposed two-directory arrangement for the eighteen-manual catalog, rather than placing all manuals directly under docs/.

- docs/product/ — product documentation.
- docs/project/ — project documentation, including the proposed shared MVS programming environment explanation.
- docs/README.md — reader-facing documentation catalog.
- Root README.md — project and public-release entry point.
- Existing packaging, component, test, tool and historical directories retain their distinct purposes and existing paths during reconciliation.

This approves the physical organization direction in [the architecture proposal](dr1-architecture-and-outlines-proposal-20261124.md), consistent with the [revised manual catalog](dr1-manual-catalog-owner-decisions-20261125.md) and [normative reference authority decision](dr1-reference-authority-owner-decision-20261125.md). Diátaxis types need not become separate directory levels. The proposed reader-need and subject navigation, canonical representation, detailed outlines and migration arrangements remain for review. The existing release-candidate how-to may remain at its current path during transition; do not duplicate it.

No directories for manuals have been created, and no existing files have been moved, deleted or rewritten apart from updating the DR.1 planning records. The DR.0 dependency qualification remains operative. DR.1 remains IN PROGRESS.
