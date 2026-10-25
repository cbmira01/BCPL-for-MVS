# WSL operator command policy

**Status:** Owner-directed repository operating rule, 25 October 2026.

This policy applies to commands supplied by ChatGPT for the
BCPL for MVS 3.8 Reconstruction project. It supplements
[`git-mvs-authority.md`](git-mvs-authority.md) and does not revise the
accepted runtime or milestone gates.

## Mandatory rules

1. Work directly on GitHub `main`. Do not create feature branches.
   Do not rewrite the history of existing commits to apply this rule.
2. Do not supply downloadable handoff files, ZIP archives, or other
   download packages. GitHub is authoritative.
3. After **every operational GitHub commit**, supply executable WSL
   commands to update the `main` checkout and perform relevant checks.
4. **Never enable fail-fast in operator-pasted WSL command blocks.**
   Do not use `set -e`, `set -u`, `set -o pipefail`,
   `set -euo pipefail`, or top-level `exit`. When useful, start a
   block with `set +e`, `set +u`, `set +o pipefail` to cancel
   options left by an earlier command block. Commands must preserve
   the interactive WSL shell when a subcommand fails.
5. Report each important command's return code. If a required
   prerequisite fails, **skip dependent operations** using ordinary
   conditional control flow, without terminating the shell. This is
   dependency gating, not shell-level fail-fast.
6. Preserve available MVS/JES output **on success and failure**. Check
   actual job completion, assembler severity and the generated report.
   Never describe a failed or incomplete execution as accepted evidence.
7. A commit is not authorization to install or overwrite permanent MVS
   datasets. MVS execution, candidate promotion, and milestone acceptance
   retain their separate approved gates.
8. Do not commit, push, or change installed datasets without owner
   approval. `main` is the only development branch.

## Command-review checklist

Before publishing operator commands, verify shell syntax without
executing MVS steps and inspect the failure path: an unsuccessful
`git pull`, offline check, JCL preparation, JES submission, or
`job-summary` must leave the WSL terminal usable. Do not chain
unrelated work behind an unconditional last command. Use captured
status values and `if` conditions to guard subsequent operations.

For BCPLQSAM Q.1, use the guarded WSL procedures in
[`bootstrap-toolchain/extensions/bcplqsam/README.md`](../bootstrap-toolchain/extensions/bcplqsam/README.md).
