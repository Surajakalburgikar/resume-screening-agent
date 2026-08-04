"""Streamlit interface for screening PDF resumes."""

from __future__ import annotations

from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from src.parser import read_resumes
from src.report import export_rankings
from src.utils import screen_candidates


def _save_uploads(uploaded_files: list[st.runtime.uploaded_file_manager.UploadedFile], folder: Path) -> None:
    for uploaded_file in uploaded_files:
        (folder / Path(uploaded_file.name).name).write_bytes(uploaded_file.getvalue())


def _ranking_table(candidates: list[dict[str, object]]) -> pd.DataFrame:
    rows = [
        {
            "Rank": candidate["rank"],
            "Candidate": candidate["name"] or candidate["resume_file"],
            "Score": candidate["final_score"],
            "Similarity": candidate["similarity_score"],
            "Top matching skills": ", ".join(candidate["matched_skills"][:5]),
            "Missing skills": ", ".join(candidate["missing_skills"]) or "None",
        }
        for candidate in candidates
    ]
    return pd.DataFrame(rows)


def main() -> None:
    st.set_page_config(page_title="Resume Screening Agent", page_icon="📄", layout="wide")
    st.title("Resume Screening Agent")
    st.caption("Upload a job description and resume files to generate an explainable ranking.")

    job_description = st.text_area("Job description", height=220, placeholder="Paste the job description here...")
    resumes = st.file_uploader("Resume files", type=["pdf", "docx"], accept_multiple_files=True)
    use_groq = st.checkbox(
        "Use Groq for deeper JD and resume analysis",
        value=True,
        help="When enabled, the uploaded job description and resume text are sent to Groq for structured analysis.",
    )

    if st.button("Screen candidates", type="primary"):
        if not job_description.strip() or not resumes:
            st.error("Provide a job description and at least one PDF or DOCX resume.")
        else:
            progress = st.progress(5, text="Preparing uploaded resumes...")
            try:
                with tempfile.TemporaryDirectory() as directory:
                    _save_uploads(resumes, Path(directory))
                    resume_texts = read_resumes(directory)
                    progress.progress(30, text="Extracting candidate details...")
                    rankings = screen_candidates(resume_texts, job_description, use_groq=use_groq)
                    progress.progress(85, text="Creating reports...")
                    csv_path, json_path = export_rankings(rankings)
                    st.session_state["rankings"] = rankings
                    st.session_state["csv_data"] = csv_path.read_bytes()
                    st.session_state["json_data"] = json_path.read_bytes()
                    progress.progress(100, text="Screening complete.")
            except (OSError, ValueError, RuntimeError) as error:
                st.error(f"Screening could not be completed: {error}")

    rankings = st.session_state.get("rankings", [])
    if rankings:
        source = rankings[0].get("job_analysis_source", "local")
        st.caption(f"Job analysis: {source}")
        minimum_score = st.slider("Minimum score", 0, 100, 0)
        visible_rankings = [
            candidate for candidate in rankings if candidate["final_score"] >= minimum_score
        ]
        st.dataframe(_ranking_table(visible_rankings), use_container_width=True, hide_index=True)
        st.download_button("Download CSV", st.session_state["csv_data"], "rankings.csv", "text/csv")
        st.download_button("Download JSON", st.session_state["json_data"], "rankings.json", "application/json")

        st.subheader("Candidate details")
        for candidate in visible_rankings:
            name = candidate["name"] or candidate["resume_file"]
            with st.expander(f"#{candidate['rank']} — {name} ({candidate['final_score']}%)"):
                st.write(candidate["reason"])
                st.success("Matched: " + (", ".join(candidate["matched_skills"][:5]) or "None"))
                st.warning("Missing: " + (", ".join(candidate["missing_skills"]) or "None"))
                for item in candidate["requirement_evidence"]:
                    if item["matched"]:
                        st.info(f"{item['requirement']}: {item['evidence']}")


if __name__ == "__main__":
    main()
