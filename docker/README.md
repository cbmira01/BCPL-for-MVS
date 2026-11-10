# Hercules / TK5 Docker Compose operations

This is the Docker Compose operations guide for the **BCPL for MVS 3.8 Reconstruction** development system. Docker runs TK5/MVS 3.8J under Hercules; the project source, scripts, JCL and documentation remain authoritative in GitHub `main`. Run the examples from the repository root in WSL unless noted otherwise.

## Project identity and interfaces

| Item | Project value |
| --- | --- |
| Compose file | `docker/compose.yaml` |
| Compose project | `Hercules` |
| Service | `mvs` |
| Container | `mvs38j` |
| Local image | `mvs38j-tk5:local` |
| 3270 terminal | TCP 3270 |
| JES socket card reader | TCP 3505 |
| Hercules HTTP interface | TCP 8038 |

The image is built from `docker/Dockerfile`, based on a digest-pinned Ubuntu 24.04 image. The build downloads the publisher's TK5 archive from a URL; that archive is **not** checked into Git or pinned by a content digest, so a future rebuild is not guaranteed to reproduce the identical TK5 bytes.

## Prerequisites and first-time image build

Install Docker Engine or Docker Desktop with Docker Compose v2 accessible from the WSL shell. Check both commands before building:

```sh
docker version
docker compose version
```

From the repository root, build the local image:

```sh
docker compose -f docker/compose.yaml build mvs
```

This builds the image; it does **not** start MVS. It requires access to the Docker daemon and to the external package/archive download sources. Check that the repository's `mvs-state/` bind-mount directories exist before the first start. The tracked `.gitkeep` placeholders establish the required directory structure in a normal checkout.

For ordinary startup, **prefer the project wrapper** rather than a raw Compose `up` command. It exports `MVS_UID` and `MVS_GID` from the invoking WSL user, so files created in bind mounts have the expected host ownership.

## Start, inspect and stop

Start MVS in the background (recommended for normal development):

```sh
tools/mvs/start-tk5 --detached
```

Alternatively, run attached to the Hercules/MVS event stream:

```sh
tools/mvs/start-tk5
```

In attached mode, interrupting `docker compose up` can stop the service; for routine log viewing, prefer the detached mode plus `logs -f`.

Inspect the service or follow the live event stream without stopping MVS:

```sh
docker compose -f docker/compose.yaml ps
docker compose -f docker/compose.yaml logs --tail=100 -f mvs
```

Press **Ctrl+C** to leave the *log-following command*; that does not stop the detached MVS container. The startup script also writes a run-specific Hercules console log under `mvs-state/log/`, with `3033.log` pointing to the current run.

For an orderly guest shutdown, use:

```sh
tools/mvs/shutdown-tk5
```

The helper calls `docker compose stop --timeout 180 mvs`. The container stop handler requests TK5's shutdown script through the Hercules HTTP interface, then allows a grace period before Docker may force termination. **Do not assume a successful Docker stop is proof of clean MVS shutdown:** inspect the console log, particularly if the stop timed out or Hercules was unresponsive. Stop JES submissions and let active jobs complete before shutdown.

After the system has stopped, restart it with `tools/mvs/start-tk5 --detached`. An ordinary stop/start does not require an image rebuild.

## Useful Compose operations

From the repository root:

| Task | Command |
| --- | --- |
| Check service state | `docker compose -f docker/compose.yaml ps` |
| View recent logs | `docker compose -f docker/compose.yaml logs --tail=100 mvs` |
| Follow logs | `docker compose -f docker/compose.yaml logs -f mvs` |
| Validate Compose configuration | `docker compose -f docker/compose.yaml config` |
| Build the image, without starting MVS | `docker compose -f docker/compose.yaml build mvs` |
| Display the image | `docker image inspect mvs38j-tk5:local` |

If you intentionally invoke Compose `up` **without** the project startup wrapper, explicitly pass your host identity:

```sh
MVS_UID="$(id -u)" MVS_GID="$(id -g)" \
    docker compose -f docker/compose.yaml up -d mvs
```

