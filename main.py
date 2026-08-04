"""Command-line entry point for resume screening."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.embedder import EmbeddingModel
from src.parser import read_resumes
from src.report import export_rankings
from src.utils import screen_candidates


def run_screening(
    resume_folder: str | Path,
    job_description_file: str | Path,
    output_dir: str | Path = "output",
    model: EmbeddingModel | None = None,
    use_groq: bool = True,
) -> tuple[list[dict[str, object]], Path, Path]:
    """Screen a resume folder against a text job description and export reports."""
    job_path = Path(job_description_file)
    if not job_path.is_file():
        raise FileNotFoundError(f"Job description file does not exist: {job_path}")

    rankings = screen_candidates(
        read_resumes(resume_folder),
        job_path.read_text(encoding="utf-8"),
        model=model,
        use_groq=use_groq,
    )
    csv_path, json_path = export_rankings(rankings, output_dir)
    return rankings, csv_path, json_path


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Rank PDF/DOCX resumes against a job description.")
    parser.add_argument("--resumes", default="resumes", help="Folder containing PDF/DOCX resumes.")
    parser.add_argument(
        "--job-description",
        default="jd/software_engineer.txt",
        help="Path to a UTF-8 text job description.",
    )
    parser.add_argument("--output", default="output", help="Folder for rankings.csv and rankings.json.")
    parser.add_argument("--no-groq", action="store_true", help="Use local extraction only.")
    return parser.parse_args()


def main() -> None:
    """Run screening and print the ranked candidates."""
    args = parse_args()
    rankings, csv_path, json_path = run_screening(
        args.resumes,
        args.job_description,
        args.output,
        use_groq=not args.no_groq,
    )
    for candidate in rankings:
        name = candidate["name"] or candidate["resume_file"]
        print(f"#{candidate['rank']} {name}: {candidate['final_score']}%")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")


if __name__ == "__main__":
    main()
