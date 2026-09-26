# Hercules Emulator: Programmer's Orientation Briefing

## Purpose and Scope

This briefing introduces **Hercules** from the standpoint of a general-purpose or systems programmer working with an IBM mainframe operating system such as **MVS 3.8J**. It is intended to establish the concepts needed to obtain, build, configure, operate, observe, automate, troubleshoot, and shut down a Hercules system.

It is deliberately **not** a complete Hercules operator's manual, device reference, networking guide, or emulator-development guide. The central question is: **what does a programmer need to understand about the machine underneath MVS?**

---

## 1. What Hercules Is

Hercules is an open-source emulator of IBM mainframe computer architectures. The actively maintained SDL Hercules 4.x Hyperion project supports System/370, ESA/390, and z/Architecture.

For an MVS 3.8 environment, the useful mental model is:

```text
+----------------------------------+
| Application / systems program    |
+----------------------------------+
| MVS 3.8J                         |
+----------------------------------+
| Emulated System/370 hardware     |
|          Hercules                |
+----------------------------------+
| Host operating system            |
| Linux / Windows / macOS / etc.   |
+----------------------------------+
| Physical computer                |
+----------------------------------+
```

Hercules implements the **machine** on which MVS runs. MVS is not part of Hercules.

Hercules therefore provides such things as:

- emulated processors and registers;
- main storage;
- System/370 instructions;
- interrupts and machine facilities;
- I/O channels and device addressing;
- emulated DASD, tape, card, printer, terminal, and communications devices.

The guest operating system sees these as hardware. Hercules maps that virtual hardware onto facilities of the host computer.

For example:

```text
MVS view                    Hercules/host representation
-------------------------   --------------------------------
3330/3350/3380 DASD   -->   host disk-image file
3420 tape              -->   tape-image file
3505 card reader       -->   file or socket
1403 printer           -->   host output file
3270 terminal          -->   network terminal connection
CPU                    -->   Hercules CPU emulation
main storage           -->   host virtual memory
```

This boundary is fundamental to understanding a Hercules system.

### What Hercules is not

Hercules is not:

- MVS;
- JES2;
- a mainframe application environment by itself;
- an assembler or compiler;
- a replacement for JCL;
- a collection of IBM operating-system utilities.

Those facilities exist **inside the guest operating system**.

---

## 2. Obtaining Hercules

The principal modern implementation is **SDL Hercules 4.x Hyperion**.

The source repository is maintained by the SDL-Hercules-390 project on GitHub:

```text
SDL-Hercules-390/hyperion
```

The repository contains the emulator source, build infrastructure, utilities, documentation, tests, and support modules.

A programmer should distinguish between:

- a released Hercules version;
- the current source tree;
- locally built binaries;
- older Hercules distributions or forks.

For a reproducible development environment, record the exact Hercules version or source revision being used.

Hercules is licensed separately from any operating system run under it. Possession of Hercules does not itself grant rights to IBM operating-system software.

---

## 3. Building Hercules

Hercules is principally written in C and can be built on common host systems. Current Hyperion documentation uses **CMake** for its modern build process.

Conceptually, building Hercules consists of:

```text
source
   |
   v
CMake configuration
   |
   v
host compiler/toolchain
   |
   v
Hercules executable + supporting modules/utilities
```

A typical source build therefore involves:

1. obtaining the source tree;
2. installing the required host compiler and libraries;
3. configuring the build;
4. compiling;
5. optionally running the supplied tests;
6. installing or packaging the resulting binaries.

The exact commands depend on the host platform and Hercules release and should be taken from the build documentation accompanying that version.

### Why a programmer should care about the build

Most MVS programming does not require knowledge of Hercules internals. It is nevertheless useful to know:

- which Hercules version is running;
- how that executable was obtained;
- which optional facilities were built;
- where its supporting modules reside;
- how to reproduce the build.

This becomes important when diagnosing behavior that may depend on the emulator rather than MVS.

---

## 4. The Hercules Configuration

