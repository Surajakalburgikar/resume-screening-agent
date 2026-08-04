"""Rank candidates by their final screening score."""

from __future__ import annotations

from collections.abc import Mapping
import math


def rank_candidates(candidates: list[Mapping[str, object]]) -> list[dict[str, object]]:
    """Return candidates ordered by final score, with a 1-based ``rank`` field.

    Candidate records must include a numeric ``final_score`` between 0 and 100.
    Ties are ordered alphabetically by candidate name for deterministic output.
    The input records are copied, never modified in place.
    """
    scored_candidates: list[tuple[float, str, Mapping[str, object]]] = []
    for candidate in candidates:
        score = candidate.get("final_score")
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            raise ValueError("Every candidate must have a numeric final_score.")
        if not math.isfinite(score) or not 0 <= score <= 100:
            raise ValueError("final_score must be between 0 and 100.")

        name = str(candidate.get("name") or candidate.get("resume_file") or "Unknown Candidate")
        scored_candidates.append((float(score), name.casefold(), candidate))

    ranked_candidates: list[dict[str, object]] = []
    for rank, (_, _, candidate) in enumerate(
        sorted(scored_candidates, key=lambda item: (-item[0], item[1])),
        start=1,
    ):
        ranked_candidate = dict(candidate)
        ranked_candidate["rank"] = rank
        ranked_candidates.append(ranked_candidate)

    return ranked_candidates
