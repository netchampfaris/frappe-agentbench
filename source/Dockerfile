# Build from the repository root: docker build -f source/Dockerfile .
# Image for review tasks on real Frappe app code. Each task fetches a snapshot
# of a repository taken before some security fixes. There is no bench: the
# installed Frappe would already contain the fixes, so an agent could diff it.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl git gnupg procps python3 ripgrep sudo \
    && curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN userdel -r ubuntu \
    && useradd -m -u 1000 -s /bin/bash frappe \
    && echo "frappe ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/frappe \
    && mkdir -p /workspace /logs && chown frappe:frappe /workspace /logs

COPY source/fetch-snapshot /usr/local/bin/
COPY base/grade.py /opt/agentbench/

ENV BENCH=/workspace
USER frappe
WORKDIR /workspace
CMD ["sleep", "infinity"]
