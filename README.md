# Frappe Agent Bench

Measures how well coding agents write and review Frappe Framework code.

Each task runs in a fresh Docker container that holds a Frappe v16 bench, a
site (`acme.localhost`) and a custom app (`acme`). The agent works inside the
container. Afterwards a grader scores the result from 0 to 1.
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

**Review tasks** give the agent code with planted problems: security holes,
bugs and patterns that go against Frappe conventions. The agent writes its
findings to `review.json`. The grader matches each finding to a planted issue
by file and line. Some correct code looks risky on purpose. These are
**decoys**, and flagging one costs as much as missing an issue:

```
reward = issues found / (planted issues + decoys flagged)
```

Findings that match neither are logged and not penalised, because they may be
real problems nobody planted.

| Task                   | Kind   | Tests what                                             |
| ---------------------- | ------ | ------------------------------------------------------ |
| `doctype-validation`   | build  | New DocType, validation that queries other records     |
| `api-permissions`      | build  | Whitelisted methods, roles, ownership, POST-only       |
| `doc-events-hook`      | build  | `doc_events` on a core DocType, status transitions     |
| `review-travel-claims` | review | 11 planted issues: SQL injection, XSS, permission gaps, bugs |

## Setup

You need Docker with the `compose` plugin, and [uv](https://docs.astral.sh/uv/).

```sh
./run.sh build          # build the base image, about 5 minutes
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

Run `./run.sh check -i <name>` afterwards. A task is ready when the reference
solution scores 1 and doing nothing scores 0. In build tasks, a test that
checks that something does not happen must also check the positive case.
Otherwise an empty app passes it.
