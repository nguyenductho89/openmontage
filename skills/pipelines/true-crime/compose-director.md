# Compose Director — True Crime Pipeline

## When to Use

The timeline is locked: cuts, label overlays, music, subtitles, chapters. Your
job is to render the final video and verify — actually verify, by extracting
frames — that every mandatory label is visible on screen, not just present in
the edit decisions.

## Runtime Routing

Route by `edit_decisions.render_runtime`, which the proposal stage locked
(default `"remotion"`). This pipeline's labeling overlays
(`section_title`/`provider_chip` on the Remotion `Explainer` composition) are
validated against Remotion; **HyperFrames** is a legitimate alternative runtime
in general but has not been validated for this pipeline's label-overlay
convention. If `edit_decisions.render_runtime` is `"hyperframes"`, confirm the
label overlays still render correctly before proceeding — if they don't,
surface the gap rather than shipping an unlabeled AI/illustrative scene.

- If `edit_decisions.render_runtime` differs from `proposal_packet`'s locked
  value, STOP — this is a CRITICAL governance violation. Route back to
  proposal to re-lock, log a `render_runtime_selection` correction, and resume.
- Pass `proposal_packet` to `video_compose.execute()` so its
  `runtime_swap_detected` check actively confirms the runtime stayed locked
  end-to-end.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/render_report.schema.json`, `schemas/artifacts/final_review.schema.json` | Artifact validation |
| Prior artifacts | `edit_decisions`, `asset_manifest` | Cuts, overlays, provenance |
| Tool | `video_compose` (Remotion Explainer composition) | Primary render engine |
| Tool | `audio_mixer` | Music ducking under narration |
| Tool (optional) | `video_stitch` | Lower-level helper if needed |

## Process

### 1. Render

```python
video_compose.execute({
    "operation": "render",
    "output_path": "projects/<name>/renders/final.mp4",
    "edit_decisions": edit_decisions,       # renderer_family="explainer-data"
    "asset_manifest": asset_manifest,
    "proposal_packet": proposal_packet,     # enables runtime_swap_detected check
})
```

Consult the live `video_compose` tool schema before writing the call — don't
invent parameter names.

### 2. Verify Labels Are Actually Visible (mandatory, not optional)

For every cut you labeled at edit time:

1. Compute a timestamp inside the overlay's `in_seconds`/`out_seconds` window
   (e.g. midpoint).
2. Extract a frame at that timestamp from the rendered output (ffmpeg frame
   extraction).
3. Confirm the label text ("AI-GENERATED RECONSTRUCTION", "ILLUSTRATION", or
   the attribution credit) is legible against the footage — not clipped,
   not hidden behind another overlay, not rendered off-canvas.

If any label is missing or illegible: this is a render defect, not a cosmetic
nit. Fix the overlay positioning/timing in `edit_decisions` and re-render —
do not ship a video where an AI-generated scene is unlabeled.

### 3. Verify the Opening Disclaimer

Extract a frame from the first few seconds and confirm the disclaimer card
rendered as planned.

### 4. Audio and Duration Check

Confirm narration is present throughout, music is ducked under it (not
competing), and total duration is within ±5% of the proposal's target.

### 5. Emit the Render Report

Standard `render_report` shape (see
`skills/pipelines/documentary-montage/compose-director.md` Step 7 for the
canonical pattern) plus:

```json
{
  "metadata": {
    "pipeline": "true-crime",
    "render_runtime": "remotion",
    "labels_verified": true,
    "label_checks": [
      {"cut_id": "cut_12", "label": "AI-GENERATED RECONSTRUCTION", "visible": true},
      {"cut_id": "cut_18", "label": "Photo: Library of Congress", "visible": true}
    ]
  }
}
```

### 6. Final Review

Build `final_review` per its schema: `status`, `checks` (include a check named
`"label_overlays_visible"`), and `issues_found` for anything that needed a
fix-and-rerender.

## Quality Gate

- Output file exists, plays, duration within ±5% of target.
- `render_runtime` in `render_report.metadata` matches the locked value —
  silent swap is a CRITICAL governance violation.
- Every planned label overlay was verified visible by frame extraction, not
  assumed from the edit decisions.
- Opening disclaimer verified visible.
- Music ducked correctly under continuous narration.

## Common Pitfalls

- **Trusting the edit decisions without extracting a frame.** An overlay can
  be positioned off-canvas, timed wrong, or hidden behind another layer — the
  only way to know is to look at the actual rendered frame.
- **Silently falling back to HyperFrames or FFmpeg because Remotion errored.**
  Surface the failure; don't swap runtimes to "make it work."
- **Treating a missing label as a minor polish item.** It's the core promise
  of this pipeline's visual-honesty policy — missing it is a blocking defect.

---

## Gate Reminder (Binding)

This stage gates on human approval for the checkpoint record even though
`human_approval_default: false` lets the pipeline auto-proceed — still write the
full `render_report` + `final_review` to the checkpoint so Backlot and the
Publish Director have a verifiable record before export.
