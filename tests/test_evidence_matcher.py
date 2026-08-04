"""Tests for requirement-to-evidence mapping."""

import unittest

from src.evidence_matcher import map_requirement_evidence


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
                                        '{"evidence": ['
                                        '{"requirement_index": 0, "matched": true, '
                                        '"evidence": "Built REST APIs for the screening app."}, '
                                        '{"requirement_index": 1, "matched": false, "evidence": ""}]}'
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


class EvidenceMatcherTests(unittest.TestCase):
    def test_map_requirement_evidence_uses_validated_requirement_indexes(self) -> None:
        evidence = map_requirement_evidence(
            {"responsibilities": ["Build APIs", "Mentor engineers"]},
            {"skills": ["Python"], "projects": ["Screening app"], "highlights": []},
            FakeGroqClient(),
        )

        self.assertEqual(
            evidence,
            [
                {
                    "requirement": "Build APIs",
                    "matched": True,
                    "evidence": "Built REST APIs for the screening app.",
                },
                {"requirement": "Mentor engineers", "matched": False, "evidence": ""},
            ],
        )

    def test_map_requirement_evidence_skips_when_no_responsibilities_exist(self) -> None:
        self.assertEqual(map_requirement_evidence({}, {}, FakeGroqClient()), [])


if __name__ == "__main__":
    unittest.main()
