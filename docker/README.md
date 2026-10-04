# Hercules / TK5 development environment

The Docker setup provides the reproducible MVS 3.8J environment used by the reconstruction. It builds a local image around TK5, exposes the services used by the host tools, and bind-mounts mutable MVS state under `mvs-state/`.

## Interfaces

The normal service exposes:

- 3270 terminal access on port 3270;
- the JES socket card reader on port 3505;
- the Hercules web interface on port 8038.

Persistent printer, punch, DASD, tape, configuration, and hardcopy paths live under `mvs-state/` and are intentionally excluded from Git except for directory placeholders.

## Start and stop

From the repository root:

```sh
tools/start-tk5 --detached
```

or run attached with:

```sh
tools/start-tk5
```

Use:

```sh
tools/shutdown-tk5
```

for an orderly MVS/Hercules shutdown.

## Project data sets

MVS-side BCPL libraries are no longer expected to accumulate by hand. `tools/dspal` creates and repopulates the manifest-defined `HERC02.BCPL.*` libraries from Git:

```sh
tools/dspal initbcpl
tools/dspal populate all
```

That lifecycle has been tested through purge and full reconstruction. See `config/README.md`, `packaging/README.md`, and `tools/README.md`.

## Third-party material

The Docker build downloads TK5 from its publisher; the TK5 archive and DASD images are not stored in this Git repository. A built image nevertheless contains TK5 and its third-party components. The repository's MIT license does not apply to those components. See `THIRD-PARTY-NOTICES.md`.