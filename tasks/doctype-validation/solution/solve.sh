#!/bin/bash
set -e
cp -r /solution/files/acme/. /workspace/frappe-bench/apps/acme/acme/
cd /workspace/frappe-bench && bench --site acme.localhost migrate
