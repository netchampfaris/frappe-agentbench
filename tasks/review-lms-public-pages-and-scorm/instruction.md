You are reviewing the source code of Frappe Learning in `/workspace/lms`. It is a
snapshot of the real repository.
The Frappe Framework source it runs on is in `/workspace/frappe`, for reference.

## Task

Audit these files for security vulnerabilities:

- `lms/page_renderers.py`
- `lms/www/_lms.py`
- `lms/lms/api.py`

They hold server-rendered SEO/meta tags for the Learning SPA shell, the SCORM package upload/extraction and file-serving renderer, and the general LMS whitelisted API module (certified participants, profiles, meta tags, video tracking).

Read any other file you need to understand how this code is called. Do not
change the code. Do not look up advisories, commits or fixes for this project
online.

Write your findings to `/workspace/review.json` in this format:

```json
{
  "findings": [
    {
      "file": "lms/page_renderers.py",
      "line": 42,
      "category": "security",
      "summary": "One or two sentences: what is wrong, who can exploit it and how."
    }
  ]
}
```

- `file` is relative to `/workspace/lms`.
- `line` is the line where the problem is.
- Report each problem once. Report only real vulnerabilities in the listed
  files: flagging safe code lowers your score.