If a container is already running, `up` may leave it running; if the image or configuration has changed, Compose may recreate it. Consider the state precautions below before any operation that might recreate the container.

## Rebuilding or updating the Docker image

The **image build** and the **BCPL clean-room reconstruction** are different operations. Rebuilding the Docker image changes the packaged Hercules/TK5 environment; rebuilding the BCPL environment changes managed MVS datasets and generated host artifacts.

For an image rebuild, first finish JES work and shut MVS down cleanly. Preserve or back up any needed host-mounted state **and any changes retained only in the container writable layer**. Then build the image:

```sh
docker compose -f docker/compose.yaml build mvs
```

The next startup may recreate the existing container to use the updated image. Do **not** treat `up --build`, `down`, `down -v`, container removal, or image pruning as harmless routine maintenance. Removal/recreation loses changes stored only in that container's writable layer, even though the named host bind mounts persist. Confirm that a recreated guest has the expected MVS state before running a reconstruction or regression.

The Docker build downloads a third-party TK5 archive, so rebuilding may also require network availability and review of upstream changes. No clean-room purge, image deletion or MVS dataset overwrite is implied by the build command itself.

## Persistent versus container-local state

The Compose file currently bind-mounts the following project paths:

| WSL checkout path | Container path | Purpose |
| --- | --- | --- |
| `mvs-state/dasd.usr/` | `/tk5/dasd.usr/` | User/development DASD images |
| `mvs-state/tape/` | `/tk5/tape/` | Hercules virtual tape images |
| `mvs-state/prt/` | `/tk5/prt/` | Printer output |
| `mvs-state/pch/` | `/tk5/pch/` | Punch output |
| `mvs-state/log/` | `/tk5/log/` | Console logs and hardcopy |
| Repository root | `/workspace/` | Read-only source checkout |

**Important:** The current Compose file does **not** bind-mount `/tk5/dasd/` (system DASD), `/tk5/conf/`, `/tk5/local_conf/`, or `/tk5/local_scripts/`. Correspondingly named `mvs-state/` folders, if present, are not proof those paths are live mounts. Changes in those locations belong to the container's writable layer unless explicitly preserved by another mechanism; they may be lost when the container is removed or recreated.

Git tracks the project configuration and source definitions; it does **not** version the running MVS disk images or JES output. Back up runtime state separately if it matters. Never remove `mvs-state/` as a substitute for an approved BCPL clean-room rebuild.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `docker` or `docker compose` unavailable | Verify the Docker installation, daemon, and WSL integration |
| Build fails while downloading TK5 or packages | Review `docker compose ... build mvs` output and network/source availability |
| Startup reports missing TK5 configuration or IPL script | Inspect `docker compose -f docker/compose.yaml logs --tail=100 mvs`; verify the built image |
| Port 3270, 3505 or 8038 is already allocated | Check `docker compose -f docker/compose.yaml ps` and other host listeners/containers |
| Permissions errors on bind-mounted files | Use `tools/mvs/start-tk5` so UID/GID are supplied; inspect host ownership, do not recursively chmod data blindly |
| MVS does not become ready or shutdown hangs | Inspect the Hercules console log in `mvs-state/log/` and recent Compose logs |
| State appears missing after image/container recreation | Check what was in host bind mounts versus the non-mounted container writable layer |

If a JES job is incomplete or a shutdown is uncertain, preserve existing console/JES evidence before attempting another submission. Do not resolve ambiguous guest state by blindly deleting the container or datasets.

## BCPL dataset lifecycle and further references

MVS-side `HERC02.BCPL.*` libraries are managed by `tools/datasets/dspal` from Git-controlled definitions. For example:

```sh
tools/datasets/dspal info
tools/datasets/dspal ls
```

Dataset initialization, population, purging and clean-room reconstruction are **separate, explicit operations** with their own approval rules. See [configuration](../config/README.md), [project packaging](../packaging/README.md), [MVS tools](../tools/mvs/README.md), and the [reconstruction guide](../docs/Rebuild-BCPL-for-MVS-from-source.md).

The bundled TK5 and Hercules components have separate third-party licenses and notices; see [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md).
