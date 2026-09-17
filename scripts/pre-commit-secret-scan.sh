#!/usr/bin/env bash
# zenOS pre-commit secret scan (Track F).
# Lightweight pattern check on the staged diff, then the Python scanner.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DIFF="$(git diff --cached)"
if [ -z "$DIFF" ]; then
  exit 0
fi

# Epic F-02 baseline patterns. The Python scanner is stricter (full token,
# not just the ghp_ prefix) so docs can mention token formats.
if echo "$DIFF" | grep -E '(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-or-v1-[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|Bearer [A-Za-z0-9]{20,})' >/dev/null; then
  echo "zenOS secret scan: staged diff matches a credential pattern." >&2
  echo "Rotate the leaked token before anything else — docs/guides/SECRET_INCIDENT_RESPONSE.md" >&2
  PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -m zen.auth.secret_scan --staged || true
  exit 1
fi

PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" python3 -m zen.auth.secret_scan --staged
