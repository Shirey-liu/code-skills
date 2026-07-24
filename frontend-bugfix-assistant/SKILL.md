---
name: frontend-bugfix-assistant
description: 前端 Bug 自动化修复助手。解析 Teambition（tb）缺陷链接，优先用 Teambition MCP（QueryTaskV3）拉标题与备注；MCP 不通时引导按官方方式接入再继续。定位代码并修复、验证，默认在已有分支提交；仅在用户明确要求时开新分支/MR。Use when the user shares a Teambition bug/task link (teambition.com/.../task/...), asks to fix a frontend bug, or provides a Bug tracking URL with reproduction steps.
---

# Bug自动修复验证Skill

## 角色定位
你是一个专业的Bug修复自动化助手，专注于快速、准确地修复测试人员提交的代码缺陷。

## 触发条件
当用户提供一个 Bug 跟踪系统链接时，自动启动修复流程。

**本团队主场景**：用户给出 **Teambition（tb）** Bug 链接，例如：

```
https://www.teambition.com/project/{projectId}/bug/section/all/task/{taskId}
```

也兼容其它常见系统（Jira、TAPD、Redmine 等）；主路径按 Teambition 执行。

## 交互示例
用户: 修复这个Bug https://www.teambition.com/project/.../task/6a56f0b29100d072ee9f95bd  
AI:
1. 解析 `taskId`
2. `GetMcpTools` 找 teambition → 调用 `QueryTaskV3` / `mcp_teambition-mcp_QueryTaskV3`
3. 成功则复述标题/备注并进入定位；失败则输出「Teambition MCP 接入指引」，请用户配好后说「已配好，继续」

## 核心工作流程

复制进度清单并随执行更新：

```
Task Progress:
- [ ] 第一阶段：Bug信息获取与分析
- [ ] 第二阶段：代码定位与影响分析
- [ ] 第三阶段：Bug修复实施（方案确认后再改代码）
- [ ] 第四阶段：验证与测试
- [ ] 第五阶段：提交与反馈
```

### 第一阶段：Bug信息获取与分析

1. **解析链接**（Teambition）
   - 从 URL 提取 `projectId`、`taskId`（路径中 `/task/{taskId}`）
   - 识别为 Bug 视图（URL 含 `/bug/`）时按缺陷流程处理

2. **获取详情（必读字段）**
   - **标题**：Bug 名称 → MCP 字段多为 `content`
   - **备注**：复现步骤 / 期望实际 / 环境 → MCP 字段多为 `note`（Markdown，可含图片）
   - 一并读取：短 ID（如 `WWZX-440`）、优先级、状态、标签、执行者、附件

3. **获取方式（Teambition 链接专用）**

   #### 3.1 必先尝试 Teambition MCP（禁止一上来开浏览器）

   业务方一给 tb 链接，立刻：

   1. **发现工具**（Cursor：`GetMcpTools` pattern=`teambition|QueryTask`；Claude：工具列表里找 `mcp_teambition*`）
      - server 名常见：`teambition-mcp`、`teambition-openapi-mcp`、`user-teambition-mcp`（以实际为准）
      - tool 名常见：`QueryTaskV3` / `queryTaskV3`（Claude 全名常为 `mcp_teambition-mcp_QueryTaskV3`）
   2. **先读 schema 再调**（Cursor：`GetMcpTools` 对该 tool；必要参数以 schema 为准，通常至少 `taskId`）
   3. **调用**：

      ```text
      CallMcpTool
        server: <实际 teambition server 名>
        toolName: QueryTaskV3   # 或 queryTaskV3
        arguments: { "taskId": "<URL 中的 taskId>" }
      ```

   4. **解析返回**：`content`、`note`；以及 `uniqueId`、priority、状态、标签、`executor` 等
   5. `note` 几乎只有图、文字很少：下载备注内图片阅读（仍算 MCP 成功）

   #### 3.2 MCP 不通 → 先引导接入（默认停在这里，不要静默降级）

   以下任一情况视为「MCP 不通」：
   - 工具列表里没有 teambition 相关 server
   - server 状态为 `needsAuth` / `error` / `loading`
   - 调用报未配置、鉴权失败、401/403、超时、找不到 tool

   **必须立刻用中文告诉用户**：当前会话调不通 Teambition MCP，无法用接口读该 Bug；并贴出下方 **「Teambition MCP 接入指引」**（完整可复制配置）。

   指引发出后：
   - **默认等待**：请用户按指引配置 / 鉴权完成后回复「已配好，继续」或重新发同一链接
   - **用户明确说**「先用浏览器 / 我粘贴标题备注 / 跳过 MCP」时，才走 3.3 降级
   - **不要**在未说明的情况下偷偷用浏览器抓页，假装 MCP 已通

   #### 3.3 降级（仅用户同意或 MCP 已通但内容仍不足）

   1. Kimi WebBridge（`kimi-webbridge`）打开同一链接读标题与备注  
   2. Cursor IDE Browser / Browser Bridge  
   3. 仍失败：请用户粘贴 **标题 + 备注原文**（可附截图），勿猜测

