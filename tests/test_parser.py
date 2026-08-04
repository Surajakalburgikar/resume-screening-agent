"""Tests for PDF resume parsing."""

from pathlib import Path
import tempfile
import unittest

import fitz

from src.parser import read_resumes


class ResumeParserTests(unittest.TestCase):
    def _create_pdf(self, path: Path, text: str) -> None:
        document = fitz.open()
        page = document.new_page()
        page.insert_text((72, 72), text)
        document.save(path)
        document.close()

    def test_read_resumes_returns_cleaned_text_for_each_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            resume_folder = Path(directory)
            self._create_pdf(resume_folder / "alice.pdf", "Alice\n\nPython Developer")
            self._create_pdf(resume_folder / "john.pdf", "John\tData Engineer")
            (resume_folder / "notes.txt").write_text("Ignore me", encoding="utf-8")

            resume_texts = read_resumes(resume_folder)

        self.assertEqual(
            resume_texts,
            {
                "alice.pdf": "Alice Python Developer",
                "john.pdf": "John Data Engineer",
            },
        )

    def test_read_resumes_rejects_missing_folder(self) -> None:
        with self.assertRaises(FileNotFoundError):
            read_resumes("missing-resume-folder")


if __name__ == "__main__":
    unittest.main()
