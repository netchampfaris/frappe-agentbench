You are reviewing the source code of Frappe Learning in `/workspace/lms`. It is a
snapshot of the real repository.
The Frappe Framework source it runs on is in `/workspace/frappe`, for reference.

## Task

Audit these files for security vulnerabilities:

- `lms/lms/doctype/lms_quiz/lms_quiz.py`
- `lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.py`
- `lms/lms/doctype/lms_quiz_submission/lms_quiz_submission.json`
- `lms/lms/payments.py`
- `lms/lms/doctype/lms_enrollment/lms_enrollment.py`

They hold quiz submission and scoring, the quiz submission doctype and its permissions, paid course/batch checkout, and course enrollment validation in Frappe Learning.

Read any other file you need to understand how this code is called. Do not
change the code. Do not look up advisories, commits or fixes for this project
online.

Write your findings to `/workspace/review.json` in this format:

```json
{
  "findings": [
    {
      "file": "lms/lms/doctype/lms_quiz/lms_quiz.py",
      "line": 42,
      "function": "get_report",
      "category": "security",
      "summary": "One or two sentences: what is wrong, who can exploit it and how."
    }
  ]
}
```

- `file` is relative to `/workspace/lms`.
- `line` is the line where the problem is.
- `function` is the name of the function the problem is in. Leave it out for
  problems outside a function, such as in a template or a JSON file.
- Report each problem once. When the same flaw is in several functions,
  report each function separately.
- Report only real vulnerabilities in the listed files: flagging safe code
  lowers your score.
