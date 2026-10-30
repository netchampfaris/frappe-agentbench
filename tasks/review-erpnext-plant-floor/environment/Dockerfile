# frappe/erpnext at 2026-06-08, before the fixes listed in tests/issues.json
FROM frappe-agentbench-source:v1
RUN fetch-snapshot frappe/erpnext d146dc543590d32a29f2e30c1bd5103025a6d52d /workspace/erpnext \
 && fetch-snapshot frappe/frappe 84fa0e3f194ae74e573a9b034d03fdce78a0cff3 /workspace/frappe
