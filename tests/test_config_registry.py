import json
from pathlib import Path


REGISTRY_PATH = Path("config/subject_registry.json")


def test_subject_registry_matches_expected_mvp_contract() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    assert isinstance(registry["subjects"], list)
    assert registry["subjects"]

    subject_ids = set()
    subject_roots = set()

    for subject in registry["subjects"]:
        assert isinstance(subject["subject_id"], str)
        assert subject["subject_id"]

        assert isinstance(subject["display_name"], str)
        assert subject["display_name"]

        assert isinstance(subject["subject_root"], str)
        assert subject["subject_root"].startswith("data/")

        assert isinstance(subject["enabled"], bool)

        if "description" in subject:
            assert isinstance(subject["description"], str)

        assert subject["subject_id"] not in subject_ids
        subject_ids.add(subject["subject_id"])

        assert subject["subject_root"] not in subject_roots
        subject_roots.add(subject["subject_root"])


def test_registered_subject_roots_exist_on_disk() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    for subject in registry["subjects"]:
        subject_root = Path(subject["subject_root"])
        assert subject_root.exists()
        assert subject_root.is_dir()
