# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Required reading for content-production requests

**Before responding to any request to make, create, edit, or produce video content** (e.g. "make me a video", "create an explainer", "edit this footage", "make something like this reference") — read [`AGENT_GUIDE.md`](AGENT_GUIDE.md) first.

AGENT_GUIDE.md is the complete agent contract: onboarding, pipeline selection (Rule Zero — all production goes through a pipeline, no ad-hoc tool calls), stage director skills, the decision-communication contract (announce before execution, ask before major changes, append-only `decision_log`), and checkpoint protocol. Skipping it leads to incorrect ad-hoc tool/API calls instead of the pipeline-driven flow this project requires.

This requirement does not apply to ordinary software-engineering requests against this repo itself (fixing a bug, adding a test, editing a tool) — use the sections below for those.

For architecture, key files, and conventions, see [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) — the single source of truth, shared across CLAUDE.md/CODEX.md/CURSOR.md/COPILOT.md/AGENTS.md so they don't duplicate it.

## Engineering commands (for working on OpenMontage's own code)

- Setup: `make setup` (core deps) · `make install-dev` (adds pytest/pytest-asyncio) · `make install-gpu` (adds torch/diffusers stack)
- All tests: `make test` (= `python -m pytest tests/ -v`)
- One suite: `python -m pytest tests/contracts -q`, `tests/tools -q`, `tests/qa -q`, `tests/pipelines -q`, etc.
- One test: `python -m pytest tests/<path>/test_file.py::test_name -v`
- Contract tests only: `make test-contracts`
- Lint (compiles core modules): `make lint`
- Tool/provider discovery: `make preflight` (dumps the live provider menu from `tools/tool_registry.py`)
- Zero-API-key demo renders: `make demo` / `make demo-list`
- HyperFrames runtime check: `make hyperframes-doctor`
- Remotion composer (`cd remotion-composer`): `npm start` (studio), `npm run build` (render `Explainer` to `out/video.mp4`), `npm run upgrade`

Python 3.10+ (see `.python-version`). Core deps: `requirements.txt`; dev: `requirements-dev.txt`; GPU: `requirements-gpu.txt`.

## Architecture

OpenMontage is **instruction-driven**: the agent is the intelligence; Python only provides tools and persistence. There is no Python orchestrator, reviewer, or stage-transition logic — all of that lives in YAML manifests and markdown skills that the agent reads and follows.

```
Agent reads pipeline manifest (YAML) → reads stage director skill (MD)
→ uses tools (Python BaseTool) → self-reviews (meta skill)
→ checkpoints (Python utility) → presents to human for approval
```

Key pieces, spread across several directories you'll need to read together to understand a change:

- **Pipelines** (`pipeline_defs/*.yaml`, listed in `PROJECT_CONTEXT.md`) declare the stage sequence `idea → script → scene_plan → assets → edit → compose → publish`, with per-stage tools, skills, and approval gates. Validated by `pipeline_manifest.schema.json`.
- **Stage director skills** (`skills/pipelines/<pipeline>/<stage>-director.md`) teach the agent how to execute each stage; must be read before doing work in that stage.
- **Tools** (`tools/<capability>/`) all inherit `tools/base_tool.py::BaseTool` (`ToolContract`), are discovered via `tools/tool_registry.py` (never imported ad hoc), and follow a selector-plus-provider pattern (e.g. `tts_selector` routing to `elevenlabs_tts` / `piper_tts` / `openai_tts` / ...).
- **Three-layer knowledge model**: Layer 1 `tools/tool_registry.py` (what tools exist/cost/status) → Layer 2 `skills/` (how OpenMontage uses them, project conventions) → Layer 3 `.agents/skills/` (how the underlying provider API/technology actually works). Each tool's `agent_skills[]` field bridges Layer 1 to Layer 3; those skills must be read before calling the tool.
- **Artifacts** — `brief`, `script`, `scene_plan`, `asset_manifest`, `edit_decisions`, `render_report`, `publish_log` — are the canonical pipeline state, validated against `schemas/artifacts/`.
- **Composition runtimes**: `tools/video/video_compose.py` routes to Remotion (`remotion-composer/`), HyperFrames (`tools/video/hyperframes_compose.py`), or FFmpeg based on `edit_decisions.render_runtime`. Both Remotion and HyperFrames support a `composition_mode`: templated (stock scene-types, fast/cheap) vs. atelier (bespoke hand-authored composition, default for hero/brand work).
- **Config**: `config.yaml` loaded via `lib/config_model.py` (Pydantic).
- **Cost governance**: `tools/cost_tracker.py` (estimate → reserve → reconcile).
- **Checkpointing**: `lib/checkpoint.py`; policy lives per-stage in the pipeline manifest (`human_approval_default`) plus `skills/meta/checkpoint-protocol.md`. `lib/checkpoint.init_project(...)` initializes a project workspace (the marker the Backlot board reads).
- **Backlot** (`backlot/`) is the browser-based living storyboard that reads project/checkpoint state live during a pipeline run.

When adding a new pipeline or tool, follow the checklists in `PROJECT_CONTEXT.md` ("When Building New Pipelines" / "When Building New Tools") rather than improvising structure.