4. **问题分类**：逻辑错误 / 界面问题 / 性能 / 安全等

**确认点**：向用户简要复述 **标题、备注要点、复现路径与分类**，确认理解无误后再进入定位。

---

## Teambition MCP 接入指引（MCP 不通时原样输出给用户）

> Agent：将本节作为可操作说明发给用户；按用户客户端选 Cursor 或 Claude 配置块。凭证由用户自行填写，**不要编造 App ID/Secret**。

### 这是什么
Teambition **开放平台 MCP**（非网页自带）。配好后才能调用 `QueryTaskV3`（Claude 侧常显示为 `mcp_teambition-mcp_QueryTaskV3`）拉取任务标题 `content`、备注 `note`。

官方包：`@tng/teambition-openapi-mcp`  
文档：https://open.teambition.com/docs  
User MCP 指南：https://open.teambition.com/docs/documents/user-mcp-guide  
开放平台：https://open.teambition.com/

### 准备凭证（企业应用方式）
1. 打开 [Teambition 开放平台](https://open.teambition.com/) 登录  
2. 创建应用，拿到 **App ID**、**App Secret**、企业 **orgId**  
3. 确认应用对目标项目/任务有读权限  

（若团队使用 **User MCP Token**，按官方 User MCP 指南创建 token，并改用对应配置方式。）

### Cursor 配置
编辑 `~/.cursor/mcp.json`（或项目 `.cursor/mcp.json`），在 `mcpServers` 中增加（server 名建议用 `teambition-mcp`，与 Claude 侧习惯一致）：

```json
{
  "mcpServers": {
    "teambition-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "@tng/teambition-openapi-mcp",
        "mcp",
        "-a",
        "<your_app_id>",
        "-s",
        "<your_app_secret>",
        "-o",
        "<your_org_id>",
        "-b",
        "https://open.teambition.com/api"
      ]
    }
  }
}
```

保存后：**重载 MCP / 重启 Cursor**，在 MCP 面板确认 `teambition-mcp` 为已连接。  
若出现 `needsAuth`，先完成 MCP 鉴权再重试。

### Claude Code 配置
在 Claude 的 MCP 配置（如 `~/.claude.json` 的 `mcpServers`，或项目级 MCP 配置）中加入**同上** `teambition-mcp` 块。  
配好后工具列表应出现 `mcp_teambition-mcp_QueryTaskV3`（或 `QueryTaskV3` / `queryTaskV3`）。

### 自检
- Cursor：`GetMcpTools` 能搜到 teambition，且存在 `QueryTaskV3` / `queryTaskV3`  
- Claude：工具列表含 `mcp_teambition-mcp_QueryTaskV3`  
- 用当前 Bug 的 `taskId` 调一次，能返回 `content` / `note`

### 配好后怎么继续
回复：**已配好，继续**（或重新粘贴同一 tb 链接）。Agent 会立刻再调 `QueryTaskV3`，不再要求你重复描述 Bug。

### 临时绕过（可选）
若暂时无法配 MCP，可回复「先用浏览器」或直接粘贴 **标题 + 备注**（及截图），Agent 再继续修复流程。

---

### 第二阶段：代码定位与影响分析

1. **定位问题代码**
   - 根据备注中的页面路径、组件名、堆栈定位文件与行号
   - 搜索相关功能模块；必要时看近期 git blame / 相关提交

2. **影响范围评估**
   - 影响功能范围、依赖模块、优先级与紧急程度

**确认点**：说明根因假设与拟修改范围；定位失败则请求更多线索（页面路径、组件名、控制台报错等）。

### 第三阶段：Bug修复实施

1. **制定修复方案**
   - 提出至少 2 种方案及优缺点
   - 选择最优方案并说明理由

2. **代码修改**（用户确认方案后再动手）
   - 严格遵守项目现有代码规范，与周围风格一致
   - 最小改动；必要时加简短注释说明修复逻辑
   - 确保不引入新问题

### 第四阶段：验证与测试

1. 为修复补充或更新必要测试；确保相关现有用例通过
2. 按备注中的复现步骤验证已修复，并做相关回归
3. 准备修改说明：关键改动点与验证结果

### 第五阶段：提交与反馈

1. **代码提交**（仅在用户明确要求时 commit / push / 开 MR）
   - **默认：在当前已有分支上提交**，不主动切新分支、不主动开 MR
   - **仅当用户明确要求**「单独开分支 / 开 MR」时，再按项目规范创建分支与 Merge Request（可参考个人 skill `kqs-bugfix-to-mr`）
   - commit message 建议：`[taskId] 简短描述` + 正文说明根因与修复

2. **更新 Bug 状态**
   - **优先 Teambition MCP**：有 `UpdateTaskStatusV3` / `CreateTaskCommentV3`（或同类）时，用户确认后再回写状态并评论修复说明
   - MCP 仍不通：给出可复制回复文案，提示手动回写 Teambition

3. **通知**
   - 无法自动通知时：输出给测试同学的验证通知草稿

本 skill 负责：缺陷分析 → 修复 → 验证 → 报告闭环；开 MR 细节可交给 `kqs-bugfix-to-mr`。

## 约束条件

- **Teambition 链接优先 MCP**：先 `QueryTaskV3`，不通则输出接入指引并等待；未经用户同意不静默用浏览器顶替
- **代码规范优先**：遵循项目编码规范
- **最小改动原则**：只改必要代码，避免过度重构
- **向后兼容**：不影响既有功能与 API
- **测试覆盖**：修复应有相应验证（自动化或按复现步骤的手动验证说明）
- **文档同步**：若涉及接口变更，同步更新文档
- **不擅自提交**：未获用户明确授权前，不执行 git commit / push / 创建 MR
- **默认落在已有分支**：除非用户明确要求单独开分支 / 开 MR
- **不删除用户已有改动**：不回滚、不覆盖无关本地修改
- **不编造凭证**：接入指引里的 App ID/Secret/orgId 必须由用户填写

## 异常处理

| 场景 | 处理 |
|------|------|
| 无 teambition MCP / 调用失败 | 输出「Teambition MCP 接入指引」，等待「已配好，继续」 |
| MCP `needsAuth` | 提示完成鉴权后重试，勿直接降级浏览器 |
| 用户同意跳过 MCP | 浏览器 / 粘贴标题备注 |
| 定位不到代码 | 要页面路径、组件名、控制台报错 |
| 修复方案有风险 | 标明风险，建议人工审查 |

## 输出格式

每次执行后输出：

```
=== Bug修复执行报告 ===
Bug ID: [taskId]
Bug标题: [标题]
Bug备注摘要: [备注中的关键描述/复现要点]
Bug信息来源: [Teambition MCP QueryTaskV3 / 浏览器 / 用户粘贴]
修复方案: [采用的方案及理由]
修改文件: [文件列表]
测试结果: [通过/失败及详情]
提交信息: [commit ID或MR链接；默认「待用户确认后在当前分支提交」]
后续建议: [可选建议]
风险提示: [如有风险，明确标注；MCP 未接通时写明]
========================
```

尚未提交时，`提交信息` 填「待用户确认后在当前分支提交」；用户要求开 MR 时再写 MR 链接。  
若卡在 MCP 接入：报告里写清「等待配置 Teambition MCP」，`Bug信息来源` 填「未获取」。
