#!/usr/bin/env python3
"""Build the audiobook edition of the story book with edge-tts.

Splits ham-radio-storybook.md into chapters, prepares each for narration
(strips markup, spells call signs and radio acronyms), and synthesizes one
MP3 per chapter into audiobook/.

Usage:
    python tools/make_audiobook.py              # all chapters
    python tools/make_audiobook.py --chapters 1-3
    python tools/make_audiobook.py --test       # short sample of chapter 1

Needs edge-tts (pip install edge-tts). Resumable: a chapter whose MP3 already
exists (> 20 KB) is skipped unless --force is given.
"""
from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

import edge_tts

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "ham-radio-storybook.md"
OUT = REPO / "audiobook"

VOICE = "en-US-AvaNeural"
RATE = "-8%"  # a touch slower, for young listeners

NUMBER_WORDS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten",
}

# Spoken forms for radio jargon.
ACRONYMS = {
    "HF": "H F",
    "DX": "D X",
    "CQ": "C Q",
    "QSL": "Q S L",
    "MHz": "megahertz",
}

CALLSIGN_RE = re.compile(r"\b([A-Z]{1,3}\d[A-Z]{1,3})\b")


def split_chapters(md_text: str) -> list[tuple[int, str, str]]:
    """Return [(number, heading, body)] for each '## Chapter N: Heading' section."""
    parts = re.split(r"^## Chapter (\d+): (.+)$", md_text, flags=re.M)
    chapters = []
    # parts = [preamble, num, heading, body, num, heading, body, ...]
    for i in range(1, len(parts), 3):
        num = int(parts[i])
        heading = parts[i + 1].strip()
        body = parts[i + 2]
        body = body.split("\n---", 1)[0]  # drop trailing rule / next section marker
        chapters.append((num, heading, body))
    return chapters


def prepare_text(body: str) -> str:
    text = re.sub(r"\{\{fig:[^}]+\}\}", "", body)      # pictures aren't narrated
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)       # bold
    text = re.sub(r"\*(.+?)\*", r"\1", text)           # italic
    for acr, spoken in ACRONYMS.items():
        text = re.sub(rf"\b{acr}\b", spoken, text)
    # Call signs like VK3ALM -> "V K three A L M"
    text = CALLSIGN_RE.sub(
        lambda m: " ".join(c if not c.isdigit() else c for c in m.group(1)), text
    )
    text = re.sub(r"^\s*\*\s*\*\s*\*\s*$", "...", text, flags=re.M)  # scene break
    text = re.sub(r"\s*\n\s*\n\s*", "\n\n", text)
    return text.strip()


async def synthesize(text: str, out_path: Path) -> None:
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(str(out_path))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapters", default=None, help="e.g. 1-3 or 2,4 (default: all)")
    parser.add_argument("--force", action="store_true", help="rebuild existing MP3s")
    parser.add_argument("--test", action="store_true", help="synthesize a short sample and exit")
    args = parser.parse_args()

    md_text = SRC.read_text(encoding="utf-8")
    chapters = split_chapters(md_text)
    if not chapters:
        print("no chapters found in", SRC)
        return 1

    if args.chapters:
        wanted = set()
        for part in args.chapters.split(","):
            if "-" in part:
                a, b = part.split("-", 1)
                wanted.update(range(int(a), int(b) + 1))
            else:
                wanted.add(int(part))
        chapters = [c for c in chapters if c[0] in wanted]

    OUT.mkdir(exist_ok=True)

    if args.test:
        num, heading, body = chapters[0]
        sample = prepare_text(body)[:400]
        out = OUT / "sample.mp3"
        asyncio.run(synthesize(f"Chapter {NUMBER_WORDS[num]}. {heading}. {sample}", out))
        print("wrote", out)
        return 0

    for num, heading, body in chapters:
        out = OUT / f"ch{num}.mp3"
        if out.exists() and out.stat().st_size > 20_000 and not args.force:
            print(f"skip ch{num} (exists)")
            continue
        spoken = f"Chapter {NUMBER_WORDS[num]}. {heading}.\n\n" + prepare_text(body)
        for attempt in range(3):
            try:
                asyncio.run(synthesize(spoken, out))
                break
            except Exception as e:
                if attempt == 2:
                    print(f"ch{num} FAILED: {e}")
                    return 1
                print(f"ch{num} retry {attempt + 1}: {e}")
        print(f"wrote {out} ({out.stat().st_size // 1024} KB)")

    print("done. tracks:", len(list(OUT.glob('ch*.mp3'))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
