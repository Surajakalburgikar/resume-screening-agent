"""Tests for candidate ranking."""

import unittest

from src.ranker import rank_candidates


class CandidateRankerTests(unittest.TestCase):
    def test_rank_candidates_orders_by_score_and_adds_rank(self) -> None:
        candidates = [
            {"name": "David", "final_score": 77.0},
            {"name": "John", "final_score": 91.0},
            {"name": "Alice", "final_score": 84.0},
        ]

        ranked = rank_candidates(candidates)

        self.assertEqual(
            ranked,
            [
                {"name": "John", "final_score": 91.0, "rank": 1},
                {"name": "Alice", "final_score": 84.0, "rank": 2},
                {"name": "David", "final_score": 77.0, "rank": 3},
            ],
        )
        self.assertNotIn("rank", candidates[0])

    def test_rank_candidates_orders_equal_scores_by_name(self) -> None:
        ranked = rank_candidates(
            [
                {"name": "Zoe", "final_score": 80.0},
                {"name": "Alice", "final_score": 80.0},
            ]
        )

        self.assertEqual([candidate["name"] for candidate in ranked], ["Alice", "Zoe"])

    def test_rank_candidates_rejects_invalid_score(self) -> None:
        with self.assertRaises(ValueError):
            rank_candidates([{"name": "John", "final_score": 110.0}])


if __name__ == "__main__":
    unittest.main()
