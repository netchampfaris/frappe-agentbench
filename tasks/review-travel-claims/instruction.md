You are working in a Frappe Framework v16 bench at `/workspace/frappe-bench`.
The site is `acme.localhost` and the custom app is `acme` (module "Acme").
MariaDB and Redis are already running.

## Task

A teammate built a travel claims feature in the `acme` app: the **Travel Claim**
DocType and the API in `acme/travel.py`. Review this code before it ships.

Look for:

- security problems
- bugs
- patterns that go against Frappe conventions and will cause trouble

Do not change the code. Write your findings to
`/workspace/frappe-bench/review.json` in this format:

```json
{
  "findings": [
    {
      "file": "acme/travel.py",
      "line": 42,
      "category": "security",
      "summary": "One or two sentences: what is wrong and why it matters."
    }
  ]
}
```

- `file` is relative to the app's Python package, `apps/acme/acme/`.
- `line` is the line where the problem is.
- `category` is `security`, `bug` or `pattern`.
- Report each problem once. Report only real problems: flagging correct code
  lowers your score.
