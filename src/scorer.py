"""Compute semantic similarity scores for candidates."""

from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


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
