# Edit Director — True Crime Pipeline

## When to Use

Every scene has an asset. Your job is to turn the asset manifest into a concrete
timeline: cuts, transitions, music, subtitles, chapter markers, and — the part
unique to this pipeline — the **mandatory label overlays** on every illustrative
or AI-generated cut.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/edit_decisions.schema.json` | Artifact validation |
| Prior artifacts | `scene_plan`, `asset_manifest` | Cuts and provenance |
| Prior artifacts (optional) | `script`, `legal_review` | Chapter structure, flags to respect |

## Renderer Lock

Set `renderer_family: "explainer-data"` and carry forward whatever
`render_runtime` the Proposal Director locked (default `"remotion"`) **unchanged**.
This routes to the Remotion `Explainer` composition (`tools/video/video_compose.py`
`RENDERER_FAMILY_MAP`), which already provides the `text_card`, `stat_card`,
`diagram`-equivalent cards, `progress_bar` (timelines), and the `section_title` /
`provider_chip` overlays this pipeline's labeling relies on. If a downstream
discovery suggests `hyperframes` would serve better, that is a MAJOR change —
surface it and log a `render_runtime_selection` correction before switching;
never swap silently.

## Mandatory Label Overlays

For every cut whose source asset has `subtype: "ai_generated"` or
`"illustrative"` where the scene plan's `overlay_notes` called for a label, add
a **text overlay** (not an asset overlay) spanning that cut's time range:

```json
{
  "type": "section_title",
  "in_seconds": 182.0,
  "out_seconds": 188.0,
  "text": "AI-GENERATED RECONSTRUCTION",
  "position": "bottom-left",
  "accentColor": "#B45309"
}
```

Use `"AI-GENERATED RECONSTRUCTION"` for `ai_generated` assets and
`"ILLUSTRATION"` for `illustrative` assets whose scene the plan flagged as
needing a label (purely generic b-roll that doesn't risk confusion does not
need one — use judgment per the scene plan's `overlay_notes`).

For every `archival_real` cut whose license requires attribution, add a
smaller, less intrusive credit overlay (same `section_title` type, shorter
text, e.g. `"Photo: Library of Congress"`) rather than the warning-style label
used for AI/illustrative content — these are different in intent and should
look different on screen.

**Every AI-generated or illustrative cut without a label overlay is a defect.**
Cross-check the full cut list against the asset manifest's `subtype` field
before submitting — do not rely on memory.

## Opening Disclaimer and Chapters

- The scene plan's opening disclaimer scene becomes the first cut's text
  overlay or card — render it before any case-specific visual appears.
- Derive chapter markers from the script's 9-part structure
  (`metadata.chapters` in `edit_decisions`, consumed by the Publish Director).
- Subtitles: `enabled: true`, sentence-level by default (word-level/karaoke is
  not required for this register).

## Music and Pacing

Low, restrained bed with ducking under narration (`audio.music.ducking: true`
— unlike `documentary-montage`, this pipeline has narration throughout).
Follow the approved music plan from the proposal; never substitute silently.

## Quality Gate

- `renderer_family` and `render_runtime` match the proposal's lock, unchanged.
- Timeline covers the full duration with no gaps/overlaps.
- Every `ai_generated`/flagged-`illustrative` cut carries a label overlay in
  its exact time range.
- Every `archival_real` cut needing attribution carries a credit overlay.
- Opening disclaimer present as the first visual element.
- Chapter markers match the script's 9 parts.
- Subtitles enabled; music ducking configured under narration.

## Common Pitfalls

- **Forgetting a label on one AI-generated cut while labeling the rest.**
  Audit the complete cut list against `asset_manifest`, not a sample.
- **Using the same loud warning-style overlay for a licensed archival credit.**
  Attribution and "this isn't real footage" are different messages — don't
  conflate them visually.
- **Silently changing `render_runtime` because Remotion felt slow.** That's a
  governance violation; surface it instead.

---

## Gate Reminder

This stage does not require human approval by default
(`human_approval_default: false`), but still write a checkpoint with the full
artifact for Backlot visibility before continuing to `compose`.
