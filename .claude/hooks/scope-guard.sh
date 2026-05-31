#!/usr/bin/env bash
# PreToolUse hook — blocks Write/Edit outside allowed project directories.
set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(python3 -c "import json,sys; print(json.loads(sys.argv[1]).get('tool_name',''))" "$INPUT" 2>/dev/null || echo "")

if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
    exit 0
fi

FILE_PATH=$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); print(d.get('tool_input',{}).get('file_path',''))" "$INPUT" 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

# Resolve project root (two levels up from this script: hooks/ → .claude/ → project/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Strip absolute project root prefix so we can match relative paths
REL_PATH="${FILE_PATH#"$PROJECT_ROOT"/}"

# Allowed path prefixes for AI-assisted edits
ALLOWED=(
    "src/"
    ".claude/"
    "docs/"
    "CLAUDE.md"
    "README.md"
    "workflow-analysis.md"
    "REPORT.md"
    "build.gradle"
)

for prefix in "${ALLOWED[@]}"; do
    if [[ "$REL_PATH" == "$prefix"* || "$FILE_PATH" == "$prefix"* ]]; then
        exit 0
    fi
done

python3 -c "
import json, sys
print(json.dumps({
    'decision': 'block',
    'reason': (
        'File \"' + sys.argv[1] + '\" is outside the allowed edit scope.\n'
        'Allowed directories: src/, .claude/, docs/\n'
        'Allowed files: CLAUDE.md, README.md, REPORT.md, build.gradle\n'
        'If you need to edit this file, do it manually.'
    )
}))
" "$REL_PATH"
exit 2
