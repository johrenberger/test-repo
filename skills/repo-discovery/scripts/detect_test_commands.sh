#!/usr/bin/env bash
# detect_test_commands.sh — derive validation commands from repo evidence.
#
# Usage: detect_test_commands.sh <repo_root>
#
# Emits: <command_id>::<command_string>::<source_file>::<confidence>
# Confidence is one of: high (manifest declares it), medium (convention),
# low (inferred). Read-only.

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <repo_root>" >&2
  exit 64
fi

REPO_ROOT="$1"

if [[ ! -d "$REPO_ROOT" ]]; then
  echo "error: repo_root not a directory: $REPO_ROOT" >&2
  exit 66
fi

emit() { printf '%s::%s::%s::%s\n' "$1" "$2" "$3" "$4"; }

# Helper: read a JSON-like script block from package.json without requiring jq.
pkg_script() {
  local name="$1"
  awk -v target="$name" '
    BEGIN { in_pkg=0; depth=0 }
    /"scripts"[[:space:]]*:/ { in_pkg=1; next }
    in_pkg && /}/ && depth==0 { in_pkg=0 }
    in_pkg {
      match($0, "[[:space:]]*\"" target "\"[[:space:]]*:[[:space:]]*\"[^\"]*\"")
      if (RSTART > 0) {
        s = substr($0, RSTART, RLENGTH)
        sub("^[^:]*:[[:space:]]*\"", "", s)
        sub("\"$", "", s)
        print s
        exit
      }
    }
  ' "$REPO_ROOT/package.json" 2>/dev/null
}

# --- Node ---
if [[ -f "$REPO_ROOT/package.json" ]]; then
  if s=$(pkg_script test);          then [[ -n "$s" ]] && emit "npm_test"     "npm test --if-present"      "package.json:test"     "high"; fi
  if s=$(pkg_script lint);          then [[ -n "$s" ]] && emit "npm_lint"     "npm run lint --if-present"  "package.json:lint"     "high"; fi
  if s=$(pkg_script typecheck) || s=$(pkg_script "type-check") || s=$(pkg_script tsc); then
    [[ -n "$s" ]] && emit "npm_typecheck" "npm run typecheck --if-present" "package.json:typecheck" "high"
  fi
  if s=$(pkg_script coverage) || s=$(pkg_script "test:coverage"); then
    [[ -n "$s" ]] && emit "npm_coverage" "npm run coverage --if-present" "package.json:coverage" "medium"
  fi
  case " " in
    *" yarn.lock "*) emit "yarn_test" "yarn test" "yarn.lock" "medium" ;;
  esac
  case " " in
    *" pnpm-lock.yaml "*) emit "pnpm_test" "pnpm test" "pnpm-lock.yaml" "medium" ;;
  esac
fi

# --- Java / Maven / Gradle ---
if [[ -f "$REPO_ROOT/mvnw" ]]; then
  emit "mvn_test" "./mvnw test" "mvnw" "high"
elif [[ -f "$REPO_ROOT/pom.xml" ]]; then
  emit "mvn_test" "mvn test" "pom.xml" "medium"
fi
if [[ -f "$REPO_ROOT/gradlew" ]]; then
  emit "gradle_test" "./gradlew test" "gradlew" "high"
elif [[ -f "$REPO_ROOT/build.gradle" || -f "$REPO_ROOT/build.gradle.kts" ]]; then
  emit "gradle_test" "gradle test" "build.gradle" "medium"
fi

# --- Python ---
# Finding 5 (A1 exercise): pytest.ini is a high-confidence source
# because it explicitly configures pytest. Demote to medium only
# if there's a tests/ or test/ directory with no pytest.ini.
if [[ -f "$REPO_ROOT/pyproject.toml" ]] && grep -q "pytest" "$REPO_ROOT/pyproject.toml" 2>/dev/null; then
  emit "pytest" "pytest" "pyproject.toml" "high"
elif [[ -f "$REPO_ROOT/pytest.ini" ]]; then
  emit "pytest" "pytest" "pytest.ini" "high"
elif [[ -f "$REPO_ROOT/conftest.py" \
      || -d "$REPO_ROOT/tests" || -d "$REPO_ROOT/test" ]]; then
  emit "pytest" "pytest" "conftest.py" "medium"
fi

# --- Go ---
[[ -f "$REPO_ROOT/go.mod" ]] && emit "go_test" "go test ./..." "go.mod" "high"

# --- Rust ---
[[ -f "$REPO_ROOT/Cargo.toml" ]] && emit "cargo_test" "cargo test" "Cargo.toml" "high"

# --- .NET ---
shopt -s nullglob
for sln in "$REPO_ROOT"/*.sln; do
  [[ -f "$sln" ]] && emit "dotnet_test" "dotnet test" "$(basename "$sln")" "high" && break
done
shopt -u nullglob

# --- CI cross-check (informational only) ---
[[ -d "$REPO_ROOT/.github/workflows" ]] \
  && emit "ci_workflows" "present" ".github/workflows" "high"

exit 0
