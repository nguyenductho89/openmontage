# Scene Director — True Crime Pipeline

## When to Use

You have a `script` (and, ideally, its `legal_review`). Your job is to turn the
narration into a visual plan: what the viewer sees at every moment, and critically,
**what provenance class each visual belongs to** — because that classification is
what drives the mandatory on-screen labeling downstream.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/scene_plan.schema.json` | Artifact validation |
| Prior artifact | `script` | Sections, enhancement cues, timing |
| Prior artifact | `legal_review` (if available) | `image_broll_flags`, privacy/graphic flags |
| Playbook | `case-file` or custom | Visual language, pacing |

## Visual Sourcing Order (binding — matches the approved proposal)

1. **Archival real** — a real photo/clip of the actual case, with a known
   license (Wikimedia Commons, Archive.org, Library of Congress, NARA, licensed
   press photography). Preferred whenever it exists and clears rights.
2. **Illustrative stock** — generic licensed footage/stills that do not claim to
   depict the actual people or place (empty courtroom corridor, generic city
   street, generic police lights). No label needed if genuinely generic, but
   never pass it off as footage of the actual case.
3. **Motion-graphics / document / map / timeline cards** — Remotion-native
   (`text_card`, `diagram`, `stat_card`, `progress_bar`) for evidence lists,
   timelines, quotes, and maps. Zero provenance risk; use liberally.
4. **AI-generated or AI-illustrated reconstruction** — last resort only, for
   moments with no real visual record (a reconstructed room, a stylized
   silhouette). **Never generate a real identifiable person's face.** Always
   requires a labeling overlay at edit time.

## Provenance Classification (every scene needs one)

For each scene, record the intended provenance in the scene's `description` and
in the corresponding `required_assets[].type`/`description` so the Asset
Director can tag the resulting asset's `subtype` correctly:

| Provenance | `subtype` convention downstream | Label required? |
|------------|----------------------------------|------------------|
| Archival real | `archival_real` | Source-credit overlay (not a warning label) if license requires attribution |
| Illustrative stock | `illustrative` | No label needed if genuinely generic |
| Motion-graphics card | n/a (native Remotion) | No label needed |
| AI-generated/illustrated | `ai_generated` | **Mandatory** "AI-GENERATED RECONSTRUCTION" or "ILLUSTRATION" overlay |

**`LICENSE_UNKNOWN` cannot appear in a finished scene plan.** If a candidate
visual's rights are unclear, either resolve it before locking the plan or route
it to the Asset Director with an explicit flag to find a cleared alternative —
never silently plan around an unresolved license.

## Hard Content Rules

- No gore, wound detail, or autopsy imagery beyond what's necessary for
  understanding — and prefer the least graphic option even then.
- No identifiable images of minors.
- No victim/family social-media photos without clear usage rights — these are
  frequently screenshotted without permission; verify before planning.
- Carry forward every `legal_review.image_broll_flags` entry — if fact-check
  flagged a planned visual, resolve it here, don't ignore it.

## Process

Follow the same scene-decomposition mechanics as
`skills/pipelines/explainer/scene-director.md` (script analysis, scene types,
coverage/variety checks, self-evaluation) with these true-crime substitutions:

1. **Scene types**: favor `diagram` (maps, timelines, evidence cards),
   `text_card` (quotes, charges, dates — never let AI-generated text stand in
   for exact legal text), `broll` (archival/illustrative footage), and
   `generated` only for the last-resort AI-reconstruction case above.
2. **Opening disclaimer scene**: plan a brief text-card scene near the start
   stating this is a factual account based on cited sources, with allegations
   distinguished from findings — mirrors the pinned-comment language from the
   Script Director.
3. **Chapter markers**: align scene groupings to the script's 9-part structure
   so the Compose/Publish Directors can derive chapter timestamps directly.
4. **Label overlay placeholders**: for every AI-generated/illustrative scene,
   add an `overlay_notes` entry describing the exact label text and duration
   (e.g. "AI-GENERATED RECONSTRUCTION, visible for full scene duration") — the
   Edit Director turns this into an actual `section_title` overlay.

## Quality Gate

- Full script duration covered, no gaps > 1s.
- At least 3 different scene types used; no 3+ consecutive scenes of the same
  type.
- Every scene has an explicit provenance classification.
- No scene plans AI-generated/illustrative material without an `overlay_notes`
  label plan.
- No scene plans gore, an identifiable minor, or an unlicensed victim/family
  photo.
- Every `legal_review.image_broll_flags` entry (if present) is addressed.

## Common Pitfalls

- **Defaulting to AI generation because it's the easiest tool call.** Archival
  search takes longer but is the whole point of this pipeline's visual policy.
- **Forgetting the label plan for an AI scene.** The Edit Director relies on
  `overlay_notes` to know a label is required — don't skip it.
- **Using a stock photo of a real-looking person and implying it's the actual
  suspect/victim.** This is exactly the confusion the provenance system exists
  to prevent — if it's not actually them, it must read as illustration.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review
passes: checkpoint with `status="awaiting_human"`, present the summary (the Backlot
board renders the artifact), and **END YOUR TURN**. Do not start the next stage in
the same response. Approval is per-gate — an earlier "go ahead" does not cover this
gate.
