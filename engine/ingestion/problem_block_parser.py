import re


PROBLEM_START_PATTERN = re.compile(
    r"(?m)^\s*(?:(?:(?:Problem|Question|Q\.?|문제|문항)\s*)?\d{1,3}[\.\)]\s+|0\d{1,2}\s+|(?:Problem|Question|Q\.?|문제|문항)\s*\d{1,3}(?:[\.\)]\s*|\s+))"
)


def split_problem_blocks(raw_text: str) -> list[str]:
    """Split extracted exam text into coarse per-problem text blocks."""

    text = raw_text.strip()
    if not text:
        return []

    blocks = [
        block.strip()
        for block in PROBLEM_START_PATTERN.split(text)
        if block.strip()
    ]
    return blocks if blocks else [text]
