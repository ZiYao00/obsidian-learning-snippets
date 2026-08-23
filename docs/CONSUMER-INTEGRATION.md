# Consumer Project 接入指南

这份文档是给其它学习项目看的。目标是让每个项目明确知道：共享 CSS 去哪里拿、自己需要哪些组件、模板要输出什么 `cssclasses`，以及哪些事情不能在本项目里做。

Canonical repository：

```text
https://github.com/ZiYao00/obsidian-learning-snippets
```

## 先理解职责

Consumer project 只负责“声明并使用”，不负责“拥有并维护”共享 CSS。

正确关系：

```text
obsidian-learning-snippets
        ↓ 提供样式契约
consumer project
        ↓ 生成正确 Frontmatter
Obsidian Vault
        ↓ 实际加载 CSS
最终笔记
```

错误关系：

```text
consumer project
  └─ 自己保存一份 learning-lab.css
```

或：

```text
consumer project/obsidian/snippets
  → junction 到共享仓库
```

后者会让 Git 穿透共享目录，产生跨项目暂存污染。

## 每个项目应增加什么

推荐增加：

```text
config/obsidian-style.json
```

最小 schema：

```json
{
  "schema_version": 1,
  "repository": "https://github.com/ZiYao00/obsidian-learning-snippets",
  "core": "snippets/learning-lab.css",
  "extensions": [],
  "cssclasses": ["learning-page"]
}
```

字段含义：

- `schema_version`：Consumer Contract 版本；
- `repository`：共享样式唯一真源；
- `core`：必需 Core；
- `extensions`：本项目需要的领域 Extension；
- `cssclasses`：生成笔记必须写入的 Frontmatter class。

## bili-learning-automation

建议配置：

```json
{
  "schema_version": 1,
  "repository": "https://github.com/ZiYao00/obsidian-learning-snippets",
  "core": "snippets/learning-lab.css",
  "extensions": ["snippets/video-note.css"],
  "cssclasses": ["learning-page", "video-note"]
}
```

笔记必须生成：

```yaml
cssclasses:
  - learning-page
  - video-note
```

项目 README 应说明：

- 样式来源于共享仓库；
- 用户需要安装 `learning-lab.css` + `video-note.css`；
- 项目不再维护这两份 CSS 的独立副本。

## github-learning-automation

建议配置：

```json
{
  "schema_version": 1,
  "repository": "https://github.com/ZiYao00/obsidian-learning-snippets",
  "core": "snippets/learning-lab.css",
  "extensions": ["snippets/github-note.css"],
  "cssclasses": ["learning-page", "github-note"]
}
```

笔记必须生成：

```yaml
cssclasses:
  - learning-page
  - github-note
```

项目内原先跟踪的：

```text
obsidian/snippets/learning-lab.css
obsidian/snippets/github-note.css
```

迁移完成后不应继续作为项目自己的 CSS 真源。

## ComfyUI-Learning-Lab

如果某一批笔记只使用通用 Core：

```json
{
  "schema_version": 1,
  "repository": "https://github.com/ZiYao00/obsidian-learning-snippets",
  "core": "snippets/learning-lab.css",
  "extensions": [],
  "cssclasses": ["learning-page"]
}
```

如果未来该项目出现自己的领域 Extension，再单独加入 `extensions`，不要把项目专属规则直接塞进 Core。

## README 推荐声明

Consumer project 的 README 建议加入：

```markdown
## Obsidian 样式

本项目使用共享 Learning Lab 样式系统：

https://github.com/ZiYao00/obsidian-learning-snippets

所需样式见 `config/obsidian-style.json`。

本项目不维护共享 CSS 的独立副本。请把所需 snippets 安装到你的 Obsidian Vault：

`<your-vault>/.obsidian/snippets/`

然后在「设置 → 外观 → CSS 代码片段」中启用。
```

## AGENTS.md 推荐声明

```markdown
## Shared Obsidian style dependency

Canonical source:
https://github.com/ZiYao00/obsidian-learning-snippets

Read `config/obsidian-style.json` before changing note layout or Frontmatter.

Do not copy, regenerate, fork, or independently modify shared Core/Extension CSS in this repository. If shared styles need to change, update the canonical repository first.
```

这条对 Codex / Claude / Hermes 很重要：它能防止 Agent 看到样式需求后，又在 consumer project 内生成一份新的 `learning-lab.css`。

## Vault 安装

Obsidian 只会读取：

```text
<Vault>/.obsidian/snippets/*.css
```

不要安装到子目录。

推荐从共享仓库运行：

```powershell
.\scripts\sync-snippets.ps1 -VaultRoot "D:\Notes\MyVault"
```

也可以人工复制，只要最终 CSS 位于 `.obsidian/snippets/` 顶层即可。

## 项目迁移时怎么处理旧 CSS

迁移 consumer project 时，先确认 Git 当前状态，再处理旧的受跟踪 CSS。

原则：

1. 先确认共享仓库中的对应文件已经是最新真源；
2. 项目 README / AGENTS / `config/obsidian-style.json` 已经声明依赖；
3. 再停止项目仓库跟踪共享 CSS；
4. 不要用 junction 让项目的受跟踪目录重新指向共享仓库；
5. 验证 note template 仍输出正确 `cssclasses`；
6. 最后运行项目自己的测试和 Git diff 检查。

具体 `git rm --cached`、`.gitignore` 等迁移动作应由各项目根据当前 Git 状态执行，不要跨项目批量操作。

## 新项目接入检查表

- [ ] 已确定是否需要 Core；
- [ ] 已确定需要哪个 Extension；
- [ ] 已创建 `config/obsidian-style.json`；
- [ ] README 已指向 Canonical repository；
- [ ] AGENTS.md 已声明禁止在项目内 fork 共享 CSS；
- [ ] note template 输出正确 `cssclasses`；
- [ ] Vault 顶层 snippets 已安装对应 CSS；
- [ ] 项目仓库没有通过 junction 跟踪整个共享 snippets 目录。

完成这些后，这个项目就已经正确接入共享基础组件。
