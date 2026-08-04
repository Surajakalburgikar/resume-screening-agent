"""Tests for structured job-description analysis."""

import unittest

from src.jd_analyzer import analyze_job_description


class FakeCompletions:
    def create(self, **kwargs: object) -> object:
        self.kwargs = kwargs
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
                                        '{"must_have_skills": ["Python", "SQL"], '
                                        '"preferred_skills": ["AWS"], '
                                        '"minimum_experience": 4, '
                                        '"seniority": "Senior", '
                                        '"responsibilities": ["Build APIs"], '
                                        '"domain": "Fintech"}'
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


class JobDescriptionAnalyzerTests(unittest.TestCase):
    def test_analyze_job_description_returns_validated_groq_output(self) -> None:
        analysis = analyze_job_description("Senior Python engineer", FakeGroqClient())

        self.assertEqual(analysis["must_have_skills"], ["Python", "SQL"])
        self.assertEqual(analysis["preferred_skills"], ["AWS"])
        self.assertEqual(analysis["minimum_experience"], 4.0)
        self.assertEqual(analysis["seniority"], "Senior")
        self.assertEqual(analysis["analysis_source"], "groq")

    def test_analyze_job_description_falls_back_for_invalid_model_response(self) -> None:
        client = FakeGroqClient()
        client.chat.completions.create = lambda **kwargs: type(
            "Completion",
            (),
            {"choices": [type("Choice", (), {"message": type("Message", (), {"content": "invalid"})()})()]},
        )()

        analysis = analyze_job_description("Python engineer with 3 years of experience", client)

        self.assertEqual(analysis["must_have_skills"], ["Python"])
        self.assertEqual(analysis["minimum_experience"], 3)
        self.assertEqual(analysis["analysis_source"], "fallback")


if __name__ == "__main__":
    unittest.main()
