#!/usr/bin/env python3
"""Stop hook — generates a session summary report from audit logs."""
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

data = json.load(sys.stdin)
session_id = data.get("session_id", "unknown")

audit_dir = os.path.join(os.path.dirname(__file__), "..", "audit")
audit_file = os.path.join(audit_dir, "audit.jsonl")
prompts_file = os.path.join(audit_dir, "prompts.jsonl")

def read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        lines = []
        for line in f:
            line = line.strip()
            if line:
                try:
                    lines.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return lines

actions = [e for e in read_jsonl(audit_file) if e.get("session_id") == session_id]
prompts = [e for e in read_jsonl(prompts_file) if e.get("session_id") == session_id]

tool_counts = Counter(e.get("tool_name", "unknown") for e in actions)
timestamps = [e["timestamp"] for e in actions if "timestamp" in e]
start = min(timestamps) if timestamps else "unknown"
end = max(timestamps) if timestamps else "unknown"

report = {
    "session_id": session_id,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "summary": {
        "session_start": start,
        "session_end": end,
        "total_actions": len(actions),
        "total_prompts": len(prompts),
        "tool_usage": dict(tool_counts.most_common()),
    },
    "prompts": [p.get("prompt", "")[:200] for p in prompts],
}

report_path = os.path.join(audit_dir, f"session-{session_id[:8]}.json")
os.makedirs(audit_dir, exist_ok=True)
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print(f"Session summary written to {report_path}")
print(f"  Actions: {len(actions)} | Prompts: {len(prompts)} | Tools: {dict(tool_counts.most_common(5))}")

sys.exit(0)
