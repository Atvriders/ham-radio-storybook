#!/usr/bin/env python3
"""Build the spoken introduction for the audiobook with edge-tts.

The intro tells listeners how this book was made (and by what), how long it
took, and why it exists. Writes audiobook/intro.mp3, published as a release
asset alongside the chapter tracks.

Usage:
    python tools/make_intro.py            # writes audiobook/intro.mp3
    python tools/make_intro.py --force    # rebuild even if it exists
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.make_audiobook import OUT, synthesize

INTRO = """
Hello! Before our story begins, here is something special about how this book
was made.

Mia and the Sky-Skipping Radio was written by an artificial intelligence, an
AI called Kimi, on July twenty-second, twenty twenty-six. In a single working
session, the AI wrote the whole story, drew all six pictures, built the
website you are listening on, and set up the machines that build and publish
this book around the world. Even the voice you are hearing right now is an AI
voice, named Ava.

How long did all of that take? The whole project took about forty-eight
minutes — and the story itself was written in one try, in about two minutes.
The AI used about twelve million tokens along the way. Tokens are how an AI
counts all the little pieces of words it reads and writes.

And why was this book made? To share the magic of ham radio with young
listeners — how a tiny signal can skip off the sky, cross an ocean, and land
in somebody's morning on the other side of the world. And maybe, just maybe,
to help a few brand-new hams get on the air one day.

Seventy-three — that means best wishes, in ham talk. And now, enjoy the story!
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    OUT.mkdir(exist_ok=True)
    out = OUT / "intro.mp3"
    if out.exists() and out.stat().st_size > 20_000 and not args.force:
        print("skip intro (exists)")
        return 0
    asyncio.run(synthesize(" ".join(INTRO.split()), out))
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
