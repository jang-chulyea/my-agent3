import pytest

from tools.simple_subject_loader import SubjectLoader


SUBJECT_ROOT = "data/subject_02_hvac"
TARGET_NODE_ID = "TD-01-PRESSURE"


@pytest.fixture
def loaded_subject() -> SubjectLoader:
    loader = SubjectLoader(SUBJECT_ROOT)
    loader.load_subject()
    return loader


def test_load_subject_populates_meta_nodes_and_relations(loaded_subject: SubjectLoader) -> None:
    assert loaded_subject.subject_meta["subject_id"] == "subject_02_hvac"
    assert loaded_subject.subject_meta["node_folder"] == "nodes"
    assert loaded_subject.subject_meta["relation_folder"] == "relations"

    assert "TD-01-PRESSURE" in loaded_subject.nodes
    assert "TD-00-FORCE" in loaded_subject.nodes
    assert "TD-00-AREA" in loaded_subject.nodes

    assert len(loaded_subject.prerequisite_edges) == 2
    assert all(edge["relation"] == "prerequisite" for edge in loaded_subject.prerequisite_edges)


def test_get_learning_bundle_for_pressure_returns_expected_bundle(
    loaded_subject: SubjectLoader,
) -> None:
    bundle = loaded_subject.get_learning_bundle(TARGET_NODE_ID)

    assert bundle["subject"]["subject_id"] == "subject_02_hvac"
    assert bundle["target_node"]["node_id"] == TARGET_NODE_ID

    prerequisite_ids = [node["node_id"] for node in bundle["prerequisite_nodes"]]
    assert prerequisite_ids == ["TD-00-FORCE", "TD-00-AREA"]


def test_get_learning_bundle_raises_for_missing_target_node(
    loaded_subject: SubjectLoader,
) -> None:
    with pytest.raises(ValueError, match="Target node not found"):
        loaded_subject.get_learning_bundle("TD-99-NOT-FOUND")
