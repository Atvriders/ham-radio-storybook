#!/usr/bin/env python3
"""Build ham-radio-storybook.html and ham-radio-storybook.txt from the markdown source."""
import re
from pathlib import Path

import markdown

SRC = Path(__file__).resolve().parent / "ham-radio-storybook.md"
md_text = SRC.read_text(encoding="utf-8")

# ---------- HTML ----------
body = markdown.markdown(md_text)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mia and the Radio That Bounced Off the Sky</title>
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
  em {{ color: inherit; }}
  strong {{ color: #1a3a6b; }}
  @media print {{
    body {{ background: white; }}
    h2 {{ page-break-before: always; margin-top: 0; }}
    h2:first-of-type {{ page-break-before: avoid; }}
    h1 + p em {{ display: block; }}
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

SRC.with_suffix(".html").write_text(html, encoding="utf-8")

# ---------- TXT ----------
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

txt = "\n".join(lines).strip() + "\n"
SRC.with_suffix(".txt").write_text(txt, encoding="utf-8")

print("Wrote", SRC.with_suffix(".html"))
print("Wrote", SRC.with_suffix(".txt"))
