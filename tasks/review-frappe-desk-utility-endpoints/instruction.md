You are reviewing the source code of Frappe Framework in `/workspace/frappe`. It is a
snapshot of the real repository.

## Task

Audit these files for security vulnerabilities:

- `frappe/desk/doctype/event/event.py`
- `frappe/core/doctype/deleted_document/deleted_document.py`
- `frappe/desk/doctype/form_tour/form_tour.py`
- `frappe/core/doctype/sms_settings/sms_settings.py`

They hold small desk helper endpoints: calendar events and attendance, restoring deleted documents, form tour resets, and SMS sending.

Read any other file you need to understand how this code is called. Do not
change the code. Do not look up advisories, commits or fixes for this project
online.

Write your findings to `/workspace/review.json` in this format:

```json
{
  "findings": [
    {
      "file": "frappe/desk/doctype/event/event.py",
      "line": 42,
      "category": "security",
      "summary": "One or two sentences: what is wrong, who can exploit it and how."
    }
  ]
}
```

- `file` is relative to `/workspace/frappe`.
- `line` is the line where the problem is.
- Report each problem once. Report only real vulnerabilities in the listed
  files: flagging safe code lowers your score.
