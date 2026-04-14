import re


def normalize_problem_block(
    block: str,
    problem_no: int,
    module: str,
    major_subject: str = "",
    minor_subject: str = "",
    topic: str = "",
    tags: list[str] | None = None,
    problem_id_prefix: str = "problem",
) -> dict:
    """Normalize one parsed problem block into the project exam problem shape."""

    fields = _parse_labeled_fields(block)
    normalized_tags = _parse_tags(fields.get("tags")) or (tags or [])
    visual_required = _requires_visual_review(block)

    return {
        "problem_id": f"{problem_id_prefix}_{problem_no:03d}",
        "problem_no": problem_no,
        "module": fields.get("module", module),
        "major_subject": fields.get("major_subject", major_subject),
        "minor_subject": fields.get("minor_subject", minor_subject),
        "topic": fields.get("topic", topic),
        "tags": normalized_tags,
        "question": fields.get("question") or _first_nonempty_line(block),
        "choices": _parse_choices(block),
        "answer": fields.get("answer", ""),
        "explanation": fields.get("explanation", ""),
        "visual_required": visual_required,
        "review_status": "manual_or_llm_review" if visual_required else "auto",
    }


def _parse_labeled_fields(block: str) -> dict[str, str]:
    fields = {}
    aliases = {
        "module": "module",
        "major_subject": "major_subject",
        "minor_subject": "minor_subject",
        "topic": "topic",
        "tags": "tags",
        "question": "question",
        "q": "question",
        "answer": "answer",
        "a": "answer",
        "explanation": "explanation",
    }

    for line in block.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        normalized_key = key.strip().casefold()
        if normalized_key in aliases:
            fields[aliases[normalized_key]] = value.strip()

    return fields


def _parse_tags(value: str | None) -> list[str]:
    if not value:
        return []
    return [tag.strip() for tag in value.split(",") if tag.strip()]


def _parse_choices(block: str) -> list[str]:
    choices = []
    for line in block.splitlines():
        match = re.match(r"^\s*([A-Da-d])[\.\)]\s+(.+)$", line)
        if match:
            choices.append(match.group(2).strip())
    return choices


def _first_nonempty_line(block: str) -> str:
    for line in block.splitlines():
        if line.strip():
            return line.strip()
    return ""


def _requires_visual_review(block: str) -> bool:
    visual_markers = [
        "table",
        "figure",
        "diagram",
        "chart",
        "graph",
        "표",
        "그림",
        "도표",
        "그래프",
    ]
    normalized_block = block.casefold()
    return any(marker in normalized_block for marker in visual_markers)
