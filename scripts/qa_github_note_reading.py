"""Visual smoke-test for GitHub Note CSS, using installed Chromium without deps.

Renders an isolated approximation of Obsidian Reading View for ODS (new editorial)
and bili-learning-automation (legacy), in light/dark and wide/narrow layouts.
It does NOT assert a screenshot of the running Obsidian app.
Images and generated HTML live in the system temp directory, not the project.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parents[1]
CSS_CORE = ROOT / "snippets" / "learning-lab.css"
CSS_EXTENSION = ROOT / "snippets" / "github-note.css"

BROWSERS = [
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
]


def inline(source: str) -> str:
    safe = html.escape(source)
    safe = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"`([^`]+)`", r"<code>\1</code>", safe)
    safe = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', safe)
    return safe


def to_simple_html(source: str, notes_root: Path) -> str:
    lines = source.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((idx for idx in range(1, len(lines)) if lines[idx].strip() == "---"), None)
        if end is not None:
            lines = lines[end + 1:]
    rendered: list[str] = []
    para: list[str] = []
    listing = False
    code = False
    code_lines: list[str] = []

    def flush_para() -> None:
        if para:
            rendered.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list() -> None:
        nonlocal listing
        if listing:
            rendered.append("</ul>")
            listing = False

    for line in lines:
        v = line.strip()
        if v.startswith("```") or v.startswith("~~~"):
            flush_para()
            flush_list()
            if code:
                rendered.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines.clear()
            code = not code
            continue
        if code:
            code_lines.append(line)
            continue
        if not v:
            flush_para()
            flush_list()
            continue
        if v.startswith("![["):
            flush_para()
            flush_list()
            # Use the actual pinned cover image, without copying or changing it.
            path = notes_root / "notes" / "github" / "_repo-data" / "Osmantic" / "ODS" / "media" / "readme-first-f9c72d216f56.png"
            if path.is_file():
                rendered.append('<div class="image-embed"><img src="' + path.as_uri() + '" width="360" alt="ODS repository first image"></div>')
            continue
        if v.startswith("<small"):
            flush_para()
            flush_list()
            rendered.append(v)
            continue
        if v.startswith("> [!"):
            flush_para()
            flush_list()
            rendered.append('<div class="callout" data-callout="summary"><div class="callout-title">先看结论</div></div>')
            continue
        if v.startswith(">"):
            flush_para()
            flush_list()
            rendered.append("<blockquote><p>" + inline(v.lstrip("> ")) + "</p></blockquote>")
            continue
        match = re.match(r"^(#{1,3})\s+(.+)", v)
        if match:
            flush_para()
            flush_list()
            level = len(match.group(1))
            rendered.append(f"<h{level}>" + inline(match.group(2)) + f"</h{level}>")
            continue
        if v == "---":
            flush_para()
            flush_list()
            rendered.append("<hr>")
            continue
        bullet = re.match(r"^[-*]\s+(.+)", v)
        if bullet:
            flush_para()
            if not listing:
                rendered.append("<ul>")
                listing = True
            rendered.append("<li>" + inline(bullet.group(1)) + "</li>")
            continue
        flush_list()
        para.append(v)
    flush_para()
    flush_list()
    return "\n".join(rendered)


def rich_source_examples(notes_root: Path, seedance_root: Path) -> dict[str, str]:
    """Construct read-only style fixtures from TWO actual local repositories.

    ODS quote: pinned Research Packet README. Prompt: real Seedance Skill's
    curated 30-second example (author-arranged, NOT a platform-official quote).
    These are temporary Chrome previews, NOT published Capture Notes.
    """
    ods_readme = (
        notes_root / "research/github/Osmantic/ODS/snapshots"
        / "9e59b2b86c96a9590b27b14219b070007093fad1/sources/001.md"
    ).read_text(encoding="utf-8")
    statement = "No cloud required. No subscriptions required."
    if statement not in ods_readme:
        raise RuntimeError("Pinned ODS source quote is missing or changed")
    quoted = f"""
<h1>ODS 官方声明 · 来源引用预览</h1>
<p>以下是 README 的逐字短引文，适用于需要回看原始说法的场景。</p>
<h2>官方原文</h2>
<div class="callout" data-callout="gh-source">
<div class="callout-title"><div class="callout-title-inner">仓库原文 ·
<a href="https://github.com/Osmantic/ODS/blob/9e59b2b86c96a9590b27b14219b070007093fad1/README.md">README 固定版本</a></div></div>
<div class="callout-content"><p>{html.escape(statement)}</p>
<blockquote><p>中文翻译（译文，非作者原文）：无需云端、无需订阅。</p></blockquote>
</div></div>
<p>正文仍属于独立的阅读层，不意味着我们实测验证了原文说法。</p>
"""
    source_file = (
        seedance_root
        / "references/official-examples.md"
    )
    if not source_file.is_file():
        raise RuntimeError("The real prompt-bearing Seedance repository is not installed locally")
    source = source_file.read_text(encoding="utf-8")
    match = re.search(
        r"## Exact 30-second structure\s+```text\s*(.*?)\s*```",
        source, re.DOTALL,
    )
    if not match:
        raise RuntimeError("Expected curated Prompt example was not found in the source")
    prompt = match.group(1)
    if "30 秒" not in prompt or "0-3 秒" not in prompt or "27-30 秒" not in prompt:
        raise RuntimeError("The Prompt example is incomplete")
    prompt_html = f"""
