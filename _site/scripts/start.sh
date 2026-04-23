#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT_DIR/.jekyll.pid"
LOG_FILE="$ROOT_DIR/.jekyll.log"
LOCAL_CONFIG="$ROOT_DIR/.tmp_local_config.yml"
URL="http://127.0.0.1:4000/rachel-new-website/"

cd "$ROOT_DIR"

if [[ -f "$PID_FILE" ]]; then
  existing_pid="$(cat "$PID_FILE")"
  if kill -0 "$existing_pid" 2>/dev/null; then
    echo "Jekyll is already running (PID $existing_pid)."
    echo "URL: $URL"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

mkdir -p "$ROOT_DIR/.gem" "$ROOT_DIR/vendor/bundle"

cat > "$LOCAL_CONFIG" <<'EOF'
exclude:
  - Gemfile
  - Gemfile.lock
  - vendor
  - .gem
EOF

export GEM_HOME="$ROOT_DIR/.gem"
export GEM_PATH="$ROOT_DIR/.gem"
export PATH="$ROOT_DIR/.gem/bin:$PATH"

if ! gem list -i bundler -v 2.4.18 >/dev/null 2>&1; then
  gem install bundler:2.4.18 --no-document
fi

bundle _2.4.18_ config set path vendor/bundle >/dev/null
bundle _2.4.18_ install

nohup bundle _2.4.18_ exec jekyll serve --config _config.yml,.tmp_local_config.yml > "$LOG_FILE" 2>&1 &
jekyll_pid=$!
echo "$jekyll_pid" > "$PID_FILE"

sleep 1
if ! kill -0 "$jekyll_pid" 2>/dev/null; then
  echo "Jekyll failed to start. See $LOG_FILE for details."
  rm -f "$PID_FILE"
  exit 1
fi

echo "Jekyll started (PID $jekyll_pid)."
echo "URL: $URL"
echo "Logs: $LOG_FILE"
