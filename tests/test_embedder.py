"""Tests for semantic embedding generation."""

import unittest

import numpy as np

from src.embedder import generate_embeddings


class FakeEmbeddingModel:
    def __init__(self) -> None:
        self.sentences: list[str] = []
        self.options: dict[str, object] = {}

    def encode(self, sentences: list[str], **kwargs: object) -> np.ndarray:
        self.sentences = sentences
        self.options = kwargs
        return np.array([[index, index + 0.5] for index in range(len(sentences))])


class EmbedderTests(unittest.TestCase):
    def test_generate_embeddings_returns_jd_and_resume_vectors(self) -> None:
        model = FakeEmbeddingModel()
        resume_embeddings, jd_embedding = generate_embeddings(
            {"alice.pdf": "Python developer", "john.pdf": "Data engineer"},
            "Python engineer",
            model,
        )

        self.assertEqual(model.sentences, ["Python engineer", "Python developer", "Data engineer"])
        self.assertTrue(model.options["convert_to_numpy"])
        self.assertTrue(model.options["normalize_embeddings"])
        np.testing.assert_array_equal(jd_embedding, np.array([0.0, 0.5]))
        np.testing.assert_array_equal(resume_embeddings["alice.pdf"], np.array([1.0, 1.5]))
        np.testing.assert_array_equal(resume_embeddings["john.pdf"], np.array([2.0, 2.5]))

    def test_generate_embeddings_rejects_blank_job_description(self) -> None:
        with self.assertRaises(ValueError):
            generate_embeddings({}, "   ", FakeEmbeddingModel())


if __name__ == "__main__":
    unittest.main()
