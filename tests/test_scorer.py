"""Tests for semantic similarity scoring."""

import unittest

import numpy as np

from src.scorer import calculate_similarity


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


if __name__ == "__main__":
    unittest.main()
