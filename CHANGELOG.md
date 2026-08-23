# Changelog

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
