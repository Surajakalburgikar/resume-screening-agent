"""Create transparent candidate-match explanations."""

from __future__ import annotations

from collections.abc import Mapping


def _unique_skills(skills: list[str]) -> list[str]:
    """Remove duplicate skill labels while preserving their first occurrence."""
    unique: list[str] = []
    seen: set[str] = set()
    for skill in skills:
        normalized = skill.casefold()
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
    candidate_skill_names = {skill.casefold() for skill in candidate_skills}
    matched_skills = [skill for skill in required if skill.casefold() in candidate_skill_names]
    missing_skills = [skill for skill in required if skill.casefold() not in candidate_skill_names]

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
