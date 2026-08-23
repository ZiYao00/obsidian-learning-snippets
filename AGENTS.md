# AGENTS.md

## Purpose

This repository is the canonical source for shared Obsidian learning-note CSS.

## Source-of-truth rules

- Treat `snippets/` as the only editable source of shared CSS.
- Do not copy consumer-project CSS back into this repository unless it is intentionally promoted into a shared Core or Extension.
- Do not hardcode personal Vault paths or local workspace paths in committed files.
- Consumer repositories should reference this repository; they should not keep tracked duplicate copies of shared snippets.

## Core / Extension contract

- `learning-lab.css` is the domain-agnostic Core and owns `--ll-*`, shared typography, semantic callouts, cards, grids, tables, and responsive behavior.
- Extensions must scope selectors with a combined class such as `.learning-page.video-note` or `.learning-page.github-note`.
- Reuse `--ll-*` tokens before adding extension-specific tokens.
- Extension-specific variables/classes must use their own namespace (`--vn-*`, `--gn-*`, etc.).
- Do not duplicate Core components inside Extensions.

## Compatibility

When changing the Core, review all registered Extensions and update `manifest.json` and documentation when the public contract changes.

When changing an Extension, preserve its declared `cssclasses` contract unless the consuming project is updated at the same time.

## Vault runtime safety

- Treat the Vault `.obsidian/snippets/` directory as a runtime/install layer, not a second source of truth.
- Do not create a permanent Vault-level junction/symlink to this repository. Use `scripts/migrate-vault-snippets.ps1` once for legacy links, then `scripts/sync-snippets.ps1` for normal updates.
- Migration must preserve unknown personal CSS and must not delete or mutate the reparse-point Target directory.
- Keep migration backups outside the active `snippets/` directory so Obsidian does not scan backup CSS.

## Consumer integration

Consumer projects should declare the canonical repository, required snippet files, and required `cssclasses` in their `README.md` and `AGENTS.md`. Follow `docs/CONSUMER-INTEGRATION.md`.
