# frappe/erpnext at 2026-07-15, before the fixes listed in tests/issues.json
FROM frappe-agentbench-source:v1
RUN fetch-snapshot frappe/erpnext e99966a38ec83555919ea1d0f7155e53f6b00a4e /workspace/erpnext \
 && fetch-snapshot frappe/frappe e6b2dae094582118fbb452ba678bb47e38043065 /workspace/frappe
