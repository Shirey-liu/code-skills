# code-skills

个人 Cursor Agent Skills 仓库。克隆后按需软链到 `~/.cursor/skills/` 使用。

## 技能一览

| 技能 | 主要做什么 |
|------|------------|
| [figma-mcp-pixel-codegen](./figma-mcp-pixel-codegen/) | 通过 Figma MCP 将 Figma 设计转换为像素级精确的 UI 代码。 |
| [frontend-bugfix-assistant](./frontend-bugfix-assistant/) | 前端 Bug 自动化修复助手。解析 TAPD/Jira/Redmine 等缺陷链接，获取详情与复现步骤，定位代码并修复，验证后提交/创建 MR，输出执行报告。 |
| [mr-experience-summary](./mr-experience-summary/) | 任务/MR 完成后输出精炼复盘并写入 docs/retros/。总结任务名、做什么、解决了什么、注意点、冲突与坑。 |

## 安装（Cursor）

```bash
git clone https://github.com/Shirey-liu/code-skills.git ~/xkw/code/SKILL/code-skills

# 需要哪个链哪个
ln -s ~/xkw/code/SKILL/code-skills/frontend-bugfix-assistant ~/.cursor/skills/frontend-bugfix-assistant
ln -s ~/xkw/code/SKILL/code-skills/mr-experience-summary ~/.cursor/skills/mr-experience-summary
ln -s ~/xkw/code/SKILL/code-skills/figma-mcp-pixel-codegen ~/.cursor/skills/figma-mcp-pixel-codegen
```

已有同名目录时，先备份或删掉本地副本再链。

## 维护约定

**每次新增 / 修改 skill 并 push 前，必须更新本 README 的「技能一览」表**（名称 + 一句话用途，与 `SKILL.md` 的 `description` 中文部分对齐）。

可选：用脚本从各 skill 的 frontmatter 重生成表格：

```bash
./scripts/update-readme-skills.py
```

## 目录约定

```text
code-skills/
├── README.md
├── scripts/
│   └── update-readme-skills.py
├── <skill-name>/
│   └── SKILL.md
└── ...
```
