# MVS 3.8J Docker Environment

This directory contains the Docker configuration for running the MVS 3.8J Turnkey 5 (TK5) environment under Hercules for the BCPL-for-MVS reconstruction.

The container is intended to be disposable. Persistent emulator state and virtual media are stored outside the container under the repository's `mvs-state/` directory. The repository itself is mounted read-only into the running container so host-side tools and MVS-resident state remain clearly separated.

## Requirements

The host requires:

- Docker Engine or Docker Desktop
- Docker Compose
- an `amd64`-compatible Docker environment, either native or through emulation
- Internet access when initially building the image

Run the following commands from the repository root.

## Build the image

```console
docker compose -f docker/compose.yaml build
```

The build downloads the TK5 distribution and constructs the local MVS/Hercules image.

## Start MVS

The [`tools/start-tk5`](../tools/start-tk5) helper starts Hercules and performs the normal TK5/MVS IPL.

Attached operation is the default:

```console
tools/start-tk5
```

It can also be requested explicitly:

```console
tools/start-tk5 --attached
```

To start the container in the background:

```console
tools/start-tk5 --detached
```

Check status with:

```console
docker compose -f docker/compose.yaml ps
```

## Interacting with MVS

The container publishes these services:

| Port | Purpose |
|---:|---|
| 3270 | 3270 terminal access |
| 3505 | JES card-reader interface |
| 8038 | Hercules web interface |

Connect a TN3270 client to port `3270` for interactive MVS access.

Project tools such as [`tools/submit-jcl`](../tools/submit-jcl),
[`tools/run-intcode`](../tools/run-intcode), and
[`tools/compile-and-run`](../tools/compile-and-run) submit work through the
socket reader on port `3505` and recover results from the configured printer
output.

The Git repository is available read-only inside the container at:

```text
/workspace
```

Persistent MVS state, virtual DASD/tape media, printer output, punch output,
and logs are maintained under:

```text
mvs-state/
```

This separation is intentional: source and host tooling remain ordinary Git
content, while emulated MVS state survives container replacement independently.

## View the event log

When started in attached mode, Hercules and MVS events are displayed directly
on the terminal.

For a detached container:

```console
docker compose -f docker/compose.yaml logs
```

Follow continuously with:

```console
docker compose -f docker/compose.yaml logs -f
```

## Shut down MVS

Use the orderly shutdown helper:

```console
tools/shutdown-tk5
```

The helper performs the MVS-specific shutdown sequence and allows TK5/MVS to
stop cleanly before Hercules exits. Allow up to three minutes for an orderly
shutdown. Do not forcibly terminate the container during this interval unless
recovering from a failed shutdown.

Files stored under `mvs-state/` remain on the host when the container is
stopped or recreated.

## Role in the reconstruction

The container is the project's repeatable development machine, not the final
BCPL packaging format. It currently hosts the reconstructed ICINT interpreter,
the preserved interpreted compiler pipeline, and all MVS-side experiments.
Upcoming work will increasingly exercise DASD-resident data sets, native
System/370 code generation, and eventually installation-oriented workflows.

See [`tools/README.md`](../tools/README.md) for normal host-side operation and
[`docs/Hercules-briefing.md`](../docs/Hercules-briefing.md) for a broader
orientation to Hercules itself.
