# TA.8 — Preservation-first and minimal documentation decision

**Date:** 24 November 2026 EST  
**March:** TA.8 — Release Audit and Controlled Publication  
**Status:** Private release preparation; publication not authorized.

The owner directs extension of the existing repository preservation-first
policy to the tape, with clear attribution. Historical redistribution
rights remain unresolved; this is an owner project-policy decision,
not legal clearance or a new grant of rights. Retain the rights status
in the frozen manifest. The earlier audit's internal stop pending a
policy decision is superseded by this direction, not by discovery of
new permissions. The owner requests minimum documentation changes
in TA.8 and defers semantic restructuring of documentation to a separate
future milestone.

Retain BC0004 unchanged. The RC4 companion guide explicitly supersedes
the older BT0003 draft prose. Accompany the AWS with the complete
existing LICENSE.md, THIRD-PARTY-NOTICES.md, historical README.Nordier,
README.orig.Yap and INDEX, and exact frozen manifest. Do not distribute
a bare tape without those notices and guide. This is a limited
release-specific documentation solution, not a new documentation
framework or a claim that all tape text has been rewritten.

Prepare a private ZIP containing these files and SHA256SUMS, verifying
each extracted archive entry against its source, including the exact
accepted AWS SHA-256. Keep the outer archive SHA-256 and review receipt
under workarea. No publication or Git release/tag creation is performed.

The read-only saved-MVS reviewer checks the pinned production,
installation, TA.4 automatic acceptance and TA.7 integration seals
and recorded result identities, both original media checksums and
the frozen manifest digest. It checks 326 actual saved functional JES
steps and their accepted semantic verdicts without rerunning MVS.
The tool does not independently recompute the original BCPL golden
comparisons; those remain the accepted predecessor reviewers' work.

Keep historical registry reservation entries unchanged; the top-level
lifecycle mapping records RC4 technical acceptance separately.
The historical registry readers inspected use the schema version and
candidates list, and the RC4 producer demands the original reservation
entry exactly. No new VOLSER or manifest is created.

Assistant workspace: Python syntax and 19/19 synthetic assertions passed,
covering successful sealed review, byte-preserving ZIP and refusal of
changed media/manifest, changed or extra evidence, bad JES and semantic
records, incorrect jobs/marker, symlinks, duplicate/unsafe seal entries.
Actual MVS receipts and AWS bytes are private; the live saved-evidence
review and private package remain pending. No MVS execution is required.

TA.8 remains open. Separate owner publication approval and exact-byte
asset transfer remain necessary. Formal TA.8 closure is not yet ordered.
