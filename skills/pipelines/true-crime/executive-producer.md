# Executive Producer — True Crime Pipeline

## When to Use

The user wants a long-form (10-15 minute) narrated true-crime documentary about a real
case: a murder, disappearance, fraud, trial, or similar. You orchestrate the full
pipeline serially — research, proposal, script, a binding fact-check gate, scene
planning, assets, edit, compose, publish — reviewing each stage's output and either
passing it forward, sending it back for revision, or stopping for human approval.

If the user wants a short retrieval-only montage with no narration, that's
`documentary-montage`, not this pipeline. If they want a generic explainer with no
real case at its center, that's `animated-explainer`.

## Why This Pipeline Exists

True crime content carries real legal and ethical exposure that a generic explainer
pipeline does not: defamation risk against still-living suspects and defendants,
privacy risk for victims and families, and a strong temptation to round "alleged" up
to "proven" because it makes a better story. This pipeline makes **research → script →
fact/legal check** binding stages that happen *before* any asset is generated, so a
risky claim is caught while it's still a sentence in a document, not a line of
narration baked into rendered audio.

## Prerequisites

| Layer | Resource | Purpose |
|-------|----------|---------|
| Pipeline | `pipeline_defs/true-crime.yaml` | Stage definitions, review focus, success criteria |
| Skills | All 9 director skills + `meta/reviewer` + `meta/checkpoint-protocol` | Stage execution knowledge |
| Schemas | `case_research_pack`, `legal_review`, plus the standard artifact schemas | Validation |
| Playbook | `case-file` (recommended) or custom | Visual/audio identity |
| Tools | Full tool registry (`make preflight`) | Available capabilities |

## Cumulative State

```
EP_STATE:
  pipeline: true-crime
  playbook: <selected playbook name>
  target_duration_seconds: <600-900, from proposal_packet.selected_concept>
  budget_total_usd: <from proposal_packet.approval.approved_budget_usd or 3.00 default>
  budget_spent_usd: 0.0

  artifacts:
    research: null       # -> case_research_pack
    proposal: null        # -> proposal_packet (+ decision_log)
    script: null          # -> script
    fact_check: null       # -> legal_review
    scene_plan: null      # -> scene_plan
    assets: null          # -> asset_manifest
    edit: null             # -> edit_decisions
    compose: null          # -> render_report (+ final_review)
    publish: null          # -> publish_log

  case_research_pack: null   # full artifact, available to every downstream stage
  legal_review: null         # full artifact, available to scene/asset/edit/compose/publish
  jurisdiction: null
  legal_status: null          # case_identity.legal_status — governs wording everywhere

  revision_counts: {}
  send_back_counts: {}
  issues_log: []
```

## Execution Protocol

Run stages in order: `research -> proposal -> script -> fact_check -> scene_plan ->
assets -> edit -> compose -> publish`.

### The Fact-Check Gate Is Binding (read this before anything else)

`fact_check` is not advisory. After it runs:

- `final_script_status == "READY"` -> proceed to `scene_plan`.
- `final_script_status == "NEEDS REVISION"` -> SEND_BACK to `script` with the
  `required_corrections` table attached verbatim. Re-run `fact_check` after the
  revision. This does not count against the normal max-send-backs-per-stage-pair
  limit the first time — legal correction loops are expected, not a planning failure.
- `final_script_status == "NOT READY"` -> STOP. Present the `legal_review` to the
  user in full (critical issues first). Do not proceed to `scene_plan` under any
  circumstance without either (a) a revised script that re-clears fact-check as
  READY, or (b) the user explicitly accepting the residual risk in writing, logged
  as a `decision_log` entry with `category: "legal_risk_accepted"` naming exactly
  which RED/ORANGE claims are being accepted and why. Never silently downgrade a
  NOT READY verdict to proceed.

Every downstream stage (`scene_plan`, `assets`, `edit`, `compose`, `publish`) must
carry `legal_review` forward and respect its `claims[].label` and
`image_broll_flags[].provenance_class` — a scene plan or edit cannot quietly
re-introduce a claim fact-check marked RED.

