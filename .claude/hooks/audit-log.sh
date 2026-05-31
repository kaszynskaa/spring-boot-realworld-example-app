#!/usr/bin/env bash
# PostToolUse hook — appends every tool action to .claude/audit/audit.jsonl.
set -euo pipefail

INPUT=$(cat)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_DIR="$SCRIPT_DIR/../audit"
mkdir -p "$AUDIT_DIR"

python3 - "$INPUT" << 'PYEOF'
import json, sys, os
from datetime import datetime, timezone

raw = sys.argv[1]
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    sys.exit(0)

tool_input = data.get("tool_input", {})

# Summarise large payloads to keep log readable
def summarise(obj, limit=300):
    s = json.dumps(obj) if not isinstance(obj, str) else obj
    return s[:limit] + ("…" if len(s) > limit else "")

entry = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "session_id": data.get("session_id", "unknown"),
    "event": "PostToolUse",
    "tool_name": data.get("tool_name", "unknown"),
    "tool_input_summary": summarise(tool_input),
    "tool_response_summary": summarise(data.get("tool_response", "")),
}

audit_path = os.path.join(os.path.dirname(sys.argv[0]) if len(sys.argv) > 0 else ".", "../audit/audit.jsonl")
# Use the script-relative path computed in bash
audit_file = os.environ.get("AUDIT_FILE", os.path.join(os.path.dirname(__file__), "../audit/audit.jsonl"))
os.makedirs(os.path.dirname(audit_file), exist_ok=True)

with open(audit_file, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")

PYEOF

exit 0
