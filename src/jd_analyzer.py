"""Analyze job descriptions with Groq and a deterministic fallback."""

from __future__ import annotations

import json
from typing import Protocol

from config import get_groq_api_key
from src.extractor import extract_candidate_data


GROQ_MODEL = "openai/gpt-oss-20b"
ANALYSIS_FIELDS = (
    "must_have_skills",
    "preferred_skills",
    "minimum_experience",
    "seniority",
    "responsibilities",
    "domain",
)


class GroqClient(Protocol):
    """The subset of the Groq SDK client used for structured analysis."""

    chat: object


def _fallback_analysis(job_description: str) -> dict[str, object]:
    extracted = extract_candidate_data(job_description)
    return {
        "must_have_skills": extracted["skills"],
        "preferred_skills": [],
        "minimum_experience": extracted["experience"],
        "seniority": "",
        "responsibilities": [],
        "domain": "",
        "analysis_source": "fallback",
    }


def _normalize_analysis(raw_analysis: object) -> dict[str, object]:
    """Validate model output and return a stable analysis shape."""
    if not isinstance(raw_analysis, dict):
        raise ValueError("Groq did not return a JSON object.")

    normalized: dict[str, object] = {}
    for field in ("must_have_skills", "preferred_skills", "responsibilities"):
        value = raw_analysis.get(field, [])
        normalized[field] = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    experience = raw_analysis.get("minimum_experience", 0)
    normalized["minimum_experience"] = max(float(experience), 0) if isinstance(experience, (int, float)) else 0
    for field in ("seniority", "domain"):
        value = raw_analysis.get(field, "")
        normalized[field] = value.strip() if isinstance(value, str) else ""
    normalized["analysis_source"] = "groq"
    return normalized


def _create_client(api_key: str) -> GroqClient:
    from groq import Groq

    return Groq(api_key=api_key)


def analyze_job_description(
    job_description: str,
    client: GroqClient | None = None,
) -> dict[str, object]:
    """Extract structured job requirements using Groq when configured.

    The model is instructed to extract only requirements supported by the job
    description. If no key is configured or the response cannot be validated,
    deterministic local extraction keeps screening available.
    """
    if not job_description.strip():
        raise ValueError("Job description must not be empty.")

    if client is None:
        api_key = get_groq_api_key()
        if not api_key:
            return _fallback_analysis(job_description)
        client = _create_client(api_key)

    prompt = f"""Extract structured hiring requirements from this job description.
Return JSON only with these fields: {", ".join(ANALYSIS_FIELDS)}.
Use arrays of strings for skills and responsibilities, a numeric value for
minimum_experience, and strings for seniority and domain. Do not infer facts
that are not stated. Separate required skills from preferred/nice-to-have skills.

JOB DESCRIPTION:
{job_description}"""
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You extract factual hiring requirements."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        return _normalize_analysis(json.loads(content))
    except Exception:
        # The external API can fail due to timeouts, authentication, rate limits,
        # or malformed output. Keep screening available with local extraction.
        return _fallback_analysis(job_description)
