"""Calculate topic importance analytics from topic frequency output.

Importance is currently defined as the same numeric value as frequency.
Labels are assigned using the Phase 1 rule:

- 10 or more: ``very_important``
- 5 to 9: ``important``
- 4 or less: ``normal``
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = PROJECT_ROOT / "data" / "analytics" / "topic_frequency.json"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data" / "analytics" / "topic_importance.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assign topic importance labels from topic frequency analytics."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT_PATH),
        help="Input path for topic frequency JSON.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Output path for topic importance JSON.",
    )
    return parser.parse_args()


def classify_importance(frequency: int) -> str:
    if frequency >= 10:
        return "very_important"
    if frequency >= 5:
        return "important"
    return "normal"


def calculate_topic_importance(frequency_payload: dict[str, Any]) -> dict[str, Any]:
    topics = frequency_payload.get("topics", [])
    if not isinstance(topics, list):
        raise ValueError("'topics' must be a list in topic frequency data")

    importance_topics: list[dict[str, Any]] = []
    for item in topics:
        if not isinstance(item, dict):
            continue

        topic = item.get("topic")
        frequency = item.get("frequency")
        if not isinstance(topic, str) or not topic.strip():
            continue
        if not isinstance(frequency, int):
            continue

        importance_topics.append(
            {
                "topic": topic,
                "frequency": frequency,
                "importance": frequency,
                "label": classify_importance(frequency),
            }
        )

    return {
        "summary": {
            "unique_topics": len(importance_topics),
        },
        "topics": importance_topics,
    }


def load_topic_frequency(input_path: Path) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError("Topic frequency data must be a JSON object")

    return payload


def save_topic_importance(output_path: Path, analytics: dict[str, Any]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(analytics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path


def main() -> None:
    args = parse_args()
    frequency_payload = load_topic_frequency(Path(args.input))
    analytics = calculate_topic_importance(frequency_payload)
    output_path = save_topic_importance(Path(args.output), analytics)
    print(f"Saved topic importance analytics to: {output_path}")


if __name__ == "__main__":
    main()
