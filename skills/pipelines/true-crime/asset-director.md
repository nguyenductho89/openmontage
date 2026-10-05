# Asset Director — True Crime Pipeline

## When to Use

The scene plan exists with every scene's provenance class decided. Your job is to
actually produce or source every asset: archival/stock visuals with real
provenance metadata, narration audio, maps/diagrams, and music — in that priority
order.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/asset_manifest.schema.json` | Artifact validation |
| Prior artifacts | `scene_plan`, `script` | What to produce |
| Prior artifact | `legal_review` (if available) | Flags to respect |
| Tools | `tts_selector` (required); `direct_clip_search`, `corpus_builder`, `clip_search` (archival/stock); `image_selector`, `video_selector` (illustration only); `diagram_gen`; `music_gen` | Generation/sourcing |

## Provenance Tagging Convention (binding)

Every visual asset's `subtype` field must be one of:

- `archival_real` — a real photo/clip of the actual case with a confirmed
  license. Record `provider`, `original_url`, and `license` — these are
  non-negotiable for a true-crime asset.
- `illustrative` — generic stock, not claiming to depict the real people/place.
- `ai_generated` — AI-produced imagery/video standing in for a real scene.
- `license_unknown` — rights unclear. **Must be resolved before the stage is
  marked complete** — either re-source with a clear license or escalate to the
  user. Never leave a `license_unknown` asset in the final manifest.

### Step 1: Archival and Licensed Stock Search (do this first)

Use `direct_clip_search` (fast path, act-by-act) or `corpus_builder` +
`clip_search` (standard path, large productions) exactly as documented in
`skills/pipelines/documentary-montage/asset-director.md` — the retrieval
mechanics are identical. Favor these sources in this order for true crime:

1. `wikimedia`, `archive_org`, `loc` (Library of Congress), `nara` — archival
   real material, often with confirmed public-domain or CC licensing.
2. General licensed stock (`pexels`, `pixabay_video`, etc.) for generic,
   non-claiming b-roll.

For every candidate, verify and record the license before accepting it — do
not accept a clip with an unclear or missing license field from the source
provider; mark it `license_unknown` and keep searching instead.

### Step 2: Document / Map / Timeline Cards

These are Remotion-native and need no external sourcing — just structured data
for `diagram_gen` or the Edit Director's card templates (handled at edit time
from `scene_plan`/`script` data). Record a lightweight `asset_manifest` entry
(`type: "data"`, `subtype: "diagram_source"`) pointing at the structured
content so edit can pick it up, if the scene plan doesn't carry it directly.

### Step 3: AI-Generated/Illustrative Reconstruction (last resort only)

Only for scenes the scene plan explicitly marked `ai_generated`. Prompting
rules:

- Describe a reconstruction or atmosphere, never a specific real person's
  face. Use phrasing like "a figure seen from behind," "a silhouette in a
  doorway," "a generic room resembling the described space" — never attempt
  to generate a likeness of the actual victim/suspect.
- Negative-prompt out: identifiable faces, text/signage that could be
  mistaken for a real document, gore.
- Tag the resulting asset `subtype: "ai_generated"` and note in
  `generation_summary` that it requires the mandatory on-screen label.

### Step 4: Narration

Use `tts_selector` with the script's `voice_performance` plan. Voice
characteristics for this pipeline: measured, documentary-neutral, no hype
energy, no excitement on violent content. Sample first (per the explainer
asset-director's Step 2b pattern), confirm with the user before batch
generation.

### Step 5: Music

Low, restrained, tension-appropriate bed — never upbeat/triumphant. Follow the
proposal's music plan exactly (see
`skills/pipelines/documentary-montage/asset-director.md` Step 8 for the
source-priority mechanics: library → user-provided → generation → explicit
"none"). Never swap music source without logging a decision.

### Step 6: Build the Asset Manifest

Same manifest shape as the explainer/documentary pipelines. True-crime
specific: every visual asset must have `subtype` set to one of the four
provenance values above, and every `archival_real` asset must have
`provider`, `original_url`, and `license` populated.

## Quality Gate

- Every scene's required assets exist on disk.
- Every visual asset's `subtype` is one of `archival_real` / `illustrative` /
  `ai_generated` — **no `license_unknown` remains** in the final manifest.
- Every `archival_real` asset has `provider`, `original_url`, `license`.
- Narration covers every script section; durations within ±15% of planned.
- Music asset exists, or `music_plan.source == "none"` with an explicit
  opt-out note.
- Total cost within approved budget.

## Common Pitfalls

- **Accepting a stock clip with no license metadata "because it looked
  right."** Keep searching, or flag it — don't guess at rights.
- **Generating an AI face for a real person because archival search came up
  empty.** Reconstruct the scene/atmosphere instead; never the face.
- **Shipping a `license_unknown` asset because the deadline is tight.** This is
  exactly the asset class the quality gate exists to catch — resolve or
  escalate.
- **Picking an energetic TTS delivery because it "sounds more engaging."**
  True crime narration should read as measured and credible, not excited.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review
passes: checkpoint with `status="awaiting_human"`, present the summary (the Backlot
board renders the artifact), and **END YOUR TURN**. Do not start the next stage in
the same response. Approval is per-gate — an earlier "go ahead" does not cover this
gate.
