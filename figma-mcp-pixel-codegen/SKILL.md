---
name: figma-mcp-pixel-codegen
description: 通过 Figma MCP 将 Figma 设计转换为像素级精确的 UI 代码。Use when the user shares a Figma or Figma node URL, asks to rebuild a page or component from a design, implement an interface from Figma, create pixel-perfect code, or extract layout, typography, color, spacing, radius, shadow, and design tokens from Figma.
---

# Figma MCP 像素级精确代码生成

## 使用时机

优先使用此技能当：

- 用户提供了 `figma.com` 文件或节点链接。
- 用户要求从设计稿实现页面或组件、1:1 还原或像素级匹配。
- 间距、字体、颜色、阴影、圆角等必须从 Figma 提取到代码中。

## 前置条件

- Figma MCP 必须已在 Cursor 中配置并启用。如果 MCP 报错，请用户在 Cursor 设置 -> MCP 中检查服务器状态和令牌。
- 调用 MCP 工具前，必须先阅读对应 MCP 工具描述符的 JSON schema，并按 schema 使用参数；不要猜测工具名称或字段。
- Figma 写入类操作必须遵守对应 Figma Skill 的前置要求；设计到代码场景优先使用 `get_design_context` 获取参考代码、截图和设计提示。

## 1. 解析 Figma 链接

从用户粘贴的 URL 中提取 `fileKey` 和 `nodeId`。

常见形式：

- `https://www.figma.com/design/<FILE_KEY>/...?node-id=<NODE_ID>`
- `https://www.figma.com/file/<FILE_KEY>/...?node-id=<NODE_ID>`
- `https://www.figma.com/design/<FILE_KEY>/branch/<BRANCH_KEY>/...?node-id=<NODE_ID>`

规则：

- `node-id` 可能形如 `123-456`；转换为 Figma API 风格时，通常将 `-` 映射为 `:`，但应以 MCP 工具文档为准。
- 如果只提供文件链接，先确认目标 frame/节点，或通过 MCP 获取元数据后让用户选择。
- 解析失败时不要编造 `fileKey` 或 `nodeId`。

## 2. 通过 MCP 系统化提取数据

逐层拉取信息，并记录原始数值和单位（`px`、`%`、`auto`、约束等），用于后续比对。

需要捕获：

- 布局：宽度、高度、内边距、外边距、flex/grid、方向、`justify`、`align`、`gap`。
- 定位与层级：`x/y`、绝对定位或相对定位、`z-index`、裁剪、溢出。
- 字体：字体系列、字号、字重、行高、字距、对齐方式、换行。
- 颜色：填充、描边、透明度、渐变色标和角度。
- 描边与形状：边框宽度、描边对齐方式、圆角半径；如四角不同，分别记录。
- 效果：阴影偏移、模糊、扩散、颜色，以及模糊效果。
- 约束与响应式：constraints、`layoutGrow`、`layoutAlign`、自动布局行为。
- 组件与变体：组件、变体、实例覆盖、交互状态。

如果某次 MCP 响应不完整，按节点拆分继续请求以补齐。仍然不足时，在假设和未知项中记录，不要编造设计值。

## 3. 结构化代码输出

匹配项目技术栈：

- 从仓库推断 Vue/React、CSS Modules、SCSS、Tailwind 或工具类模式。
- 遵循现有文件夹、组件命名、样式命名和设计令牌规范。
- 复用现有组件、主题变量、UI 套件和资产，避免重复造轮子。

结构要求：

- 使用语义化标记或项目惯用的框架结构。
- 类名、BEM、组件拆分方式与项目保持一致。
- 静态设计值应集中到设计令牌、CSS 变量或项目已有 token 文件中。

样式要求：

- 如果项目使用 Tailwind，优先用 Tailwind；工具类无法精确表达时，使用任意值或少量自定义 CSS。
- 否则使用 CSS/SCSS，并让值与 Figma 匹配。
- 至少对齐或生成这些 token：color、font、spacing、radius、shadow。
- 合并到现有语义命名中，避免创建重复 token。

## 4. 像素级一致性与迭代

标准：像素精度优先，不用“差不多”替代可读取的设计值。

重点比较：

- 模块间距、内部间隙、内边距。
- 文本、图标、多列内容的对齐和基线。
- 字号、行高、字重、字距。
- 背景、边框、阴影和层级顺序。
- hover、active、disabled、loading、empty 等交互或状态；设计包含时应实现，否则说明缺失。

每轮迭代简要记录：

```markdown
检查项:
设计值:
当前代码:
修复:
```

## 5. 假设、风险和交付物

需要指出的未知项包括：

- 字体：网络字体可用性、降级方案。
- 动态数据：列表长度、空状态、加载状态、异常状态。
- 响应式：设计中未定义的断点、缩放规则、容器宽度。
- 图片和图标：导出规范、`@2x`、SVG 或栅格图。
- 平台限制：浏览器渲染差异、字体抗锯齿、MCP 无法返回的属性。

最终交付应包括：

- 可交付代码：组件、样式、必要资产说明。
- 样式映射：Figma 属性 -> token、class 或 CSS。
- 差异列表：与设计不一致之处及原因。
- 验证步骤：如何在浏览器或 DevTools 中检查间距、Computed 样式、截图对比。

## 执行清单

复制并跟踪：

```markdown
- [ ] 解析 Figma URL，确认 fileKey 和 nodeId
- [ ] 读取 MCP 工具 schema
- [ ] 获取设计上下文、截图、元数据和关键节点属性
- [ ] 梳理项目技术栈、组件库、样式体系和 token
- [ ] 建立 Figma 属性到代码 token/class/CSS 的映射
- [ ] 实现组件、样式和资产引用
- [ ] 对比设计值与实现值，修复像素差异
- [ ] 记录假设、风险、差异和验证步骤
```

## 质量标准

- 像素级保真度优先。
- 不编造颜色、尺寸、阴影或字体；未知时明确说明假设。
- 优先复用组件库、现有布局和现有 token。
- 保持代码可维护：结构清晰、token 集中、类名易读，方便后续维护。
