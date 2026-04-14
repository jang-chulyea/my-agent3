import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

import ollama
from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.input.pdf_loader import extract_text_from_pdf
from schemas.exam_schema import ExamSchema
from utils.json_extractor import extract_json


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "Return ONLY valid JSON. No explanation."
OUTPUT_DIR = PROJECT_ROOT / "data/exams/json"


def extract_text(file_path: str) -> str:
    return extract_text_from_pdf(file_path)


def split_questions(text: str) -> list[str]:
    chunks = [
        chunk.strip()
        for chunk in re.split(r"(?m)^\s*(?:Question\s+)?\d+[\.\)]\s+", text)
        if chunk.strip()
    ]
    return chunks if chunks else [text.strip()]


def call_llm_structurer(question_text: str, error_message: str | None = None) -> dict[str, Any]:
    prompt = (
        "Structure the following exam question as JSON matching this schema:\n"
        "{\n"
        '  "id": "string",\n'
        '  "subject": "string",\n'
        '  "topic": "string",\n'
        '  "question": "string",\n'
        '  "question_type": "calculation | concept | judgement",\n'
        '  "given": {},\n'
        '  "asked": "string",\n'
        '  "concepts": ["string"]\n'
        "}\n\n"
        f"Question text:\n{question_text}"
    )

    if error_message:
        prompt += f"\n\nPrevious validation error:\n{error_message}\nReturn corrected JSON only."

    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return extract_json(response["message"]["content"])


def validate_and_save(payload: dict[str, Any], output_dir: Path = OUTPUT_DIR) -> dict[str, Any]:
    exam = ExamSchema.model_validate(payload)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{_safe_filename(exam.id)}.json"
    output_path.write_text(
        json.dumps(exam.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return exam.model_dump()


def process_pdf(file_path: str) -> list[dict[str, Any]]:
    text = extract_text(file_path)
    questions = split_questions(text)
    saved_exams = []

    for index, question_text in enumerate(questions, start=1):
        try:
            payload = call_llm_structurer(question_text)
            saved_exams.append(validate_and_save(payload))
        except ValidationError as exc:
            logger.warning("validation failed for question %s: %s", index, exc)
            payload = call_llm_structurer(question_text, str(exc))
            saved_exams.append(validate_and_save(payload))

    return saved_exams


def _safe_filename(value: str) -> str:
    filename = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return filename or "exam"


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert PDF exam questions to JSON.")
    parser.add_argument("file_path", help="Path to the input PDF file.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    saved_exams = process_pdf(args.file_path)
    print(json.dumps(saved_exams, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
