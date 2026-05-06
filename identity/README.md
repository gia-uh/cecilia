# Cecilia — Visual Identity

This is the canonical visual identity package for Cecilia. It is organised in three layers:

```
identity/
  canon.md              # narrative + voice + register rules
  model-sheet.md        # rigid character canon (mulata, guayabera, gaze, earrings)
  palette.yml           # color tokens (sampled from the canonical bust) + WCAG pairs
  typography.yml        # Fraunces (display) + Inter (body)
  references/
    cecilia-logo.jpg    # the canonical bust (used as visual anchor for renders)
  projects/             # mosaico project YAMLs (API-driven renders)
    hero.yml            # full-body canonical hero
    utility.yml         # geometric icon set
    character-bible.yml # turnaround sheet + expression sheet
  bin/
    derive_assets.py    # PIL-driven derivations (resize, crop, BW, wordmark SVGs, favicons)
  out/                  # rendered + derived deliverables
    hero/               # portrait-canonical-{1024,1200x630}, portrait-bw, cecilia-fullbody-canonical
    utility/            # icon-sheet + per-slug cells, wordmark/lockup SVGs, favicons
    character-bible/    # turnaround-sheet, expression-sheet
```

## What's in v1

**Hero register** (illustrated, character-led):
- `out/hero/cecilia-fullbody-canonical.jpg` — new full-body render in guayabera (introduces the wardrobe canon).
- `out/hero/portrait-canonical-1024.jpg` — the canonical bust at 1024×1024.
- `out/hero/portrait-canonical-1200x630.jpg` — social-card crop.
- `out/hero/portrait-bw.jpg` — monochrome bust for low-color-budget surfaces.

**Utility register** (geometric, scalable):
- `out/utility/icon-sheet.jpg` + `out/utility/icon-sheet/cells/{speech-bubble,open-book,code-brackets,spark,network-nodes,forward-arrow}.jpg` — six geometric icons.
- `out/utility/wordmark{,-mono,-reverse}.svg` — "Cecilia" in Fraunces.
- `out/utility/lockup-{horizontal,stacked}{,-mono}.svg` — mark + wordmark.
- `out/utility/favicon-{32,16}.png` — face crops.

**Character bible** (the constraint scaffold for v2):
- `out/character-bible/turnaround-sheet.jpg` — front / 3-quarter / side.
- `out/character-bible/expression-sheet.jpg` — eight expressions including the canonical upward gaze.

## How to regenerate

API-driven artifacts (mosaico):

```bash
cd identity
mosaico render projects/hero.yml --save=true
mosaico render projects/utility.yml --save=true
mosaico render projects/character-bible.yml --save=true
```

Deterministic derivations (PIL):

```bash
cd identity
uv run --with pillow python bin/derive_assets.py
```

The mosaico runs are content-addressed — only artifacts whose prompt or refs changed will re-render.

## Where to read first

- For a new contributor or AI agent producing a new asset: read [`canon.md`](canon.md), then [`model-sheet.md`](model-sheet.md), then look at `references/cecilia-logo.jpg`. The mosaico project YAMLs embed the model-sheet content verbatim — they are the operationalised canon.

## Known limitations

- **Mosaico cropper fails on dense character sheets.** The cell auto-crop in `mosaico render` is content-aware and assumes content-on-empty-bg; when cells are densely filled (face/hair/dress sharing connected pixels across cell boundaries), the cropper writes warnings and skips cells. The character-bible sheets (turnaround, expression) are usable as whole-sheet references; per-cell extraction would need a manual grid-cut. Filed as a separate mosaico issue.
- **Wordmark SVGs reference Fraunces by font name.** Consumers (HTML, Quarto, slides) must have Fraunces installed locally or load it via `<link>` to Google Fonts. No font is embedded in the SVG.

## Spec

Full design at `vault/Atlas/Architecture/2026-05-06-cecilia-visual-identity-design.md`.

## v2 (deferred)

Secondary stylistic registers — retro-futurist (Alex's first v2 ask), anime, Cuban comics, children's-book illustration — are deferred. They will be added by writing new mosaico project YAMLs against this canon. The character bible is what makes those v2 registers stay on-model.
