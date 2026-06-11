#!/usr/bin/env bash
# detect_project_stack.sh — read-only repo stack detection.
#
# Usage: detect_project_stack.sh <repo_root>
#
# Prints evidence lines in the form: <kind>::<value>::<source_file>
# to stdout. Exits 0 on success, non-zero only on bad args. Never modifies
# the filesystem and never reads environment secrets.

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

emit() { printf '%s::%s::%s\n' "$1" "$2" "$3"; }

# --- Java / JVM ---
[[ -f "$REPO_ROOT/pom.xml" ]] && emit "package_manager" "maven" "pom.xml"
[[ -f "$REPO_ROOT/build.gradle" || -f "$REPO_ROOT/build.gradle.kts" ]] \
  && emit "package_manager" "gradle" "build.gradle"
[[ -f "$REPO_ROOT/mvnw" ]] && emit "wrapper" "maven" "mvnw"
[[ -f "$REPO_ROOT/gradlew" ]] && emit "wrapper" "gradle" "gradlew"
[[ -d "$REPO_ROOT/src/main/java" ]] && emit "source_dir" "java" "src/main/java"
[[ -d "$REPO_ROOT/src/test/java" ]] && emit "test_dir" "java" "src/test/java"
if grep -q -E "spring-boot|springframework" "$REPO_ROOT/pom.xml" 2>/dev/null; then
  emit "framework" "spring-boot" "pom.xml"
fi
if grep -q -E "spring-boot|springframework" "$REPO_ROOT/build.gradle" 2>/dev/null; then
  emit "framework" "spring-boot" "build.gradle"
fi

# --- Node / JS / TS ---
[[ -f "$REPO_ROOT/package.json" ]] && {
  emit "package_manager" "npm" "package.json"
  # Yarn/pnpm detected by lockfile presence, not package.json.
  [[ -f "$REPO_ROOT/yarn.lock" ]] && emit "package_manager" "yarn" "yarn.lock"
  [[ -f "$REPO_ROOT/pnpm-lock.yaml" ]] && emit "package_manager" "pnpm" "pnpm-lock.yaml"
  [[ -f "$REPO_ROOT/package-lock.json" ]] && emit "package_manager_alt" "npm" "package-lock.json"
}
[[ -d "$REPO_ROOT/src" && -d "$REPO_ROOT/node_modules" || -f "$REPO_ROOT/package.json" ]] \
  && [[ -d "$REPO_ROOT/src" ]] && emit "source_dir" "node" "src"
[[ -d "$REPO_ROOT/test" || -d "$REPO_ROOT/tests" || -d "$REPO_ROOT/__tests__" ]] \
  && emit "test_dir" "node" "test"
[[ -f "$REPO_ROOT/tsconfig.json" ]] && emit "language" "typescript" "tsconfig.json"
[[ -f "$REPO_ROOT/jest.config.js" || -f "$REPO_ROOT/jest.config.ts" \
   || -f "$REPO_ROOT/jest.config.json" ]] && emit "framework" "jest" "jest.config"
[[ -f "$REPO_ROOT/vitest.config.js" || -f "$REPO_ROOT/vitest.config.ts" ]] \
  && emit "framework" "vitest" "vitest.config"
[[ -f "$REPO_ROOT/pnpm-workspace.yaml" ]] && emit "workspace" "pnpm" "pnpm-workspace.yaml"
[[ -f "$REPO_ROOT/lerna.json" ]] && emit "workspace" "lerna" "lerna.json"
[[ -f "$REPO_ROOT/nx.json" ]] && emit "workspace" "nx" "nx.json"
[[ -f "$REPO_ROOT/turbo.json" ]] && emit "workspace" "turborepo" "turbo.json"

# --- Python ---
[[ -f "$REPO_ROOT/requirements.txt" ]] && emit "package_manager" "pip" "requirements.txt"
[[ -f "$REPO_ROOT/pyproject.toml" ]] && emit "package_manager" "pyproject" "pyproject.toml"
[[ -f "$REPO_ROOT/Pipfile" ]] && emit "package_manager" "pipenv" "Pipfile"
[[ -f "$REPO_ROOT/poetry.lock" ]] && emit "package_manager" "poetry" "poetry.lock"
[[ -f "$REPO_ROOT/uv.lock" ]] && emit "package_manager" "uv" "uv.lock"
[[ -d "$REPO_ROOT/src" && -f "$REPO_ROOT/pyproject.toml" ]] && emit "source_dir" "python" "src"
[[ -d "$REPO_ROOT/tests" || -d "$REPO_ROOT/test" ]] && emit "test_dir" "python" "tests"
[[ -f "$REPO_ROOT/pytest.ini" || -f "$REPO_ROOT/pyproject.toml" ]] \
  && grep -q "pytest" "$REPO_ROOT/pyproject.toml" 2>/dev/null \
  && emit "framework" "pytest" "pyproject.toml"
