"""Tests for structured resume analysis."""

import unittest

from src.resume_analyzer import analyze_resume


class FakeCompletions:
    def create(self, **kwargs: object) -> object:
        return type(
            "Completion",
            (),
            {
                "choices": [
                    type(
                        "Choice",
                        (),
                        {
                            "message": type(
                                "Message",
                                (),
                                {
                                    "content": (
                                        '{"name": "Alice Doe", "skills": ["Python", "SQL"], '
                                        '"education": "BSc Computer Science", "experience": 4, '
                                        '"email": "alice@example.com", "phone": "", '
                                        '"projects": ["Screening App"], '
                                        '"highlights": ["Built APIs"]}'
                                    )
                                },
                            )()
                        },
                    )()
                ]
            },
        )()


class FakeGroqClient:
    def __init__(self) -> None:
        self.chat = type("Chat", (), {"completions": FakeCompletions()})()


class ResumeAnalyzerTests(unittest.TestCase):
    def test_analyze_resume_returns_validated_groq_output(self) -> None:
        analysis = analyze_resume("Alice Doe Python SQL", FakeGroqClient())

        self.assertEqual(analysis["name"], "Alice Doe")
        self.assertEqual(analysis["skills"], ["Python", "SQL"])
        self.assertEqual(analysis["experience"], 4.0)
        self.assertEqual(analysis["highlights"], ["Built APIs"])
        self.assertEqual(analysis["analysis_source"], "groq")


if __name__ == "__main__":
    unittest.main()
