"""Calculate topic frequency analytics from a single exam JSON file."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "exams"
    / "ac_refrigeration_engineer"
    / "2024_1"
    / "exam_2024_1.json"
)
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data" / "analytics" / "topic_frequency.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count problem topics from a single exam JSON file."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT_PATH),
        help="Input path for the exam JSON file.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Output path for the topic frequency JSON file.",
    )
    return parser.parse_args()


def load_exam_payload(input_path: Path) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError("Exam JSON must be a JSON object")

    return payload


def calculate_topic_frequency(input_path: Path) -> dict[str, Any]:
    payload = load_exam_payload(input_path)
    problems = payload.get("problems", [])
    if not isinstance(problems, list):
        raise ValueError("'problems' must be a list in the exam JSON")

    counter: Counter[str] = Counter()
    processed_problems = 0
    skipped_problems = 0

    for problem in problems:
        if not isinstance(problem, dict):
            skipped_problems += 1
            continue

        processed_problems += 1
        topic = problem.get("topic")
        if not isinstance(topic, str) or not topic.strip():
            skipped_problems += 1
            continue

        counter[topic.strip()] += 1

    topic_frequency = [
        {"topic": topic, "frequency": frequency}
        for topic, frequency in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]

    return {
        "summary": {
            "input_file": str(input_path),
            "processed_files": 1,
            "processed_problems": processed_problems,
            "skipped_problems": skipped_problems,
            "counted_topics": sum(counter.values()),
            "unique_topics": len(counter),
        },
        "topics": topic_frequency,
    }


def save_topic_frequency(output_path: Path, analytics: dict[str, Any]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(analytics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    args = parse_args()
    analytics = calculate_topic_frequency(Path(args.input))
    output_path = save_topic_frequency(Path(args.output), analytics)
    print(f"Saved topic frequency analytics to: {output_path}")


if __name__ == "__main__":
    main()
