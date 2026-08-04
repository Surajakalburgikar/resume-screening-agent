"""Tests for candidate detail extraction."""

import unittest

from src.extractor import extract_candidate_data


class CandidateExtractorTests(unittest.TestCase):
    def test_extract_candidate_data_returns_requested_fields(self) -> None:
        resume_text = """John Doe
        john.doe@example.com | +1 (555) 123-4567
        Software engineer with 4+ years of experience in Python, FastAPI, SQL,
        Docker, AWS, pandas, and scikit-learn.
        Education: Bachelor of Technology in Computer Science
        Projects: Resume Screener | API Monitoring Dashboard
        Certifications: AWS Certified Cloud Practitioner"""

        candidate = extract_candidate_data(resume_text)

        self.assertEqual(candidate["name"], "John Doe")
        self.assertEqual(candidate["email"], "john.doe@example.com")
        self.assertEqual(candidate["phone"], "+1 (555) 123-4567")
        self.assertEqual(candidate["experience"], 4)
        self.assertEqual(
            candidate["skills"],
            ["Python", "SQL", "FastAPI", "Docker", "AWS", "pandas", "scikit-learn"],
        )
        self.assertEqual(candidate["education"], "Bachelor of Technology in Computer Science")
        self.assertEqual(
            candidate["projects"],
            ["Resume Screener", "API Monitoring Dashboard"],
        )

    def test_extract_candidate_data_uses_empty_defaults_for_missing_details(self) -> None:
        candidate = extract_candidate_data("An unstructured resume")

        self.assertEqual(candidate["name"], "")
        self.assertEqual(candidate["skills"], [])
        self.assertEqual(candidate["education"], "")
        self.assertEqual(candidate["experience"], 0)
        self.assertEqual(candidate["email"], "")
        self.assertEqual(candidate["phone"], "")
        self.assertEqual(candidate["projects"], [])


if __name__ == "__main__":
    unittest.main()
