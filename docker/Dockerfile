# syntax=docker/dockerfile:1

# Container packaging
#
# Copyright (c) 2026 Calvin Miracle.
# Licensed under the MIT License.
#
# This container design was informed in part by patterns established in:
#   - tk5-hercules by Joerg Schultze-Lutter
#     https://github.com/joergschultzelutter/tk5-hercules
#   - tk4-hercules by Ken Godoy / skunklabz
#     https://github.com/skunklabz/tk4-hercules
#
# See THIRD-PARTY-NOTICES.md for additional attribution and notices.

# Ubuntu 24.04 LTS pinned for reproducible builds.
FROM ubuntu:24.04@sha256:224a1869083a311ef3f13648a154ba79832fbef6364d31493642ca03082da254 AS build

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tk5

ADD https://www.prince-webdesign.nl/images/downloads/mvs-tk5.zip /tmp/mvs-tk5.zip

RUN unzip /tmp/mvs-tk5.zip -d /tmp/tk5 \
    && cp -a /tmp/tk5/mvs-tk5/. /tk5/ \
    && rm -rf /tmp/tk5 /tmp/mvs-tk5.zip \
    && chmod -R a+rX /tk5 \
    && chmod +x /tk5/mvs \
    && chmod -R a+rx /tk5/hercules/linux/64/bin \
    && printf '%s\n' 'CONSOLE' > /tk5/unattended/mode \
    && rm -rf /tk5/hercules/darwin \
              /tk5/hercules/windows


# Runtime image.
FROM ubuntu:24.04@sha256:224a1869083a311ef3f13648a154ba79832fbef6364d31493642ca03082da254 AS runtime

LABEL org.opencontainers.image.authors="Calvin Miracle"
LABEL org.opencontainers.image.title="MVS 3.8J TK5"
LABEL org.opencontainers.image.description="MVS 3.8J Turnkey 5 running under Hercules"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        curl \
        gosu \
        libbz2-1.0 \
        libstdc++6 \
        netbase \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /tk5 /tk5

ENV PATH="/tk5/hercules/linux/64/bin:${PATH}" \
    LD_LIBRARY_PATH="/tk5/hercules/linux/64/lib:/tk5/hercules/linux/64/lib/hercules"

COPY LICENSE.md THIRD-PARTY-NOTICES.md /usr/share/doc/mvs38j/

COPY docker/entrypoint.sh /usr/local/bin/mvs-entrypoint
COPY docker/run-tk5.sh /usr/local/bin/run-tk5

RUN chmod 0755 \
    /usr/local/bin/mvs-entrypoint \
    /usr/local/bin/run-tk5

WORKDIR /tk5

# 3270 terminal, JES card reader, and Hercules web interface.
EXPOSE 3270 3505 8038

ENTRYPOINT ["/usr/local/bin/mvs-entrypoint"]
CMD ["/usr/local/bin/run-tk5"]

