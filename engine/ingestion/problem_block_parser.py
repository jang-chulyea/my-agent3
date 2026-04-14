import re


def split_problem_blocks(raw_text: str) -> list[str]:
    """Split extracted exam text into coarse per-problem text blocks."""

    text = raw_text.strip()
    if not text:
        return []

    blocks = [
        block.strip()
        for block in re.split(r"(?m)^\s*(?:Problem\s+|Question\s+|Q\.?\s*)?\d+[\.\)]\s+", text)
        if block.strip()
    ]
    return blocks if blocks else [text]
