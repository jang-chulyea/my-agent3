import pytest

from engine import load_learning_bundle
from engine.registry import SubjectNotFoundError


SUBJECT_ID = "subject_02_hvac"
TARGET_NODE_ID = "TD-01-PRESSURE"


def test_engine_entrypoint_loads_learning_bundle_from_subject_id() -> None:
    bundle = load_learning_bundle(SUBJECT_ID, TARGET_NODE_ID)

    assert bundle["subject"]["subject_id"] == "subject_02_hvac"
    assert bundle["target_node"]["node_id"] == TARGET_NODE_ID
    assert [node["node_id"] for node in bundle["prerequisite_nodes"]] == [
        "TD-00-FORCE",
        "TD-00-AREA",
    ]


def test_engine_entrypoint_raises_for_missing_target_node() -> None:
    with pytest.raises(ValueError, match="Target node not found"):
        load_learning_bundle(SUBJECT_ID, "TD-99-NOT-FOUND")


def test_engine_entrypoint_raises_for_unknown_subject_id() -> None:
    with pytest.raises(SubjectNotFoundError, match="subject_id not found in registry"):
        load_learning_bundle("subject_99_missing", TARGET_NODE_ID)
