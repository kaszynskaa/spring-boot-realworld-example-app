#!/usr/bin/env python3
"""UserPromptSubmit hook — logs every user prompt to .claude/audit/prompts.jsonl."""
import json
import os
import sys
from datetime import datetime, timezone

data = json.load(sys.stdin)

audit_dir = os.path.join(os.path.dirname(__file__), "..", "audit")
os.makedirs(audit_dir, exist_ok=True)

entry = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "session_id": data.get("session_id", "unknown"),
    "event": "UserPromptSubmit",
    "prompt": data.get("prompt", ""),
}

with open(os.path.join(audit_dir, "prompts.jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")

sys.exit(0)
