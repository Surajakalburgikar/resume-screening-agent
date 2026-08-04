"""Tests for candidate-match explanation generation."""

import unittest
import json
from pathlib import Path
import tempfile

import pandas as pd

from src.report import export_rankings, generate_match_reason


class MatchReasonTests(unittest.TestCase):
    def test_generate_match_reason_reports_evidence_and_gaps(self) -> None:
        result = generate_match_reason(
            {
                "name": "John",
                "rank": 1,
                "skills": ["Python", "FastAPI", "SQL", "Docker"],
                "experience": 4,
            },
            ["Python", "FastAPI", "SQL", "Docker", "Kubernetes", "AWS"],
            required_experience=3,
        )

        self.assertEqual(result["matched_skills"], ["Python", "FastAPI", "SQL", "Docker"])
        self.assertEqual(result["missing_skills"], ["Kubernetes", "AWS"])
        self.assertEqual(
            result["experience_summary"],
            "4 years of experience meets the 3-year requirement.",
        )
        self.assertEqual(
            result["reason"],
            "John is ranked #1 because of matching skills: Python, FastAPI, SQL, Docker. "
            "4 years of experience meets the 3-year requirement. "
            "Missing skills: Kubernetes, AWS.",
        )

    def test_generate_match_reason_handles_no_job_requirements(self) -> None:
        result = generate_match_reason({"name": "Alice", "skills": []}, [])

        self.assertEqual(result["matched_skills"], [])
        self.assertEqual(result["missing_skills"], [])
        self.assertIn("no listed required skills", result["reason"])
        self.assertIn("does not state an experience requirement", result["reason"])

    def test_export_rankings_writes_csv_and_json(self) -> None:
        rankings = [
            {
                "rank": 1,
                "name": "John",
                "final_score": 91.0,
                "matched_skills": ["Python", "SQL"],
                "missing_skills": ["AWS"],
            }
        ]
        with tempfile.TemporaryDirectory() as directory:
            csv_path, json_path = export_rankings(rankings, directory)

            self.assertEqual(csv_path, Path(directory) / "rankings.csv")
            self.assertEqual(json_path, Path(directory) / "rankings.json")
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), rankings)
            exported_csv = pd.read_csv(csv_path)

        self.assertEqual(exported_csv.loc[0, "name"], "John")
        self.assertEqual(exported_csv.loc[0, "matched_skills"], "Python, SQL")
        self.assertEqual(exported_csv.loc[0, "missing_skills"], "AWS")


if __name__ == "__main__":
    unittest.main()
