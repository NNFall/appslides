from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.integrations.text_generation import (  # noqa: E402
    PresentationGenerationClient,
    TextGenerationError,
)


class StaticOutlineClient(PresentationGenerationClient):
    def __init__(self, content: str) -> None:
        super().__init__(
            api_key='test-key',
            base_url='',
            text_model='test-model',
            image_model='',
            text_endpoint='http://test.local/chat',
        )
        self.content = content

    def _post(self, url: str, payload: dict) -> dict:
        return {
            'choices': [
                {
                    'message': {
                        'content': self.content,
                    }
                }
            ]
        }


class OutlineGenerationParsingTests(unittest.TestCase):
    def test_rejects_provider_apology_as_outline(self) -> None:
        client = StaticOutlineClient(
            'I seem to be encountering an error. Can I try something else for you?'
        )

        with self.assertRaises(TextGenerationError):
            client.generate_outline('Elon Musk and modern innovation', 6)

    def test_filters_intro_code_fence_and_keeps_exact_slide_titles(self) -> None:
        client = StaticOutlineClient(
            '\n'.join(
                [
                    'Here is the presentation outline you requested.',
                    '```text:elon_musk_innovation_outline.txt',
                    'Elon Musk: The Visionary Architect',
                    'Revolutionizing Sustainable Energy with Tesla',
                    'Pushing Frontiers: SpaceX and Commercial Spaceflight',
                    'Neuralink and the Future of Brain-Computer Interfaces',
                    'The Boring Company and Urban Transportation',
                    'Risks, Criticism, and Future Impact',
                    '```',
                ]
            )
        )

        self.assertEqual(
            client.generate_outline('Elon Musk and modern innovation', 6),
            [
                'Elon Musk: The Visionary Architect',
                'Revolutionizing Sustainable Energy with Tesla',
                'Pushing Frontiers: SpaceX and Commercial Spaceflight',
                'Neuralink and the Future of Brain-Computer Interfaces',
                'The Boring Company and Urban Transportation',
                'Risks, Criticism, and Future Impact',
            ],
        )

    def test_rejects_outline_when_valid_titles_are_missing(self) -> None:
        client = StaticOutlineClient(
            '\n'.join(
                [
                    'Here is the presentation outline you requested.',
                    '```text:elon_musk_innovation_outline.txt',
                    'Elon Musk: The Visionary Architect',
                    'Revolutionizing Sustainable Energy with Tesla',
                    'Pushing Frontiers: SpaceX and Commercial Spaceflight',
                    'Neuralink and the Future of Brain-Computer Interfaces',
                ]
            )
        )

        with self.assertRaises(TextGenerationError):
            client.generate_outline('Elon Musk and modern innovation', 6)

    def test_keeps_first_required_titles_when_provider_returns_extra(self) -> None:
        client = StaticOutlineClient(
            '\n'.join(
                [
                    'Elon Musk: The Visionary Architect',
                    'Revolutionizing Sustainable Energy with Tesla',
                    'Pushing Frontiers: SpaceX and Commercial Spaceflight',
                    'Neuralink and the Future of Brain-Computer Interfaces',
                    'The Boring Company and Urban Transportation',
                    'Risks, Criticism, and Future Impact',
                    'Extra title that should be ignored',
                ]
            )
        )

        self.assertEqual(
            client.generate_outline('Elon Musk and modern innovation', 6),
            [
                'Elon Musk: The Visionary Architect',
                'Revolutionizing Sustainable Energy with Tesla',
                'Pushing Frontiers: SpaceX and Commercial Spaceflight',
                'Neuralink and the Future of Brain-Computer Interfaces',
                'The Boring Company and Urban Transportation',
                'Risks, Criticism, and Future Impact',
            ],
        )


if __name__ == '__main__':
    unittest.main()
