# Mia and the Radio That Bounced Off the Sky

*A ham radio story book for children — HF, skywave skip, and the bands.*

Mia discovers her grandpa's radio shack and learns how HF shortwave signals
skip off the ionosphere like stones across a pond — and why each ham band has
its own personality. Six short chapters plus a glossary for young hams —
with hand-drawn illustrations and a narrated audiobook.

## How it was made

Written by **Kimi** (model `kimi-code/k3`) running in Kimi Code CLI on
**22 July 2026**, in a single interactive session that also produced the
typeset editions, this GitHub repo, and the Docker/CI pipeline. Sibling
project: **[200 Meters and Down](https://github.com/Atvriders/200-meters-and-down)**,
whose build machinery this repo reuses.

| | |
|---|---|
| **Sections** | 6 chapters + glossary |
| **Words** | 2,254 |
| **Illustrations** | 6 (hand-authored SVG, inlined at build time) |
| **Audiobook** | 6 tracks, ≈ 13 min total (edge-tts, voice `en-US-AvaNeural`) |
| **Model turns** | 172 (story, tooling, figures, audiobook, file ops, CI setup) |
| **Output tokens** | ≈ 151,000 — everything the model wrote |
| **Total API tokens** | ≈ 11.8 million, summed over all turns (the agent re-reads the growing conversation every turn; nearly all input was served from cache) |
| **Wall time** | ≈ 48 min for the whole project; the story draft itself was one pass, ≈ 2 min |

Measured at ship from the session's wire-log `usage` records.

## Formats

The source is [`ham-radio-storybook.md`](ham-radio-storybook.md). The typeset
editions are built from it by CI into `build/` (not stored in git):

| File | What it is |
|---|---|
| `build/index.html` | The book as a single self-contained page, with the six illustrations inline. The nicest way to read it. |
| `build/ham-radio-storybook.pdf` | PDF edition, one chapter per page, illustrations included. |
| `build/ham-radio-storybook.txt` | Plain-text edition. |
| Audiobook ([release v1.0](https://github.com/Atvriders/ham-radio-storybook/releases/tag/v1.0)) | One MP3 per chapter (`ch1.mp3` … `ch6.mp3`), narrated with [edge-tts](https://pypi.org/project/edge-tts/) (voice `en-US-AvaNeural`) via [`tools/make_audiobook.py`](tools/make_audiobook.py). Not stored in git. |
| [`figures/`](figures/) | The six illustrations as hand-authored SVG, inlined into the HTML/PDF editions at build time. |
| [`Dockerfile`](Dockerfile) / [`docker-compose.yml`](docker-compose.yml) | Serve the book yourself — see below. |

## Docker

The image packages the book and the audiobook behind nginx, built and pushed to
`ghcr.io/atvriders/ham-radio-storybook` by CI on every push to `main`.
On any Docker host:

```sh
docker compose pull && docker compose up -d
```

Serves the book at [http://localhost:3024](http://localhost:3024) and the
audiobook player at `/audiobook/`.

To build locally instead: regenerate the typeset editions, fetch the audiobook
from the release (it is not stored in git), then build the image:

```sh
pip install -r requirements.txt
python3 tools/build_book.py --html --txt --pdf --out build/
# fetch audiobook/ from release v1.0 (see .github/workflows/build.yml), then:
docker build -t ghcr.io/atvriders/ham-radio-storybook:latest .
```