A Hercules configuration file describes the emulated computer.

Conceptually it performs the role that physical machine configuration would once have performed:

```text
Hercules configuration
        |
        +--> architecture
        +--> CPUs
        +--> memory
        +--> consoles
        +--> channels/devices
        +--> DASD images
        +--> tape units
        +--> card equipment
        +--> printers
        +--> communications devices
```

A simplified configuration might conceptually say:

```text
ARCHMODE S/370
MAINSIZE ...

000C 3505 ...
000D 3525 ...
000E 1403 ...
0148 3270
0150 3330 ...
0480 3420 ...
```

The exact syntax and options vary by device and Hercules version.

### Device addresses matter

Mainframe software identifies I/O devices by their **device addresses**. Thus the address in the Hercules configuration is part of the interface between Hercules and MVS.

If MVS expects a card reader at one address while Hercules provides it at another, the two configurations disagree.

For an established environment such as TK5, the existing configuration normally provides the expected correspondence.

### Configuration versus guest configuration

There are often two relevant definitions:

```text
Hercules                         MVS
--------                         ---
"Device 0480 is a 3420"  <-->   "Device 0480 is known to MVS"
```

Hercules defines what virtual hardware exists. MVS must also know how to use that hardware.

---

## 5. Starting Hercules and IPLing MVS

Starting Hercules and starting MVS are distinct operations.

When the Hercules process starts, it constructs the configured virtual machine. At that point the emulated CPU and devices exist, but MVS is not necessarily running.

MVS is started by performing an **IPL — Initial Program Load** — from an appropriate emulated device.

The conceptual sequence is:

```text
start Hercules
      |
      v
read Hercules configuration
      |
      v
construct virtual machine
      |
      v
IPL from boot DASD
      |
      v
MVS initialization
      |
      v
JES initialization
      |
      v
operational system
```

This distinction is useful during troubleshooting. A failure before IPL is likely to concern Hercules or its configuration. A failure during or after IPL may concern the guest operating system, although underlying emulation or configuration problems remain possible.

---

## 6. The Hercules Operator Interface

Hercules has its own command interface. These commands control the **emulator**, not MVS.

Typical categories of Hercules commands include:

- displaying emulator status;
- examining CPUs;
- starting or stopping processors;
- examining storage and registers;
- querying devices;
- attaching or detaching virtual media;
- changing device definitions;
- controlling tracing;
- performing an IPL;
- terminating Hercules.

For example, `devinit` is an important Hercules concept: it can associate an emulated device with a new host resource, such as mounting another virtual tape image.

The exact syntax should be checked against the command reference for the Hercules version in use.

### Hercules commands versus MVS commands

These are different command domains.

```text
Command intended for Hercules
          |
          v
Hercules emulator

Command intended for MVS
          |
          v
MVS operator console
```

An MVS `DISPLAY` command does not mean the same thing as a Hercules display command. Likewise, a Hercules command that manipulates device 0480 operates below MVS.

Always ask:

> **Who is supposed to consume this command: Hercules or the guest operating system?**

---

## 7. Reading the Event and Message Stream

A Hercules session can produce messages from several conceptual layers:

```text
Hercules itself
     |
     +--> configuration messages
     +--> device messages
     +--> CPU/emulation messages
     +--> network messages
     +--> diagnostics

MVS
     |
     +--> system messages
     +--> operator messages
     +--> allocation messages

JES2
     |
     +--> job messages
     +--> reader/printer activity

Programs
     |
     +--> WTO messages
     +--> program output
```

These streams can appear close together in an interactive environment, which makes their origin easy to confuse.

For a programmer, the first diagnostic question should often be:

> **Which layer emitted this message?**

### Example

Suppose a batch program cannot read an input data set.

Possible sources include:

- the application program;
- an MVS access method;
- allocation/catalog processing;
- MVS device management;
- Hercules device emulation;
- the host file representing the emulated medium.

Recognizing the message source greatly reduces the search space.

### Logs

For repeatable development and CI work, retain useful Hercules console/log output. It can provide evidence that:

