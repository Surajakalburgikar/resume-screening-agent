"""Map JD responsibilities to resume evidence with Groq."""

from __future__ import annotations

import json
from collections.abc import Mapping

from config import get_groq_api_key
from src.jd_analyzer import GROQ_MODEL, GroqClient, _create_client


def _responsibilities(job_analysis: Mapping[str, object]) -> list[str]:
    raw_responsibilities = job_analysis.get("responsibilities", [])
    if not isinstance(raw_responsibilities, list):
        return []
    return [item for item in raw_responsibilities[:5] if isinstance(item, str) and item.strip()]


def _normalize_evidence(raw_evidence: object, responsibilities: list[str]) -> list[dict[str, object]]:
    """Keep only evidence tied to an original JD responsibility."""
    if not isinstance(raw_evidence, list):
        raise ValueError("Groq did not return an evidence list.")

    normalized: list[dict[str, object]] = []
    seen_indexes: set[int] = set()
    for item in raw_evidence:
        if not isinstance(item, dict):
            continue
        index = item.get("requirement_index")
        matched = item.get("matched")
        evidence = item.get("evidence", "")
        if (
            not isinstance(index, int)
            or index in seen_indexes
            or not 0 <= index < len(responsibilities)
            or not isinstance(matched, bool)
            or not isinstance(evidence, str)
        ):
            continue
        normalized.append(
            {
                "requirement": responsibilities[index],
                "matched": matched,
                "evidence": evidence.strip() if matched else "",
            }
        )
        seen_indexes.add(index)
    return normalized


def map_requirement_evidence(
    job_analysis: Mapping[str, object],
    candidate: Mapping[str, object],
    client: GroqClient | None = None,
) -> list[dict[str, object]]:
    """Return factual project/highlight evidence for up to five JD responsibilities."""
    responsibilities = _responsibilities(job_analysis)
    if not responsibilities:
        return []

    if client is None:
        api_key = get_groq_api_key()
        if not api_key:
            return []
        client = _create_client(api_key)

    candidate_context = {
        "skills": candidate.get("skills", []),
        "projects": candidate.get("projects", []),
        "highlights": candidate.get("highlights", []),
        "experience": candidate.get("experience", 0),
    }
    prompt = f"""Map JD responsibilities to factual candidate evidence.
Return JSON only as {{"evidence": [...]}}. Each evidence item must have a
requirement_index (integer), matched (boolean), and evidence (string). Use only
the supplied candidate context; do not infer or invent accomplishments. Include
at most one item for each requirement index.

JD RESPONSIBILITIES:
{json.dumps(responsibilities)}

CANDIDATE CONTEXT:
{json.dumps(candidate_context)}"""
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You map requirements to factual candidate evidence."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        response = json.loads(completion.choices[0].message.content)
        return _normalize_evidence(response.get("evidence"), responsibilities)
    except Exception:
        return []
