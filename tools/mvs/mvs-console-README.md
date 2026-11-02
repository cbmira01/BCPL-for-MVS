# mvs-console — Hercules / MVS 3.8J operator console

`tools/mvs/mvs-console` is a **host-side Python 3 tool** for the project's `mvs38j` Docker/TK5 instance. It offers one-shot commands, an interactive REPL, and curated, locally documented command discovery. It does **not** install code into MVS, submit JES jobs by itself, or replace a 3270 terminal.

## Quick start

From the repository root:

```sh
tools/mvs/mvs-console --help
tools/mvs/mvs-console commands
tools/mvs/mvs-console devices
tools/mvs/mvs-console '?'
tools/mvs/mvs-console help tape
tools/mvs/mvs-console jes2 printers
tools/mvs/mvs-console mvs 'D A,L'
tools/mvs/mvs-console hercules devices
tools/mvs/mvs-console hercules devices dasd
tools/mvs/mvs-console 'hercules' 'devices' '?'
tools/mvs/mvs-console
```

No arguments starts a REPL with `mvs>`. `?` works like `help`, including `? tape`, `tape ?`, `mvs ?`, `jes2 ?`, `hercules ?`, and `devices ?`. These commands show help locally without contacting the emulator. `devices` prints an offline, static, grouped IBM device-model directory; use `hercules devices` for the actual configured devices.

 Type `help`, `commands`, `help tape`, `explain jes2 printers`, or `quit`. `history` lists commands typed during the current session (in memory only). Quote commands with spaces if needed.

Native commands are accepted as well as friendly aliases:

```sh
tools/mvs/mvs-console jes2 '$D U,PRTS'
tools/mvs/mvs-console mvs 'D U,DASD'
tools/mvs/mvs-console hercules 'help devinit'
```

A `mvs` command is prefixed with `/` when passed to the Hercules panel; a `jes2` command is passed as `/$...`; a `hercules` command is passed unchanged. The dispatch uses Docker `exec` to reach the running container's HTTP command endpoint, and captures the **new tail** of `mvs-state/log/3033.log`. This log may include asynchronous messages unrelated to the command, or duplicate echoes; a successful HTTP response is **not** evidence of MVS command completion. If the command returns before later messages arrive, re-run a display command or inspect the console log. The tool never automatically retries command transmission.

Use `--dry-run` to see the exact underlying console command without connecting; `--settle SECONDS` controls the post-request observation interval, and `--timeout SECONDS` controls HTTP transport timeout.

## Hercules device inquiries and help

`hercules devices` translates the friendly alias to native Hercules `devlist`.
Use `hercules devices dasd`, `tape`, `printer`, `card`, `terminal`,
or `communications` to filter the one `devlist` response **locally** by
device model. Common plurals are accepted. These are always inquiries: they
must not prompt for confirmation. `hercules devices help` and
`hercules devices ?` display usage **without sending any console command**.
Unknown device categories are rejected locally, rather than sent as invalid
Hercules commands. All namespace commands ending in `?` or `help` are
handled locally; in particular `mvs devices ?` explains available MVS
unit-display aliases rather than sending an invalid `/devices ?` command. `? hercules devices` is another local-help form.

`hercules 'help devlist'` forwards a real Hercules help command. The short
IBM model directory provided by `devices` is separate from live inventory.

To address observed repeated panel output, the collector suppresses **only
adjacent, byte-for-byte identical complete Hercules command-response blocks**.
Different replies and all MVS/JES messages remain intact. A successful HTTP
request does not prove that a guest command completed.

## IBM device models

Use `devices` for a short, grouped reference dump of IBM model numbers (terminals, printers, card equipment, DASD, tape, controllers). No search or console traffic is involved. The list includes later IBM devices for context; it is not a statement of support in MVS 3.8J. Model numbers are not channel addresses.

For live hardware attached to Hercules, use `hercules devices`; for tape drives use `tape list`.

References for descriptions: IBM *OS/VS System Generation* (GC28-6554); IBM I/O device/control-unit listings; IBM tape recording format documentation.

## Tape operations

```sh
tools/mvs/mvs-console help tape
tools/mvs/mvs-console tape list
tools/mvs/mvs-console tape files
tools/mvs/mvs-console tape status 580
tools/mvs/mvs-console --dry-run tape mount 580 example.aws
tools/mvs/mvs-console tape mount 580 example.aws
tools/mvs/mvs-console tape unmount 580
```

`tape list` queries Hercules `devlist` and displays **only recognized tape drives**, once per device address. `tape status ADDRESS` filters the same full inventory locally rather than relying on an unverified `devlist ADDRESS` form. Supported tape device types are 3410, 3420, 3422, 3430, 3480, 3490, 3590, 8809 and 9347. Before **each mount or unmount**, a fresh `devlist` check must identify a non-busy tape drive; otherwise the operation is refused. This check cannot independently prove that MVS has released the device. `tape files` lists regular files under the host's `mvs-state/tape/` directory. Mount accepts only a single ordinary filename in that directory and maps it to `/tk5/tape/FILENAME` inside the container. It does not create or overwrite an image; for new/blank tape creation use a separate, explicitly reviewed workflow. Unmount maps to `devinit ADDRESS *` (Hercules virtual tape only); it does not run an MVS unload or free an allocation.

**Warning:** `devinit` reinitializes a device and can displace mounted media or disrupt a guest job. Verify the device is idle, the correct tape is selected, and the MVS/JCL allocation is appropriate. MVS tape drive status is separately available via `mvs tapes` (the exact display form should be verified against the running guest). An MVS tape mount request may require intervention on *both* sides: Hercules media association and MVS operator interaction. Never issue an unreviewed tape mount merely because a guest prompts for a volume.

## Safety model

The **small curated catalog** contains read-only display aliases. Literal commands beyond explicitly recognized displays are conservatively classified as operational, or disruptive for recognized high-impact prefixes. This is a usability precaution, **not** a complete MVS or Hercules command parser. Read the exact command and its target before approving.

- Inquiry commands execute directly.
- Operational commands ask for an exact `YES` at a terminal. `--yes` can opt into noninteractive operational commands.
- Recognized disruptive commands require `--allow-disruptive` **and** an interactive exact `YES`; `--yes` alone does not authorize them.
- `--dry-run` never sends a console command.

Neither this tool nor its text catalog guarantees that an individual guest command is harmless. Commands issued to the real console affect the live MVS/Hercules system, including jobs and tape attachments. `--allow-disruptive` is a local safety override, not an MVS authorization facility.

## Prerequisites and tests

Run from the Git checkout with Python 3 and Docker available. Start the project container with `tools/mvs/start-tk5 --detached` if it is not already running. The console endpoint and log path are fixed to the repository's TK5 configuration (`mvs38j`, port 8038 inside the container, `mvs-state/log/3033.log`).

Offline unit tests require no Docker or MVS:

```sh
python3 -m unittest discover -s tools/mvs -p 'test_mvs_console.py' -v
python3 -m py_compile tools/mvs/mvs-console
```

Complete, identical Hercules `devlist` response blocks are collapsed, and tape listings also remove duplicate device addresses. Identical MVS/JES messages are left intact, since they may represent distinct asynchronous events. HTTP 200 establishes transport acceptance, not completion of an MVS operation.

The native Hercules `help` command gives more complete emulator command details. The friendly catalog is deliberately limited to verified/common examples, rather than inventing complete MVS 3.8J/JES2 coverage. References: the project's actual console transcript and `docker/compose.yaml`, plus Hercules command documentation (including `devlist` and `devinit`).
