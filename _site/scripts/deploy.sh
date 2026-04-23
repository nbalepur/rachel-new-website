#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEFAULT_MESSAGE="Update site content"

COMMIT_MESSAGE="${1:-$DEFAULT_MESSAGE}"
REMOTE_NAME="${2:-origin}"

cd "$ROOT_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This is not a git repository: $ROOT_DIR"
  exit 1
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ -z "$CURRENT_BRANCH" || "$CURRENT_BRANCH" == "HEAD" ]]; then
  echo "Unable to determine current branch. Please checkout a branch first."
  exit 1
fi

if ! git remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
  echo "Remote '$REMOTE_NAME' not found."
  exit 1
fi

# Stage everything except local runtime/build artifacts.
git add -A . \
  ':!vendor' ':!vendor/**' \
  ':!.gem' ':!.gem/**' \
  ':!_site' ':!_site/**' \
  ':!.jekyll.log' ':!.jekyll.pid' ':!.tmp_local_config.yml'

if git diff --cached --quiet; then
  echo "No changes to deploy."
  exit 0
fi

git commit -m "$COMMIT_MESSAGE"
git push "$REMOTE_NAME" "$CURRENT_BRANCH"

echo "Deployed: pushed '$CURRENT_BRANCH' to '$REMOTE_NAME'."
