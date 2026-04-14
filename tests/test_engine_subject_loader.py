import pytest

from engine.subject_loader import SubjectLoaderService


SUBJECT_ROOT = "data/subject_02_hvac"


@pytest.fixture
def loaded_service() -> SubjectLoaderService:
    service = SubjectLoaderService(SUBJECT_ROOT)
    service.load_subject()
    return service


def test_engine_subject_loader_loads_subject_state() -> None:
    service = SubjectLoaderService(SUBJECT_ROOT)

    service.load_subject()

    assert service.subject_meta["subject_id"] == "subject_02_hvac"
    assert "TD-01-PRESSURE" in service.nodes
    assert len(service.prerequisite_edges) == 2


def test_engine_subject_loader_get_node_returns_loaded_node(
    loaded_service: SubjectLoaderService,
) -> None:
    node = loaded_service.get_node("TD-01-PRESSURE")

    assert node is not None
    assert node["node_id"] == "TD-01-PRESSURE"


def test_engine_subject_loader_raises_for_missing_subject_json(tmp_path) -> None:
    service = SubjectLoaderService(str(tmp_path))

    with pytest.raises(FileNotFoundError, match="subject.json not found"):
        service.load_subject_meta()
