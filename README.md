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

## StartAI 提示词画廊

新增 `snippets/prompt-gallery.css`（依赖 `learning-lab.css`），用于 Obsidian 的 StartAI 图文提示词笔记。笔记 Frontmatter 使用 `cssclasses: [learning-page, prompt-gallery]`，正文使用 `[!prompt-pair]` Callout：宽视图左图右文、窄视图上下排列。该扩展已纳入 `manifest.json` 和 `scripts/sync-snippets.ps1`。源案例笔记保存在用户的 Obsidian Vault 内，不在本共享样式仓库保存图片和提示词。

## 组件

| 文件 | 角色 | 适用范围 | 必需 `cssclasses` |
| --- | --- | --- | --- |
| `snippets/learning-lab.css` | Core Design System | 所有 Learning Lab 页面 | `learning-page` |
| `snippets/video-note.css` | Video Note Extension | 视频/B站学习笔记 | `learning-page`, `video-note` |
| `snippets/github-note.css` | GitHub Note Extension | GitHub 仓库学习笔记 | `learning-page`, `github-note` |
| `snippets/x-case-note.css` | X Case Extension | X 案例笔记 | `learning-page`, `x-case-note` |
| `snippets/prompt-gallery.css` | Prompt Gallery Extension | StartAI 案例画廊 | `learning-page`, `prompt-gallery` |

### Core：`learning-lab.css`

Core 只负责通用设计语言：

- `--ll-*` Design Tokens；
- 页面内边距、排版与标题层级；最终正文宽度由 Obsidian、主题或宽度控制插件负责；
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

**GitHub Note v0.4 编辑式阅读：** 此 Extension 用字号层级、章节引导线、段落节奏、简洁的列表和行内代码区分信息；不把 Markdown 长文拆成固定卡片，也不更改正文宽度控制。继承 Obsidian 亮色/暗色主题变量；可单独关闭以回退原生阅读样式。`GitHub-Note/_repo-data` 的隐藏仅作用于 File Explorer，不移动或删除文件。

**来源原文与 Prompt 的可选视觉组件：** `[!gh-source]` 是带来源归属的简约引用（竖线、圆点、译文缩进），`~~~prompt` 是只针对原始提示词的阅读代码块（顶部 PROMPT 栏、Obsidian 原生复制按钮、320px 内滚动）。这两种组件只在 `learning-page + github-note` 页面生效，不依赖或修改 X 案例库的 `x-post`、`x-reply`、完整 Gallery、媒体目录或插件。普通正文、安装命令和普通代码块不加专属装饰。只有现有 Research Packet 中真实、完整可核的来源才能标成官方原文或原始 Prompt。转换规则由 `github-learning-automation/docs/NOTE-SPEC.md` 定义。

**视觉回归：** 有 Chromium 和真实测试素材时可运行 `py -3.12 scripts/qa_github_note_reading.py --github-root "<GitHub Note 项目目录>" --seedance-root "<Seedance Director 资料目录>"`。也可使用 `GITHUB_LEARNING_ROOT`、`SEEDANCE_DIRECTOR_ROOT` 环境变量。测试不依赖项目与共享仓库相邻放置。测试基于原 ODS 与旧笔记六组，再加入固定 ODS 官方短引文和真实 Seedance Director Prompt 的四组，合计 **10 组**亮/暗、宽/窄的静态模拟预览；自动检查标题字号、首图、来源引用样式、Prompt 标题栏与原生复制入口、320px 滚动、横向溢出和阅读宽度。不访问网络、不修改 Vault。这不是 Obsidian 客户端真实截图，最终仍需用户在真实主题和 Live Preview 下验收。

### 只有 Core 的学习页面

Frontmatter：

```yaml
cssclasses:
  - learning-page
```

## 推荐的 Vault 同步方式

不建议把各项目的 `obsidian/snippets/` junction 到本仓库，也不建议把整个 Vault 的 `.obsidian/snippets/` 长期做成 junction/symlink。

### 从旧 junction 迁移一次

如果现有 Vault 的 `.obsidian/snippets/` 仍然是历史 junction/symlink，先运行：

```powershell
.\scripts\migrate-vault-snippets.ps1 -VaultRoot "D:\Notes\MyVault"
```

迁移脚本会：

- 检测 `snippets` 是否是普通目录或 reparse point；
- junction/symlink 场景下先备份当前顶层文件，再只解除链接对象；
- 把 `snippets` 恢复为普通目录；
- 保留未知的个人 CSS；
- 从本仓库同步 `learning-lab.css`、`video-note.css`、`github-note.css`；
- 用 SHA-256 验证备份和最终同步结果；
- 把迁移备份放在 `.obsidian/snippets-migration-backup/<timestamp>/`，不会塞进 Obsidian 实际扫描的 `snippets/`。

### 日常同步

完成一次性迁移后，日常更新可以直接运行：

```powershell
.\scripts\sync-snippets.ps1 -VaultRoot "<your-vault>" -Check
.\scripts\sync-snippets.ps1 -VaultRoot "<your-vault>" -Apply
```

Windows 也可以双击仓库根目录的：

```text
sync-obsidian.bat
```

BAT 会按以下顺序解析 Vault 路径：

1. 命令行参数，例如 `sync-obsidian.bat "D:\Notes\MyVault"`；
2. 本机私有文件 `config/vault.local.txt` 的第一行；
3. 环境变量 `OBSIDIAN_VAULT`。

`config/vault.local.txt` 已被 Git 忽略，适合保存本机 Vault 绝对路径，不会进入仓库历史。

`sync-snippets.ps1` 从 `manifest.json` 生成安装清单，`-Check` 仅报告，`-Apply` 安装或升级。同步记录保存在 Vault 的 `.obsidian/snippets-sync-state.json`；升级前校验已知版本并备份到 `.obsidian/snippets-sync-backups/`。首次遇到已有但与源文件不同的 CSS，必须人工核对，不会强制覆盖。个人 `vault-local.css` 不属于共享清单，永远不会被公共同步脚本覆盖。目标目录是 junction/symlink 时依然拒绝写入。

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
│  ├─ migrate-vault-snippets.ps1
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
