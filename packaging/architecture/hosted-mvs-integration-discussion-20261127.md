# Hosted MVS Integration — Discussion and Deferred Direction

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 27 November 2026 EST  
**Status:** Deferred by owner direction; no implementation authorized.

## Findings

| Subject | Finding |
|---|---|
| Execution environment | GitHub-hosted Linux runners can run Docker and should accommodate Hercules/TK5. |
| Computing resources | Standard public-repository runners appear adequate in CPU, memory and execution time. Local disk capacity requires measurement. |
| Docker images | Prebuilt images can be preserved in GitHub Container Registry. |
| TK5 distribution | Download once, retain the checksum-verified archive and avoid repeated requests to Prince Webdesign. |
| Persistent MVS state | Requires explicit restoration and preservation of DASD images and other mutable data. |
| Network isolation | Hercules console, 3270 and JES submission ports should remain private by default. |
| Repository integration | Actions workflows, execution history, artifacts and permissions are repository-scoped. |
| Assistant integration | Existing GitHub connector supports repository access, workflow inspection, logs and artifact retrieval. Direct workflow dispatch remains unresolved. |
| Release production | Potentially supports reconstruction, regression, tape production, recipient verification and packaging. |
| Owner control | Console monitoring, status inspection and orderly shutdown must be supported. |

## Requirements for future consideration

- Respect TK5 distribution terms and minimize publisher download traffic.
- Preserve a checksum-verified TK5 archive in durable private storage.
- Separate immutable Docker images from mutable MVS state.
- Protect the last known-good DASD snapshot against interrupted execution.
- Prevent concurrent modification of shared MVS state.
- Provide orderly IPL and shutdown procedures.
- Distinguish graceful shutdown from emergency workflow cancellation.
- Provide owner monitoring and operational control.
- Protect credentials, authenticated decks, private JES reports and system state.
- Retain separate owner approval for release publication.
- Prefer existing project tools over additional infrastructure.

## Unresolved questions

- Actual Docker image and MVS storage requirements.
- Durable private storage mechanism and costs.
- Connector permissions and on-demand workflow invocation.
- Secure interactive console and terminal access.
- Behavior during runner cancellation and infrastructure failures.
- Actual Hercules/TK5 performance and lifecycle verification.
- Current GitHub resource limits, policies and retention provisions when implementation resumes.

## Owner disposition

Defer GitHub Actions-based hosted MVS integration. Continue using the established WSL/Docker/Hercules/TK5 environment.

Preserve existing offline Actions capabilities. No new milestone, infrastructure, workflow, live experiment or verification campaign is authorized.

Reconsider hosted integration when its practical benefits justify the additional complexity.
