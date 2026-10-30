# Base image for every task: one Frappe v16 bench with a site and an empty app.
# MariaDB and Redis run inside the container, started by the entrypoint.
# Everything runs as the `frappe` user because bench refuses to run as root.
FROM ubuntu:24.04

ARG FRAPPE_BRANCH=version-16
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    BENCH=/workspace/frappe-bench \
    SITE=acme.localhost

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl git sudo build-essential pkg-config \
      libmariadb-dev mariadb-server mariadb-client redis-server \
    && curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g yarn \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Swap Ubuntu's default user for `frappe` (uid 1000) and let it run MariaDB.
RUN userdel -r ubuntu \
    && useradd -m -u 1000 -s /bin/bash frappe \
    && echo "frappe ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/frappe \
    && mkdir -p /workspace /run/mysqld /logs \
    && chown -R frappe:frappe /workspace /run/mysqld /var/lib/mysql /logs

COPY mariadb.cnf /etc/mysql/mariadb.conf.d/99-frappe.cnf
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

USER frappe
ENV PATH=/home/frappe/.local/bin:$PATH
RUN uv python install 3.14 && uv tool install frappe-bench

WORKDIR /workspace
RUN bench init frappe-bench \
      --frappe-branch "$FRAPPE_BRANCH" \
      --python "$(uv python find 3.14)" \
      --skip-assets --no-backups \
    && git -C frappe-bench/apps/frappe log -1 --format='frappe %h %cs'

COPY --chown=frappe:frappe acme /workspace/frappe-bench/apps/acme
WORKDIR /workspace/frappe-bench
RUN uv pip install -q --python env/bin/python -e apps/acme unittest-xml-reporting \
    && sed -i "\$a acme" sites/apps.txt \
    && /usr/local/bin/entrypoint.sh true \
    && bench new-site "$SITE" --db-root-password root --admin-password admin --install-app acme \
    && bench use "$SITE" \
    && bench --site "$SITE" set-config allow_tests true \
    && git -C apps/acme init -q && git -C apps/acme add -A \
    && git -C apps/acme -c user.name=bench -c user.email=bench@localhost commit -qm "Initial app" \
    && mariadb-admin -uroot -proot shutdown

# Kept last so editing the grader does not rebuild the bench.
COPY grade.py prepare-task /opt/agentbench/

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["sleep", "infinity"]
