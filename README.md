# code-skills

个人 Cursor / Claude Agent Skills 仓库。克隆后按需软链到 `~/.cursor/skills/`（或 `~/.claude/skills/`）使用。

## 技能一览

| 技能 | 主要做什么 |
|------|------------|
| [figma-mcp-pixel-codegen](./figma-mcp-pixel-codegen/) | 通过 Figma MCP 将 Figma 设计转换为像素级精确的 UI 代码。 |
| [frontend-bugfix-assistant](./frontend-bugfix-assistant/) | 前端 Bug 自动化修复助手。解析 Teambition（tb）缺陷链接，优先用 Teambition MCP（QueryTaskV3）拉标题与备注；MCP 未配置时简短引导接入。 |
| [mr-experience-summary](./mr-experience-summary/) | 任务/MR 完成后输出精炼复盘并写入 docs/retros/。总结任务名、做什么、解决了什么、注意点、冲突与坑。 |

## 安装（Cursor）

```bash
git clone https://github.com/Shirey-liu/code-skills.git ~/xkw/code/SKILL/code-skills

# 需要哪个链哪个
ln -sfn ~/xkw/code/SKILL/code-skills/frontend-bugfix-assistant ~/.cursor/skills/frontend-bugfix-assistant
ln -sfn ~/xkw/code/SKILL/code-skills/mr-experience-summary ~/.cursor/skills/mr-experience-summary
ln -sfn ~/xkw/code/SKILL/code-skills/figma-mcp-pixel-codegen ~/.cursor/skills/figma-mcp-pixel-codegen
```

Claude Code 可同样链到 `~/.claude/skills/<skill-name>`。已有同名目录时，先备份或删掉本地副本再链。

## frontend-bugfix-assistant 与 Teambition MCP

拿到 tb 链接后会优先调 `QueryTaskV3`。未配置时 Agent 只做简短引导，详细配置放在这里：

```json
{
  "mcpServers": {
    "teambition-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "@tng/teambition-openapi-mcp",
        "mcp",
        "-a", "<your_app_id>",
        "-s", "<your_app_secret>",
        "-o", "<your_org_id>",
        "-b", "https://open.teambition.com/api"
      ]
    }
  }
}
```

写入 `~/.cursor/mcp.json`（或 Claude `mcpServers`），凭证见 [开放平台](https://open.teambition.com/)。

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
