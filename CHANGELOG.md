# Changelog

## Unreleased — GitHub Note v0.4 source/prompt presentation

- Add optional `gh-source` source-attributed, quote-first callout and `prompt` fenced-code presentation inspired by X-case, with independent `--gn-*` tokens and selectors.
- Preserve original source text; show a translation only as a separately labeled quote. Bound long Prompt display at 320px while retaining Obsidian's native copy control.
- No changes to `x-case-note.css`, Learning Lab Core or repository Capture Note identity; the shared CSS does not introduce JavaScript copying or gallery dependencies.


## Unreleased — GitHub Note File Explorer cleanup

- Upgrade `github-note.css` to v0.2. Hide only the `GitHub-Note/_repo-data` root in Obsidian File Explorer using the same pattern as X-case storage separation.
- Keep media, manifests and WikiLinks available on disk; no changes to shared Core, note CSS classes or unrelated CSS snippets.


## 0.1.4 - 2026-10-06

X-case Layout V2 compatibility update. No consumer `cssclasses` or shared Core contract changed.

- Upgrade `x-case-note.css` to v0.7.
- Hide the new `X案例库/_case-data` source/media root from Obsidian File Explorer while keeping files available to embeds, plugins, repair, and filesystem tools.
- Keep the legacy per-case `media/` and `source.json` hiding selectors during the staged migration from Layout V1.

## 0.1.3 - 2026-10-06

X-case File Explorer hygiene update. No consumer `cssclasses` or shared Core contract changed.

- Upgrade `x-case-note.css` to v0.6.
- Keep `source.json` as the on-disk factual source of truth while hiding it from Obsidian File Explorer under `X案例库/**`.
- Continue hiding physical X-case `media/` directories without affecting Gallery, media playback, collection, validation, repair, or filesystem access.

## 0.1.2 - 2026-10-03

Compatible layout update. No consumer `cssclasses`, shared class names, or Extension contract changed.

- Stop the Core from hard-capping Obsidian's `.markdown-preview-sizer`, so Obsidian/theme/plugin width controls can own the final readable width.
- Add conservative responsive bounds for embedded images and local video without forcing a fixed image height.
- Put regular Reading/Live Preview table wrappers in charge of horizontal overflow and let wide tables expand inside their own scroll container.
- Cap the Video Note Bilibili player at 960px on desktop while keeping narrow layouts responsive.
- Add `sync-obsidian.bat` for one-click Windows sync while keeping the machine-local Vault path in ignored `config/vault.local.txt`.

## 0.1.1 - 2026-08-23

Vault migration safety update.

- Add `scripts/migrate-vault-snippets.ps1` for one-time migration from a Vault-level junction/symlink to a normal `.obsidian/snippets/` directory.
- Back up active top-level snippet files before unlinking a reparse point and preserve non-shared personal CSS.
- Verify backups and synchronized shared CSS with SHA-256 hashes.
- Harden `sync-snippets.ps1` so it refuses to write through a junction/symlink and directs users to the migration tool first.
- Document the separation between canonical repository source, Vault runtime installation, and consumer-project dependency declarations.

## 0.1.0 - 2026-08-23

Initial shared design-system repository.

- Establish `learning-lab.css` as the canonical Learning Lab Core.
- Register `video-note.css` and `github-note.css` as scoped Extensions.
- Add Provider/Consumer architecture documentation.
- Add machine-readable `manifest.json`.
- Add consumer-project handoff guidance and recommended `config/obsidian-style.json` contract.
- Add a parameterized Vault sync script without hardcoded personal paths.
- Explicitly stop using consumer-project directory junctions as the distribution mechanism for tracked CSS.
