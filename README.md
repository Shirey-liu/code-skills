# code-skills

个人 Cursor Agent Skills 仓库。克隆后按需软链到 `~/.cursor/skills/` 使用。

## 技能一览

| 技能 | 主要做什么 |
|------|------------|
| [frontend-bugfix-assistant](./frontend-bugfix-assistant/) | 拿到 TAPD/Jira 等 Bug 链接后，走分析→定位→修复→验证→报告；前端缺陷自动化修复助手 |
| [mr-experience-summary](./mr-experience-summary/) | 任务/MR 做完后说「总结这次」，输出精炼复盘并写入项目 `docs/retros/` |

## 安装（Cursor）

```bash
git clone https://github.com/Shirey-liu/code-skills.git ~/xkw/code/SKILL/code-skills

# 需要哪个链哪个
ln -s ~/xkw/code/SKILL/code-skills/frontend-bugfix-assistant ~/.cursor/skills/frontend-bugfix-assistant
ln -s ~/xkw/code/SKILL/code-skills/mr-experience-summary ~/.cursor/skills/mr-experience-summary
```

已有同名目录时，先备份或删掉本地副本再链。

## 维护约定

**每次新增 / 修改 skill 并 push 前，必须更新本 README 的「技能一览」表**（名称 + 一句话用途，与 `SKILL.md` 的 `description` 中文部分对齐）。

可选：用脚本从各 skill 的 frontmatter 重生成表格：

```bash
./scripts/update-readme-skills.sh
```

## 目录约定

```text
code-skills/
├── README.md
├── scripts/
│   └── update-readme-skills.sh
├── <skill-name>/
│   └── SKILL.md
└── ...
```
