You are reviewing the source code of ERPNext in `/workspace/erpnext`. It is a
snapshot of the real repository.
The Frappe Framework source it runs on is in `/workspace/frappe`, for reference.

## Task

Audit these files for security vulnerabilities:

- `erpnext/manufacturing/doctype/workstation/workstation.py`
- `erpnext/manufacturing/doctype/plant_floor/plant_floor.py`
- `erpnext/manufacturing/doctype/plant_floor/stock_summary_template.html`
- `erpnext/public/js/templates/visual_plant_floor_template.html`

They hold the manufacturing Workstation and Plant Floor features: job card start and complete actions driven from a workstation, the visual plant floor dashboard, and the plant floor stock summary.

Read any other file you need to understand how this code is called. Do not
change the code. Do not look up advisories, commits or fixes for this project
online.

Write your findings to `/workspace/review.json` in this format:

```json
{
  "findings": [
    {
      "file": "erpnext/manufacturing/doctype/workstation/workstation.py",
      "line": 42,
      "category": "security",
      "summary": "One or two sentences: what is wrong, who can exploit it and how."
    }
  ]
}
```

- `file` is relative to `/workspace/erpnext`.
- `line` is the line where the problem is.
- Report each problem once. Report only real vulnerabilities in the listed
  files: flagging safe code lowers your score.
