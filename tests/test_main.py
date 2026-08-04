"""Tests for the command-line screening entry point."""

from pathlib import Path
import tempfile
import unittest

import fitz
import numpy as np

from main import run_screening


class FakeEmbeddingModel:
    def encode(self, sentences: list[str], **kwargs: object) -> np.ndarray:
        return np.array([[1.0, 0.0] for _ in sentences])


class CommandLineTests(unittest.TestCase):
    def _create_pdf(self, path: Path) -> None:
        document = fitz.open()
        page = document.new_page()
        page.insert_text((72, 72), "Alice Doe\nPython developer with 4 years of experience.")
        document.save(path)
        document.close()

    def test_run_screening_exports_rankings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            resume_folder = workspace / "resumes"
            resume_folder.mkdir()
            self._create_pdf(resume_folder / "alice.pdf")
            job_file = workspace / "job.txt"
            job_file.write_text("Python engineer with 3 years of experience.", encoding="utf-8")

            rankings, csv_path, json_path = run_screening(
                resume_folder,
                job_file,
                workspace / "output",
                FakeEmbeddingModel(),
                use_groq=False,
            )

            self.assertEqual(rankings[0]["name"], "Alice Doe")
            self.assertTrue(csv_path.is_file())
            self.assertTrue(json_path.is_file())

    def test_run_screening_rejects_missing_job_description(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                run_screening(directory, "missing-job-description.txt", model=FakeEmbeddingModel())


if __name__ == "__main__":
    unittest.main()
