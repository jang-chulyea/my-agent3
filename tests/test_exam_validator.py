import copy

import pytest

from engine.validation.exam_validator import validate_exam_payload, validate_problem


def _problem(problem_no: int) -> dict:
    return {
        "problem_id": f"sample_{problem_no:03d}",
        "problem_no": problem_no,
        "module": "exam",
        "major_subject": "thermodynamics",
        "minor_subject": "closed_system_work",
        "topic": "constant_pressure_boundary_work",
        "tags": ["thermodynamics", "boundary_work"],
        "question": "What is the boundary work?",
        "choices": ["450 kJ", "350 kJ", "250 kJ", "150 kJ"],
        "answer": "250 kJ",
        "explanation": "W = P(V2 - V1).",
        "visual_required": False,
        "review_status": "auto",
    }


def _payload(problems: list[dict]) -> dict:
    return {
        "exam_info": {
            "source_file": "sample.pdf",
            "ingestion_mode": "multimodal_llm",
        },
        "problems": problems,
    }


def test_exam_validator_accepts_valid_single_problem_payload() -> None:
    assert validate_exam_payload(_payload([_problem(1)])) is True


def test_exam_validator_accepts_valid_two_problem_payload() -> None:
    assert validate_exam_payload(_payload([_problem(1), _problem(2)])) is True


def test_exam_validator_rejects_missing_required_field() -> None:
    problem = _problem(1)
    del problem["question"]

    with pytest.raises(ValueError, match="Missing required problem field: question"):
        validate_problem(problem)


def test_exam_validator_rejects_invalid_field_type() -> None:
    problem = _problem(1)
    problem["tags"] = "thermodynamics"

    with pytest.raises(ValueError, match="problem.tags must be a list"):
        validate_problem(problem)


def test_exam_validator_rejects_non_sequential_problem_numbers() -> None:
    payload = _payload([_problem(1), _problem(3)])

    with pytest.raises(ValueError, match="problem_no values must be sequential"):
        validate_exam_payload(payload)


def test_exam_validator_rejects_duplicate_problem_numbers() -> None:
    first = _problem(1)
    second = copy.deepcopy(first)
    second["problem_id"] = "sample_duplicate"

    with pytest.raises(ValueError, match="Duplicate problem_no values"):
        validate_exam_payload(_payload([first, second]))


def test_exam_validator_accepts_visual_required_problem() -> None:
    problem = _problem(1)
    problem["visual_required"] = True
    problem["review_status"] = "manual_or_llm_review"

    assert validate_problem(problem) is True


def test_exam_validator_rejects_invalid_review_status() -> None:
    problem = _problem(1)
    problem["review_status"] = "needs_review"

    with pytest.raises(ValueError, match="problem.review_status must be one of"):
        validate_problem(problem)


def test_exam_validator_rejects_invalid_ingestion_mode() -> None:
    payload = _payload([_problem(1)])
    payload["exam_info"]["ingestion_mode"] = "ocr_pipeline"

    with pytest.raises(ValueError, match="payload.exam_info.ingestion_mode must be one of"):
        validate_exam_payload(payload)
