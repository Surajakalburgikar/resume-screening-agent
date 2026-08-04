"""Create transparent candidate-match explanations."""

from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path

import pandas as pd

from src.scorer import normalize_skill


def _unique_skills(skills: list[str]) -> list[str]:
    """Remove duplicate skill labels while preserving their first occurrence."""
    unique: list[str] = []
    seen: set[str] = set()
    for skill in skills:
        normalized = normalize_skill(skill)
        if normalized not in seen:
            unique.append(skill)
            seen.add(normalized)
    return unique


def generate_match_reason(
    candidate: Mapping[str, object],
    required_skills: list[str],
    required_experience: float = 0,
) -> dict[str, object]:
    """Return matched/missing skills and a readable explanation for a candidate."""
    if required_experience < 0:
        raise ValueError("Required experience must not be negative.")

    candidate_skills = [
        skill for skill in candidate.get("skills", []) if isinstance(skill, str)
    ]
    required = _unique_skills(required_skills)
    candidate_skill_names = {normalize_skill(skill) for skill in candidate_skills}
    matched_skills = [skill for skill in required if normalize_skill(skill) in candidate_skill_names]
    missing_skills = [skill for skill in required if normalize_skill(skill) not in candidate_skill_names]

    experience = candidate.get("experience", 0)
    if not isinstance(experience, (int, float)) or isinstance(experience, bool):
        experience = 0
    name = str(candidate.get("name") or candidate.get("resume_file") or "Candidate")
    rank = candidate.get("rank")
    rank_prefix = f"ranked #{rank} " if isinstance(rank, int) and rank > 0 else ""

    if required_experience == 0:
        experience_summary = "The job description does not state an experience requirement."
    elif experience >= required_experience:
        experience_summary = (
            f"{experience:g} years of experience meets the {required_experience:g}-year requirement."
        )
    else:
        experience_summary = (
            f"{experience:g} years of experience is below the {required_experience:g}-year requirement."
        )

    matched_summary = ", ".join(matched_skills) if matched_skills else "no listed required skills"
    missing_summary = ", ".join(missing_skills) if missing_skills else "none"
    reason = (
        f"{name} is {rank_prefix}because of matching skills: {matched_summary}. "
        f"{experience_summary} Missing skills: {missing_summary}."
    )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "experience_summary": experience_summary,
        "reason": reason,
    }


def _format_csv_value(value: object) -> object:
    """Make collection values readable in a flat CSV cell."""
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return value


def export_rankings(
    rankings: list[Mapping[str, object]],
    output_dir: str | Path = "output",
) -> tuple[Path, Path]:
    """Write ranked candidates to ``rankings.csv`` and ``rankings.json``.

    JSON preserves the original record values; CSV converts lists and other
    collections into readable cell values. The output directory is created when
    it does not already exist.
    """
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    records = [dict(candidate) for candidate in rankings]

    json_path = destination / "rankings.json"
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)

    csv_path = destination / "rankings.csv"
    csv_records = [
        {key: _format_csv_value(value) for key, value in record.items()}
        for record in records
    ]
    pd.DataFrame(csv_records).to_csv(csv_path, index=False)

    return csv_path, json_path
