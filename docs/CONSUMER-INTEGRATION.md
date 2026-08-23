# Consumer integration

Projects that generate Obsidian learning notes should declare this repository as the canonical style source instead of tracking duplicate CSS files locally.

## Recommended declaration

Add a short section to the consumer project's `README.md`:

```markdown
## Obsidian styles

This project uses the shared Learning Lab style system from:

https://github.com/ZiYao00/obsidian-learning-snippets

Required snippets:

- `snippets/learning-lab.css`
- `<project extension>.css`

Required Frontmatter classes:

```yaml
cssclasses:
  - learning-page
  - <extension-class>
```

Install the snippets in your Obsidian Vault and enable them under Settings → Appearance → CSS snippets.
```

Add the same dependency contract to `AGENTS.md` so coding agents do not recreate or fork the shared CSS by accident:

```markdown
## Shared Obsidian style dependency

Canonical source: https://github.com/ZiYao00/obsidian-learning-snippets

Do not copy, regenerate, or modify shared Core CSS inside this repository. If the shared design system must change, update the canonical repository first.
```

## Current consumers

### Video-note projects

Use:

- `snippets/learning-lab.css`
- `snippets/video-note.css`

Frontmatter:

```yaml
cssclasses:
  - learning-page
  - video-note
```

### GitHub learning notes

Use:

- `snippets/learning-lab.css`
- `snippets/github-note.css`

Frontmatter:

```yaml
cssclasses:
  - learning-page
  - github-note
```

## Local development rule

Do not junction a consumer repository's tracked `obsidian/snippets/` folder directly to this repository. Git can traverse directory junctions and accidentally stage unrelated extensions.

For local usage, install/sync the snippets at the **Vault** level. Consumer repositories should only store the dependency declaration and their note-generation contract.

## Updating the shared styles

When a project needs a new shared behavior:

1. Decide whether the behavior belongs to the domain-agnostic Core or a project-specific Extension.
2. Update this repository first.
3. Update `manifest.json` when the public class/token contract changes.
4. Update the consumer project's documentation or generated Frontmatter only if its dependency contract changes.
