import json
import logging
import re
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEARCH_ROOTS = [
    PROJECT_ROOT / "data/exams/json",
    PROJECT_ROOT / "data/core_problems",
    PROJECT_ROOT / "data/subjects",
]


def load_json_files(search_roots: list[Path] | None = None) -> list[dict[str, Any]]:
    roots = search_roots or SEARCH_ROOTS
    items = []

    for root in roots:
        if not root.exists():
            continue

        for path in sorted(root.rglob("*.json")):
            if _is_lecture_material_path(path):
                continue

            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                logger.warning("failed to parse JSON file %s: %s", path, exc)
                continue

            items.append(
                {
                    "source": str(path),
                    "source_type": _source_type(path),
                    "data": data,
                }
            )

    return items


def filter_items(
    items: list[dict[str, Any]],
    subject: str | None = None,
    topic: str | None = None,
) -> list[dict[str, Any]]:
    filtered_items = items

    if subject:
        filtered_items = [
            item for item in filtered_items if _field_matches(item["data"], "subject", subject)
        ]

    if topic:
        filtered_items = [
            item for item in filtered_items if _field_matches(item["data"], "topic", topic)
        ]

    return filtered_items


def score_item(
    item: dict[str, Any],
    query: str,
    subject: str | None = None,
    topic: str | None = None,
    concepts: list[str] | None = None,
) -> float:
    data = item["data"]
    score = 0.0
    reasons = []

    if subject and _field_matches(data, "subject", subject):
        score += 3.0
        reasons.append("subject +3")

    if topic and _field_matches(data, "topic", topic):
        score += 2.0
        reasons.append("topic +2")

    item_concept_tokens = set(_concept_tokens(data))
    if concepts:
        for concept in concepts:
            concept_tokens = _tokens(str(concept))
            if concept_tokens and set(concept_tokens).issubset(item_concept_tokens):
                score += 2.0
                reasons.append(f"concept:{concept} +2")

    text_tokens = set(_question_text_tokens(data))
    for keyword in _keywords(query):
        if keyword in text_tokens:
            score += 1.0
            reasons.append(f"keyword:{keyword} +1")

    reason_text = ", ".join(reasons) if reasons else "no match"
    logger.debug("RAG score source=%s score=%s reasons=%s", item.get("source", ""), score, reason_text)
    print(f"RAG score source={item.get('source', '')} score={score} reasons={reason_text}")
    return score


def top_k(items: list[dict[str, Any]], k: int = 5) -> list[dict[str, Any]]:
    ranked_items = sorted(items, key=lambda item: item["score"], reverse=True)
    return ranked_items[:k]


def retrieve_context(
    query: str,
    subject: str | None = None,
    topic: str | None = None,
    concepts: list[str] | None = None,
) -> dict[str, Any]:
    items = load_json_files()
    filtered_items = filter_items(items, subject=subject, topic=topic)

    scored_items = []
    for item in filtered_items:
        score = score_item(
            item,
            query=query,
            subject=subject,
            topic=topic,
            concepts=concepts,
        )
        if score < 2:
            continue

        scored_items.append(
            {
                "source": item["source"],
                "source_type": item.get("source_type", "unknown"),
                "score": score,
                "data": item["data"],
            }
        )

    return {
        "query": query,
        "matches": top_k(scored_items, k=5),
    }


def _field_matches(data: Any, field_name: str, expected_value: str) -> bool:
    normalized_expected = _normalize(expected_value)

    for key, value in _walk_key_values(data):
        normalized_key = _normalize(key)
        if normalized_key not in {field_name, f"{field_name}_id"}:
            continue

        if normalized_expected == _normalize(str(value)):
            return True

    return False


def _walk_key_values(data: Any) -> list[tuple[str, Any]]:
    values = []

    if isinstance(data, dict):
        for key, value in data.items():
            values.append((str(key), value))
            values.extend(_walk_key_values(value))
    elif isinstance(data, list):
        for item in data:
            values.extend(_walk_key_values(item))

    return values


def _to_searchable_text(data: Any) -> str:
    if isinstance(data, dict):
        return " ".join(_to_searchable_text(value) for value in data.values())
    if isinstance(data, list):
        return " ".join(_to_searchable_text(item) for item in data)
    return _normalize_text(str(data))


def _keywords(text: str) -> list[str]:
    return _tokens(text)


def _normalize(value: str) -> str:
    return _normalize_text(value).strip()


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold())


def _tokens(value: str) -> list[str]:
    return [token for token in _normalize_text(value).split() if token]


def _concept_tokens(data: Any) -> list[str]:
    tokens = []
    for key, value in _walk_key_values(data):
        if _normalize(key) != "concepts":
            continue

        if isinstance(value, list):
            for item in value:
                tokens.extend(_tokens(str(item)))
        else:
            tokens.extend(_tokens(str(value)))

    return tokens


def _question_text_tokens(data: Any) -> list[str]:
    tokens = []
    for key, value in _walk_key_values(data):
        normalized_key = _normalize(key)
        searchable_keys = {
            "question",
            "concept_text",
        }
        if normalized_key not in searchable_keys and "text" not in normalized_key:
            continue

        tokens.extend(_tokens(str(value)))

    return tokens


def _source_type(path: Path) -> str:
    normalized_path = str(path).replace("\\", "/")
    if "/data/exams/json/" in normalized_path:
        return "exam"
    if "/data/core_problems/" in normalized_path:
        return "core_problem"
    if "/data/subjects/" in normalized_path:
        return "subject"
    return "unknown"


def _is_lecture_material_path(path: Path) -> bool:
    return "/data/lecture_materials/" in str(path).replace("\\", "/")
