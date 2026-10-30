#!/bin/bash
# Start MariaDB and the two Redis servers the bench expects, then run the command.
set -e

if ! mariadb-admin ping --silent 2>/dev/null; then
  mysqld_safe --user="$(id -un)" >/tmp/mariadb.log 2>&1 &
  for _ in $(seq 60); do mariadb-admin ping --silent 2>/dev/null && break; sleep 0.5; done

  # First start: MariaDB's root uses socket auth for the OS root user only.
  # Give it the password Frappe uses so the frappe user can log in.
  if ! mariadb -uroot -proot -e 'select 1' >/dev/null 2>&1; then
    sudo mariadb -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'root'; FLUSH PRIVILEGES;"
  fi
fi

for port in 13000 11000; do
  redis-cli -p "$port" ping >/dev/null 2>&1 || redis-server --port "$port" --save "" --appendonly no --daemonize yes >/dev/null
done

exec "$@"
