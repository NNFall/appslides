from __future__ import annotations


def title_prompt(topic: str) -> str:
    return (
        'Create a short presentation title (3-7 words) from the user request, '
        'matching the user request as closely as possible. '
        'No quotes, no final period, text only. Use English.\n'
        f'Topic: {topic}\n'
    )


def outline_prompt(topic: str, slides: int) -> str:
    return (
        'Create a presentation outline. Return only a list of slide titles, '
        'one title per line, without numbering. Use English.\n'
        f'Topic: {topic}\n'
        f'Number of slides: {slides}\n'
    )


def outline_comment_prompt(topic: str, slides: int, outline: list[str], comment: str) -> str:
    outline_text = '\n'.join(f'- {item}' for item in outline)
    return (
        'You have the current presentation outline and the user revision comment. '
        'Regenerate the outline with the specified number of slides and apply the comment. '
        'Return only a list of slide titles, one title per line, without numbering. Use English.\n'
        f'Topic: {topic}\n'
        f'Number of slides: {slides}\n'
        f'Current outline:\n{outline_text}\n'
        f'User comment: {comment}\n'
    )


def slides_prompt(topic: str, outline: list[str]) -> str:
    return (
        'Generate a JSON array of slides. Each item: '
        '{"title": str, "text": str, "image_prompt": str}. '
        'Text must be brief (2-3 sentences), no longer than 320 characters. '
        'Title 4-7 words. '
        'Return only JSON. Use English.\n'
        f'Topic: {topic}\n'
        f'Outline: {outline}\n'
    )
