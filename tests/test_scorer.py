"""Tests for semantic similarity scoring."""

import unittest

import numpy as np

from src.scorer import (
    calculate_experience_score,
    calculate_similarity,
    calculate_skill_match,
    calculate_weighted_score,
)


class SimilarityScorerTests(unittest.TestCase):
    def test_calculate_similarity_returns_percentage(self) -> None:
        score = calculate_similarity(
            np.array([1.0, 0.0]),
            np.array([0.874, 0.486]),
        )

        self.assertEqual(score, 87.4)

    def test_calculate_similarity_returns_zero_for_zero_vector(self) -> None:
        score = calculate_similarity(np.array([1.0, 0.0]), np.array([0.0, 0.0]))

        self.assertEqual(score, 0.0)

    def test_calculate_similarity_rejects_mismatched_vectors(self) -> None:
        with self.assertRaises(ValueError):
            calculate_similarity(np.array([1.0, 0.0]), np.array([1.0, 0.0, 0.0]))

    def test_calculate_skill_match_compares_unique_skills_case_insensitively(self) -> None:
        score = calculate_skill_match(
            ["Python", "SQL", "python"],
            ["python", "Docker", "SQL"],
        )

        self.assertEqual(score, 66.7)

    def test_calculate_skill_match_recognizes_common_skill_aliases(self) -> None:
        score = calculate_skill_match(
            ["K8s", "Amazon Web Services", "Postgres", "sklearn"],
            ["Kubernetes", "AWS", "PostgreSQL", "scikit-learn"],
        )

        self.assertEqual(score, 100.0)

    def test_calculate_experience_score_caps_at_100(self) -> None:
        self.assertEqual(calculate_experience_score(6, 4), 100.0)
        self.assertEqual(calculate_experience_score(2, 4), 50.0)
        self.assertEqual(calculate_experience_score(2, 0), 100.0)

    def test_calculate_weighted_score_uses_requested_weights(self) -> None:
        final_score = calculate_weighted_score(80.0, 50.0, 100.0)

        self.assertEqual(final_score, 76.0)

    def test_calculate_weighted_score_rejects_invalid_component(self) -> None:
        with self.assertRaises(ValueError):
            calculate_weighted_score(101.0, 50.0, 100.0)


if __name__ == "__main__":
    unittest.main()
