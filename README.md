# obsidian-learning-snippets

Shared Obsidian CSS design system for learning notes.

This repository is the **single source of truth** for the shared visual components used by learning-note projects. Consumer projects should reference this repository instead of keeping their own copies of the CSS files.

## Components

| File | Role | Required `cssclasses` |
| --- | --- | --- |
| `snippets/learning-lab.css` | Core design system | `learning-page` |
| `snippets/video-note.css` | Video-note extension | `learning-page`, `video-note` |
| `snippets/github-note.css` | GitHub-note extension | `learning-page`, `github-note` |

`learning-lab.css` is the Core. Extensions must reuse the Core tokens/components and only contain domain-specific overrides.

## Install in Obsidian

Copy the CSS files you need into:

```text
<your-vault>/.obsidian/snippets/
```

Then enable them in **Settings → Appearance → CSS snippets**.

For video notes, enable `learning-lab` and `video-note`. For GitHub repository notes, enable `learning-lab` and `github-note`.

Obsidian scans CSS files in the top level of `.obsidian/snippets/`; do not place an extension inside a nested project subdirectory.

## Frontmatter contract

Base learning page:

```yaml
cssclasses:
  - learning-page
```

Video note:

```yaml
cssclasses:
  - learning-page
  - video-note
```

GitHub repository note:

```yaml
cssclasses:
  - learning-page
  - github-note
```

## Consumer projects

Consumer repositories should **not vendor these CSS files and should not junction their project `obsidian/snippets/` directory to this repository**. Instead:

1. Declare the dependency in the consumer project's `README.md` and `AGENTS.md`.
2. Point to this repository as the canonical source.
3. State which Core/Extension files and `cssclasses` the project requires.
4. Keep the actual Obsidian installation at the Vault level.

See `docs/CONSUMER-INTEGRATION.md` for the recommended declaration block and `docs/ARCHITECTURE.md` for design rules.

`manifest.json` records the current Core/Extension contract for tools and agents.
