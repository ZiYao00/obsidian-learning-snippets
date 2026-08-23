# Architecture

## Single source of truth

`snippets/` is the canonical source for all shared learning-note CSS. Consumer repositories should reference these files instead of maintaining tracked copies.

## Layers

### Core

`snippets/learning-lab.css`

Responsibilities:

- shared design tokens (`--ll-*`)
- page frame and typography
- semantic callouts (`lead`, `summary`, `meta`, `risk`, `resource`)
- grids and cards
- shared table styles
- reusable micro UI
- responsive behavior

Required Frontmatter class:

```yaml
cssclasses:
  - learning-page
```

### Extensions

Extensions add domain-specific behavior without reimplementing Core components.

Rules:

1. Scope selectors with a combined class such as `.learning-page.video-note`.
2. Reuse `--ll-*` tokens first.
3. Use an extension namespace for new variables/classes.
4. Do not move domain-specific selectors into Core.
5. Do not duplicate Core components in an Extension.

Current extensions:

- `video-note.css` → `video-note`, namespace `--vn-*`
- `github-note.css` → `github-note`, namespace `--gn-*`

## Distribution model

The repository is the canonical upstream. Obsidian loads installed copies from the user's Vault `.obsidian/snippets/` directory.

Consumer repositories do not need to contain the CSS files themselves. They only need to declare:

- canonical upstream repository
- required snippet files
- required `cssclasses`

This avoids directory-junction Git pollution and keeps updates centralized.

## Change policy

A Core change can affect every consumer, so review all registered extensions before release.

An Extension change should preserve its declared `cssclasses` and namespace unless the consumer contract changes at the same time.

Update `manifest.json` whenever the public Core/Extension contract changes.
