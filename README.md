# Frappe Agent Bench

Measures how well coding agents write and review Frappe Framework code.

Each task runs in a fresh Docker container. Build tasks and planted reviews
get a Frappe v16 bench with a site (`acme.localhost`) and a custom app
(`acme`). Real vulnerability tasks get the source code of a Frappe app as it was
before some of its security fixes. The agent works inside the container.
Afterwards a grader scores the result from 0 to 1.
[Harbor](https://github.com/laude-institute/harbor) runs the containers and
agents and records the results.

```
 tasks/<name>/          Harbor                         jobs/<timestamp>/
 ┌──────────────┐      ┌─────────────────────────┐     ┌──────────────┐
 │ instruction  │ ───▶ │ 1. start container       │ ──▶ │ reward.json  │
 │ environment  │      │ 2. agent does the task   │     │ transcript   │
 │ tests/       │      │ 3. copy in tests, grade  │     │ test output  │
 │ solution/    │      └─────────────────────────┘     └──────────────┘
 └──────────────┘
```

## Task kinds

**Build tasks** ask the agent to write a feature. The grader copies hidden
tests into the app, runs `bench migrate` and `bench run-tests`, and scores the
share of tests that pass. It gives 0 if the agent changed the `frappe` app.

**Planted reviews** give the agent code with planted problems: security holes,
bugs and patterns that go against Frappe conventions. The agent writes its
findings to `review.json`. The grader matches each finding to a planted issue
by file and line. Some correct code looks risky on purpose. These are
**decoys**, and flagging one costs as much as missing an issue:

```
reward = issues found / (planted issues + decoys flagged)
```

Findings that match neither are logged and not penalised, because they may be
real problems nobody planted.

**Real vulnerability tasks** give the agent a snapshot of a real Frappe app
(Frappe Framework, ERPNext, HRMS, CRM or Learning) taken before some of its
security fixes, and a list of 2 to 5 files to audit. The answer key holds the
vulnerabilities that were later fixed in those files, with their advisory and
fix commit. Only published advisories are used. Each key has 6 to 8 issues and
2 or 3 decoys, and is graded like a planted review.

The snapshot has no git history, and there is no installed bench, because an
installed Frappe would already contain the fixes. The agent's web search and
web fetch tools are turned off. The advisories are public, so treat these
scores as an upper bound: a model may remember a fix.

| Task                   | Kind   | Tests what                                             |
| ---------------------- | ------ | ------------------------------------------------------ |
| `doctype-validation`   | build  | New DocType, validation that queries other records     |
| `api-permissions`      | build  | Whitelisted methods, roles, ownership, POST-only       |
| `doc-events-hook`      | build  | `doc_events` on a core DocType, status transitions     |
| `review-travel-claims` | review | 11 planted issues: SQL injection, XSS, permission gaps, bugs |
| `review-frappe-*`      | real   | 3 tasks: document follow and likes, desk endpoints, file handling |
| `review-erpnext-*`     | real   | 3 tasks: plant floor, projects portal, payment requests and bank import |
| `review-hrms-*`        | real   | 2 tasks: mobile app API, payroll reports |
| `review-crm-*`         | real   | 1 task: user and role management APIs |
| `review-lms-*`         | real   | 3 tasks: quizzes and checkout, public pages and SCORM, enrollment and certificates |

## Setup

You need Docker with the `compose` plugin, and [uv](https://docs.astral.sh/uv/).

```sh
./run.sh build          # build both images, about 5 minutes
./run.sh check          # every task: reference solution scores 1, doing nothing scores 0
cp .env.example .env    # then fill in credentials
```

## Running agents

```sh
./run.sh claude                   # Claude Code, Opus 5.5
./run.sh claude claude-sonnet-5-5 # another model
./run.sh codex                    # Codex, ChatGPT subscription via ~/.codex/auth.json
./run.sh deepseek                 # Pi, DeepSeek through an OpenAI-compatible endpoint

./run.sh claude -k 3              # 3 attempts per task; results vary between runs
./run.sh claude -i api-permissions
```

Results go to `jobs/`. Browse transcripts with `uv run harbor view jobs`.
Move smoke runs, and trials broken by harness bugs, to `jobs/excluded/` so they
stay out of reports.

## Results

```sh
uv run report.py                                # Markdown tables in the terminal
uv run report.py --json dashboard/results.json  # data for the dashboard
python3 -m http.server -d dashboard             # open http://localhost:8000
```

`dashboard/` is a static page with no build step. It shows the score per model,
the score per model and task, which planted issues each model found, and every
attempt with its failed tests or missed issues.

## Adding a task

Copy the closest existing task and change it:

```
tasks/<name>/
├── task.toml           name, timeouts. Keep environment_mode = "shared".
├── instruction.md      what the agent sees
├── environment/
│   ├── Dockerfile      FROM frappe-agentbench-base:v16
│   └── acme/           optional starting code, then RUN /opt/agentbench/prepare-task
├── tests/
│   ├── test.sh         runs /opt/agentbench/grade.py
│   ├── test_task.py    build tasks: hidden IntegrationTestCase tests
│   └── issues.json     review tasks: planted issues and decoys
└── solution/
    └── solve.sh        reference answer
```

A real vulnerability task uses `FROM frappe-agentbench-source:v1` and runs
`fetch-snapshot <owner/repo> <commit> /workspace/<app>`. Its `issues.json` also
has `repo` and `snapshot`, and each issue has a `fix_commit` and, when the match
is certain, a `ghsa` id. Use only published advisories: the repository is public.

Run `./run.sh check -i <name>` afterwards. A task is ready when the reference
solution scores 1 and doing nothing scores 0. In build tasks, a test that
checks that something does not happen must also check the positive case.
Otherwise an empty app passes it.
