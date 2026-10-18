"""Regression tests for manifest-driven Obsidian CSS sync (Windows PowerShell).

Uses temporary provider and Vault folders; does not touch the user's Vault.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sync-snippets.ps1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SnippetSyncTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory(prefix="obsidian-style-sync-")
        self.addCleanup(self.work.cleanup)
        base = Path(self.work.name)
        self.provider = base / "some-renamed-provider"
        self.vault = base / "example-vault"
        (self.provider / "scripts").mkdir(parents=True)
        (self.provider / "snippets").mkdir()
        (self.vault / ".obsidian" / "snippets").mkdir(parents=True)
        shutil.copy2(SCRIPT, self.provider / "scripts" / SCRIPT.name)
        self.style = self.provider / "snippets" / "learning-lab.css"
        self.style.write_text(".learning-page{color:var(--text-normal)}\n", encoding="utf-8")
        (self.provider / "manifest.json").write_text(json.dumps({
            "schema_version": 1, "repository": "https://github.com/example/renamed-provider",
            "core": {"name": "learning-lab", "path": "snippets/learning-lab.css", "version": "0.3"},
            "extensions": []
        }), encoding="utf-8")
        self.personal = self.vault / ".obsidian" / "snippets" / "vault-local.css"
        self.personal.write_text(".nav-folder{display:none}\n", encoding="utf-8")
        self.personal_hash = digest(self.personal)

    def invoke(self, mode: str):
        return subprocess.run([
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(self.provider / "scripts" / SCRIPT.name),
            "-VaultRoot", str(self.vault), mode
        ], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)

    def test_install_check_update_backup_and_conflict(self):
        target = self.vault / ".obsidian" / "snippets" / "learning-lab.css"
        state = self.vault / ".obsidian" / "snippets-sync-state.json"
        before = self.invoke("-Check")
        self.assertEqual(before.returncode, 0, before.stderr)
        self.assertIn('"status":  "install"', before.stdout)
        self.assertFalse(state.exists())
        self.assertFalse(target.exists())

        first = self.invoke("-Apply")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(digest(target), digest(self.style))
        self.assertTrue(state.exists())
        self.assertEqual(digest(self.personal), self.personal_hash)

        unchanged = self.invoke("-Check")
        self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
        self.assertIn('"status":  "unchanged"', unchanged.stdout)

        prior_hash = digest(target)
        self.style.write_text(".learning-page{color:var(--text-muted)}\n", encoding="utf-8")
        update_check = self.invoke("-Check")
        self.assertEqual(update_check.returncode, 0, update_check.stderr)
        self.assertIn('"status":  "update"', update_check.stdout)
        self.assertEqual(digest(target), prior_hash)

        update = self.invoke("-Apply")
        self.assertEqual(update.returncode, 0, update.stderr)
        self.assertEqual(digest(target), digest(self.style))
        backup = self.vault / ".obsidian" / "snippets-sync-backups" / ("learning-lab.css." + prior_hash + ".bak")
        self.assertTrue(backup.is_file())
        self.assertEqual(digest(backup), prior_hash)

        target.write_text("/* personal change */\n", encoding="utf-8")
        self.style.write_text(".learning-page{color:var(--text-faint)}\n", encoding="utf-8")
        dirty_hash = digest(target)
        blocked = self.invoke("-Apply")
        self.assertNotEqual(blocked.returncode, 0, "Untracked personal change must be blocked")
        self.assertIn("Refusing to overwrite", blocked.stderr)
        self.assertEqual(digest(target), dirty_hash)
        self.assertEqual(digest(self.personal), self.personal_hash)

    def test_existing_unknown_css_never_overwritten(self):
        other = self.vault / ".obsidian" / "snippets" / "other-theme.css"
        other.write_text("/* custom */\n", encoding="utf-8")
        self.assertEqual(self.invoke("-Apply").returncode, 0)
        self.assertEqual(other.read_text(encoding="utf-8"), "/* custom */\n")
        self.assertEqual(digest(self.personal), self.personal_hash)


if __name__ == "__main__":
    unittest.main()
