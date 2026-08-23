# obsidian-learning-snippets

为学习型 Obsidian 笔记提供统一视觉语言的共享 CSS 组件仓库。

这个仓库是 Learning Lab 样式体系的 **唯一真源（Single Source of Truth）**。其它学习自动化项目只声明自己依赖哪些样式，不再各自维护 `learning-lab.css`、`video-note.css`、`github-note.css` 的副本，也不再把项目目录通过 junction 直接指向共享仓库。

## 为什么需要这个仓库

过去多个项目各自保存或链接同一组 CSS，会带来几个问题：

- Core 在多个仓库中出现副本，难以判断哪一份才是最新版本；
- Windows directory junction 会让 Git 穿透到共享目录，`git add -A` 可能把其它项目的 Extension 一起暂存；
- Obsidian 只识别 `.obsidian/snippets/` 顶层 CSS，放进项目子目录的 Extension 不会被加载；
- Core 与各领域 Extension 的职责容易混淆。

现在统一为：

```text
obsidian-learning-snippets
        │
        ├─ learning-lab.css   Core
        ├─ video-note.css     Video Extension
        └─ github-note.css    GitHub Extension
                │
                ▼
      consumer projects
  只声明依赖和 cssclasses
                │
                ▼
        Obsidian Vault
       实际安装并加载 CSS
```

## 组件

| 文件 | 角色 | 适用范围 | 必需 `cssclasses` |
| --- | --- | --- | --- |
| `snippets/learning-lab.css` | Core Design System | 所有 Learning Lab 页面 | `learning-page` |
| `snippets/video-note.css` | Video Note Extension | 视频/B站学习笔记 | `learning-page`, `video-note` |
| `snippets/github-note.css` | GitHub Note Extension | GitHub 仓库学习笔记 | `learning-page`, `github-note` |

### Core：`learning-lab.css`

Core 只负责通用设计语言：

- `--ll-*` Design Tokens；
- 页面宽度、排版与标题层级；
- `lead / summary / meta / risk / resource` 语义 callout；
- `grid-2 / grid-3 / grid-auto + card` 布局组件；
- `.ll-badge / .ll-metric / .ll-note / .ll-chip-*` 微型 UI；
- 表格与响应式规则。

Core 不写视频播放器、GitHub 仓库元信息等领域规则。

### Extension

Extension 只做某类笔记特有的样式，并必须遵守：

1. 依赖 `learning-lab.css`；
2. 使用组合 class 限定作用域，例如 `.learning-page.video-note`；
3. 优先复用 `--ll-*`；
4. 新变量使用独立命名空间，例如 `--vn-*`、`--gn-*`；
5. 不复制 Core 已经提供的组件。

## 在 Obsidian 中安装

把需要的 CSS 复制到：

```text
<your-vault>/.obsidian/snippets/
```

然后在：

```text
设置 → 外观 → CSS 代码片段
```

启用对应文件。

> Obsidian 只扫描 `.obsidian/snippets/` 顶层 CSS，不要把 `github-note.css`、`video-note.css` 放进项目名称子目录。

### 视频笔记

启用：

```text
learning-lab
video-note
```

Frontmatter：

```yaml
cssclasses:
  - learning-page
  - video-note
```

### GitHub 仓库笔记

启用：

```text
learning-lab
github-note
```

Frontmatter：

```yaml
cssclasses:
  - learning-page
  - github-note
```

### 只有 Core 的学习页面

Frontmatter：

```yaml
cssclasses:
  - learning-page
```

## 推荐的 Vault 同步方式

不建议把各项目的 `obsidian/snippets/` junction 到本仓库。

推荐在 Vault 层统一安装。仓库提供：

```text
scripts/sync-snippets.ps1
```

示例：

```powershell
.\scripts\sync-snippets.ps1 -VaultRoot "D:\Notes\MyVault"
```

脚本只把本仓库的 CSS 同步到 `<Vault>/.obsidian/snippets/`，不会要求各 consumer project 持有 CSS 副本。

## 其它项目如何接入

Consumer 项目不应该复制共享 CSS，而应该声明自己的依赖。

推荐每个项目增加：

```text
config/obsidian-style.json
```

GitHub 学习笔记示例：

```json
{
  "schema_version": 1,
  "repository": "https://github.com/ZiYao00/obsidian-learning-snippets",
  "core": "snippets/learning-lab.css",
  "extensions": ["snippets/github-note.css"],
  "cssclasses": ["learning-page", "github-note"]
}
```

视频笔记示例：

```json
{
  "schema_version": 1,
  "repository": "https://github.com/ZiYao00/obsidian-learning-snippets",
  "core": "snippets/learning-lab.css",
  "extensions": ["snippets/video-note.css"],
  "cssclasses": ["learning-page", "video-note"]
}
```

同时在项目 `README.md` / `AGENTS.md` 里声明：

- Canonical repository；
- 需要的 Core / Extension；
- 生成笔记必须带哪些 `cssclasses`；
- 不允许在 consumer repository 内重新生成或独立修改共享 CSS。

完整接入规范见：[`docs/CONSUMER-INTEGRATION.md`](docs/CONSUMER-INTEGRATION.md)。

## 仓库结构

```text
obsidian-learning-snippets/
├─ snippets/
│  ├─ learning-lab.css
│  ├─ video-note.css
│  └─ github-note.css
├─ docs/
│  ├─ ARCHITECTURE.md
│  └─ CONSUMER-INTEGRATION.md
├─ scripts/
│  └─ sync-snippets.ps1
├─ manifest.json
├─ AGENTS.md
├─ CHANGELOG.md
└─ README.md
```

## 更新规则

修改 Core 时：

1. 先判断需求是否真的属于所有 Learning Lab 笔记；
2. 检查所有 Extension 是否仍兼容；
3. 如果公开 token / class 契约改变，同步更新 `manifest.json`；
4. 再通知 consumer project 是否需要调整 Frontmatter 或模板。

修改 Extension 时：

1. 保持组合 class 作用域；
2. 不把领域逻辑放回 Core；
3. 如果 `cssclasses` 契约发生变化，同步更新对应 consumer project。

## 当前消费者

目前至少包括：

- `bili-learning-automation` → Core + `video-note.css`；
- `github-learning-automation` → Core + `github-note.css`；
- `ComfyUI-Learning-Lab` → Core，具体 Extension 由该项目按笔记类型声明。

## Canonical repository

```text
https://github.com/ZiYao00/obsidian-learning-snippets
```
