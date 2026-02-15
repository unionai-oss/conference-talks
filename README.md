# Conference Talks

This repo uses [Slidev](https://sli.dev) to create and present slides from Markdown.

## Quick start

```bash
npm install
npm run dev
```

Then open the URL shown in the terminal (default: http://localhost:3030).

### Commands (from repo root)

| Command | Description |
|--------|-------------|
| `npm run dev` | Start dev server for sample talk and open in browser |
| `npm run build` | Build sample talk as static site (e.g. for hosting) |
| `npm run export` | Export sample talk to PDF, PPTX, or PNGs |

## Adding a new talk

1. Copy `sample-talk/` to a new folder (e.g. `my-talk/`).
2. Edit `slides.md` in that folder with your content.
3. Add scripts in root `package.json` (e.g. `"dev:my-talk": "slidev my-talk/slides.md --open"`) and run `npm run dev:my-talk`.

Slides are written in Markdown; use `---` to separate slides. See the [Slidev guide](https://sli.dev/guide/) for syntax and options.
