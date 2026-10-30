You are reviewing the source code of Frappe HR in `/workspace/hrms`. It is a
snapshot of the real repository.
The Frappe Framework source it runs on is in `/workspace/frappe`, for reference.

## Task

Audit these files for security vulnerabilities:

- `hrms/api/__init__.py`
- `hrms/api/roster.py`

They hold the whitelisted API layer behind the HRMS employee mobile app (PWA) and the shift roster UI: attendance, shifts, leave balances, expense claims, advances, attachments and roster helpers.

Read any other file you need to understand how this code is called. Do not
change the code. Do not look up advisories, commits or fixes for this project
online.

Write your findings to `/workspace/review.json` in this format:

```json
{
  "findings": [
    {
      "file": "hrms/api/__init__.py",
      "line": 42,
      "category": "security",
      "summary": "One or two sentences: what is wrong, who can exploit it and how."
    }
  ]
}
```

- `file` is relative to `/workspace/hrms`.
- `line` is the line where the problem is.
- Report each problem once. Report only real vulnerabilities in the listed
  files: flagging safe code lowers your score.