<h1>Seedance 导演 Skill · 可复制 Prompt</h1>
<p>此例来自该仓库整理的示例文件，并非字节跳动官方原文。</p>
<h2>参考 Prompt 原文</h2>
<p>来源：<a href="https://github.com/liyue-aigc/seedance-2-5-video-director/blob/main/references/official-examples.md">仓库文档</a>。</p>
<pre><code class="language-prompt">{html.escape(prompt)}</code><button
 class="copy-code-button" type="button" aria-label="Copy code">复制</button></pre>
<p>以上仅作为源文本的只读视觉示例，不执行 Prompt，不验证生成效果。</p>
"""
    return {"source": quoted, "prompt": prompt_html}


def fixture(theme: str, markup: str, wide: bool) -> str:
    scheme = "light" if theme == "light" else "dark"
    colors = {
        "light": {
            "bg": "#ffffff", "text": "#23272d", "muted": "#586371", "surface": "#f5f6f8",
            "border": "#d8dde4", "accent": "#3869a4",
        },
        "dark": {
            "bg": "#1f242b", "text": "#e9eef3", "muted": "#b5beca", "surface": "#2b313a",
            "border": "#47515e", "accent": "#9fc1f0",
        },
    }[theme]
    style = f"""
:root {{
  color-scheme: {scheme};
  --background-primary:{colors['bg']}; --background-secondary:{colors['surface']};
  --background-primary-alt:{colors['surface']}; --background-modifier-border:{colors['border']};
  --background-modifier-border-hover:{colors['border']};
  --text-normal:{colors['text']}; --text-muted:{colors['muted']};
  --text-faint:{colors['muted']}; --text-accent:{colors['accent']};
  --interactive-accent:{colors['accent']};
  --font-text:'Microsoft YaHei','Segoe UI',sans-serif;
}}
* {{box-sizing:border-box}}
body {{margin:0;background:var(--background-primary);color:var(--text-normal);font-family:var(--font-text);font-size:16px}}
.markdown-preview-sizer {{margin:0 auto; max-width:{'880px' if wide else 'none'}; min-width:0;}}
.markdown-preview-view {{width:100%;min-width:0}}
a {{color:var(--text-accent)}}
pre {{max-width:100%;overflow:auto;padding:0.9rem;background:var(--background-secondary)}}
.callout {{padding:0.75rem 1rem;margin:1rem 0;border:1px solid var(--background-modifier-border);border-radius:10px;background:var(--background-secondary)}}
.callout-title {{font-weight:700}}
.copy-code-button {{position:absolute;top:0.5rem;right:0.5rem;cursor:pointer}}
"""
    return """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="%s">
