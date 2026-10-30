"""Summarise agent results from Harbor job folders.

Usage:
  uv run report.py [JOB_DIR ...]                 Print Markdown tables
  uv run report.py --json OUT.json [JOB_DIR ...] Write the data the dashboard reads

With no job folders, reads every folder in jobs/ except jobs/excluded/, which
holds smoke runs and trials set aside because of harness bugs. Oracle and nop runs are left out.
"""

import json
import re
import sys
import tomllib
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

SKIP_AGENTS = {"oracle", "nop"}
TASKS = Path("tasks")


def main(args: list[str]) -> None:
	out = None
	if args[:1] == ["--json"]:
		out, args = Path(args[1]), args[2:]
	job_dirs = [Path(a) for a in args] or sorted(
		p for p in Path("jobs").iterdir() if p.is_dir() and p.name != "excluded"
	)
	trials = [t for d in job_dirs for t in load_trials(d)]
	if not trials:
		sys.exit("No agent trials found")

	if out:
		out.parent.mkdir(parents=True, exist_ok=True)
		data = {"generated_at": datetime.now(UTC).isoformat(timespec="seconds"), "tasks": load_tasks(), "trials": trials}
		out.write_text(json.dumps(data, indent=1))
		print(f"Wrote {len(trials)} trials to {out}")
	else:
		print_markdown(trials)


def print_markdown(trials: list[dict]) -> None:
	by_cell = defaultdict(list)
	for t in trials:
		by_cell[t["model"], t["task"]].append(t)
	models = sorted({t["model"] for t in trials})
	tasks = sorted({t["task"] for t in trials})

	print("| Model | Task | Reward | Solved | Agent time | Output tokens | Errors |")
	print("| --- | --- | --- | --- | --- | --- | --- |")
	for model in models:
		for task in tasks:
			if cell := by_cell.get((model, task)):
				print(
					f"| {model} | {task} | {mean(t['reward'] for t in cell):.2f} "
					f"| {sum(t['solved'] for t in cell)}/{len(cell)} "
					f"| {mean(t['seconds'] for t in cell) / 60:.1f} min "
					f"| {mean(t['output_tokens'] for t in cell):,.0f} "
					f"| {sum(t['error'] is not None for t in cell)} |"
				)
		model_trials = [t for t in trials if t["model"] == model]
		print(f"| **{model}** | **all** | **{mean(t['reward'] for t in model_trials):.2f}** "
		      f"| **{sum(t['solved'] for t in model_trials)}/{len(model_trials)}** | | | |")

	for task in sorted({t["task"] for t in trials if t["issues"]}):
		issue_ids = list(next(t["issues"] for t in trials if t["task"] == task and t["issues"]))
		print(f"\n**{task}**: share of trials that found each issue\n")
		print("| Issue | " + " | ".join(models) + " |")
		print("| --- |" + " --- |" * len(models))
		for issue in issue_ids:
			row = []
			for model in models:
				cell = [t for t in by_cell.get((model, task), []) if t["issues"]]
				row.append(f"{sum(t['issues'].get(issue, False) for t in cell)}/{len(cell)}" if cell else "-")
			print(f"| {issue} | " + " | ".join(row) + " |")
		decoys = [str(sum(t["decoy_hits"] for t in by_cell.get((m, task), []))) for m in models]
		print("| *decoys flagged (total)* | " + " | ".join(decoys) + " |")


def load_tasks() -> list[dict]:
	tasks = []
	for toml in sorted(TASKS.glob("*/task.toml")):
		config = tomllib.loads(toml.read_text())["task"]
		issues_file = toml.parent / "tests/issues.json"
		issues = json.loads(issues_file.read_text())["issues"] if issues_file.exists() else []
		tasks.append({
			"name": toml.parent.name,
			"kind": "review" if issues else "build",
			"description": config.get("description", ""),
			"issues": [{"id": i["id"], "category": i["category"], "note": i["note"]} for i in issues],
		})
	return tasks


def load_trials(job_dir: Path) -> list[dict]:
	trials = []
	for path in sorted(job_dir.glob("*/result.json")):
		r = json.loads(path.read_text())
		agent = r["config"]["agent"]
		if agent["name"] in SKIP_AGENTS:
			continue
		rewards = (r.get("verifier_result") or {}).get("rewards") or {}
		usage = r.get("agent_result") or {}
		verifier = path.parent / "verifier"
		trials.append({
			"job": job_dir.name,
			"trial": r["trial_name"],
			"agent": agent["name"],
			"agent_version": (r.get("agent_info") or {}).get("version"),
			"model": agent["model_name"].split("/")[-1],
			"task": r["task_name"].split("/")[-1],
			"started_at": r.get("started_at"),
			"reward": rewards.get("reward", 0.0),
			"solved": int(rewards.get("solved", 0)),
			"decoy_hits": int(rewards.get("decoy_hits", 0)),
			"seconds": round(seconds(r.get("agent_execution") or {}), 1),
			"output_tokens": usage.get("n_output_tokens") or 0,
			"error": (r.get("exception_info") or {}).get("exception_type"),
			"issues": review_outcomes(verifier / "test-stdout.txt"),
			"failed_tests": failed_tests(verifier / "junit.xml"),
		})
	return trials


def review_outcomes(stdout: Path) -> dict[str, bool]:
	"""Issue id -> found, read from the grader's found/missed log lines."""
	if not stdout.exists():
		return {}
	return {
		m["id"]: m["kind"] == "found"
		for m in re.finditer(r"^(?P<kind>found|missed) +(?P<id>[\w-]+)", stdout.read_text(), re.M)
	}


def failed_tests(junit: Path) -> list[str]:
	if not junit.exists() or junit.stat().st_size == 0:
		return []
	return [
		case.get("name", "?")
		for case in ET.parse(junit).getroot().iter("testcase")
		if any(c.tag in ("failure", "error") for c in case)
	]


def seconds(span: dict) -> float:
	if not span.get("started_at") or not span.get("finished_at"):
		return 0.0
	start, end = (datetime.fromisoformat(span[k]) for k in ("started_at", "finished_at"))
	return (end - start).total_seconds()


if __name__ == "__main__":
	main(sys.argv[1:])
