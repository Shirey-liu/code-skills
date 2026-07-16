#!/usr/bin/env bash
# 从各 */SKILL.md 的 name / description 重写 README「技能一览」表。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
README="$ROOT/README.md"
TABLE_FILE="$(mktemp)"
OUT="$(mktemp)"
trap 'rm -f "$TABLE_FILE" "$OUT"' EXIT

{
  echo '| 技能 | 主要做什么 |'
  echo '|------|------------|'
  for skill_md in "$ROOT"/*/SKILL.md; do
    [ -f "$skill_md" ] || continue
    dir="$(basename "$(dirname "$skill_md")")"
    name="$(sed -n 's/^name:[[:space:]]*//p' "$skill_md" | head -1)"
    desc="$(sed -n 's/^description:[[:space:]]*//p' "$skill_md" | head -1)"
    brief="$(printf '%s\n' "$desc" | sed -E 's/[[:space:]]*Use when.*$//; s/[.。].*$//; s/"//g')"
    [ -n "$name" ] || name="$dir"
    printf '| [%s](./%s/) | %s |\n' "$name" "$dir" "$brief"
  done | LC_ALL=C sort
} > "$TABLE_FILE"

# 用 python 替换「技能一览」段落后的表格，避免 awk 多行字符串问题
python3 - "$README" "$TABLE_FILE" "$OUT" <<'PY'
import sys
readme, table_path, out_path = sys.argv[1:4]
table = open(table_path, encoding="utf-8").read().rstrip() + "\n"
lines = open(readme, encoding="utf-8").read().splitlines(True)
out = []
i = 0
while i < len(lines):
    out.append(lines[i])
    if lines[i].strip() == "## 技能一览":
        # 保留标题后空行
        i += 1
        if i < len(lines) and lines[i].strip() == "":
            out.append(lines[i])
            i += 1
        out.append(table)
        out.append("\n")
        # 跳过旧表格直到下一个 ##
        while i < len(lines) and not (lines[i].startswith("## ") and lines[i].strip() != "## 技能一览"):
            i += 1
        continue
    i += 1
open(out_path, "w", encoding="utf-8").writelines(out)
print(f"Updated skill table in {readme}")
PY

mv "$OUT" "$README"
trap - EXIT
rm -f "$TABLE_FILE"
