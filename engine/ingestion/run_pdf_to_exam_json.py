# PDF/Image-to-exam JSON ingestion scaffold.
#
# Primary path: structure the input with a multimodal LLM.
# Fallback path: extract selectable text, split problem blocks, and normalize.
# Final stages: validate required fields and write the final exam JSON payload.

import argparse

from engine.ingestion.exam_json_writer import write_exam_json
from engine.ingestion.multimodal_exam_structurer import extract_problems_from_file
from engine.ingestion.pdf_text_extractor import extract_text
from engine.ingestion.problem_block_parser import split_problem_blocks
from engine.ingestion.problem_normalizer import normalize_problem_block


def run_pipeline(
    input_path: str,
    output_path: str,
    module: str,
    exam_name: str = "",
    subject: str = "",
    round: str = "",
) -> dict:
    """Run multimodal ingestion first, then fallback to selectable text."""

    ingestion_mode = "multimodal_llm"
    multimodal_error = None
    try:
        problems = extract_problems_from_file(input_path, module)
        _validate_minimum_problem_quality(problems)
    except Exception as exc:
        multimodal_error = f"{type(exc).__name__}: {exc}"
        print(f"[run_pipeline] multimodal failed; falling back: {multimodal_error}")
        problems = _extract_problems_with_text_fallback(input_path, module)
        ingestion_mode = "selectable_text_fallback"

    _validate_minimum_problem_quality(problems)
    problems = _normalize_exam_problem_sequence(problems)

    exam_info = {
        "exam_name": exam_name,
        "subject": subject,
        "round": round,
        "source_file": input_path,
        "ingestion_mode": ingestion_mode,
    }
    if multimodal_error:
        exam_info["multimodal_error"] = multimodal_error
        exam_info["fallback_reason"] = "multimodal_exception"

    return write_exam_json(
        problems,
        output_path,
        exam_info=exam_info,
    )


def _extract_problems_with_text_fallback(input_path: str, module: str) -> list[dict]:
    raw_text = extract_text(input_path)
    blocks = split_problem_blocks(raw_text)
    return [
        normalize_problem_block(block, index, module)
        for index, block in enumerate(blocks, start=1)
    ]


def _validate_minimum_problem_quality(problems: list[dict]) -> None:
    if not problems:
        raise ValueError("No problems were detected. Refusing to write an empty exam JSON.")

    for problem in problems:
        if not problem.get("problem_no"):
            raise ValueError("Structured problem is missing problem_no.")


def _normalize_exam_problem_sequence(problems: list[dict]) -> list[dict]:
    normalized = []
    for index, problem in enumerate(problems, start=1):
        normalized_problem = dict(problem)
        normalized_problem["problem_no"] = index
        normalized_problem["problem_id"] = f"problem_{index:03d}"
        normalized_problem.setdefault("module", "exam")
        normalized_problem.setdefault("major_subject", "")
        normalized_problem.setdefault("minor_subject", "")
        normalized_problem.setdefault("topic", "")
        normalized_problem.setdefault("tags", [])
        normalized_problem.setdefault("question", "")
        normalized_problem.setdefault("choices", [])
        normalized_problem.setdefault("answer", "")
        normalized_problem.setdefault("explanation", "")
        normalized_problem.setdefault("visual_required", False)
        normalized_problem.setdefault(
            "ingestion_status",
            "visual_required" if normalized_problem["visual_required"] else "structured",
        )
        normalized_problem.setdefault("solve_status", "not_started")
        normalized.append(normalized_problem)
    return normalized


def main() -> None:
    """CLI entrypoint for PDF-to-exam JSON ingestion."""

    parser = argparse.ArgumentParser(description="Convert a selectable-text PDF into exam JSON.")
    parser.add_argument("--input", required=True, help="Input PDF path.")
    parser.add_argument("--output", required=True, help="Output JSON path.")
    parser.add_argument("--module", required=True, help="Problem module value, e.g. exam or core.")
    parser.add_argument("--exam-name", default="", help="Exam name metadata.")
    parser.add_argument("--subject", default="", help="Subject metadata.")
    parser.add_argument("--round", default="", help="Round metadata.")
    args = parser.parse_args()

    run_pipeline(
        args.input,
        args.output,
        args.module,
        exam_name=args.exam_name,
        subject=args.subject,
        round=args.round,
    )


if __name__ == "__main__":
    main()
