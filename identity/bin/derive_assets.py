"""Derive non-API assets for the Cecilia visual identity.

Produces deterministic, transformation-only artifacts that don't justify an
API call. mosaico handles the API-driven artifacts (full-body hero, icon
sheet, character bible). This script handles:

  * Bust derivations (resize, social-card crop, monochrome).
  * Wordmark + lockup SVGs (font-referenced — Fraunces).
  * Favicons (downsampled from the bust).

Run from the identity/ directory:

    cd repos/cecilia/identity
    uv run --with pillow python bin/derive_assets.py

Idempotent. Safe to re-run.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

IDENTITY = Path(__file__).resolve().parent.parent
BUST_REF = IDENTITY / "references" / "cecilia-logo.jpg"
HERO_OUT = IDENTITY / "out" / "hero"
UTILITY_OUT = IDENTITY / "out" / "utility"


def derive_bust() -> None:
    """Resize / crop / desaturate the canonical bust into delivery sizes."""
    img = Image.open(BUST_REF).convert("RGB")
    HERO_OUT.mkdir(parents=True, exist_ok=True)

    # 1024x1024 canonical (the bust is already 1024x1024; resize is a no-op
    # but documented here for completeness).
    if img.size != (1024, 1024):
        sized = img.resize((1024, 1024), Image.Resampling.LANCZOS)
    else:
        sized = img
    sized.save(HERO_OUT / "portrait-canonical-1024.jpg", "JPEG", quality=92)

    # 1200x630 social-card crop. The bust is square; crop the top-center
    # band so the face stays in frame.
    src = img
    w, h = src.size
    target_aspect = 1200 / 630
    src_aspect = w / h
    if src_aspect > target_aspect:
        # source too wide — crop sides
        new_w = int(h * target_aspect)
        x0 = (w - new_w) // 2
        cropped = src.crop((x0, 0, x0 + new_w, h))
    else:
        # source too tall — crop top + bottom (keep top-biased to retain face)
        new_h = int(w / target_aspect)
        # Bias 30% from the top so the face stays in the frame.
        y0 = (h - new_h) // 3
        cropped = src.crop((0, y0, w, y0 + new_h))
    cropped.resize((1200, 630), Image.Resampling.LANCZOS).save(
        HERO_OUT / "portrait-canonical-1200x630.jpg", "JPEG", quality=92
    )

    # Monochrome desaturation for low-color-budget surfaces.
    bw = ImageOps.grayscale(img).convert("RGB")
    bw.save(HERO_OUT / "portrait-bw.jpg", "JPEG", quality=92)


def derive_favicons() -> None:
    """Downsample the canonical bust into favicon sizes."""
    img = Image.open(BUST_REF).convert("RGB")
    UTILITY_OUT.mkdir(parents=True, exist_ok=True)

    # Center-crop a tighter face region for the favicon (the full bust is
    # too zoomed-out at 16x16 to be readable).
    w, h = img.size
    # Heuristic: face occupies the upper-middle ~50% of the bust. Crop a
    # square centered on (w*0.55, h*0.35) with side 0.55*h.
    side = int(0.55 * h)
    cx, cy = int(w * 0.55), int(h * 0.35)
    x0 = max(0, cx - side // 2)
    y0 = max(0, cy - side // 2)
    face = img.crop((x0, y0, x0 + side, y0 + side))

    for size in (32, 16):
        small = face.resize((size, size), Image.Resampling.LANCZOS)
        small.save(UTILITY_OUT / f"favicon-{size}.png", "PNG")


# SVG wordmark / lockup. Font is referenced by name (Fraunces). Downstream
# consumers should embed Fraunces via @font-face or <link> in their HTML;
# print/PDF consumers should have Fraunces installed locally.

WORDMARK_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 200" role="img"
     aria-label="Cecilia wordmark">
  <style>
    .word {{ font-family: 'Fraunces', 'Fraunces-VariableFont', serif;
             font-weight: 700; font-size: 144px;
             font-variation-settings: 'opsz' 144;
             fill: {color}; }}
  </style>
  <text x="50%" y="68%" text-anchor="middle" class="word">Cecilia</text>
</svg>
"""

LOCKUP_HORIZONTAL_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 1000 280" role="img" aria-label="Cecilia logo with mark">
  <style>
    .word {{ font-family: 'Fraunces', serif; font-weight: 700;
             font-size: 144px; font-variation-settings: 'opsz' 144;
             fill: {color}; }}
  </style>
  <image href="../hero/portrait-canonical-1024.jpg" x="0" y="0" width="280" height="280"
         preserveAspectRatio="xMidYMid slice" clip-path="url(#round)" />
  <clipPath id="round">
    <circle cx="140" cy="140" r="140" />
  </clipPath>
  <text x="320" y="180" class="word">Cecilia</text>
</svg>
"""

LOCKUP_STACKED_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 600 720" role="img" aria-label="Cecilia stacked logo">
  <style>
    .word {{ font-family: 'Fraunces', serif; font-weight: 700;
             font-size: 120px; font-variation-settings: 'opsz' 120;
             fill: {color}; text-anchor: middle; }}
  </style>
  <image href="../hero/portrait-canonical-1024.jpg" x="100" y="0" width="400" height="400"
         preserveAspectRatio="xMidYMid slice" clip-path="url(#round-stacked)" />
  <clipPath id="round-stacked">
    <circle cx="300" cy="200" r="200" />
  </clipPath>
  <text x="300" y="560" class="word">Cecilia</text>
</svg>
"""


def derive_wordmarks() -> None:
    UTILITY_OUT.mkdir(parents=True, exist_ok=True)

    sienna = "#692705"   # warm-sienna (palette skin.shadow) — primary brand color for type
    black = "#000000"    # mono variant
    white = "#ffffff"    # for use on dark grounds

    (UTILITY_OUT / "wordmark.svg").write_text(WORDMARK_SVG.format(color=sienna))
    (UTILITY_OUT / "wordmark-mono.svg").write_text(WORDMARK_SVG.format(color=black))
    (UTILITY_OUT / "wordmark-reverse.svg").write_text(WORDMARK_SVG.format(color=white))

    (UTILITY_OUT / "lockup-horizontal.svg").write_text(
        LOCKUP_HORIZONTAL_SVG.format(color=sienna)
    )
    (UTILITY_OUT / "lockup-horizontal-mono.svg").write_text(
        LOCKUP_HORIZONTAL_SVG.format(color=black)
    )

    (UTILITY_OUT / "lockup-stacked.svg").write_text(
        LOCKUP_STACKED_SVG.format(color=sienna)
    )
    (UTILITY_OUT / "lockup-stacked-mono.svg").write_text(
        LOCKUP_STACKED_SVG.format(color=black)
    )


def main() -> None:
    derive_bust()
    derive_favicons()
    derive_wordmarks()
    print(f"derived assets written under {HERO_OUT.parent}/")


if __name__ == "__main__":
    main()
