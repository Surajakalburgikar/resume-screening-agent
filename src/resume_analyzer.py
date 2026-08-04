"""Analyze resume content with Groq and a deterministic fallback."""

from __future__ import annotations

import json

from config import get_groq_api_key
from src.extractor import extract_candidate_data
from src.jd_analyzer import GROQ_MODEL, GroqClient, _create_client


RESUME_FIELDS = (
    "name",
    "skills",
    "education",
    "experience",
    "email",
    "phone",
    "projects",
    "highlights",
)


def _fallback_analysis(resume_text: str) -> dict[str, object]:
    return {**extract_candidate_data(resume_text), "highlights": [], "analysis_source": "fallback"}


def _normalize_analysis(raw_analysis: object) -> dict[str, object]:
    """Validate model output and return the candidate-data shape."""
    if not isinstance(raw_analysis, dict):
        raise ValueError("Groq did not return a JSON object.")

    normalized: dict[str, object] = {}
    for field in ("name", "education", "email", "phone"):
        value = raw_analysis.get(field, "")
        normalized[field] = value.strip() if isinstance(value, str) else ""
    for field in ("skills", "projects", "highlights"):
        value = raw_analysis.get(field, [])
        normalized[field] = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    experience = raw_analysis.get("experience", 0)
    normalized["experience"] = max(float(experience), 0) if isinstance(experience, (int, float)) else 0
    normalized["analysis_source"] = "groq"
    return normalized


def analyze_resume(resume_text: str, client: GroqClient | None = None) -> dict[str, object]:
    """Extract candidate evidence with Groq when a key is configured."""
    if not resume_text.strip():
        raise ValueError("Resume text must not be empty.")

    if client is None:
        api_key = get_groq_api_key()
        if not api_key:
            return _fallback_analysis(resume_text)
        client = _create_client(api_key)

    prompt = f"""Extract factual candidate information from this resume.
Return JSON only with these fields: {", ".join(RESUME_FIELDS)}.
Use arrays of strings for skills, projects, and highlights; a numeric value for
experience; strings for remaining fields. Do not invent information. Highlights
must be brief accomplishments or project evidence stated in the resume.

RESUME:
{resume_text}"""
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You extract factual resume evidence."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return _normalize_analysis(json.loads(completion.choices[0].message.content))
    except Exception:
        return _fallback_analysis(resume_text)