if [[ -f "$REPO_ROOT/requirements.txt" ]]; then
  grep -q -i "fastapi" "$REPO_ROOT/requirements.txt" 2>/dev/null \
    && emit "framework" "fastapi" "requirements.txt"
  grep -q -i "django" "$REPO_ROOT/requirements.txt" 2>/dev/null \
    && emit "framework" "django" "requirements.txt"
fi

# --- Go ---
[[ -f "$REPO_ROOT/go.mod" ]] && emit "package_manager" "go-modules" "go.mod"
[[ -d "$REPO_ROOT/cmd" ]] && emit "source_dir" "go" "cmd"
[[ -d "$REPO_ROOT/internal" ]] && emit "source_dir" "go" "internal"
[[ -d "$REPO_ROOT/pkg" ]] && emit "source_dir" "go" "pkg"

# --- Rust ---
[[ -f "$REPO_ROOT/Cargo.toml" ]] && emit "package_manager" "cargo" "Cargo.toml"
[[ -d "$REPO_ROOT/src" && -f "$REPO_ROOT/Cargo.toml" ]] && emit "source_dir" "rust" "src"
[[ -d "$REPO_ROOT/tests" && -f "$REPO_ROOT/Cargo.toml" ]] && emit "test_dir" "rust" "tests"

# --- .NET ---
[[ -f "$REPO_ROOT/global.json" ]] && emit "package_manager" "dotnet-sdk" "global.json"
shopt -s nullglob
for sln in "$REPO_ROOT"/*.sln; do
  [[ -f "$sln" ]] && emit "solution" "dotnet" "$(basename "$sln")"
done
shopt -u nullglob

# --- Docker / IaC / CI ---
[[ -f "$REPO_ROOT/Dockerfile" ]] && emit "container" "docker" "Dockerfile"
[[ -f "$REPO_ROOT/docker-compose.yml" || -f "$REPO_ROOT/docker-compose.yaml" \
   || -f "$REPO_ROOT/compose.yml" || -f "$REPO_ROOT/compose.yaml" ]] \
  && emit "container" "compose" "docker-compose.yml"
[[ -d "$REPO_ROOT/.github/workflows" ]] && emit "ci" "github-actions" ".github/workflows"
[[ -d "$REPO_ROOT/.gitlab" ]] && emit "ci" "gitlab-ci" ".gitlab"
[[ -f "$REPO_ROOT/.circleci/config.yml" ]] && emit "ci" "circleci" ".circleci/config.yml"
[[ -f "$REPO_ROOT/Jenkinsfile" ]] && emit "ci" "jenkins" "Jenkinsfile"

# --- IaC ---
[[ -d "$REPO_ROOT/terraform" || -f "$REPO_ROOT/main.tf" ]] && emit "iac" "terraform" "main.tf"
[[ -d "$REPO_ROOT/k8s" || -d "$REPO_ROOT/kubernetes" \
   || -f "$REPO_ROOT/kustomization.yaml" ]] && emit "iac" "kubernetes" "k8s/"
[[ -f "$REPO_ROOT/ansible.cfg" || -d "$REPO_ROOT/roles" ]] && emit "iac" "ansible" "ansible.cfg"
[[ -f "$REPO_ROOT/Pulumi.yaml" ]] && emit "iac" "pulumi" "Pulumi.yaml"

# --- Migrations ---
[[ -d "$REPO_ROOT/migrations" || -d "$REPO_ROOT/db/migrations" \
   || -d "$REPO_ROOT/prisma/migrations" || -d "$REPO_ROOT/alembic/versions" ]] \
  && emit "migrations" "present" "migrations/"

# --- Risk zones (filenames commonly associated with secrets/auth) ---
shopt -s nullglob
for f in "$REPO_ROOT"/.env "$REPO_ROOT"/.env.* "$REPO_ROOT"/secrets.* \
         "$REPO_ROOT"/id_rsa "$REPO_ROOT"/id_rsa.pub \
         "$REPO_ROOT"/credentials.json "$REPO_ROOT"/service-account*.json; do
  [[ -f "$f" ]] && emit "risk" "secrets_file_present" "$(basename "$f")"
done
shopt -u nullglob
[[ -d "$REPO_ROOT/auth" || -d "$REPO_ROOT/src/auth" || -d "$REPO_ROOT/app/auth" ]] \
  && emit "risk" "auth_module" "auth/"

exit 0
