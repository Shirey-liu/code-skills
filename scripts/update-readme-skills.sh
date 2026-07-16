#!/usr/bin/env bash
# 从各 */SKILL.md 的 name / description 重写 README「技能一览」表。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
README="$ROOT/README.md"
TMP="$(mktemp)"

rows=()
for skill_md in "$ROOT"/*/SKILL.md; do
  [ -f "$skill_md" ] || continue
  dir="$(basename "$(dirname "$skill_md")")"
  name="$(sed -n 's/^name:[[:space:]]*//p' "$skill_md" | head -1)"
  desc="$(sed -n 's/^description:[[:space:]]*//p' "$skill_md" | head -1)"
  # 表格里只用中文首句（到第一个句号/Use when 之前）
  brief="$(printf '%s' "$desc" | sed -E 's/[.。].*$//; s/[[:space:]]*Use when.*$//; s/"//g')"
  [ -n "$name" ] || name="$dir"
  rows+=("| [${name}](./${dir}/) | ${brief} |")
done

IFS=$'\n'
sorted="$(printf '%s\n' "${rows[@]}" | LC_ALL=C sort)"

awk -v table="$sorted" '
  BEGIN { in_table=0 }
  /^## 技能一览$/ {
    print
    print ""
    print "| 技能 | 主要做什么 |"
    print "|------|------------|"
    n = split(table, lines, "\n")
    for (i = 1; i <= n; i++) if (lines[i] != "") print lines[i]
    in_table=1
    next
  }
  in_table && /^## / { in_table=0 }
  in_table && (/^\| / || /^$/ || /^\|[-| ]+\|/) { next }
  !in_table { print }
' "$README" > "$TMP"

mv "$TMP" "$README"
echo "Updated skill table in $README"