- the emulator initialized correctly;
- devices attached successfully;
- MVS IPLed;
- jobs entered through the reader;
- devices encountered errors;
- shutdown completed.

---

## 8. Emulated Devices

Hercules supports a broad range of IBM mainframe device classes. A programmer does not need to memorize the catalog of supported models. The important point is how the major classes map into a development environment.

### DASD

Direct-access storage devices are represented by host files containing virtual disk volumes.

To MVS they behave like mainframe disks. MVS places VTOCs, data sets, libraries, catalogs, and other structures on them.

The host normally sees only the **disk image**, not the individual MVS data sets as ordinary host files.

### Magnetic tape

Tape drives can be backed by virtual tape images.

MVS still sees sequential tape behavior:

- tape marks;
- files;
- labels;
- rewind operations;
- volume mounting.

Hercules maps those operations onto a host representation.

### Card reader

A virtual card reader provides a particularly useful bridge into a historical batch environment.

```text
host JCL file
     |
     v
Hercules virtual reader
     |
     v
JES2 input processing
     |
     v
MVS job
```

A reader may be backed by a file or, in suitable configurations, a socket. Socket-backed readers are especially useful for automated job submission.

### Card punch

A virtual punch maps punched-card output onto a host file or comparable host resource.

### Line printer

A virtual line printer commonly writes its output to a host file. This makes historical SYSOUT and JES output easy to capture with modern tools.

### 3270 terminals

Hercules can provide terminal connectivity suitable for 3270-family operation. A TN3270-capable terminal emulator is normally used from the host or another computer.

### Communications devices

Hercules provides several mechanisms for emulating mainframe communications adapters and networking, including channel-to-channel and virtual network interfaces.

The details can become extensive. For an MVS programmer, the important distinction is:

```text
MVS networking stack
        |
        v
emulated communications adapter
        |
      Hercules
        |
        v
host networking facilities
```

---

## 9. Virtual Media and Persistent State

The distinction between **emulator state** and **guest state** is important.

A Hercules installation may use host files representing:

- DASD volumes;
- tape volumes;
- card decks;
- punched output;
- printer output;
- logs;
- configuration data.

Some of these are inputs, some are outputs, and some contain the persistent state of the guest operating system.

### DASD images deserve special care

An MVS DASD image may contain the entire persistent filesystem-like state of a guest volume. Deleting or replacing the image can therefore be equivalent to removing a physical disk pack.

Do not confuse a disposable Hercules executable or container with disposable **guest storage**.

### Virtual media operations

A useful working vocabulary includes:

- attach;
- detach;
- mount;
- unmount;
- initialize;
- rewind;
- read-only versus writable media;
- virtual volume;
- device address.

The emulator performs the hardware-level side of these operations. MVS retains responsibility for the operating-system interpretation of the medium.

---

## 10. Networking and Exposed Services

Hercules can expose several kinds of host interfaces. Which ones exist depends entirely on the configuration.

Examples can include:

- terminal listeners;
- socket-based virtual card readers;
- inter-emulator channel connections;
- virtual network adapters;
- interfaces used for automation or remote operation.

Hercules supports multiple networking models, including CTCA-based mechanisms and LCS/OSA-style virtual adapters. On Unix-like hosts, some modes use TUN/TAP networking and may require additional host privileges or network configuration.

### Do not confuse host and guest networking

There are potentially two different networking worlds:

```text
Host network
    |
 Hercules
    |
virtual communications hardware
    |
 MVS networking software
    |
Guest network identity
```

A TCP listener provided directly by Hercules is not necessarily a TCP service provided by MVS.

### Security

Treat Hercules listeners as real network services. Bind them deliberately, publish only required ports, and use host firewalling where appropriate.

This is particularly important when an environment originally intended for localhost development is placed in a container or on a network server.

---

## 11. Useful External Tools

Hercules becomes substantially easier to use when combined with ordinary host tools.

### 3270 terminal emulator

