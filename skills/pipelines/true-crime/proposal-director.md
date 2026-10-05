# Proposal Director — True Crime Pipeline

## When to Use

You are the Proposal Director. You sit between the Research Director and the Script
Director. You receive a `case_research_pack` full of verified findings and turn it
into a concrete, reviewable production proposal that the user approves before any
money is spent or any narrative framing is locked in.

**This is the approval gate.** Nothing downstream runs until the user says "go."

## Runtime Selection (required field — `render_runtime`)

True-crime proposals must lock **both** a `renderer_family` and a `render_runtime`.
Read `skills/meta/animation-runtime-selector.md` and `skills/core/hyperframes.md`
for the decision matrix and `AGENT_GUIDE.md` → "Present Both Composition Runtimes
(HARD RULE)" for the governance contract.

**MANDATORY workflow — present both runtimes, don't silently default:**

1. Query `video_compose.get_info()["render_engines"]`. If both `remotion` and
   `hyperframes` are `True`, present both. If only one is available, say so.
2. Present both runtimes with brief-specific analysis:
   - **Remotion** — fits this pipeline well: the Explainer composition's
     `text_card`, `stat_card`, `callout`, `progress_bar` (timelines), and
     `section_title`/`provider_chip` overlays cover documentary cards, maps,
     document stills, and the mandatory AI/illustration labels out of the box.
     Set `renderer_family: "explainer-data"`.
   - **HyperFrames** — mention it, but note that the mandatory label overlays
     (ILLUSTRATION / AI-GENERATED RECONSTRUCTION) and the archival-source-credit
     overlay convention this pipeline relies on are built against the Remotion
     Explainer composition; HyperFrames parity for those overlays has not been
     validated for this pipeline yet.
3. Recommend **Remotion** for true-crime unless the user has a specific reason to
   prefer HyperFrames, and explain why in one line.
4. Wait for explicit user approval before writing `render_runtime` into
   `proposal_packet.production_plan`.
5. Log a `render_runtime_selection` decision in `decision_log` with both runtimes
   in `options_considered`, the user's pick as `selected`, and the rationale as
   `reason`. **Present both** runtimes even when the recommendation is obvious —
   a single-option `render_runtime_selection` entry is a CRITICAL reviewer finding.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Schema | `schemas/artifacts/proposal_packet.schema.json` | Artifact validation |
| Prior artifact | `case_research_pack` from Research Director | Verified findings |
| Pipeline manifest | `pipeline_defs/true-crime.yaml` | Stage and tool definitions |
| Tool registry | `support_envelope()` output | What's actually available right now |
| Style playbooks | `styles/custom/case-file.yaml` (recommended) | Visual/audio identity |
| Meta skill | `skills/meta/voice-performance-director.md` | Narration delivery plan |
| User input | Any preferences expressed | Creative direction |

## Process

### Step 1: Absorb the Research

Read `case_research_pack` end to end. Note especially:
- `verified_summary` and `case_identity.legal_status` — these constrain every
  wording choice downstream.
- `story_worthy_facts` — your raw concept material.
- `contradictions` and `gaps` — these shape how cautious the framing needs to be.
- `sources` — source_quality here will roughly predict the fact-check verdict
  later; if sources are thin, say so now rather than let the user discover it at
  the fact-check gate.

### Step 2: Run Preflight

```bash
python -c "from tools.tool_registry import registry; import json; registry.discover(); print(json.dumps(registry.support_envelope(), indent=2))"
```

Check TTS availability (`tts_selector`), archival/stock sourcing
(`direct_clip_search`, `corpus_builder`), image generation (illustration-only —
`image_selector`), and Remotion render engine status.

### Step 3: Design 2-3 Concept Options

