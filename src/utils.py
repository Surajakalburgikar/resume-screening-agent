"""Orchestrate the resume-screening workflow."""

from __future__ import annotations

from src.embedder import EmbeddingModel, generate_embeddings
from src.evidence_matcher import map_requirement_evidence
from src.extractor import extract_candidate_data
from src.jd_analyzer import analyze_job_description
from src.ranker import rank_candidates
from src.report import generate_match_reason
from src.resume_analyzer import analyze_resume
from src.scorer import (
    calculate_experience_score,
    calculate_similarity,
    calculate_skill_match,
    calculate_weighted_score,
)


def screen_candidates(
    resume_texts: dict[str, str],
    job_description: str,
    model: EmbeddingModel | None = None,
    use_groq: bool = False,
) -> list[dict[str, object]]:
    """Score, rank, and explain resumes against a job description.

    When ``use_groq`` is enabled, the job description and each resume receive
    structured external analysis; unavailable Groq analysis falls back locally.
    """
    if not resume_texts:
        raise ValueError("At least one resume is required.")

    job_details = (
        analyze_job_description(job_description) if use_groq else extract_candidate_data(job_description)
    )
    if use_groq:
        required_skills = job_details.get("must_have_skills", [])
        required_experience = job_details.get("minimum_experience", 0)
    else:
        required_skills = job_details["skills"]
        required_experience = job_details["experience"]
    resume_embeddings, jd_embedding = generate_embeddings(
        resume_texts,
        job_description,
        model,
    )

    candidates: list[dict[str, object]] = []
    for resume_file, resume_text in resume_texts.items():
        candidate = analyze_resume(resume_text) if use_groq else extract_candidate_data(resume_text)
        similarity = calculate_similarity(jd_embedding, resume_embeddings[resume_file])
        skill_match = calculate_skill_match(candidate["skills"], required_skills)
        experience_score = calculate_experience_score(
            candidate["experience"],
            required_experience,
        )
        candidate.update(
            {
                "resume_file": resume_file,
                "similarity_score": similarity,
                "skill_match_score": skill_match,
                "experience_score": experience_score,
                "final_score": calculate_weighted_score(
                    similarity,
                    skill_match,
                    experience_score,
                ),
                "job_analysis_source": job_details.get("analysis_source", "local"),
            }
        )
        candidates.append(candidate)

    ranked_candidates = rank_candidates(candidates)
    for candidate in ranked_candidates:
        candidate["requirement_evidence"] = (
            map_requirement_evidence(job_details, candidate) if use_groq else []
        )
        candidate.update(
            generate_match_reason(candidate, required_skills, required_experience)
        )
    return ranked_candidates
