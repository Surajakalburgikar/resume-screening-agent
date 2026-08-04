"""Application configuration helpers."""

from __future__ import annotations

import os
from pathlib import Path


def get_groq_api_key(env_file: str | Path = ".env") -> str:
    """Read the Groq key from the environment or an ignored local ``.env`` file."""
    if api_key := os.getenv("GROQ_API_KEY"):
        return api_key

    path = Path(env_file)
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if key.strip() == "GROQ_API_KEY" and separator:
            return value.strip().strip('"').strip("'")
    return ""
