# NOTICES

## Historical BCPL sources

This project uses historical BCPL compiler and runtime material from the `bcpltape` transport tape associated with **Martin Richards**, the designer and original implementer of BCPL. The copy used here was curated by **Robert Nordier** and is available in the `oldbcpl` directory of [Martin Richards’ BCPL and Tripos Archive](https://www.cl.cam.ac.uk/~mr10/Archive.html).

**Ken Yap** made an earlier archive of the tape available. Nordier corrected character mapping problems, assigned filenames, and organized the files into directories. We thank Richards, Yap, Nordier, and the other contributors who created and preserved this material.

The historical files remain the work of their respective authors. This project’s MIT License applies only to its original work and does not relicense those files. Retain any notices accompanying the historical sources.

Martin Richards’ [BCPL home page](https://www.cl.cam.ac.uk/~mr10/) describes terms for his *current* BCPL distribution. Those terms should not be assumed to grant redistribution rights for every file on the historical tape.

## Container packaging

Copyright (c) 2026 Calvin Miracle. Licensed under the MIT License.

The container design was informed in part by these projects:

- [tk5-hercules](https://github.com/joergschultzelutter/tk5-hercules) — Joerg Schultze-Lutter
- [tk4-hercules](https://github.com/skunklabz/tk4-hercules) — Ken Godoy / skunklabz

## Hercules emulator

This project uses [Hercules](https://github.com/SDL-Hercules-390/hyperion), a mainframe emulator created by Roger Bowler and developed by its contributors. Hercules is distributed under the [Q Public License, Version 1.0](https://hercules-aethra.github.io/html/herclic.html).

Hercules remains the work of its respective copyright holders. This repository’s license applies only to this project’s original code and does not replace the license governing Hercules.

## MVS Turnkey 5 (TK5)

This project uses [MVS Turnkey 5 (TK5)](https://www.prince-webdesign.nl/tk5), published by Prince Webdesign. TK5 includes IBM OS/VS2 MVS Release 3.8J and software from other contributors. **Rob Prins** assembled TK5 with help from others; its [Introduction and User Manual](https://www.prince-webdesign.nl/images/downloads/TK5-Introduction-and-User-Manual.pdf) credits Rob Prins and Thomas Armstrong and traces the distribution’s lineage through **Volker Bandke’s TK3** and **Jürgen Winkelmann’s TK4-**.

The Docker build downloads TK5 from its publisher. The TK5 archive and DASD images are not stored in this repository, but they are included in an image built with this Dockerfile. This project’s MIT License does not apply to TK5 or supersede the rights and terms applicable to its components.

## Ubuntu base image 

The Docker image is built from the [Ubuntu Official Image](https://hub.docker.com/_/ubuntu). Ubuntu and the packages included in the image remain subject to their respective licenses and copyright notices. This project’s MIT License applies only to its original work.

Ubuntu is a trademark of Canonical Ltd. This project is not affiliated with or endorsed by Canonical.

## Acknowledgment of AI assistance

I used [OpenAI’s ChatGPT](https://chatgpt.com/) to help research historical BCPL materials, draft code and documentation, and review implementation ideas. 

Portions of this project were also developed with assistance from [Claude by Anthropic](https://claude.ai/). 

I reviewed and revised the resulting work and am responsible for the repository’s contents.
