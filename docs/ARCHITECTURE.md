# 架构说明

## 目标

`obsidian-learning-snippets` 只解决一件事：为多个学习型 Obsidian 项目提供稳定、统一、可复用的 CSS 设计系统。

它不是某个单一项目的附属目录，也不负责笔记内容生成、业务逻辑或 Obsidian Vault 管理。

## 三层职责

### 1. Provider：本仓库

负责：

- 维护共享 Core；
- 维护被多个项目复用的 Extension；
- 定义公开 token / class / cssclasses 契约；
- 提供安装/同步脚本；
- 记录兼容关系。

不负责：

- consumer project 的笔记模板；
- consumer project 的运行配置；
- 用户私人 Vault 路径；
- 项目业务逻辑。

### 2. Consumer project

例如：

- `bili-learning-automation`；
- `github-learning-automation`；
- `ComfyUI-Learning-Lab`。

负责：

- 声明需要哪些共享样式；
- 生成正确的 `cssclasses`；
- 保证自己的模板与共享样式契约一致。

不应该：

- 复制并独立维护共享 CSS；
- 在项目内部 fork 一份 Core；
- 通过 junction 把受 Git 跟踪的项目目录直接指向共享 snippets。

### 3. Runtime：Obsidian Vault

负责：

- 真正加载 CSS；
- 在 `.obsidian/snippets/` 顶层保存启用的 snippet；
- 由用户决定启用哪些样式。

Vault 是运行位置，不是源码真源。

## Core / Extension 模型

```text
learning-lab.css
      │
      ├─ video-note.css
      ├─ github-note.css
      └─ future-extension.css
```

### Core

Core 必须保持领域无关。

允许放入：

- typography；
- spacing；
- shared surfaces；
- semantic callouts；
- grid/card；
- shared table；
- responsive rules；
- `--ll-*` tokens。

不应放入：

- Bilibili player；
- GitHub repository header；
- 某一个项目专有字段；
- 只对单一笔记类型有意义的 UI。

### Extension

Extension 必须使用组合选择器：

```css
.learning-page.video-note { ... }
.learning-page.github-note { ... }
```

避免裸全局选择器。

Extension 先复用 Core token，再增加自己的 namespace：

```text
Video:  --vn-* / video-note-*
GitHub: --gn-* / github-note-*
```

## 为什么不再使用项目级 junction

Windows directory junction 对本地开发很方便，但 Git 会穿透目录联接。若 consumer repository 的 `obsidian/snippets/` 指向共享目录，执行 `git add -A` 时可能把别的 Extension 当成本项目文件暂存。

因此统一规则：

- 不在 consumer repository 内建立指向本仓库的受跟踪 snippets junction；
- 在 Vault 层同步/安装 CSS；
- consumer project 只保存依赖声明。

## Obsidian 的目录约束

Obsidian 读取：

```text
<Vault>/.obsidian/snippets/*.css
```

Extension 必须出现在 snippets 顶层。

不要这样安装：

```text
<Vault>/.obsidian/snippets/github-learning-automation/github-note.css
```

应该：

```text
<Vault>/.obsidian/snippets/github-note.css
```

## Provider Contract

根目录 `manifest.json` 是本仓库对外提供的机器可读契约。

它描述：

- Core；
- Extension；
- 所需 cssclasses；
- Extension 对 Core 的依赖关系。

当公开契约变化时必须同步更新。

## Consumer Contract

推荐 consumer project 建立：

```text
config/obsidian-style.json
```

示例：

```json
{
  "schema_version": 1,
  "repository": "https://github.com/ZiYao00/obsidian-learning-snippets",
  "core": "snippets/learning-lab.css",
  "extensions": ["snippets/github-note.css"],
  "cssclasses": ["learning-page", "github-note"]
}
```

这样 Agent 和程序都不需要从 README 文本里猜依赖。

## 版本与兼容建议

当前 CSS 自身使用独立版本：

- Core v0.3；
- Video Extension v0.2；
- GitHub Extension v0.1。

未来如果 Core 出现破坏性 class/token 变化，优先升级 Core 大版本并同步检查所有 Extension。

仅调整视觉数值、且不改变公开 class/token 语义时，可视为兼容更新。

## 变更判断

一个新样式需求进入本仓库前，应先回答：

1. 所有 Learning Lab 页面都需要吗？
   - 是 → Core 候选。
   - 否 → Extension。
2. 是否已经有 Core token/component 可复用？
3. 是否会改变 consumer 的 Frontmatter？
4. 是否会导致其它 Extension 选择器失效？
5. 是否需要更新 `manifest.json`？

只有通过以上判断后才修改共享契约。
