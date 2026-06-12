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
#
# Per-command `status` values (printed as the 2nd field of the
# single-line record):
#   passed         - exit 0, meaningful work done
#   failed         - exit != 0
#   trivial_pass   - exit 0 but a "no work done" pattern was detected
#                    (e.g. "No tests to run" + "BUILD SUCCESS" for Maven)
#   refused        - the runner refused to execute (installer detected)
#   skipped        - the orchestrator chose to skip the command

set -uo pipefail

# ---- trivial-pass detection ----
# Args: $1 = log file path. Echoes "trivial" if matched, returns 0 on
# match, 1 otherwise. Patterns detected (one match is enough):
#   * Maven: log contains both "No tests to run" and "BUILD SUCCESS"
#   * Maven: log contains both "No sources to compile" and "BUILD SUCCESS"
#   * Gradle: log contains "BUILD SUCCESSFUL" but no "test" or "spec" line
#   * pytest: log contains "0 tests collected" or "collected 0 items"
#   * pytest: log summary line "0 passed" (and no failures)
#   * Generic: log is < 100 bytes AND no recognizable success pattern
detect_trivial_pass() {
  local logf="$1"
  local log_content
  log_content=$(cat "$logf" 2>/dev/null || true)
  [[ -z "$log_content" ]] && return 1

  # Maven: BUILD SUCCESS with no real test/source activity
  if echo "$log_content" | grep -q "BUILD SUCCESS"; then
    if echo "$log_content" | grep -q "No tests to run" \
       || echo "$log_content" | grep -q "No sources to compile"; then
      echo "trivial" && return 0
    fi
  fi

  # Gradle: BUILD SUCCESSFUL with no test references
  if echo "$log_content" | grep -q "BUILD SUCCESSFUL"; then
    if ! echo "$log_content" | grep -qiE "test|spec"; then
      echo "trivial" && return 0
    fi
  fi

  # pytest: zero tests collected / zero items / zero passed
  if echo "$log_content" | grep -qE "(0 tests collected|collected 0 items|=+ 0 passed)"; then
    echo "trivial" && return 0
  fi

  # Generic: very short log with no test-like content
  local log_len=${#log_content}
  if (( log_len < 100 )) && ! echo "$log_content" | grep -qiE "test|spec|pass|fail|build|error"; then
    echo "trivial" && return 0
  fi

  return 1
}


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

# Detect "trivial pass": exit 0 but no meaningful work was done. A test
# command that exits 0 with "No tests to run" is masking a real failure
# (e.g. orphaned build.gradle, missing test sources). Downgrade the
# status to `trivial_pass` and the report's overall outcome becomes
# `partial` (handled by the orchestrator).
if [[ $rc -eq 0 ]]; then
  status="passed"
  if [[ -r "$LOG_FILE" ]] && detect_trivial_pass "$LOG_FILE"; then
    status="trivial_pass"
  fi
else
  status="failed"
fi

printf '%s::%s::%d::%d\n' "$CMD_ID" "$status" "$rc" "$dur_ms"
exit $rc
