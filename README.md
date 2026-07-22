# Mia and the Radio That Bounced Off the Sky

*A ham radio story book for children — HF, skywave skip, and the bands.*

Mia discovers her grandpa's radio shack and learns how HF shortwave signals
skip off the ionosphere like stones across a pond — and why each ham band has
its own personality. Six short chapters plus a glossary for young hams.

## Formats

The source is [`ham-radio-storybook.md`](ham-radio-storybook.md). The typeset
editions are built from it by CI into `build/` (not stored in git):

| File | What it is |
|---|---|
| `build/index.html` | The book as a single self-contained page. The nicest way to read it. |
| `build/ham-radio-storybook.pdf` | PDF edition, one chapter per page. |
| `build/ham-radio-storybook.txt` | Plain-text edition. |
| [`Dockerfile`](Dockerfile) / [`docker-compose.yml`](docker-compose.yml) | Serve the book yourself — see below. |

## Docker

The image packages the book behind nginx, built and pushed to
`ghcr.io/atvriders/ham-radio-storybook` by CI on every push to `main`.
On any Docker host:

```sh
docker compose pull && docker compose up -d
```

Serves the book at [http://localhost:3024](http://localhost:3024).

To build locally instead:

```sh
pip install -r requirements.txt
python3 tools/build_book.py --html --txt --pdf --out build/
docker build -t ghcr.io/atvriders/ham-radio-storybook:latest .
```
