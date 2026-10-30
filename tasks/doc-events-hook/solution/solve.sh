#!/bin/bash
set -e
APP=/workspace/frappe-bench/apps/acme/acme
cp /solution/files/todo.py "$APP/todo.py"
cat >> "$APP/hooks.py" <<'PY'

doc_events = {
	"ToDo": {
		"on_update": "acme.todo.add_closed_comment",
	},
}
PY
