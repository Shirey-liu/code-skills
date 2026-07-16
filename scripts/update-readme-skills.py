#!/usr/bin/env python3
"""从各 */SKILL.md 的 name / description 重写 README「技能一览」表（只替换表格，不动其它章节）。"""
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
    """优先保留中文说明：去掉 Use when 英文段，再按句号截断到合适长度。"""
    # 若含中文，截到 Use when 之前
    cut = re.split(r"\s+Use when\b", desc, maxsplit=1, flags=re.I)[0].strip()
    # 过长则取前两句（。/.）
    parts = re.split(r"(?<=[。.])\s*", cut)
    parts = [p for p in parts if p]
    if len(parts) >= 2:
        return (parts[0] + parts[1]).strip()
    return cut


def build_table() -> str:
    rows: list[tuple[str, str, str]] = []
    for skill_md in sorted(ROOT.glob("*/SKILL.md")):
        meta = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        name = meta.get("name") or skill_md.parent.name
        brief = brief_desc(meta.get("description", "")) or "（待补充 description）"
        rows.append((name, skill_md.parent.name, brief))
    lines = ["| 技能 | 主要做什么 |", "|------|------------|"]
    for name, dirname, brief in rows:
        lines.append(f"| [{name}](./{dirname}/) | {brief} |")
    return "\n".join(lines)


def main() -> None:
    text = README.read_text(encoding="utf-8")
    table = build_table()
    # 只替换「技能一览」标题后、下一个 ## 之前的表格块
    pattern = re.compile(
        r"(## 技能一览\n\n)(\| 技能 \| 主要做什么 \|\n\|------\|------------\|\n(?:\|.*\|\n)*)",
        re.M,
    )
    m = pattern.search(text)
    if not m:
        raise SystemExit("README 中未找到「技能一览」标准表格，请手动检查格式")
    new_text = text[: m.start(2)] + table + "\n" + text[m.end(2) :]
    README.write_text(new_text, encoding="utf-8")
    print(f"Updated skill table in {README}")
    print(table)


if __name__ == "__main__":
    main()
