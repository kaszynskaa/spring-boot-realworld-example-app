#!/usr/bin/env python3
"""PreToolUse hook — blocks file writes that contain leaked secrets."""
import json
import re
import sys

data = json.load(sys.stdin)

if data.get("tool_name") not in ("Write", "Edit"):
    sys.exit(0)

tool_input = data.get("tool_input", {})
# Write uses 'content', Edit uses 'new_string'
content = tool_input.get("content") or tool_input.get("new_string") or ""
file_path = tool_input.get("file_path", "")

# Never block test fixtures or example/placeholder files
SAFE_PATHS = (".test.", "test/", "example", "placeholder", ".sample", ".example")
if any(p in file_path.lower() for p in SAFE_PATHS):
    sys.exit(0)

SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{20,}', "API key"),
    (r'(?i)password\s*[=:]\s*["\'][^"\'${]{6,}["\']', "hardcoded password"),
    (r'(?i)secret\s*[=:]\s*["\'][^"\'${]{8,}["\']', "hardcoded secret"),
    (r'(?i)(access[_-]?token|auth[_-]?token)\s*[=:]\s*["\']?[A-Za-z0-9_\-\.]{20,}', "access token"),
    (r'(?i)aws[_-]?access[_-]?key[_-]?id\s*[=:]\s*["\']?[A-Z0-9]{20}', "AWS access key ID"),
    (r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\']?[A-Za-z0-9/+=]{40}', "AWS secret key"),
    (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', "private key"),
    (r'ghp_[A-Za-z0-9]{36}', "GitHub personal access token"),
    (r'sk-[A-Za-z0-9]{48}', "OpenAI API key"),
    (r'(?i)bearer\s+[A-Za-z0-9_\-\.]{40,}', "bearer token"),
]

findings = []
for pattern, label in SECRET_PATTERNS:
    if re.search(pattern, content):
        findings.append(label)

if findings:
    print(
        json.dumps({
            "decision": "block",
            "reason": (
                f"Potential secret(s) detected in {file_path}: {', '.join(findings)}.\n"
                "Remove hardcoded credentials before writing. "
                "Use environment variables or application.properties with ${VAR} substitution."
            ),
        })
    )
    sys.exit(2)

sys.exit(0)
