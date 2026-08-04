"""Generate semantic embeddings for job descriptions and resumes."""

from __future__ import annotations

from typing import Protocol

import numpy as np


MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingModel(Protocol):
    """The subset of SentenceTransformer used by this module."""

    def encode(self, sentences: list[str], **kwargs: object) -> np.ndarray: ...


def load_embedding_model() -> EmbeddingModel:
    """Load the default Sentence Transformers model when it is needed."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


def generate_embeddings(
    resume_texts: dict[str, str],
    job_description: str,
    model: EmbeddingModel | None = None,
) -> tuple[dict[str, np.ndarray], np.ndarray]:
    """Return normalized resume embeddings and a normalized JD embedding."""
    if not job_description.strip():
        raise ValueError("Job description must not be empty.")

    encoder = model or load_embedding_model()
    resume_names = list(resume_texts)
    texts_to_encode = [job_description, *(resume_texts[name] for name in resume_names)]
    embeddings = encoder.encode(
        texts_to_encode,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    jd_embedding = embeddings[0]
    resume_embeddings = {
        name: embeddings[index + 1] for index, name in enumerate(resume_names)
    }
    return resume_embeddings, jd_embedding
