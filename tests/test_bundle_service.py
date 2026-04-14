import pytest

from engine.bundle_service import BundleService
from engine.subject_loader import SubjectLoaderService


SUBJECT_ROOT = "data/subject_02_hvac"
TARGET_NODE_ID = "TD-01-PRESSURE"


@pytest.fixture
def bundle_service() -> BundleService:
    loader = SubjectLoaderService(SUBJECT_ROOT)
    loader.load_subject()
    return BundleService(loader)


def test_bundle_service_returns_prerequisite_node_ids_in_order(
    bundle_service: BundleService,
) -> None:
    prerequisite_ids = bundle_service.get_prerequisite_node_ids(TARGET_NODE_ID)

    assert prerequisite_ids == ["TD-00-FORCE", "TD-00-AREA"]


def test_bundle_service_returns_prerequisite_nodes(
    bundle_service: BundleService,
) -> None:
    prerequisite_nodes = bundle_service.get_prerequisite_nodes(TARGET_NODE_ID)

    assert [node["node_id"] for node in prerequisite_nodes] == [
        "TD-00-FORCE",
        "TD-00-AREA",
    ]


def test_bundle_service_builds_learning_bundle(bundle_service: BundleService) -> None:
    bundle = bundle_service.get_learning_bundle(TARGET_NODE_ID)

    assert bundle["subject"]["subject_id"] == "subject_02_hvac"
    assert bundle["target_node"]["node_id"] == TARGET_NODE_ID
    assert [node["node_id"] for node in bundle["prerequisite_nodes"]] == [
        "TD-00-FORCE",
        "TD-00-AREA",
    ]


def test_bundle_service_raises_for_missing_target_node(
    bundle_service: BundleService,
) -> None:
    with pytest.raises(ValueError, match="Target node not found"):
        bundle_service.get_learning_bundle("TD-99-NOT-FOUND")
