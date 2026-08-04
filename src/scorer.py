"""Compute semantic similarity scores for candidates."""

from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


SIMILARITY_WEIGHT = 0.7
SKILL_MATCH_WEIGHT = 0.2
EXPERIENCE_WEIGHT = 0.1


def calculate_similarity(
    jd_embedding: np.ndarray,
    resume_embedding: np.ndarray,
) -> float:
    """Return cosine similarity between a JD and resume as a percentage.

    The result is bounded to the practical 0--100 range and rounded to one
    decimal place. A zero-valued embedding has no directional similarity and
    therefore receives 0.0.
    """
    jd_vector = np.asarray(jd_embedding, dtype=float).reshape(-1)
    resume_vector = np.asarray(resume_embedding, dtype=float).reshape(-1)

    if jd_vector.size == 0 or resume_vector.size == 0:
        raise ValueError("Embeddings must not be empty.")
    if jd_vector.size != resume_vector.size:
        raise ValueError("JD and resume embeddings must have the same size.")
    if not np.any(jd_vector) or not np.any(resume_vector):
        return 0.0

    similarity = cosine_similarity([jd_vector], [resume_vector])[0, 0]
    return round(float(np.clip(similarity * 100, 0, 100)), 1)


def calculate_skill_match(
    candidate_skills: list[str],
    required_skills: list[str],
) -> float:
    """Return the percentage of required skills held by a candidate."""
    required = {skill.casefold() for skill in required_skills}
    candidate = {skill.casefold() for skill in candidate_skills}
    if not required:
        return 100.0
    return round(len(required & candidate) / len(required) * 100, 1)


def calculate_experience_score(
    candidate_experience: float,
    required_experience: float,
) -> float:
    """Return an experience score capped at 100 percent."""
    if candidate_experience < 0 or required_experience < 0:
        raise ValueError("Experience values must not be negative.")
    if required_experience == 0:
        return 100.0
    return round(min(candidate_experience / required_experience * 100, 100), 1)


def calculate_weighted_score(
    similarity: float,
    skill_match: float,
    experience_score: float,
) -> float:
    """Combine score components using 70% similarity, 20% skills, and 10% experience."""
    components = (similarity, skill_match, experience_score)
    if any(not 0 <= component <= 100 for component in components):
        raise ValueError("Each score component must be between 0 and 100.")

    final_score = (
        SIMILARITY_WEIGHT * similarity
        + SKILL_MATCH_WEIGHT * skill_match
        + EXPERIENCE_WEIGHT * experience_score
    )
    return round(final_score, 1)
