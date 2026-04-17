REVIEW_STATUS_VALUES = {
    "auto",
    "manual_reviewed",
    "manual_or_llm_review",
    "low_confidence",
    "fallback_generated",
}

INGESTION_MODE_VALUES = {
    "multimodal_llm",
    "selectable_text_fallback",
    "manual_text_assumption",
    "manual_input",
}

REQUIRED_PROBLEM_FIELDS = {
    "problem_id": str,
    "problem_no": int,
    "module": str,
    "major_subject": str,
    "minor_subject": str,
    "topic": str,
    "tags": list,
    "question": str,
    "choices": list,
    "answer": str,
    "explanation": str,
    "visual_required": bool,
    "review_status": str,
}

OPTIONAL_PROBLEM_FIELDS = {
    "answer_choice": int,
    "source_page": int,
    "ingestion_mode": str,
}


def validate_problem(p):
    """Validate one normalized exam problem object."""

    if not isinstance(p, dict):
        raise ValueError("Problem must be a dict.")

    for field, expected_type in REQUIRED_PROBLEM_FIELDS.items():
        if field not in p:
            raise ValueError(f"Missing required problem field: {field}")
        _validate_type(p[field], expected_type, f"problem.{field}")

    for field, expected_type in OPTIONAL_PROBLEM_FIELDS.items():
        if field in p and p[field] is not None:
            _validate_type(p[field], expected_type, f"problem.{field}")

    _validate_string_list(p["tags"], "problem.tags")
    _validate_string_list(p["choices"], "problem.choices")
    _validate_review_status(p["review_status"], "problem.review_status")

    if "ingestion_mode" in p and p["ingestion_mode"] is not None:
        _validate_ingestion_mode(p["ingestion_mode"], "problem.ingestion_mode")

    return True


def validate_exam_payload(payload):
    """Validate a full exam JSON payload."""

    if not isinstance(payload, dict):
        raise ValueError("Exam payload must be a dict.")

    if "exam_info" not in payload:
        raise ValueError("Missing required payload field: exam_info")
    if not isinstance(payload["exam_info"], dict):
        raise ValueError("payload.exam_info must be a dict.")

    ingestion_mode = payload["exam_info"].get("ingestion_mode")
    if ingestion_mode is not None:
        _validate_ingestion_mode(ingestion_mode, "payload.exam_info.ingestion_mode")

    if "problems" not in payload:
        raise ValueError("Missing required payload field: problems")
    if not isinstance(payload["problems"], list):
        raise ValueError("payload.problems must be a list.")

    for problem in payload["problems"]:
        validate_problem(problem)

    _validate_problem_sequence(payload["problems"])

    return True


def _validate_problem_sequence(problems):
    problem_numbers = [problem["problem_no"] for problem in problems]
    duplicates = sorted(
        problem_no
        for problem_no in set(problem_numbers)
        if problem_numbers.count(problem_no) > 1
    )
    if duplicates:
        raise ValueError(f"Duplicate problem_no values: {duplicates}")

    expected = list(range(1, len(problem_numbers) + 1))
    if problem_numbers != expected:
        raise ValueError(
            f"problem_no values must be sequential from 1. "
            f"Expected {expected}, got {problem_numbers}"
        )


def _validate_type(value, expected_type, field_path):
    if expected_type is int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{field_path} must be an int.")
        return

    if expected_type is bool:
        if not isinstance(value, bool):
            raise ValueError(f"{field_path} must be a bool.")
        return

    if not isinstance(value, expected_type):
        type_name = expected_type.__name__
        raise ValueError(f"{field_path} must be a {type_name}.")


def _validate_string_list(value, field_path):
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_path} must contain only strings.")


def _validate_review_status(value, field_path):
    if value not in REVIEW_STATUS_VALUES:
        allowed = ", ".join(sorted(REVIEW_STATUS_VALUES))
        raise ValueError(f"{field_path} must be one of: {allowed}")


def _validate_ingestion_mode(value, field_path):
    if value not in INGESTION_MODE_VALUES:
        allowed = ", ".join(sorted(INGESTION_MODE_VALUES))
        raise ValueError(f"{field_path} must be one of: {allowed}")
