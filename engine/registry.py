import json
from pathlib import Path
from typing import Any, Dict, List


REGISTRY_PATH = Path("config/subject_registry.json")


class SubjectRegistryError(ValueError):
    """Raised when subject registry data is invalid or incomplete."""


class SubjectNotFoundError(LookupError):
    """Raised when the requested subject_id is not present in the registry."""


def load_subject_registry(registry_path: Path | str = REGISTRY_PATH) -> List[Dict[str, Any]]:
    """Load and validate subject registry entries from config."""

    path = Path(registry_path)
    with path.open("r", encoding="utf-8") as file:
        registry = json.load(file)

    subjects = registry.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        raise SubjectRegistryError("subject registry must contain a non-empty 'subjects' list")

    return subjects


def load_subject_root(subject_id: str, registry_path: Path | str = REGISTRY_PATH) -> str:
    """Resolve a subject_id into a subject_root using the registry only."""

    subjects = load_subject_registry(registry_path)

    for subject in subjects:
        if subject.get("subject_id") == subject_id:
            subject_root = subject.get("subject_root")
            if not isinstance(subject_root, str) or not subject_root:
                raise SubjectRegistryError(
                    f"subject_root is missing or invalid for subject_id: {subject_id}"
                )
            return subject_root

    raise SubjectNotFoundError(f"subject_id not found in registry: {subject_id}")


def load_subject_ids(registry_path: Path | str = REGISTRY_PATH) -> List[str]:
    """Return registered subject IDs from the registry."""

    subjects = load_subject_registry(registry_path)
    return [subject["subject_id"] for subject in subjects if isinstance(subject.get("subject_id"), str)]
