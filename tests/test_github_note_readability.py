"""Scope and design-contract regression tests for GitHub Note editorial CSS v0.3."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "snippets" / "github-note.css"


class EditorialCssContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = CSS.read_text(encoding="utf-8")
        cls.css = re.sub(r"/\*.*?\*/", "", cls.raw, flags=re.S)

    def test_version_and_themed_design(self) -> None:
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        entry = next(x for x in manifest["extensions"] if x["name"] == "github-note")
        self.assertEqual(entry["version"], "0.4")
        self.assertIn("Learning Lab Extension v0.4", self.raw)
        self.assertIn("var(--interactive-accent)", self.raw)
        self.assertIn("var(--background-secondary)", self.raw)
        self.assertIsNone(re.search(r"#[0-9a-fA-F]{3,8}\b", self.css), "Do not hardcode theme-specific colors")

    def test_preserves_width_control_and_shared_core(self) -> None:
        self.assertNotIn(".markdown-preview-sizer {", self.css)
        self.assertNotIn("max-width: 1120px", self.css)
        self.assertIn(".learning-page.github-note h1", self.css)
        self.assertIn(".learning-page.github-note h2", self.css)
        self.assertIn(".learning-page.github-note h3", self.css)
        self.assertIn(".learning-page.github-note p", self.css)
        self.assertIn("@media (max-width: 720px)", self.css)
        self.assertNotRegex(self.css, r"(?m)^\s*(?:html|body)\s*\{")

    def test_hidden_data_only_in_github_file_explorer(self) -> None:
        self.assertIn('.nav-folder-title[data-path="GitHub-Note/_repo-data"]', self.css)
        self.assertIn("display: none !important", self.css)
        self.assertNotIn("X案例库/", self.css)
        self.assertNotIn("_case-data", self.css)
        self.assertNotIn("visibility: hidden", self.css)

    def test_no_forced_cards_images_or_editing_overrides(self) -> None:
        self.assertIn(".learning-page.github-note ul li::marker", self.css)
        self.assertIn(".learning-page.github-note .image-embed img", self.css)
        self.assertIn(".learning-page.github-note :not(pre) > code", self.css)
        self.assertNotIn(".cm-content", self.css)
        self.assertNotIn("grid-template-columns", self.css)
        self.assertNotIn("position: fixed", self.css)

    def test_optional_source_quote_is_independently_scoped(self) -> None:
        self.assertIn('.learning-page.github-note .callout[data-callout="gh-source"]', self.css)
        self.assertIn('> .callout-content > blockquote', self.css)
        self.assertIn("--gn-source-rail", self.css)
        self.assertIn("--gn-source-dot", self.css)
        self.assertNotIn(".learning-page.x-case-note", self.css)
        self.assertNotIn('data-callout="x-post"', self.css)
        self.assertNotIn('data-callout="x-reply"', self.css)

    def test_prompt_uses_native_copy_and_bounded_scrolling(self) -> None:
        self.assertIn("pre:has(code.language-prompt)", self.css)
        self.assertIn("pre code.language-prompt", self.css)
        self.assertIn('content: "PROMPT"', self.css)
        self.assertIn("max-height: 320px", self.css)
        self.assertIn("overflow-y: auto", self.css)
        self.assertIn(".copy-code-button", self.css)
        self.assertIn(".copy-code-button:focus-visible", self.css)
        self.assertNotIn("navigator.clipboard", self.css)
        self.assertNotIn("@javascript", self.css)
        self.assertNotIn(".cm-content", self.css)

    def test_real_writing_examples_are_not_modified(self) -> None:
        github_root = os.environ.get("GITHUB_LEARNING_ROOT")
        if not github_root:
            self.skipTest("Set GITHUB_LEARNING_ROOT for optional real-project integration QA")
        reference = Path(github_root) / "docs" / "ODS-NATURAL-PRODUCT-V2.2-REFERENCE.md"
        legacy = Path(github_root) / "notes" / "github" / "00-待整理" / "bili-learning-automation.md"
        if not reference.is_file() or not legacy.is_file():
            self.skipTest("Configured GitHub Note samples are not available")
        self.assertIn("仓库自己强调的七项能力", reference.read_text(encoding="utf-8"))
        self.assertIn("## 能做什么", legacy.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
