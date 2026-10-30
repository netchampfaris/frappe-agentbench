# frappe/erpnext at 2026-08-01, before the fixes listed in tests/issues.json
FROM frappe-agentbench-source:v1
RUN fetch-snapshot frappe/erpnext e694d45ed49cd00e07a81aab67a4b08ca8516317 /workspace/erpnext \
 && fetch-snapshot frappe/frappe cdac677ffa96170db231febeed7604d42ec2f974 /workspace/frappe
