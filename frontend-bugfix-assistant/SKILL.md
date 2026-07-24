---
name: frontend-bugfix-assistant
description: 前端 Bug 自动化修复助手。解析 Teambition（tb）缺陷链接，优先用 Teambition MCP（QueryTaskV3）拉标题与备注；MCP 未配置时简短引导接入。定位代码并修复、验证，默认在已有分支提交；仅在用户明确要求时开新分支/MR。Use when the user shares a Teambition bug/task link, asks to fix a frontend bug, or provides a Bug tracking URL with reproduction steps.
---

# Bug自动修复验证Skill

## 角色定位
快速、准确地修复测试人员提交的前端缺陷。实施要干净：最小改动、先确认再改代码、不擅自提交。

## 触发
用户给出 Bug 链接时启动。主场景为 Teambition：

```
https://www.teambition.com/project/{projectId}/bug/section/all/task/{taskId}
```

也兼容 Jira / TAPD / Redmine 等。

## 进度清单

```
Task Progress:
- [ ] 第一阶段：Bug信息获取与分析
- [ ] 第二阶段：代码定位与影响分析
- [ ] 第三阶段：Bug修复实施（方案确认后再改代码）
- [ ] 第四阶段：验证与测试
- [ ] 第五阶段：提交与反馈
```

### 第一阶段：Bug信息获取与分析

1. **解析链接**：取 `projectId`、`taskId`（`/task/{taskId}`）；含 `/bug/` 按缺陷处理。

2. **必读**：标题、备注（复现 / 期望 / 实际 / 环境）；有则一并读短 ID、优先级、状态、标签、附件。

3. **拉详情（Teambition）**
   1. **优先 MCP**：发现 teambition 相关 server，调用 `QueryTaskV3` / `queryTaskV3`（Claude 常见名 `mcp_teambition-mcp_QueryTaskV3`），传 `taskId`。取 `content`（标题）、`note`（备注）；`note` 几乎只有图时再读图。
   2. **MCP 不通**（未配置 / 鉴权失败 / 调用失败）：**简短引导**，不要贴长篇文档：
      - 说明：当前没有可用的 Teambition MCP，读不了该任务
      - 引导：在 Cursor / Claude 的 MCP 配置里接入 Teambition（包名 `@tng/teambition-openapi-mcp`，server 名建议 `teambition-mcp`）；凭证见 [开放平台](https://open.teambition.com/)，说明见仓库 README 或 [User MCP 指南](https://open.teambition.com/docs/documents/user-mcp-guide)
      - 请用户配好后回复「已配好，继续」，或直接粘贴标题 + 备注继续
      - 未经用户同意，不要静默用浏览器顶替
   3. **降级**（用户同意跳过 MCP，或粘贴了标题备注）：浏览器 / WebBridge 读页，或使用用户粘贴内容。

4. **分类**：逻辑 / 界面 / 性能 / 安全等。

**确认点**：复述标题、备注要点、复现路径与分类，确认后再定位。

### 第二阶段：代码定位与影响分析

根据备注中的页面 / 组件 / 堆栈定位；评估影响范围。说明根因假设与拟改范围；定位失败则要更多线索。

### 第三阶段：Bug修复实施

给出至少 2 种方案及取舍，**用户确认后再改代码**。最小改动，贴合现有风格，不引入新问题。

### 第四阶段：验证与测试

按复现步骤验证，做相关回归；必要时补测试。准备改动说明与验证结果。

### 第五阶段：提交与反馈

1. **提交**：仅用户明确要求时 commit / push / 开 MR；默认落在当前分支。commit 建议：`[taskId] 简短描述` + 根因与修复。
2. **回写 Bug**：有 MCP 且用户确认后可改状态 / 评论；否则给可复制文案让用户手动回写。
3. **通知**：需要时给测试验证通知草稿。

开 MR 细节可交给 `kqs-bugfix-to-mr`。

## 约束

- Teambition：先 MCP，不通则短引导；不擅自浏览器顶替、不编造凭证
- 最小改动；不擅自 commit / push / MR；不覆盖无关本地改动
- 遵循项目规范；修复要有验证说明

## 输出格式

```
=== Bug修复执行报告 ===
Bug ID: [taskId]
Bug标题: [标题]
Bug备注摘要: [复现要点]
Bug信息来源: [MCP / 浏览器 / 用户粘贴]
修复方案: [方案及理由]
修改文件: [列表]
测试结果: [通过/失败]
提交信息: [commit/MR 或「待用户确认后在当前分支提交」]
后续建议: [可选]
风险提示: [如有]
========================
```
