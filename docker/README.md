# MVS 3.8J Docker Environment

This directory contains the Docker configuration for running the MVS 3.8J Turnkey 5 (TK5) environment under Hercules.

The container is intended to be disposable. Persistent emulator state and virtual media are stored outside the container under the repository's `mvs-state/` directory.

## Requirements

The host requires:

- Docker Engine or Docker Desktop
- Docker Compose
- An `amd64`-compatible Docker environment, either native or through emulation
- Internet access when initially building the image

Run the following commands from the repository root.

## Build the Image

Build the image with Docker Compose:

```console
docker compose -f docker/compose.yaml build
```

The build downloads the TK5 distribution and constructs the local MVS/Hercules image.

## Start MVS

The `tools/start-tk5.sh` script starts Hercules and performs the normal TK5/MVS IPL.

To start attached to the Hercules/MVS event stream:

```console
./tools/start-tk5.sh
```

Attached operation is the default. It can also be requested explicitly:

```console
./tools/start-tk5.sh --attached
```

To start the container in the background:

```console
./tools/start-tk5.sh --detached
```

To check its status:

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

JCL can be submitted to the JES card-reader interface on port `3505`.

The Git repository is available read-only inside the container at:

```text
/workspace
```

Persistent MVS state, virtual tapes, printer output, punch output, and logs are maintained under:

```text
mvs-state/
```

## View the Event Log

When started in attached mode, Hercules and MVS events are displayed directly on the terminal.

For a detached container, display the log with:

```console
docker compose -f docker/compose.yaml logs
```

Follow it continuously with:

```console
docker compose -f docker/compose.yaml logs -f
```

## Shut Down MVS

Use the shutdown helper:

```console
./tools/shutdown-tk5.sh
```

The container handles the MVS-specific shutdown sequence and allows TK5/MVS to shut down cleanly before Hercules exits.

Allow up to **three minutes** for an orderly shutdown. Do not forcibly terminate the container during this interval unless recovery from a failed shutdown is necessary.

Files stored under `mvs-state/` remain on the host when the container is stopped or recreated.

