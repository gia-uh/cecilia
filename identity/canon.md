# Cecilia — Visual Identity Canon

This document is the source of truth for Cecilia's visual identity. Read it before producing any new asset that will appear next to her name.

For the rigid render-time rules (skin tone, hair, gaze, earrings, attire, posture), see [`model-sheet.md`](model-sheet.md). For machine-readable tokens, see [`palette.yml`](palette.yml) and [`typography.yml`](typography.yml). For the canonical reference render, see [`references/cecilia-logo.jpg`](references/cecilia-logo.jpg).

## 1. Cecilia, the character

Cecilia is the public face of a family of language models continual-pretrained on Cuban Spanish, developed by GIA-UH at the University of Havana with GPLSI (Alicante) and the support of Syalia and Epistemial.

She is named for **Cecilia Valdés**, the heroine of Cirilo Villaverde's 1882 novel — Cuba's foundational mulata literary figure. The literary lineage is acknowledged as cultural subtext, not period costume: our Cecilia is contemporary, not 19th-century. The naming honors a Cuban tradition of giving voice to women who carry the language and culture forward.

She is mid-twenties, mulata, Habanera. Her **signature gesture** is an aspirational upward gaze — confident, looking forward, never coquettish, never downcast. Her wardrobe canon is the **female guayabera dress** (white or cream, embroidered, contemporary cut), the same garment Cuban women wear to formal-but-Cuban occasions. She is proud, articulate, and warm.

Cecilia is a **fixed character**. Every visualization across every register and medium must be recognizably her, governed by [`model-sheet.md`](model-sheet.md). She is not a logo, not an abstract concept, not a mood. She is a person.

## 2. Two registers

The identity is built around two registers that share palette and gesture sensibility but differ in execution:

- **Hero register.** Illustrated portrait of Cecilia herself: warm-brown skin, deep dark hair, **negative-space white planes** carving the face along the light direction, white architectural sweeps in the negative space of the composition. Hand-drawn / vector-illustration aesthetic. Used for: the canonical bust, full-body hero, social cards, HuggingFace model card heroes, conference covers, the bot avatar. Character-led; high presence; not scalable below ~256px.

- **Utility register.** Geometric, monochrome-friendly, flat-fill. Used for: the wordmark, lockups, favicon, document iconography, paper-figure adornments, anywhere the hero register would muddy at small sizes or compete with content. Same palette tokens as the hero register; the **negative-space sensibility** carries through (white planes against warm browns) but as flat geometry rather than illustrated planes.

Both registers descend from the same canon and reference the same palette. The choice between them is governed by **scale and adjacency**:

- If the asset will be ≥256px and stand alone or pair with copy → hero.
- If the asset will be <256px, repeated, or adjacent to body text → utility.

## 3. Gesture language

The defining gesture of the hero register is **negative-space white planes** carving warm-brown forms. The bust establishes the vocabulary:

- White is **light**, never decoration. White planes appear where light hits — forehead, cheekbone, jaw, the side of the neck.
- White is also **architecture**: gestural sweeps in the negative-space ground hint at structure (a column, a wall, a corner of a room) without rendering it.
- The **earring is white** — a diagnostic detail of the character, the only white element that's a literal object rather than a light plane.
- Warm browns range from deep near-black (hair, shadow planes) through caramel (mid-tones) to copper (highlights below the white planes).

The utility register inherits the **white-against-warm-brown** logic but renders it geometrically: a wordmark is white planes on a brown ground, an icon is a brown shape with a white internal cut.

Avoid: gradients, painterly textures, soft edges, photographic realism, period-costume detailing, drop shadows, glow effects, anything that softens the deliberate hard edges of the hero register.

## 4. Voice and tone (for paired copy)

When copy appears next to Cecilia's image, it should match her gaze — **forward-looking, declarative, warmly confident**. Avoid hedging, avoid hype. Spanish copy is preferred for Cuban-facing surfaces; English copy is acceptable for academic and international surfaces. Bilingual is fine when the surface naturally demands it.

The model is named Cecilia. The character speaks for the model. When in doubt, ask: *would Cecilia herself say this?*

## 5. Application

- **HuggingFace model cards** (3 variants — base, instruct, GGUF): hero register, full-frame bust at 1200×630.
- **GitHub README**: hero register banner, lockup at top-right.
- **Telegram bot avatar** (`@cecilia_cuba_bot`): hero register, square 1024 crop of the bust.
- **Web** (`cecilia.uhgia.org` — landing, report, training): hero register on landing, utility register on report and training pages so it doesn't compete with content.
- **Internal technical report** (Quarto/Typst): utility register cover; hero register optional on title page only.
- **Springer paper** (LNCS): no Cecilia visuals (template constraints); the lineage is acknowledged in the acknowledgments section.
- **Slide decks**: hero register on title, utility register on body slides.

## 6. Heritage

The portrait at [`references/cecilia-logo.jpg`](references/cecilia-logo.jpg) is the canonical bust. It is **not regenerated** as part of v1 — it is already public on HuggingFace, the GitHub README, the Telegram bot, and downstream citations. Treating it as immutable preserves the public-facing identity.

The full-body hero rendered as part of v1 is the **first new canonical asset** — it introduces the guayabera into the visible canon (the bust crops above the neckline, so wardrobe was previously implicit only).

## 7. v2 and beyond

Secondary stylistic registers — **retro-futurist**, anime, Cuban comics, children's-book illustration — are deferred to v2. They will be added by writing new mosaico project YAMLs against this canon. The character bible (full-body turnaround, expression sheet, proportional rules) is what makes those v2 registers stay on-model: each new register is "Cecilia rendered in style X," anchored on the bible.
