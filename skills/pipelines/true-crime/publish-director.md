# Publish Director — True Crime Pipeline

## When to Use

You have a `render_report` with the final video. Your job is to prepare it for
distribution: SEO metadata, thumbnail concept, chapters, export packaging — plus
the true-crime-specific requirement of a sources list, a pinned comment that
distinguishes allegation from verdict, and a non-legal-advice disclaimer.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/publish_log.schema.json` | Artifact validation |
| Prior artifacts | `render_report`, `proposal_packet`, `script.metadata` (title/description/pinned-comment drafts) | Video file and drafted copy |
| Prior artifact (optional) | `legal_review`, `case_research_pack` | Final accuracy pass, source list |

## Process

### Step 1: Gather Context

Pull the title options, hook, description draft, and pinned-comment draft from
`script.metadata` (drafted by the Script Director). Pull chapter boundaries
from `edit_decisions.metadata.chapters` / the script's 9-part structure. Pull
the source list from `case_research_pack.sources`.

### Step 2: Last-Pass Accuracy Check

Before finalizing any on-screen or metadata text, re-check it against
`legal_review` one more time — titles and descriptions are exactly where
over-claiming creeps back in ("The Killer Who..." headline energy) even after
the script itself passed fact-check. If a title/description phrase asserts
something `case_identity.legal_status` doesn't support, fix it now.

### Step 3: SEO Metadata

**Title** (max 60 chars): from the Script Director's balanced option by
default — avoid the suspense-leaning option if it implies a certainty the case
doesn't have (e.g., an unsolved case should not get a title implying a known
culprit).

**Description**: first line restates the hook, body covers what's actually
covered, chapters, CTA, and — specific to this pipeline — a short sources line
and the disclaimer.

**Tags**: derived from the case's actual names/location/legal terms as used in
the research pack, not sensationalized add-ons.

### Step 4: Sources and Disclaimer (mandatory, true-crime specific)

Append to the description:

```
Sources: [publisher 1], [publisher 2], [court records if cited], ...
This video distinguishes allegations, court findings, and verified facts
throughout. It is for informational purposes and is not legal advice.
```

### Step 5: Pinned Comment

Build from the Script Director's draft, finalized against `legal_review`:

```
This video is based on [N] sourced reports and [court records / case filings,
if applicable]. Where the case involves ongoing proceedings, allegations are
identified as such and are distinct from any court finding. Sources: [list].
```

### Step 6: Thumbnail Concept

Same mechanics as `skills/pipelines/explainer/publish-director.md` Step 3,
with one addition: if the thumbnail concept includes any AI-generated/
illustrative imagery, note in `style_notes` that it must not be presented as
real footage/photography of the case.

### Step 7: Chapter Markers

Map the 9-part structure to timestamps from `script`/`edit_decisions`.

### Step 8: Package Export

Use `export_bundle` exactly as documented in
`skills/pipelines/explainer/publish-director.md` Step 5 — same tool, same
output layout (`exports/<project>/video|metadata|thumbnails/`).

### Step 9: Build Publish Log

Persist `export_bundle`'s returned `publish_log` directly (same schema
constraints as the explainer pipeline — `additionalProperties: false` on
entries).

### Step 10: Self-Evaluate

| Criterion | Question |
|-----------|----------|
| Accuracy | Does the title/description assert anything beyond the case's actual legal status? |
| Sources | Is the sources list present and does it match `case_research_pack.sources`? |
| Disclaimer | Is the non-legal-advice disclaimer included? |
| Pinned comment | Does it distinguish allegation from verdict where relevant? |
| Chapters | Do they match the 9-part structure? |

If any dimension fails, revise before submitting.

## Common Pitfalls

- **Letting a punchy title re-introduce a claim fact-check already flagged.**
  The title/description is new text — it needs its own pass against
  `legal_review`, it doesn't inherit the script's clean bill automatically.
- **Omitting the sources line because it "clutters the description."** It's
  mandatory for this pipeline.
- **Thumbnail implying AI art is real crime-scene photography.** Note the
  provenance in `style_notes` explicitly.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review
passes: checkpoint with `status="awaiting_human"`, present the summary (the Backlot
board renders the artifact), and **END YOUR TURN**. Do not start the next stage in
the same response. Approval is per-gate — an earlier "go ahead" does not cover this
gate.
