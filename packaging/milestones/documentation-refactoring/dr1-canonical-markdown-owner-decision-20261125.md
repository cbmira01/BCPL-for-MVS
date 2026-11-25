# DR.1 — Canonical documentation format: owner decision

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.1 — Architecture and Outlines (IN PROGRESS)  
**Date:** 25 November 2026 EST  
**Status:** Owner-approved canonical format and presentation direction.

The owner agreed to the proposed Markdown approach: repository Markdown is the canonical documentation format, with GitHub as the primary reading experience. Offline and MVS-readable representations derive from the same documentation, with release-specific information drawn from the relevant authoritative metadata where practical.

## Agreed direction

- Maintain canonical human-authored manuals as UTF-8 Markdown in the Git repository, versioned with corresponding source and contracts.
- Use GitHub repository rendering as the primary reader-facing presentation.
- Do not maintain a separate, independently authored Wiki.
- Defer GitHub Pages until a demonstrated need arises; any later Pages presentation should derive from the canonical documents.
- Derive offline and MVS-readable documentation from the canonical material rather than maintaining independent competing manuals.

The exact offline representation, rendering and conversion tools, MVS record formats and member mappings, and release integration remain DR.4 design decisions. Preserve the exact existing RC4 publication artifacts and frozen release-specific documentation. Existing machine-readable manifests, registries, configuration, historical sources, evidence and legal records retain their respective formats and authority. Markdown canonicality applies to the manuals, not a conversion mandate for every repository file.

This decision complements the [approved directory scheme](dr1-directory-organization-owner-decision-20261125.md), [revised manual catalog](dr1-manual-catalog-owner-decisions-20261125.md) and [normative reference authority decision](dr1-reference-authority-owner-decision-20261125.md). Detailed navigation, outlines, migration and acceptance arrangements remain for review. No rendering infrastructure, manual implementation, relocation, deletion, release activity or MVS operation has been undertaken. DR.1 remains IN PROGRESS.
