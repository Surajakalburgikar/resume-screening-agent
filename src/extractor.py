"""Extract structured candidate details from resume text."""

from __future__ import annotations

import re


SKILL_PATTERNS = {
    "Python": r"\bpython\b",
    "Java": r"\bjava\b",
    "C++": r"\bc\+\+\b",
    "JavaScript": r"\bjavascript\b|\bjs\b",
    "TypeScript": r"\btypescript\b",
    "SQL": r"\bsql\b",
    "FastAPI": r"\bfastapi\b",
    "Django": r"\bdjango\b",
    "Flask": r"\bflask\b",
    "React": r"\breact(?:\.js)?\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b|\bk8s\b",
    "AWS": r"\baws\b|\bamazon web services\b",
    "Azure": r"\bazure\b",
    "GCP": r"\bgcp\b|\bgoogle cloud platform\b",
    "Git": r"\bgit\b",
    "Machine Learning": r"\bmachine learning\b",
    "NLP": r"\bnlp\b|\bnatural language processing\b",
    "pandas": r"\bpandas\b",
    "scikit-learn": r"\bscikit-learn\b|\bsklearn\b",
}

SECTION_ENDINGS = r"experience|education|skills|certifications?|achievements?|publications?|languages?"


def _extract_name(text: str) -> str:
    """Infer a name from a title-cased line near the start of a resume."""
    first_line = text.strip().splitlines()[0] if text.strip() else ""
    first_line = re.sub(r"\s+", " ", first_line).strip()
    if re.fullmatch(r"[A-Z][a-z]+(?:[ -][A-Z][a-z]+){1,3}", first_line):
        return first_line
    return ""


def _extract_education(text: str) -> str:
    degree_pattern = re.compile(
        r"\b(?:b\.?\s?(?:tech|e|sc|a)|m\.?\s?(?:tech|e|sc|a)|"
        r"bachelor(?:'s)?|master(?:'s)?|ph\.?d\.?)\b[^.\n;]{0,100}",
        re.IGNORECASE,
    )
    match = degree_pattern.search(text)
    return match.group(0).strip(" ,:-") if match else ""


def _extract_experience_years(text: str) -> int:
    matches = re.findall(
        r"\b(\d{1,2})\s*\+?\s*(?:years?|yrs?)(?:\s+of)?\s+experience\b",
        text,
        flags=re.IGNORECASE,
    )
    return max((int(years) for years in matches), default=0)


def _extract_projects(text: str) -> list[str]:
    match = re.search(
        rf"\bprojects?\b\s*[:\-]?\s*(.*?)(?=\b(?:{SECTION_ENDINGS})\b|$)",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return []

    project_text = match.group(1).strip()
    projects = re.split(r"\s*[|;•]\s*|\n+", project_text)
    return [project.strip(" -:") for project in projects if project.strip(" -:")]


def extract_candidate_data(resume_text: str) -> dict[str, object]:
    """Extract contact details, qualifications, skills, and projects from a resume.

    The extractor uses deterministic regex and text-pattern heuristics so it
    works without an additional NLP model or service. Missing fields are
    returned as empty strings, empty lists, or zero.
    """
    email_match = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", resume_text, re.I)
    phone_match = re.search(r"(?<!\w)(?:\+?\d{1,3}[ .-]?)?(?:\(?\d{2,4}\)?[ .-]?){2,3}\d{3,4}(?!\w)", resume_text)
    skills = [
        skill
        for skill, pattern in SKILL_PATTERNS.items()
        if re.search(pattern, resume_text, flags=re.IGNORECASE)
    ]

    return {
        "name": _extract_name(resume_text),
        "skills": skills,
        "education": _extract_education(resume_text),
        "experience": _extract_experience_years(resume_text),
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else "",
        "projects": _extract_projects(resume_text),
    }
