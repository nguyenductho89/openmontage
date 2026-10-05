"""Contract tests for the true-crime pipeline.

Mirrors tests/contracts/test_character_animation_pipeline.py's pattern: verify
the manifest's custom stage sequence, that its new artifacts are registered and
schema-valid (both for a correct sample and for samples that should fail), that
the binding fact-check gate is actually a human-approval gate, that the new
Remotion text-overlay shape in edit_decisions validates alongside the legacy
asset-overlay shape, and that the case-file playbook loads.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import jsonschema

from lib.checkpoint import _stage_requires_approval, get_pipeline_stages
from lib.pipeline_loader import load_pipeline
from schemas.artifacts import ARTIFACT_NAMES, validate_artifact
from styles.playbook_loader import load_playbook

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"


def test_true_crime_manifest_stage_order():
    manifest = load_pipeline("true-crime")
    assert manifest["name"] == "true-crime"
    assert get_pipeline_stages("true-crime") == [
        "research",
        "proposal",
        "script",
        "fact_check",
        "scene_plan",
        "assets",
        "edit",
        "compose",
        "publish",
    ]


def test_true_crime_required_skills_all_exist():
    manifest = load_pipeline("true-crime")
    for skill_ref in manifest["required_skills"]:
        path = SKILLS_DIR / f"{skill_ref}.md"
        assert path.is_file(), f"required_skills entry {skill_ref!r} has no file at {path}"

    for stage in manifest["stages"]:
        skill_ref = stage.get("skill")
        if skill_ref:
            path = SKILLS_DIR / f"{skill_ref}.md"
            assert path.is_file(), f"stage {stage['name']!r} skill {skill_ref!r} missing at {path}"


def test_true_crime_artifacts_are_registered():
    assert {"case_research_pack", "legal_review"}.issubset(set(ARTIFACT_NAMES))


def test_fact_check_is_a_binding_human_gate():
    assert _stage_requires_approval("true-crime", "fact_check") is True


MINIMAL_RESEARCH_PACK = {
    "version": "1.0",
    "case_identity": {
        "case_name": "The Riverside Case",
        "jurisdiction": "US-CA",
        "legal_status": "convicted",
        "disambiguation_note": "Confirmed via docket number against the 2019 Riverside County filing; not to be confused with the unrelated 2003 case of the same nickname.",
    },
    "verified_summary": "A verified one-paragraph summary using only FACT-tier material.",
    "timeline": [
        {
            "event": "Victim reported missing by family",
            "verification": "VERIFIED",
            "source_ids": ["src_01"],
        }
    ],
    "sources": [
        {"id": "src_01", "url": "https://example-court.gov/case/123", "tier": "A"},
        {"id": "src_02", "url": "https://example-news.test/article", "tier": "B"},
        {"id": "src_03", "url": "https://example-news2.test/article", "tier": "B"},
    ],
}


def test_minimal_case_research_pack_validates():
    validate_artifact("case_research_pack", MINIMAL_RESEARCH_PACK)


def test_case_research_pack_rejects_timeline_entry_missing_verification():
    bad = {
        **MINIMAL_RESEARCH_PACK,
        "timeline": [
            {
                "event": "Something happened",
                "source_ids": ["src_01"],
                # missing required "verification"
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("case_research_pack", bad)


def test_case_research_pack_rejects_unknown_verification_label():
    bad = {
        **MINIMAL_RESEARCH_PACK,
        "timeline": [
            {
                "event": "Something happened",
                "verification": "PROBABLY_TRUE",  # not in the enum
                "source_ids": ["src_01"],
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("case_research_pack", bad)


MINIMAL_LEGAL_REVIEW = {
    "version": "1.0",
    "jurisdiction": "US-CA",
    "factual_readiness": "READY",
    "legal_risk": "LOW",
    "source_quality": "STRONG",
    "claims": [
        {
            "section_id": "s1",
            "text": "The victim was reported missing on the stated date.",
            "label": "FACT",
            "risk": "GREEN",
        }
    ],
    "final_script_status": "READY",
    "disclaimer": (
        "This review assesses factual and reputational content risk. It is not "
        "legal advice. Consult a licensed attorney in the relevant jurisdiction "
        "for legal certainty."
    ),
}


def test_minimal_legal_review_validates():
    validate_artifact("legal_review", MINIMAL_LEGAL_REVIEW)


def test_legal_review_rejects_bad_final_script_status():
    bad = {**MINIMAL_LEGAL_REVIEW, "final_script_status": "PROBABLY_FINE"}
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("legal_review", bad)


def test_legal_review_rejects_claim_missing_risk():
    bad = {
        **MINIMAL_LEGAL_REVIEW,
        "claims": [
            {
                "section_id": "s1",
                "text": "Some claim.",
                "label": "FACT",
                # missing required "risk"
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("legal_review", bad)


def test_edit_decisions_accepts_remotion_label_overlay_and_legacy_asset_overlay():
    edit_decisions = {
        "version": "1.0",
        "render_runtime": "remotion",
        "renderer_family": "explainer-data",
        "cuts": [
            {
                "id": "cut_01",
                "source": "asset_reconstruction_01",
                "in_seconds": 0,
                "out_seconds": 6,
            }
        ],
        "overlays": [
            {
                # legacy asset overlay shape
                "asset_id": "asset_watermark",
                "start_seconds": 0,
                "end_seconds": 6,
                "position": {"x": 10, "y": 10},
            },
            {
                # new Remotion text-overlay shape (provenance label)
                "type": "section_title",
                "in_seconds": 0,
                "out_seconds": 6,
                "text": "AI-GENERATED RECONSTRUCTION",
                "position": "bottom-left",
                "accentColor": "#C08A3E",
            },
        ],
    }
    validate_artifact("edit_decisions", edit_decisions)


def test_edit_decisions_rejects_overlay_matching_neither_shape():
    edit_decisions = {
        "version": "1.0",
        "render_runtime": "remotion",
        "cuts": [
            {"id": "cut_01", "source": "x", "in_seconds": 0, "out_seconds": 1}
        ],
        "overlays": [
            {"nonsense_field": "no asset_id, no type"},
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("edit_decisions", edit_decisions)


def test_case_file_playbook_loads():
    playbook = load_playbook("case-file")
    assert playbook["identity"]["name"] == "case-file"
