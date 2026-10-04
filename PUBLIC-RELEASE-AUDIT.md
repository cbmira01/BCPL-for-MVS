# Public-release audit

Audit date: 4 October 2026.

This note records the repository review performed before changing the GitHub repository from private to public. It is a release checklist, not a warranty or legal opinion.

## Credentials and private data

The checked-in tree was reviewed for common credential material and private configuration. No private key, API-key file, `.env` file, or checked-in `config/dspal.local.yaml` was found.

The Git history for the intended local secret paths was also checked through GitHub's commit-history API:

- `.env` has no commits;
- `config/dspal.local.yaml` has no commits;
- `id_rsa` has no commits.

The commits that introduced `dspal` batch authentication were inspected. They introduced `batch_password: null`, password redaction, and the documented placeholder `YOURPASS`; no real password was found in those changes.

The repository currently has only the `main` branch. No additional public branch tip was found that would expose a different tree.

One privacy item remains by design: ordinary Git author/committer metadata contains the author's email address. Making the repository public also makes historical commit metadata public. Removing or replacing that metadata would require a history rewrite and is a separate decision from secret removal.

### Audit limitation

The review covered the complete reachable `main` history for known secret-bearing paths, the authentication-related diffs, branch state, and common credential patterns visible through the repository interfaces available during this audit. It was not a byte-for-byte entropy scan of every historical blob. As an additional mechanical check before or immediately after publication, a local clone should be scanned with a dedicated history scanner such as `gitleaks` or `trufflehog` against all revisions.

No known credential requires rotation as a result of this audit.

## Historical material and redistribution

`richards-bcpltape/` is a preserved historical collection, not original project code.

The provenance chain is well supported:

1. the files derive from Martin Richards' BCPL "transport" tape;
2. Ken Yap made a tar archive of the tape files available around the early 1990s;
3. Robert Nordier corrected character-mapping problems, assigned meaningful names, and organized the files;
4. Nordier publicly redistributes that archive as `bcpltape`;
5. Martin Richards' archive and the Computer History Museum Software Preservation Group both point to the Nordier-curated historical material.

What this audit did **not** find is a blanket conventional open-source license that clearly grants unrestricted redistribution of every file on the 1984 tape. That is not surprising for preserved software of this period. Martin Richards' current BCPL page describes a present-day machine-independent distribution as free for private and academic use; that statement should not be silently applied to every historical tape file.

Accordingly:

- the project's MIT license does not cover `richards-bcpltape/`;
- historical notices and provenance files must remain with the archive;
- public availability upstream is treated as provenance evidence, not as relicensing;
- anyone redistributing the historical material should make their own assessment of the applicable rights.

### Release decision: preserve first

The project has chosen to keep the historical tape payload in the public repository rather than remove it and replace it with a fetch step.

The reasons are archival and technical: the exact preserved snapshot is primary evidence for the reconstruction, its provenance is documented, and the same material has been intentionally preserved and made publicly available by established BCPL archival sources. The repository therefore publishes the historical material as historical material, with its provenance intact and without claiming that the project's MIT license applies to it.

This preservation-first decision resolves the release-policy question noted during the audit. It does not convert the historical files into MIT-licensed or otherwise newly licensed material.

## Imported artifacts

The following project files are imported or derived from historical material and are called out explicitly in `THIRD-PARTY-NOTICES.md`:

- `richards-bcpltape/**` — curated historical transport-tape material;
- `intcode/blibi.int` — byte-for-byte copy of `richards-bcpltape/mr10/bcplkit/blibi`;
- `intcode/cgi.int` — byte-for-byte copy of `richards-bcpltape/mr10/bcplkit/cgi`;
- `intcode/syni.int` — byte-for-byte copy of `richards-bcpltape/mr10/bcplkit/syni`;
- `intcode/trni.int` — byte-for-byte copy of `richards-bcpltape/mr10/bcplkit/trni`;
- the ICINT assembler line in `asm/` is a reconstruction based closely on `richards-bcpltape/mr10/bcplkit/icint`, with MVS-hosting changes documented in source and tests;
- the Richards factorial demonstration is retained as a historical/reconstruction example and is duplicated between the early compiler probe and the readable demo suite.

TK5 and Hercules are dependencies, not vendored source trees in this repository. The Docker build downloads TK5; built images therefore contain third-party material even though the TK5 archive is not committed here.

## Documentation review

All README files present at audit time were reviewed. Stale references to the abandoned Cambridge-first bootstrap direction and to a hypothetical new System/370 code generator were removed or corrected. Repetitive one-paragraph demo READMEs were consolidated into `suite/README.md`. Obsolete `pdspal`/early-`dspal` planning notes were removed from the current tree; their history remains in Git.

AI assistance is acknowledged briefly in `THIRD-PARTY-NOTICES.md`. Project documentation no longer uses lengthy process descriptions of AI drafting as a substitute for technical provenance.
