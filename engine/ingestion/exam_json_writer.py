import json
from pathlib import Path

from engine.validation.exam_validator import validate_problem


def write_exam_json(
    problems: list[dict],
    output_path: str,
    exam_info: dict | None = None,
) -> dict:
    """Validate normalized problems and write the final exam JSON file."""

    for problem in problems:
        validate_problem(problem)

    payload = {
        "exam_info": exam_info or {},
        "problems": problems,
    }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload
