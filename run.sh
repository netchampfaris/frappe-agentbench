#!/bin/bash
# Usage:
#   ./run.sh build                 Build the Frappe base image all tasks start from
#   ./run.sh check                 Reference solutions must score 1, doing nothing must score 0
#   ./run.sh claude [model] [...]  Run Claude Code (default model: claude-opus-5-5)
#   ./run.sh codex [model] [...]   Run Codex with ~/.codex/auth.json (default: Codex's own default)
#   ./run.sh deepseek [...]        Run Pi against DEEPSEEK_BASE_URL
#
# Extra arguments go to `harbor run`, for example `-k 3` for three attempts per
# task or `-i doctype-validation` to run one task.
set -euo pipefail
cd "$(dirname "$0")"

[ -f .env ] && set -a && . ./.env && set +a
harbor() { uv run --quiet harbor "$@"; }
run() { harbor run -p tasks -o jobs -n "${CONCURRENCY:-4}" "$@"; }

command="${1:-}"; shift || true
case "$command" in
  build)
    docker build -t frappe-agentbench-base:v16 base ;;
  check)
    run -a oracle "$@"
    run -a nop "$@" ;;
  claude)
    model="${1:-claude-opus-5-5}"; shift || true
    run -a claude-code -m "anthropic/$model" "$@" ;;
  codex)
    model=(); [ -n "${1:-}" ] && [[ "$1" != -* ]] && { model=(-m "openai/$1"); shift; }
    CODEX_FORCE_AUTH_JSON=1 run -a codex "${model[@]}" "$@" ;;
  deepseek)
    : "${DEEPSEEK_BASE_URL:?Set DEEPSEEK_BASE_URL in .env}" "${DEEPSEEK_API_KEY:?Set DEEPSEEK_API_KEY in .env}"
    OPENAI_API_KEY="$DEEPSEEK_API_KEY" run -a pi -m "deepseek/${DEEPSEEK_MODEL:-deepseek-v4.1-flash}" \
      --ak base_url="$DEEPSEEK_BASE_URL" --ak model_api=openai-completions "$@" ;;
  *)
    sed -n '2,10p' "$0"; exit 1 ;;
esac
