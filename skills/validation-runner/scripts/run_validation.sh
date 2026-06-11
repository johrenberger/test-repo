#!/usr/bin/env bash
# run_validation.sh — execute a single command captured from
# detect_validation_commands.sh, capturing exit code, stdout, stderr,
# and elapsed time. Read-only by design: never installs, never modifies
# the repo, never reaches the network.
#
# Usage: run_validation.sh <repo_root> <command_id> <command_string>
#
# Emits a single-line record to stdout:
#   <command_id>::<status>::<exit_code>::<duration_ms>
# Captured output is written to:
#   /data/.openclaw/workspace/tasks/<TASK_ID>/validation/logs/<command_id>.log
# (TASK_ID is read from $TASK_ID env var if set, else the current dir
# is used as a fallback only when explicitly enabled by the caller.)
#
# Exit codes:
#   0  command ran and succeeded
#   1  command ran and failed
#   2  command not executable / not present on PATH
#  64  bad usage
#  66  bad repo_root

set -uo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: $0 <repo_root> <command_id> <command_string...>" >&2
  exit 64
fi

REPO_ROOT="$1"
shift
CMD_ID="$1"
shift
CMD_STRING="$*"

if [[ ! -d "$REPO_ROOT" ]]; then
  echo "error: repo_root not a directory: $REPO_ROOT" >&2
  exit 66
fi

# Refuse to install. The whitelist is enforced by the caller; this is a
# belt-and-suspenders check for the most common installers.
case "$CMD_STRING" in
  *"npm install"*|*"yarn add"*|*"pnpm add"*|*"pip install"*|*"pip3 install"*|\
  *"go mod tidy"*|*"go get "*|*"cargo add"*|*"dotnet add "*|*"dotnet restore"*)
    echo "refused: installer command not allowed: $CMD_STRING" >&2
    printf '%s::refused::2::0\n' "$CMD_ID"
    exit 1
    ;;
esac

# Log destination. Prefer TASK_ID from env; fall back to ./validation-logs.
LOG_DIR=""
if [[ -n "${TASK_ID:-}" ]]; then
  LOG_DIR="/data/.openclaw/workspace/tasks/${TASK_ID}/validation/logs"
  mkdir -p "$LOG_DIR" 2>/dev/null || true
fi
LOG_FILE="${LOG_DIR:+${LOG_DIR}/}${CMD_ID}.log"
: > "$LOG_FILE" 2>/dev/null || LOG_FILE="/dev/null"

# Execute from the repo root, capture timings.
start_ns=$(date +%s%N)
set +e
(
  cd "$REPO_ROOT" && bash -c "$CMD_STRING"
) >"$LOG_FILE" 2>&1
rc=$?
end_ns=$(date +%s%N)

dur_ms=$(( (end_ns - start_ns) / 1000000 ))

if [[ $rc -eq 0 ]]; then
  status="passed"
else
  status="failed"
fi

printf '%s::%s::%d::%d\n' "$CMD_ID" "$status" "$rc" "$dur_ms"
exit $rc
