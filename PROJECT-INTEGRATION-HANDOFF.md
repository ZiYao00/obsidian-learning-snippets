# 共享 Obsidian 样式接入交接

这份文件用于交给其它学习项目的 Agent / Codex / Claude 阅读。

共享样式唯一真源：

```text
https://github.com/ZiYao00/obsidian-learning-snippets
```

本地开发目录名称可以不同，但项目逻辑必须以这个 GitHub 仓库为 Canonical Source。

## 统一原则

1. 不再把 `learning-lab.css`、`video-note.css`、`github-note.css` 当作 consumer project 自己的源码维护。
2. 不要把 consumer project 的受 Git 跟踪 `obsidian/snippets/` 目录 junction 到共享仓库。
3. 每个项目只声明自己需要哪些共享组件。
4. Obsidian Vault 才是 CSS 的实际安装/加载位置。
5. 共享样式需要修改时，先修改 `obsidian-learning-snippets`，再评估 consumer 是否需要同步模板或 `cssclasses`。

## 每个项目统一增加

建议创建：

```text
config/obsidian-style.json
```

同时更新：

```text
README.md
AGENTS.md
```

如果项目有独立的样式说明文档，也同步更新，但不要复制共享 CSS 内容本身。

---

## bili-learning-automation

使用：

```text
snippets/learning-lab.css
snippets/video-note.css
```

建议 `config/obsidian-style.json`：

```json
{
  "schema_version": 1,
  "repository": "https://github.com/ZiYao00/obsidian-learning-snippets",
  "core": "snippets/learning-lab.css",
  "extensions": ["snippets/video-note.css"],
  "cssclasses": ["learning-page", "video-note"]
}
```

模板必须保持：

```yaml
cssclasses:
  - learning-page
  - video-note
```

迁移重点：

- 检查原来项目内的 `obsidian/snippets/` 是否为真实目录、junction 或已跟踪文件；
- 不要直接 `git add -A` 后再判断；
- 确认共享仓库 CSS 已包含当前最新版本后，再停止项目仓库跟踪重复 CSS；
- README 中改为“从共享仓库安装”，而不是“从本项目复制”。

---

## github-learning-automation

使用：

```text
snippets/learning-lab.css
snippets/github-note.css
```

建议 `config/obsidian-style.json`：

```json
{
  "schema_version": 1,
  "repository": "https://github.com/ZiYao00/obsidian-learning-snippets",
  "core": "snippets/learning-lab.css",
  "extensions": ["snippets/github-note.css"],
  "cssclasses": ["learning-page", "github-note"]
}
```

模板必须保持：

```yaml
cssclasses:
  - learning-page
  - github-note
```

迁移重点：

- `src/github_learning/note_template.py` 已经输出 `learning-page + github-note`，不要回退；
- README / QUICKSTART / NOTE-SPEC 中原先“从项目内 `obsidian/snippets` 复制 CSS”的说明要改成共享仓库；
- 项目内现有共享 CSS 不再作为 Canonical Source；
- 保留对 `cssclasses` 的测试，但测试不应要求共享 CSS 文件一定存在于当前项目。

---

## ComfyUI-Learning-Lab

默认至少使用：

```text
snippets/learning-lab.css
```

建议基础配置：

```json
{
  "schema_version": 1,
  "repository": "https://github.com/ZiYao00/obsidian-learning-snippets",
  "core": "snippets/learning-lab.css",
  "extensions": [],
  "cssclasses": ["learning-page"]
}
```

如果某类笔记确实需要自己的领域 Extension：

- 先确认它不是 Core 通用能力；
- 再决定是否新增共享 Extension；
- 不要因为单个页面需求直接修改 Core。

---

## README 必须告诉用户什么

至少包含：

1. 本项目依赖 `obsidian-learning-snippets`；
2. 需要哪几个 CSS；
3. CSS 应安装到 `<Vault>/.obsidian/snippets/` 顶层；
4. 在 Obsidian「设置 → 外观 → CSS 代码片段」中启用；
5. 项目生成的 Frontmatter 会自动带所需 `cssclasses`（若项目确实自动生成）。

## AGENTS.md 必须告诉 Agent 什么

至少明确：

```text
共享 CSS 的 Canonical Source 是 obsidian-learning-snippets。
不要在当前项目复制、重建、fork 或独立修改共享 Core / Extension。
先读取 config/obsidian-style.json。
如果需要改共享视觉系统，修改共享仓库，而不是当前 consumer repository。
```

## 验收

一个 consumer project 接入完成后应满足：

- [ ] `config/obsidian-style.json` 存在且路径正确；
- [ ] README 指向共享仓库；
- [ ] AGENTS.md 有共享依赖规则；
- [ ] 模板输出正确 `cssclasses`；
- [ ] 项目 Git 不会因 junction 穿透而看到其它 Extension；
- [ ] Vault 中所需 CSS 位于 `.obsidian/snippets/` 顶层；
- [ ] 原项目测试全部通过；
- [ ] Git diff 只包含本项目应有的迁移改动。

不要跨多个 consumer repository 一次性做 `git add -A`、批量删除或批量提交。每个项目单独迁移、单独验证。
