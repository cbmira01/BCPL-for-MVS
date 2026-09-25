
# MVS 3.8J Docker Environment

This directory contains the Docker configuration for running the MVS 3.8J Turnkey 5 (TK5) environment under Hercules.

The container is intended to be disposable. Persistent emulator state and virtual media are stored outside the container under the repository's `mvs-state/` directory.

## Requirements

The host requires:

- Docker Engine or Docker Desktop
- Docker Compose
- An `amd64`-compatible Docker environment, either native or through emulation
- Internet access when initially building the image

Run the following commands from the repository root unless otherwise noted.

## Build the Image

Build the image using:

```console
docker compose -f docker/compose.yaml build
```

The build downloads the TK5 distribution and constructs the local MVS/Hercules image.

## Create and Start the Container

Start MVS with:

```console
docker compose -f docker/compose.yaml up -d
```

Docker creates the container if necessary and starts Hercules and MVS.

To see the container status:

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

Connect a TN3270 client to port `3270` to use an interactive MVS terminal.

JCL can be submitted to the card-reader service on port `3505`.

The repository is mounted read-only inside the container as:

```text
/workspace
```

Persistent MVS files, virtual tapes, printer output, punch output, and logs are maintained under:

```text
mvs-state/
```

## View Hercules Output

View the container output with:

```console
docker compose -f docker/compose.yaml logs
```

Follow it continuously with:

```console
docker compose -f docker/compose.yaml logs -f
```

## Stop MVS

Perform a normal Compose shutdown with:

```console
docker compose -f docker/compose.yaml down
```

The container may be recreated later. Files stored in the repository's `mvs-state/` directories remain on the host.

MVS should normally be shut down cleanly before the container is forcibly stopped, particularly when writable DASD devices are active.

