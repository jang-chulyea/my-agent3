from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data" / "analytics" / "topic_frequency.json"


def load_exam_payload(input_path: Path) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError("Exam JSON must be a JSON object")

    return payload


def resolve_input_files(input_path: Path) -> List[Path]:
    if input_path.is_file():
        return [input_path]

    if input_path.is_dir():
        return [p for p in input_path.glob("*.json") if p.is_file()]

    raise ValueError(f"Invalid input path: {input_path}")


def calculate_topic_frequency(input_path: Path) -> dict[str, Any]:
    counter: Counter[str] = Counter()
    processed_files = 0
    processed_problems = 0
    skipped_problems = 0

    input_files = resolve_input_files(input_path)

    for json_file in input_files:
        payload = load_exam_payload(json_file)
        problems = payload.get("problems", [])

        if not isinstance(problems, list):
            raise ValueError(f"'problems' must be a list in {json_file}")

        processed_files += 1

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
        {"topic": topic, "frequency": freq}
        for topic, freq in sorted(counter.items(), key=lambda x: (-x[1], x[0]))
    ]

    summary = {
        "processed_files": processed_files,
        "processed_problems": processed_problems,
        "skipped_problems": skipped_problems,
        "counted_topics": sum(counter.values()),
        "unique_topics": len(counter),
    }
    
    if input_path.is_file():
        summary["input_file"] = str(input_path)
    else:
        summary["input_path"] = str(input_path)

    return {
        "summary": summary,
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    analytics = calculate_topic_frequency(input_path)
    save_topic_frequency(output_path, analytics)

    print(f"Saved topic frequency analytics to: {output_path}")


if __name__ == "__main__":
    main()