### Phase 0: Initialize

1. Load `pipeline_defs/true-crime.yaml`.
2. Load the `case-file` playbook (or whatever the user selects).
3. Set budget (default $3.00 — this pipeline typically needs more archival-search
   iteration than a generated explainer).

### Phase 1: Execute Stages Serially

Follow the same `PREPARE / SPAWN DIRECTOR / REVIEW / GATE DECISION` loop used by the
explainer pipeline's EP (see `skills/pipelines/explainer/executive-producer.md` for
the full mechanics if unfamiliar). The true-crime-specific cross-stage checks:

#### After RESEARCH
- Case identity unambiguous? If the case name could collide with another
  (common for well-known crime names), `case_identity.disambiguation_note` must
  be present. If not: REVISE research.
- At least 3 sources, at least 1 tier A/B per key timeline entry? If not: REVISE.

#### After PROPOSAL
- Approval gate cleared (same as explainer EP).
- `render_runtime_selection` decision logged with both runtimes considered.
- Visual sourcing policy recorded (archival-first, AI-illustration-last-and-labeled).

#### After SCRIPT
- Word count maps to 600-900s target duration at the chosen pace.
- Every section has a `source_ref` pointing into `case_research_pack`.
- No section asserts guilt/identity beyond what `case_research_pack.case_identity.legal_status`
  supports. Spot-check 3 sentences with strong verbs ("killed", "murdered", "stole")
  against the research pack before passing to fact_check — this is a cheap
  pre-filter, not a replacement for the fact-check stage.

#### After FACT_CHECK (see binding gate above)
- Confirm every script section id appears in `legal_review.claims[].section_id`
  at least once. A section with zero claims logged means fact-check skipped it —
  SEND_BACK to fact_check, do not proceed.

#### After SCENE_PLAN
- Same coverage/variety checks as explainer.
- No scene plans an AI-generated or stock-with-unclear-license visual without a
  corresponding label overlay downstream. Cross-check against
  `legal_review.image_broll_flags`.

#### After ASSETS
- No asset has `subtype: "license_unknown"` left unresolved — either re-source it
  or escalate to the user per `AGENT_GUIDE.md`'s Decision Communication Contract.
- Narration duration feedback loop — same mechanics as explainer EP.

#### After EDIT
- Every cut whose source asset is `illustrative` or `ai_generated` carries a
  labeling overlay in the same cut's time range. Spot-check at least 3.

#### After COMPOSE
- `render_report` probe (duration, resolution, audio) same as explainer EP.
- Extract at least one frame during a labeled overlay's window and confirm the
  label text is actually legible on top of the footage, not just planned.

#### After PUBLISH
- Pinned comment / description distinguishes allegation from verdict and names
  sources. Disclaimer present.

### Phase 2: Final QA

Same holistic probe as the explainer EP (duration, A/V sync, style consistency,
budget reconciliation), plus: re-skim the final script against `legal_review` one
more time before handing the project to the user — this is the last point where a
missed RED claim is cheap to fix.

## Execution Limits

| Limit | Value |
|-------|-------|
| Max revisions per stage | 3 |
| Max send-backs per stage pair | 1 (script<->fact_check is exempt on the first loop, see above) |
| Max total send-backs | 4 |
| Max total budget | $3.00 default, configurable |
| Max total wall-time | 30 minutes |

## Common Pitfalls

- **Treating fact_check as a formality**: it is the entire reason this pipeline
  exists instead of routing through animated-explainer. Never auto-pass it.
- **Letting scene/asset/edit forget legal_review**: label overlays are not optional
  decoration — they are the thing that makes an AI-reconstructed scene honest.
- **Quietly resolving a license_unknown asset by just shipping it**: resolve it or
  escalate, never ship it silently.
- **Rushing past NOT READY because the user is impatient**: stop, present the
  review, and get an explicit, logged decision either way.
