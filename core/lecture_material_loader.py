import json
import logging
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LECTURE_MATERIAL_ROOT = PROJECT_ROOT / "data/lecture_materials"


def get_lecture_by_subject_topic(subject: str, topic: str) -> list[dict[str, Any]]:
    if not LECTURE_MATERIAL_ROOT.exists():
        return []

    normalized_subject = _normalize(subject)
    normalized_topic = _normalize(topic)
    materials = []

    for path in sorted(LECTURE_MATERIAL_ROOT.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.warning("failed to parse lecture material JSON file %s: %s", path, exc)
            continue

        if _normalize(data.get("subject")) != normalized_subject:
            continue
        if _normalize(data.get("topic")) != normalized_topic:
            continue

        item = dict(data)
        item["source"] = str(path)
        materials.append(item)

    return materials


def _normalize(value: Any) -> str:
    return str(value or "").casefold().strip()
