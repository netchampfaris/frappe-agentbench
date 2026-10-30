"""Grade a task and write /logs/verifier/reward.json.

Usage: grade.py <tests-dir>

The tests directory decides the kind of task:

- test_task.py  Build task. The file is copied into the app and run with
                `bench run-tests`. reward = share of tests that passed.
- issues.json   Review task. The agent's review.json is matched against the
                planted issues. reward = share of issues found (recall).
"""

import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BENCH = Path(os.environ.get("BENCH", "/workspace/frappe-bench"))
SITE = os.environ.get("SITE", "acme.localhost")
LOGS = Path("/logs/verifier")
HIDDEN = BENCH / "apps/acme/acme/hidden_tests"
REVIEW = BENCH / "review.json"

# A finding may point a few lines outside the planted range and still count.
LINE_SLACK = 3


def main(tests_dir: Path) -> None:
	LOGS.mkdir(parents=True, exist_ok=True)
	# The agent, or a crash, may have stopped MariaDB or Redis. This starts
	# whichever is not running.
	run("/usr/local/bin/entrypoint.sh", "true")
	if (tests_dir / "issues.json").exists():
		reward = grade_review(json.loads((tests_dir / "issues.json").read_text()))
	else:
		reward = grade_build(tests_dir / "test_task.py")
	print(f"Reward: {reward}")
	(LOGS / "reward.json").write_text(json.dumps(reward))


def grade_build(test_file: Path) -> dict[str, float]:
	if changed := run("git", "-C", "apps/frappe", "status", "--porcelain").stdout.strip():
		print(f"Frappe core was modified, which tasks do not allow:\n{changed}")
		return build_reward(0, 1)

	shutil.rmtree(HIDDEN, ignore_errors=True)
	HIDDEN.mkdir()
	(HIDDEN / "__init__.py").touch()
	shutil.copy(test_file, HIDDEN / "test_task.py")

	if run("bench", "--site", SITE, "migrate").returncode != 0:
		return build_reward(0, 1)
	# Agents may turn tests off again after running their own.
	run("bench", "--site", SITE, "set-config", "allow_tests", "true")

	junit = LOGS / "junit.xml"
	run(
		"bench", "--site", SITE, "run-tests",
		"--module", "acme.hidden_tests.test_task",
		"--junit-xml-output", str(junit),
	)
	if not junit.exists() or junit.stat().st_size == 0:
		print("No test report was written; the test module probably failed to import")
		return build_reward(0, 1)

	cases = list(ET.parse(junit).getroot().iter("testcase"))
	passed = sum(not any(c.tag in ("failure", "error", "skipped") for c in case) for case in cases)
	return build_reward(passed, len(cases))


def build_reward(passed: int, total: int) -> dict[str, float]:
	total = max(total, 1)
	return {"reward": passed / total, "solved": int(passed == total)}


def grade_review(expected: dict) -> dict[str, float]:
	"""Match findings to planted issues by file and line.

	issues.json has `issues` (problems the agent should report) and `decoys`
	(code that looks wrong but is correct). Each has `id`, `file` and `lines`.

	reward = found / (issues + decoy hits), so flagging correct code costs as
	much as missing an issue. Findings that match neither may be real problems
	nobody planted, so they are logged but not penalised.
	"""
	issues, decoys = expected["issues"], expected.get("decoys", [])
	if REVIEW.exists():
		shutil.copy(REVIEW, LOGS / "review.json")
	try:
		findings = json.loads(REVIEW.read_text())["findings"]
	except (OSError, ValueError, KeyError, TypeError) as e:
		print(f"Could not read {REVIEW}: {e!r}")
		findings = []

	found: set[str] = set()
	decoy_hits: set[str] = set()
	for finding in findings:
		where = f"{finding.get('file')}:{finding.get('line')}"
		if issue := closest(finding, [i for i in issues if i["id"] not in found]):
			found.add(issue["id"])
			print(f"found     {issue['id']} <- {where}")
		elif decoy := closest(finding, decoys):
			decoy_hits.add(decoy["id"])
			print(f"decoy hit {decoy['id']} <- {where}")
		elif not closest(finding, issues):
			print(f"unmatched {where}: {finding.get('summary', '')[:100]}")

	for issue in issues:
		if issue["id"] not in found:
			print(f"missed    {issue['id']}")

	return {
		"reward": len(found) / (len(issues) + len(decoy_hits)),
		"solved": int(len(found) == len(issues) and not decoy_hits),
		"recall": len(found) / len(issues),
		"decoy_hits": len(decoy_hits),
	}


def closest(finding: dict, targets: list[dict]) -> dict | None:
	"""The target in the same file whose line range is nearest the finding."""
	try:
		path, line = str(finding["file"]), int(finding["line"])
	except (KeyError, TypeError, ValueError):
		return None
	distances = [
		(max(t["lines"][0] - line, line - t["lines"][1], 0), t)
		for t in targets
		if path.endswith(t["file"])
	]
	distances = [(d, t) for d, t in distances if d <= LINE_SLACK]
	return min(distances, key=lambda dt: dt[0])[1] if distances else None


def run(*cmd: str) -> subprocess.CompletedProcess[str]:
	result = subprocess.run(cmd, cwd=BENCH, text=True, capture_output=True)
	print(f"$ {' '.join(cmd)}\n{result.stdout}{result.stderr}", flush=True)
	return result


if __name__ == "__main__":
	main(Path(sys.argv[1]))