Every concept must use the **same verified facts** from the research pack — this
isn't the explainer pipeline's "different insight" diversity, it's "different
narrative structure or angle on the same true facts." Vary:
- which thread opens the cold open (a piece of evidence vs. a moment in the
  victim's life vs. the discovery);
- pacing emphasis (more time on investigation vs. more time on trial);
- target platform / duration within the 10-15 minute window.

For each concept, specify title, hook, structure emphasis, and why it works —
grounded in specific `case_research_pack` references, same as the explainer
pipeline's `grounded_in` convention.

**Hard rule inherited from research:** no concept's hook may assert something
stronger than `case_identity.legal_status` supports. A hook like "The man who got
away with it" is not usable pre-conviction.

### Step 4: Visual Sourcing Policy (mandatory section of every proposal)

Record explicitly, for the user to approve:

```
VISUAL SOURCING POLICY
1. Archival / licensed footage and stills first — Wikimedia Commons, Archive.org,
   Library of Congress, NARA, and licensed news photography where rights allow.
2. Generic licensed stock (Pexels, Pixabay, etc.) for scene-setting b-roll that
   isn't claiming to depict the actual people or place.
3. Motion graphics / document / map / timeline cards (Remotion-native) for
   evidence, timelines, and quotes — zero provenance risk, used liberally.
4. AI-generated or AI-illustrated imagery and video — LAST RESORT, reconstruction
   only, never depicting a real identifiable person's face. Every such asset is
   labeled on screen as "ILLUSTRATION" or "AI-GENERATED RECONSTRUCTION" at edit
   time. No exceptions.
```

Get explicit user sign-off on this policy — it is the thing that keeps the video
honest with its audience about what's real footage and what isn't.

### Step 5: Build the Production Plan and Cost Estimate

Same mechanics as the explainer pipeline's proposal-director (tool selection,
availability, itemized cost, fallback paths) — see
`skills/pipelines/explainer/proposal-director.md` Steps 5-6 for the full pattern.
True-crime-specific line items to include: archival search time (not literally
billed, but note it in the production plan as a time cost), narration (measured,
documentary voice), and any map/diagram generation.

### Step 6: Music and Voice Plan

Music: low, restrained, tension-appropriate bed — check `music_library/` first,
then generation. Never upbeat or triumphant registers for an unresolved or tragic
case. Voice: measured, neutral, non-sensational — explicitly rule out an
excited/hype TTS delivery style when selecting a provider/voice.

### Step 7: Jurisdiction Check

Record which jurisdiction's checklist the Fact-Check Director should apply
(`case_research_pack.case_identity.jurisdiction`). If it's outside VN/US, note
that the Fact-Check Director will use the generic "other jurisdiction" checklist
and flag where a local-law consultation might eventually be warranted — this
proposal does not and cannot give legal advice.

### Step 8: Assemble the Approval Gate

```
PROPOSAL READY FOR APPROVAL
Concept: [selected title]
Duration: [X] seconds (10-15 min target)
Visual sourcing policy: archival-first, AI illustration labeled & last resort
render_runtime: remotion (Explainer composition) — recommended
Estimated cost: $[X.XX] of $[budget] budget
Proceed? (approve / approve with changes / reject)
```

Set `approval.status: "pending"`. The pipeline must not proceed past this stage
without explicit approval.

### Step 9: Submit

Validate `proposal_packet` against its schema and submit.

## Common Pitfalls

- **Presenting a concept whose hook outruns the legal status.** Check every hook
  against `case_identity.legal_status` before presenting it.
- **Skipping the visual sourcing policy section.** It's the single most
  consequential approval in this proposal — don't bury it.
- **Only naming one render_runtime option.** CRITICAL reviewer finding; always
  present both.
- **Picking an upbeat music mood because "it tested well" on another pipeline.**
  True crime needs restraint, not energy.

---

## Gate Reminder (Binding)

This stage gates on human approval (`human_approval_default: true`). After review
passes: checkpoint with `status="awaiting_human"`, present the summary (the Backlot
board renders the artifact), and **END YOUR TURN**. Do not start the next stage in
the same response. Approval is per-gate — an earlier "go ahead" does not cover this
gate.