Useful for interactive guest sessions and MVS consoles configured through 3270-compatible connections.

### `telnet`, `nc`, and similar socket tools

These can be useful for testing simple Hercules TCP listeners or submitting data to socket-backed devices where the protocol permits it.

For example, a socket-backed virtual card reader can make this pattern possible:

```text
JCL deck --> nc --> Hercules reader --> JES2
```

### Shell and Python

Host scripting is extremely useful for:

- generating JCL;
- submitting jobs;
- waiting for expected messages;
- collecting printer output;
- extracting return codes;
- mounting media;
- starting and stopping environments;
- implementing regression tests.

### Hercules utilities

The Hercules distribution includes utilities associated with virtual media and emulator maintenance. These are useful for manipulating DASD and tape representations without treating the files as opaque blobs.

Use the utility appropriate to the Hercules version and media format in use.

### Host diagnostic tools

Ordinary tools remain valuable:

- process monitors;
- filesystem utilities;
- `ss`/`netstat`-style network inspection;
- `tcpdump` or Wireshark;
- `grep`, `sed`, and `awk`;
- Python;
- Docker inspection and logging tools when containerized.

These observe the **host side** of the environment.

---

## 12. Automation and Development Workflows

Hercules is particularly useful for historical software development because a complete mainframe workflow can be automated from a modern host.

A useful pattern is:

```text
                  modern development host
                           |
             +-------------+-------------+
             |                           |
        assembler source                 |
             |                           |
        generate JCL                     |
             |                           |
             +--> submit to reader ------+
                           |
                        Hercules
                           |
                          MVS
                           |
                         JES2
                           |
                assembler/linker/program
                           |
                      SYSOUT/printer
                           |
                        Hercules
                           |
                     host output file
                           |
                    analysis/script
```

This turns a 1970s batch environment into something that can participate in a modern source-controlled development workflow.

### Automation boundaries

It is useful to identify exactly which layer performs each action:

| Action | Principal layer |
|---|---|
| Start emulator | Host/Hercules |
| IPL MVS | Hercules + MVS |
| Submit JCL | Hercules reader/JES2 |
| Assemble program | MVS assembler |
| Link-edit program | MVS linkage editor |
| Run program | MVS |
| Produce SYSOUT | Program/MVS/JES2 |
| Materialize printer file | Hercules/host |
| Parse results | Host tooling |

This model prevents automation scripts from becoming a collection of unexplained delays and assumptions.

### Prefer observable state

Where practical, automation should wait for a recognizable event rather than merely sleeping for a fixed period.

Examples include observing:

- expected initialization messages;
- job submission acknowledgement;
- job termination messages;
- expected printer output;
- emulator termination.

---

## 13. Diagnostics and Debugging

Hercules is more than a machine runner. It can also provide visibility into the emulated hardware.

Diagnostic facilities include, depending on version and configuration:

- CPU and register inspection;
- storage inspection;
- instruction tracing;
- device tracing;
- trace-to-file facilities;
- CPU/device status displays;
- diagnostic messages.

These capabilities can be invaluable in systems programming because Hercules can expose machine-level behavior that would have been considerably less convenient to inspect on physical hardware.

### Diagnose by layer

A useful fault model is:

```text
Application problem?
       |
Assembler/linkage problem?
       |
MVS service or configuration problem?
       |
MVS device problem?
       |
Hercules device/configuration problem?
       |
Host resource problem?
```

For example, if MVS reports an I/O error, do not immediately assume that the application is at fault. Inspect both the MVS messages and the corresponding Hercules device messages.

### Disabled waits and severe guest failures

A stopped or waiting MVS system may still leave Hercules perfectly operational. Hercules can then provide information about CPU state, registers, storage, and devices.

This illustrates the advantage of the emulator boundary: the machine monitor can remain available even when the operating system inside that machine is no longer functioning normally.

### Avoid unnecessary tracing

Instruction and device tracing can produce enormous amounts of output. Enable detailed tracing to answer a specific diagnostic question rather than as a routine operating mode.

