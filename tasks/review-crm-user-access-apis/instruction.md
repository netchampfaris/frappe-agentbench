You are reviewing the source code of Frappe CRM in `/workspace/crm`. It is a
snapshot of the real repository.
The Frappe Framework source it runs on is in `/workspace/frappe`, for reference.

## Task

Audit these files for security vulnerabilities:

- `crm/api/__init__.py`
- `crm/api/user.py`
- `crm/api/session.py`
- `crm/fcrm/doctype/crm_invitation/crm_invitation.py`
- `crm/fcrm/doctype/crm_view_settings/crm_view_settings.py`

They hold Frappe CRM user and access management: inviting users, accepting invitations, assigning CRM roles, session bootstrap data and saved list views.

Read any other file you need to understand how this code is called. Do not
change the code. Do not look up advisories, commits or fixes for this project
online.

Write your findings to `/workspace/review.json` in this format:

```json
{
  "findings": [
    {
      "file": "crm/api/__init__.py",
      "line": 42,
      "function": "get_report",
      "category": "security",
      "summary": "One or two sentences: what is wrong, who can exploit it and how."
    }
  ]
}
```

- `file` is relative to `/workspace/crm`.
- `line` is the line where the problem is.
- `function` is the name of the function the problem is in. Leave it out for
  problems outside a function, such as in a template or a JSON file.
- Report each problem once. When the same flaw is in several functions,
  report each function separately.
- Report only real vulnerabilities in the listed files: flagging safe code
  lowers your score.