<link rel="stylesheet" href="%s">
<style>%s</style></head>
<body class="theme-%s">
<article class="markdown-preview-view markdown-rendered learning-page github-note">
<div class="markdown-preview-sizer">%s</div>
</article>
<script>
window.addEventListener('load',()=> {
 const root=document.querySelector('.markdown-preview-sizer');
 const h1=document.querySelector('h1'),h2=document.querySelector('h2'),p=document.querySelector('p');
 const styles=el=>el?getComputedStyle(el):null;
 const data={
   h1FontSize:styles(h1)?.fontSize,
   h2FontSize:styles(h2)?.fontSize,
   paraLineHeight:styles(p)?.lineHeight,
   sizerMaxWidth:styles(root)?.maxWidth,
   viewportWidth:document.documentElement.clientWidth,
   totalWidth:document.documentElement.scrollWidth,
   horizontalOverflow:document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
   imageCount:document.querySelectorAll('.image-embed img').length,
   renderedH2Marker:h2?getComputedStyle(h2,'::before').content:null,
   sourceQuoteCount:document.querySelectorAll('.callout[data-callout="gh-source"]').length,
   sourceQuoteRail:getComputedStyle(document.querySelector('.callout[data-callout="gh-source"]')||document.body,'::before').content,
   promptCount:document.querySelectorAll('code.language-prompt').length,
   promptCodeMaxHeight:document.querySelector('code.language-prompt')?getComputedStyle(document.querySelector('code.language-prompt')).maxHeight:null,
   promptCodeScrollHeight:document.querySelector('code.language-prompt')?.scrollHeight||0,
   promptCodeClientHeight:document.querySelector('code.language-prompt')?.clientHeight||0,
   promptWrapped:document.querySelector('code.language-prompt')?getComputedStyle(document.querySelector('code.language-prompt')).whiteSpace:null,
   copyButtonCount:document.querySelectorAll('pre:has(code.language-prompt) .copy-code-button').length,
   copyButtonPosition:document.querySelector('pre:has(code.language-prompt) .copy-code-button')?getComputedStyle(document.querySelector('pre:has(code.language-prompt) .copy-code-button')).position:null,
   promptLabel:document.querySelector('pre:has(code.language-prompt)')?getComputedStyle(document.querySelector('pre:has(code.language-prompt)'),'::before').content:null
 };
 document.body.setAttribute('data-qa',encodeURIComponent(JSON.stringify(data)));
});
</script></body></html>""" % (CSS_CORE.as_uri(), CSS_EXTENSION.as_uri(), style, theme, markup)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", help="Print base64 of a screenshot for inspection")
    parser.add_argument("--offset", type=int, default=0, help="Base64 output offset")
    parser.add_argument("--limit", type=int, default=85000, help="Output chunk length")
    parser.add_argument("--only", choices=("ods", "legacy", "source", "prompt"), help="Smoke-test one category (default: all 10 scenarios)")
    parser.add_argument("--github-root", type=Path, help="Local GitHub learning project (or GITHUB_LEARNING_ROOT)")
    parser.add_argument("--seedance-root", type=Path, help="Local Seedance director sample (or SEEDANCE_DIRECTOR_ROOT)")
    options = parser.parse_args()
    if options.emit:
        image = Path(options.emit).resolve()
        if not image.name.startswith("github-note-") or image.suffix not in {".png", ".jpg"} or not image.is_file():
            raise SystemExit("Invalid screenshot")
        encoded = base64.b64encode(image.read_bytes()).decode("ascii")
        sys.stdout.write(encoded[options.offset : options.offset + options.limit])
        return 0
    github_value = options.github_root or os.environ.get("GITHUB_LEARNING_ROOT")
    seedance_value = options.seedance_root or os.environ.get("SEEDANCE_DIRECTOR_ROOT")
    if not github_value or not seedance_value:
        raise SystemExit("Real source fixtures require --github-root and --seedance-root (or environment variables)")
    notes_root = Path(github_value).expanduser().resolve()
    seedance_root = Path(seedance_value).expanduser().resolve()
    source_note = notes_root / "docs" / "ODS-NATURAL-PRODUCT-V2.2-REFERENCE.md"
    legacy_note = notes_root / "notes" / "github" / "00-待整理" / "bili-learning-automation.md"
    if not source_note.is_file() or not legacy_note.is_file():
        raise SystemExit("Explicit project fixtures are missing; do not invent replacement notes")
    exe = next((x for x in BROWSERS if x.is_file()), None)
    if exe is None:
        raise SystemExit("No local Chromium browser is available")
    root = Path(tempfile.mkdtemp(prefix="github-note-css-qa-"))
    cases = [
        ("ods", "light", True, 1366, 1230, source_note),
        ("ods", "dark", True, 1366, 1230, source_note),
        ("ods", "light", False, 590, 1100, source_note),
        ("ods", "dark", False, 590, 1100, source_note),
        ("legacy", "light", True, 1366, 1150, legacy_note),
        ("legacy", "dark", False, 590, 1000, legacy_note),
        ("source", "light", True, 1366, 1050, None),
        ("source", "dark", False, 590, 1050, None),
        ("prompt", "light", True, 1366, 1050, None),
        ("prompt", "dark", False, 590, 1050, None),
    ]
    if options.only:
        cases = [case for case in cases if case[0] == options.only]
    rich = rich_source_examples(notes_root, seedance_root)
    results = []
    for kind, theme, wide, width, height, source in cases:
        stem = f"github-note-{kind}-{theme}-{'wide' if wide else 'narrow'}"
        page = root / (stem + ".html")
        png = root / (stem + ".png")
        markup = rich[kind] if kind in rich else to_simple_html(source.read_text(encoding="utf-8"), notes_root)
        page.write_text(fixture(theme, markup, wide), encoding="utf-8")
        proc = subprocess.run(
            [str(exe),"--headless=new","--disable-gpu","--no-first-run","--hide-scrollbars",
             f"--window-size={width},{height}",f"--screenshot={png}",
             f"--user-data-dir={root / 'chrome-profile'}",page.as_uri()],
            capture_output=True,text=True,timeout=45,encoding="utf-8",errors="replace",
        )
        jpg = png.with_suffix(".jpg")
        if png.exists():
            # GDI+ ships with Windows; this is only a lightweight internal
            # visual QA export, never a dependency of the user's Obsidian setup.
            src = str(png).replace("'", "''")
            dst = str(jpg).replace("'", "''")
            convert = (
                "Add-Type -AssemblyName System.Drawing;"
                f"$i=[System.Drawing.Image]::FromFile('{src}');"
                "try {"
                "$f=[Math]::Min(1.0,900.0/$i.Width);"
                "$w=[int][Math]::Round($i.Width*$f);$h=[int][Math]::Round($i.Height*$f);"
                "$b=New-Object System.Drawing.Bitmap -ArgumentList @($w,$h);"
                "try {"
                "$g=[System.Drawing.Graphics]::FromImage($b);"
                "try {$g.InterpolationMode='HighQualityBicubic';$g.DrawImage($i,0,0,$w,$h)}"
                "finally {$g.Dispose()};"
                f"$b.Save('{dst}',[System.Drawing.Imaging.ImageFormat]::Jpeg)"
                "} finally {$b.Dispose()}"
                "} finally {$i.Dispose()}"
            )
            subprocess.run(["powershell.exe","-NoProfile","-Command",convert],
                           capture_output=True,text=True,timeout=35)
        # Assert CSS-computed layout, not merely the existence of screenshot files.
        dumped = subprocess.run(
            [str(exe),"--headless=new","--no-first-run","--virtual-time-budget=750",
             f"--window-size={width},{height}",
             f"--user-data-dir={root / 'chrome-profile'}","--dump-dom",page.as_uri()],
            capture_output=True,text=True,timeout=45,encoding="utf-8",errors="replace",
        )
        found = re.search(r'data-qa="([^"]+)"', dumped.stdout)
        computed = json.loads(unquote(html.unescape(found.group(1)))) if found else {}
        if not computed:
            raise RuntimeError(f"Could not obtain browser-computed CSS metrics for {stem}")
        if computed.get("horizontalOverflow"):
            raise RuntimeError(f"Unexpected horizontal overflow in {stem}: {computed}")
        def pixels(value: str) -> float:
            return float(value.removesuffix("px"))
        if pixels(computed["h1FontSize"]) <= pixels(computed["h2FontSize"]) + 3:
            raise RuntimeError(f"Heading hierarchy is not clear in {stem}: {computed}")
        if not 1.55 <= pixels(computed["paraLineHeight"]) / 16.0 <= 1.9:
            raise RuntimeError(f"Body line height out of expected editorial range in {stem}: {computed}")
        if wide and computed["sizerMaxWidth"] != "880px":
            raise RuntimeError(f"Obsidian reading-width authority was overridden in {stem}: {computed}")
        if not wide and computed["sizerMaxWidth"] != "none":
            raise RuntimeError(f"Narrow reading width was overridden in {stem}: {computed}")
        if computed["imageCount"] != (1 if kind == "ods" else 0):
            raise RuntimeError(f"Cover image count changed in {stem}: {computed}")
        if kind == "source":
            if computed["sourceQuoteCount"] != 1 or computed["sourceQuoteRail"] != '""':
                raise RuntimeError(f"The gh-source citation styling did not apply: {computed}")
            if computed["promptCount"] or computed["copyButtonCount"]:
                raise RuntimeError(f"A normal source quote became a Prompt: {computed}")
        if kind == "prompt":
            if computed["promptCount"] != 1 or computed["copyButtonCount"] != 1:
                raise RuntimeError(f"Original Prompt or native copy control missing: {computed}")
            if computed["promptCodeMaxHeight"] != "320px" or computed["promptWrapped"] != "pre-wrap":
                raise RuntimeError(f"Prompt overflow/wrapping rules did not apply: {computed}")
            if computed["copyButtonPosition"] != "absolute" or computed["promptLabel"] != '"PROMPT"':
                raise RuntimeError(f"Prompt header/copy-button layout did not apply: {computed}")
            if not wide and computed["promptCodeScrollHeight"] <= computed["promptCodeClientHeight"]:
                raise RuntimeError(f"Long Prompt did not scroll inside the narrow view: {computed}")
        results.append({"case":stem, "computed":computed, "returncode":proc.returncode, "screenshot":str(png),
                        "bytes":png.stat().st_size if png.exists() else 0,
                        "preview_jpg":str(jpg) if jpg.exists() else "",
                        "jpeg_bytes":jpg.stat().st_size if jpg.exists() else 0,
                        "error":proc.stderr[-300:] if not png.exists() else ""})
    print(json.dumps({"output_dir":str(root), "browser":str(exe), "cases":results},ensure_ascii=False,indent=2))
    return 0 if all(v["bytes"] > 5000 for v in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
