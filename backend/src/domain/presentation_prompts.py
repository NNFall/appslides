from __future__ import annotations


def title_prompt(topic: str) -> str:
    return (
        'Create a concise presentation title from the user request. '
        'Use 3-7 words. Return only the title text, with no quotes and no final period. '
        'The title must be in English unless the user explicitly asked for another language.\n'
        f'Topic: {topic}\n'
    )


def outline_prompt(topic: str, slides: int) -> str:
    return (
        'Create a presentation outline. Return only slide titles, one title per line, '
        'without numbering or extra commentary. '
        'The outline must be in English unless the user explicitly asked for another language.\n'
        f'Topic: {topic}\n'
        f'Number of content slides: {slides}\n'
    )


def outline_comment_prompt(topic: str, slides: int, outline: list[str], comment: str) -> str:
    outline_text = '\n'.join(f'- {item}' for item in outline)
    return (
        'You have the current presentation outline and the user revision comment. '
        'Regenerate the outline with the requested number of content slides and apply the comment. '
        'Return only slide titles, one per line, without numbering or extra commentary. '
        'The outline must be in English unless the user explicitly asked for another language.\n'
        f'Topic: {topic}\n'
        f'Number of content slides: {slides}\n'
        f'Current outline:\n{outline_text}\n'
        f'User comment: {comment}\n'
    )


def slides_prompt(topic: str, outline: list[str]) -> str:
    return (
        'Generate a JSON array of slide content. Each item must have this shape: '
        '{"title": str, "text": str, "image_prompt": str}. '
        'The text must be concise: 2-3 sentences, no longer than 320 characters. '
        'Each title must be 4-7 words. '
        'Each image_prompt must be a vivid English prompt for a clean presentation illustration, '
        'not a long paragraph and not a copy of the slide text. '
        'Return only valid JSON. '
        'All slide content must be in English unless the user explicitly asked for another language.\n'
        f'Topic: {topic}\n'
        f'Outline: {outline}\n'
    )
