#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT_DIR/.jekyll.pid"

cd "$ROOT_DIR"

if [[ ! -f "$PID_FILE" ]]; then
  echo "No PID file found at $PID_FILE."
  echo "If Jekyll is still running, stop it manually (example: lsof -ti tcp:4000 | xargs kill)."
  exit 0
fi

pid="$(cat "$PID_FILE")"

if ! kill -0 "$pid" 2>/dev/null; then
  echo "Process $pid is not running. Removing stale PID file."
  rm -f "$PID_FILE"
  exit 0
fi

kill "$pid"
for _ in {1..10}; do
  if ! kill -0 "$pid" 2>/dev/null; then
    rm -f "$PID_FILE"
    echo "Jekyll stopped."
    exit 0
  fi
  sleep 1
done

echo "Process did not stop gracefully; forcing kill."
kill -9 "$pid"
rm -f "$PID_FILE"
echo "Jekyll stopped."
