"""Tests for the complete screening workflow."""

import unittest

import numpy as np
from unittest.mock import patch

from src.utils import screen_candidates


class FakeEmbeddingModel:
    def encode(self, sentences: list[str], **kwargs: object) -> np.ndarray:
        vectors = {
            "Python FastAPI engineer with 3 years of experience.": [1.0, 0.0],
            "Alice Doe\nPython FastAPI developer with 4 years of experience.": [1.0, 0.0],
            "John Smith\nSQL developer with 1 year of experience.": [0.0, 1.0],
        }
        return np.array([vectors[sentence] for sentence in sentences])


class ScreeningWorkflowTests(unittest.TestCase):
    def test_screen_candidates_returns_ranked_explainable_results(self) -> None:
        rankings = screen_candidates(
            {
                "alice.pdf": "Alice Doe\nPython FastAPI developer with 4 years of experience.",
                "john.pdf": "John Smith\nSQL developer with 1 year of experience.",
            },
            "Python FastAPI engineer with 3 years of experience.",
            FakeEmbeddingModel(),
        )

        self.assertEqual([candidate["name"] for candidate in rankings], ["Alice Doe", "John Smith"])
        self.assertEqual(rankings[0]["final_score"], 100.0)
        self.assertEqual(rankings[0]["matched_skills"], ["Python", "FastAPI"])
        self.assertEqual(rankings[1]["missing_skills"], ["Python", "FastAPI"])

    def test_screen_candidates_rejects_empty_resume_collection(self) -> None:
        with self.assertRaises(ValueError):
            screen_candidates({}, "Python engineer", FakeEmbeddingModel())

    @patch("src.utils.analyze_resume")
    @patch("src.utils.analyze_job_description")
    def test_screen_candidates_uses_groq_analysis_when_enabled(
        self,
        mock_job_analysis: object,
        mock_resume_analysis: object,
    ) -> None:
        mock_job_analysis.return_value = {
            "must_have_skills": ["Python"],
            "minimum_experience": 3,
            "analysis_source": "groq",
        }
        mock_resume_analysis.return_value = {
            "name": "Alice Doe",
            "skills": ["Python"],
            "education": "",
            "experience": 4,
            "email": "",
            "phone": "",
            "projects": [],
            "highlights": [],
            "analysis_source": "groq",
        }

        rankings = screen_candidates(
            {"alice.pdf": "Alice Doe\nPython FastAPI developer with 4 years of experience."},
            "Python FastAPI engineer with 3 years of experience.",
            FakeEmbeddingModel(),
            use_groq=True,
        )

        mock_job_analysis.assert_called_once()
        mock_resume_analysis.assert_called_once()
        self.assertEqual(rankings[0]["job_analysis_source"], "groq")


if __name__ == "__main__":
    unittest.main()
