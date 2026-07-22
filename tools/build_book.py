#!/usr/bin/env python3
"""Build the story book editions from the markdown source.

Usage:
    python3 tools/build_book.py --html --txt --pdf --out build/

With no format flags, all three are built. Outputs:
    <out>/index.html               typeset single-page edition
    <out>/ham-radio-storybook.txt  plain-text edition
    <out>/ham-radio-storybook.pdf  PDF edition (best-effort)

PDF rendering tries a headless Chromium/Chrome binary first, falling back to
weasyprint, and is skipped (non-fatal) if neither is available.

Chapter markdown format: body text may contain "{{fig:NAME}}" on its own line
to inline figures/NAME.svg with the caption from FIGS below. The plain-text
edition renders a one-line caption instead.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "ham-radio-storybook.md"
FIGDIR = ROOT / "figures"

# figure name -> caption (files live in figures/<name>.svg)
FIGS = {
    "shack": "Grandpa's radio shack — glowing dials, headphones, and a wire antenna out the window.",
    "waves": "Slow, long ripples and quick, short ripples. HF waves are the quick, short ones!",
    "skip": "The signal skips off the ionosphere — plip, plip, plip — all the way to Australia!",
    "bands": "The band parade. Every ham band has its own personality.",
    "globe": "Monday night for Mia, tomorrow morning for Bruce — one skip across the world.",
    "cq": "CQ, CQ, CQ… the newest ham on the air.",
}

_CHROME_BINARIES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "headless_shell",
)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mia and the Sky-Skipping Radio</title>
<style>
  :root {{ color-scheme: light; }}
  body {{
    font-family: Georgia, "DejaVu Serif", serif;
    line-height: 1.65;
    color: #222;
    max-width: 42em;
    margin: 0 auto;
    padding: 2em 1.2em 4em;
    background: #fdfcf7;
  }}
  h1 {{
    text-align: center;
    font-size: 2em;
    margin: 1.2em 0 0.2em;
    color: #1a3a6b;
  }}
  h1 + p em {{ display: block; text-align: center; }}
  h2 {{
    font-size: 1.35em;
    margin-top: 1.8em;
    color: #1a3a6b;
    border-bottom: 2px solid #d8cfae;
    padding-bottom: 0.25em;
  }}
  h2 + p::first-letter {{
    font-size: 2.6em;
    float: left;
    line-height: 0.85;
    padding: 0.06em 0.12em 0 0;
    color: #1a3a6b;
  }}
  hr {{
    border: none;
    text-align: center;
    margin: 2.5em 0;
  }}
  hr::after {{ content: "\\2736  \\2736  \\2736"; color: #b3a265; letter-spacing: 1em; }}
  ul {{ padding-left: 1.4em; }}
  li {{ margin-bottom: 0.5em; }}
  strong {{ color: #1a3a6b; }}
  figure {{ margin: 2em 0; text-align: center; }}
  figure svg {{
    max-width: 100%;
    height: auto;
    border: 2px solid #d8cfae;
    border-radius: 12px;
  }}
  figcaption {{
    font-style: italic;
    color: #666;
    font-size: 0.9em;
    margin-top: 0.5em;
  }}
  .listen {{ text-align: center; font-size: 0.85em; margin-top: -0.4em; }}
  @media print {{
    body {{ background: white; }}
    h2 {{ page-break-before: always; margin-top: 0; }}
    h2:first-of-type {{ page-break-before: avoid; }}
    h1 + p em {{ display: block; }}
    figure {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

_FIG_RE = re.compile(r"\{\{fig:([a-z0-9_-]+)\}\}")


def _fig_html(match: re.Match) -> str:
    name = match.group(1)
    svg_path = FIGDIR / f"{name}.svg"
    caption = FIGS.get(name, "")
    if not svg_path.exists():
        print(f"warning: figure {svg_path} not found - skipped")
        return ""
    svg = svg_path.read_text(encoding="utf-8").strip()
    return f"<figure>{svg}<figcaption>{caption}</figcaption></figure>"


def build_html(md_text: str, out_html: pathlib.Path) -> pathlib.Path:
    import markdown

    md_text = _FIG_RE.sub(_fig_html, md_text)
    body = markdown.markdown(md_text)
    # Link to the audiobook player (served by the Docker image at /audiobook/).
    subtitle = "<p><em>A ham radio adventure for young readers</em></p>"
    if subtitle in body:
        body = body.replace(
            subtitle,
            subtitle + '\n<p class="listen"><a href="/audiobook/">🎧 Listen to the audiobook</a></p>',
            1,
        )
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(HTML_TEMPLATE.format(body=body), encoding="utf-8")
    print(f"wrote {out_html}")
    return out_html


def build_txt(md_text: str, out_txt: pathlib.Path) -> pathlib.Path:
    md_text = _FIG_RE.sub(lambda m: f"\n[ Picture: {FIGS.get(m.group(1), m.group(1))} ]\n", md_text)
    lines = []
    for raw in md_text.splitlines():
        line = raw.rstrip()
        if line.strip() == "---":
            lines.append("                *  *  *")
            continue
        line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)   # bold
        line = re.sub(r"\*(.+?)\*", r"\1", line)       # italic
        line = re.sub(r"^- ", r"* ", line)             # list bullets
        if line.startswith("# "):
            line = line[2:].upper()
        elif line.startswith("## "):
            line = "\n" + line[3:] + "\n" + "-" * min(len(line[3:]), 60)
        lines.append(line)

    out_txt.parent.mkdir(parents=True, exist_ok=True)
    out_txt.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(f"wrote {out_txt}")
    return out_txt


def build_pdf(html_path: pathlib.Path, out_pdf: pathlib.Path) -> bool:
    """Best-effort PDF rendering of the built HTML file. Non-fatal on failure."""
    html_path = html_path.resolve()
    out_pdf = out_pdf.resolve()
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    for binary in _CHROME_BINARIES:
        exe = shutil.which(binary)
        if not exe:
            continue
        cmd = [
            exe,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={out_pdf}",
            f"file://{html_path}",
        ]
        try:
            subprocess.run(cmd, capture_output=True, timeout=120)
        except Exception:
            continue
        if out_pdf.exists() and out_pdf.stat().st_size > 0:
            print(f"wrote {out_pdf} (via {binary})")
            return True

    try:
        import weasyprint  # type: ignore

        weasyprint.HTML(filename=str(html_path)).write_pdf(str(out_pdf))
        if out_pdf.exists() and out_pdf.stat().st_size > 0:
            print(f"wrote {out_pdf} (via weasyprint)")
            return True
    except Exception:
        pass

    print("PDF skipped: no chromium/weasyprint")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", action="store_true", help="build the HTML edition")
    parser.add_argument("--txt", action="store_true", help="build the plain-text edition")
    parser.add_argument("--pdf", action="store_true", help="build the PDF edition (best-effort)")
    parser.add_argument("--out", default="build", help="output directory (default: build)")
    args = parser.parse_args()

    if not (args.html or args.txt or args.pdf):
        args.html = args.txt = args.pdf = True

    out_dir = pathlib.Path(args.out)
    md_text = SRC.read_text(encoding="utf-8")

    html_path = out_dir / "index.html"
    if args.html or args.pdf:
        build_html(md_text, html_path)
    if args.txt:
        build_txt(md_text, out_dir / "ham-radio-storybook.txt")
    if args.pdf:
        build_pdf(html_path, out_dir / "ham-radio-storybook.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main())