---

## 14. Performance and Timing

Hercules reproduces architectural behavior; it does not attempt to make a modern host run at exactly the speed of a particular historical processor unless explicitly configured or controlled for such a purpose.

Therefore:

> **Emulated elapsed time is not a reliable measure of historical machine performance.**

A System/370 program that executes very quickly under Hercules has not thereby demonstrated that it would have run equally quickly on a 1970s processor.

Factors affecting emulator performance include:

- host CPU speed;
- host scheduling;
- Hercules configuration;
- number of emulated CPUs;
- storage configuration;
- host filesystem performance;
- virtual-device implementation;
- container or VM overhead.

For compiler, assembler, and systems-programming work, correctness and repeatability are normally more important than historical timing fidelity.

---

## 15. Orderly Shutdown and Recovery

Stopping Hercules is not necessarily the same thing as shutting down MVS.

The preferred sequence is conceptually:

```text
stop application activity
        |
        v
stop/quiesce JES and system services as required
        |
        v
perform orderly MVS shutdown
        |
        v
confirm guest has reached a safe stopped state
        |
        v
terminate Hercules
```

The exact MVS shutdown procedure depends on the distribution and system configuration.

### Why this matters

Hercules may have writable DASD images open while MVS is running. Abruptly killing the emulator is analogous to removing power from a physical machine rather than performing an operating-system shutdown.

MVS and its data sets were designed with recovery mechanisms, but those mechanisms are not a substitute for orderly shutdown.

### Forced termination

Forced termination remains useful when:

- Hercules itself has failed;
- the guest is irrecoverably hung;
- an experiment deliberately tests abnormal failure;
- orderly shutdown cannot complete.

Treat it as an abnormal event and verify the system after restart.

---

## 16. Containerizing Hercules

Hercules is well suited to containerization because there is a clean conceptual separation between the emulator executable and the files representing the virtual machine.

A minimal container model is:

```text
Container image
+--------------------------------+
| Hercules executable            |
| runtime libraries              |
| startup scripts                |
+--------------------------------+

External/persistent storage
+--------------------------------+
| Hercules configuration         |
| DASD images                    |
| tape images                    |
| reader/JCL files               |
| printer/punch output           |
| logs                           |
+--------------------------------+
```

The container can therefore be disposable while the emulated system remains persistent.

### Container concerns

A practical container definition needs to consider:

- Hercules executable and dependencies;
- configuration files;
- persistent storage mounts;
- exposed terminal/reader/network ports;
- UID/GID ownership of mounted files;
- host networking requirements;
- any required capabilities;
- startup behavior;
- signal handling;
- orderly guest shutdown before container termination.

Docker Compose is convenient for describing these relationships reproducibly.

### Do not over-containerize the mental model

Docker does not replace Hercules architecture or MVS administration.

```text
Docker
   |
   +--> manages the host process environment

Hercules
   |
   +--> emulates the mainframe

MVS
   |
   +--> manages the guest operating environment
```

Keeping these layers separate makes troubleshooting much easier.

---

## 17. The Hercules/MVS Boundary

This is the most important conceptual distinction in the briefing.

When something happens, determine which side of the boundary owns it.

### Example: a disk

```text
HOST

/tk5/dasd/xxxx.dasd
        |
        | host file
        v
+--------------------+
| Hercules           |
| emulated DASD      |
| device 0150        |
+--------------------+
        |
        | channel I/O
        v
+--------------------+
| MVS                |
| volume             |
| VTOC               |
| data sets          |
+--------------------+
        |
        v
      program
```

The host knows about the image file. Hercules knows about the emulated device. MVS knows about volumes and data sets. The application normally knows about data sets, DD names, and records.

### Example: a batch job

```text
host JCL file
      |
Hercules card reader
      |
JES2 reader processing
      |
MVS initiator
      |
program execution
      |
JES2 SYSOUT
      |
Hercules printer
      |
host printer file
```

Each transition crosses an interface. Knowing those interfaces is extremely useful when building automation.

