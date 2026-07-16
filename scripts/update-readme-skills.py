#!/usr/bin/env python3
"""从各 */SKILL.md 的 name / description 重写 README「技能一览」表。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"


def parse_frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        data[key.strip()] = val.strip().strip('"').strip("'")
    return data


def brief_desc(desc: str) -> str:
    desc = re.sub(r"\s*Use when.*$", "", desc, flags=re.I)
    # 取到第一个中文句号或英文句号
    m = re.split(r"[。.]", desc, maxsplit=1)
    return (m[0] if m else desc).strip()


def build_table() -> str:
    rows: list[tuple[str, str, str]] = []
    for skill_md in sorted(ROOT.glob("*/SKILL.md")):
        meta = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        name = meta.get("name") or skill_md.parent.name
        brief = brief_desc(meta.get("description", ""))
        rows.append((name, skill_md.parent.name, brief))
    lines = ["| 技能 | 主要做什么 |", "|------|------------|"]
    for name, dirname, brief in rows:
        lines.append(f"| [{name}](./{dirname}/) | {brief} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    text = README.read_text(encoding="utf-8")
    table = build_table()
    pattern = re.compile(
        r"(## 技能一览\n\n)(?:\| 技能 \| 主要做什么 \|.*?\n(?:\|.*\n)*)",
        re.S,
    )
    if not pattern.search(text):
        raise SystemExit("README 中未找到「技能一览」表格，请手动检查")
    new_text = pattern.sub(rf"\1{table}", text, count=1)
    README.write_text(new_text, encoding="utf-8")
    print(f"Updated skill table in {README}")


if __name__ == "__main__":
    main()
