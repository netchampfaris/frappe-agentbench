You are reviewing the source code of Frappe Learning in `/workspace/lms`. It is a
snapshot of the real repository.
The Frappe Framework source it runs on is in `/workspace/frappe`, for reference.

## Task

Audit these files for security vulnerabilities:

- `lms/lms/utils.py`
- `lms/lms/doctype/lms_enrollment/lms_enrollment.py`
- `lms/lms/doctype/lms_batch_enrollment/lms_batch_enrollment.py`
- `lms/lms/doctype/lms_certificate/lms_certificate.py`

They hold course and batch detail APIs, self-enrollment into courses, batches and programs, batch enrollment controller, and certificate issuing and website visibility in Frappe Learning.

Read any other file you need to understand how this code is called. Do not
change the code. Do not look up advisories, commits or fixes for this project
online.

Write your findings to `/workspace/review.json` in this format:

```json
{
  "findings": [
    {
      "file": "lms/lms/utils.py",
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