### Four questions to ask

When diagnosing any Hercules/MVS problem, ask:

1. **Which layer generated the message or symptom?**
2. **Which layer owns the resource involved?**
3. **Which interface connects that layer to the next one?**
4. **What evidence can be collected at each side of that interface?**

These questions are often more useful than immediately searching for a particular error message.

---

## 18. A Programmer's Working Model

For ordinary development, the following compact model is sufficient.

### Hercules provides the computer

It provides:

- processors;
- storage;
- channels;
- devices;
- virtual media;
- machine-level controls and diagnostics.

### MVS provides the operating environment

It provides:

- address spaces and tasks;
- program loading and execution;
- data-set management;
- access methods;
- system services;
- device management;
- recovery and ABEND processing;
- operator facilities.

### JES2 provides the batch environment

It provides the principal path through which jobs enter, execute, and produce spool output.

### The host provides the modern development environment

It provides:

- source control;
- editors;
- scripts;
- containers;
- network tools;
- file processing;
- automated testing;
- CI/CD infrastructure.

The resulting development system spans all four layers:

```text
+------------------------------------------------+
| Modern host                                    |
| Git, editor, Python, shell, Docker, CI          |
+------------------------+-----------------------+
                         |
+------------------------v-----------------------+
| Hercules                                       |
| System/370 CPU, storage, channels, devices     |
+------------------------+-----------------------+
                         |
+------------------------v-----------------------+
| MVS 3.8J                                       |
| execution, storage, data sets, system services |
+------------------------+-----------------------+
                         |
+------------------------v-----------------------+
| JES2 / language toolchain / application        |
| JCL -> assemble -> link-edit -> execute         |
+------------------------------------------------+
```

---

## 19. What a Programmer Should Know First

A programmer beginning work with Hercules does **not** need to master the emulator before writing programs for MVS.

The practical minimum is to understand:

1. Hercules emulates the hardware; MVS is the guest operating system.
2. The Hercules configuration defines the virtual machine and its devices.
3. Device addresses connect the Hercules hardware configuration to the MVS hardware configuration.
4. Starting Hercules and IPLing MVS are separate events.
5. Hercules commands and MVS operator commands belong to different command environments.
6. Hercules messages, MVS messages, JES messages, and program output have different sources.
7. DASD and tape images are virtual media and may contain important persistent state.
8. Readers and printers provide useful bridges between modern host files and historical batch processing.
9. Hercules diagnostics can expose CPU, storage, and device behavior when systems-level debugging requires it.
10. MVS should normally be shut down cleanly before Hercules is terminated.
11. Containerization packages the host execution environment; it does not change the Hercules/MVS boundary.
12. When debugging, identify the failing **layer and interface** before changing things.

With these concepts established, the remaining Hercules material can be learned as needed from the configuration, command, device, networking, and utility references.

---

## References

Primary references for further study:

- **SDL Hercules 4.x Hyperion source repository** — `SDL-Hercules-390/hyperion` on GitHub.
- **SDL Hercules documentation** — configuration, commands, operation, networking, and build documentation maintained by the project.
- **IBM System/370 Principles of Operation** — architectural reference for the machine Hercules emulates when operating in System/370 mode.
- **MVS documentation** — reference for the operating-system behavior above the emulated hardware boundary.

For day-to-day MVS development, the Hercules **configuration file**, **command reference**, and documentation for the particular emulated devices in use are usually more valuable than the emulator's implementation source.

---

## Closing Perspective

Hercules is best understood not as an application that "runs MVS," but as a **software implementation of the computer on which MVS runs**.

That distinction explains most of the environment:

```text
Host files and sockets
        ^
        |
     Hercules
        ^
        |
 emulated hardware
        ^
        |
       MVS
        ^
        |
 JES / system services
        ^
        |
     programs
```

For general-purpose programming, Hercules can remain largely invisible once the system is operational. For systems programming, toolchain development, automation, and diagnosis, the emulator boundary becomes an exceptionally useful observation and control point.
