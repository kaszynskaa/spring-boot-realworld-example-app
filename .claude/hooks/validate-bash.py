#!/usr/bin/env python3
"""PreToolUse hook — blocks dangerous Bash commands."""
import json
import re
import sys

data = json.load(sys.stdin)

if data.get("tool_name") != "Bash":
    sys.exit(0)

command = data.get("tool_input", {}).get("command", "")

DANGEROUS = [
    (r"\brm\s+(-\w*f\w*|-\w*r\w*){1,2}\s", "recursive/force deletion (rm -rf)"),
    (r"\brm\s+--force\b", "force deletion (rm --force)"),
    (r"(?i)\bDROP\s+TABLE\b", "SQL DROP TABLE"),
    (r"(?i)\bDROP\s+DATABASE\b", "SQL DROP DATABASE"),
    (r"(?i)\bTRUNCATE\s+TABLE\b", "SQL TRUNCATE TABLE"),
    (r"git\s+push\b.*--force\b", "force-push (git push --force)"),
    (r"git\s+push\b.*\s-f\b", "force-push (git push -f)"),
    (r"git\s+reset\s+--hard\b", "hard git reset"),
    (r"git\s+checkout\s+--\s", "destructive git checkout"),
    (r"chmod\s+777\b", "insecure chmod 777"),
    (r">\s*/etc/", "write to /etc/"),
    (r"\bdd\s+if=", "raw disk write (dd)"),
    (r"\bmkfs\b", "filesystem format (mkfs)"),
    (r":\s*\(\s*\)\s*\{.*:\s*\|", "fork bomb"),
    (r"curl\b.*\|\s*(ba)?sh\b", "piping curl to shell"),
    (r"wget\b.*\|\s*(ba)?sh\b", "piping wget to shell"),
]

for pattern, description in DANGEROUS:
    if re.search(pattern, command, re.IGNORECASE):
        print(
            json.dumps({
                "decision": "block",
                "reason": (
                    f"Blocked: {description} detected.\n"
                    f"Command: {command[:120]}\n"
                    "If this is intentional, run the command manually in a terminal."
                ),
            })
        )
        sys.exit(2)

sys.exit(0)
