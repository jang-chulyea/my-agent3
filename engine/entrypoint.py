from typing import Any, Dict

from engine.bundle_service import BundleService
from engine.registry import load_subject_root
from engine.subject_loader import SubjectLoaderService


def infer_subject_and_target(problem_input: str) -> tuple[str, str] | None:
    text = problem_input.lower()

    rules = [
        (("압력", "pressure"), ("subject_02_hvac", "TD-01-PRESSURE")),
        (("힘", "force"), ("subject_02_hvac", "TD-00-FORCE")),
        (("면적", "area"), ("subject_02_hvac", "TD-00-AREA")),
        (("number", "math", "수"), ("subject_03_basic_math", "BM-01-NUMBER")),
    ]

    for keywords, result in rules:
        if any(keyword in text for keyword in keywords):
            return result

    return None


def get_node_ids(subject_id: str) -> list[str]:
    subject_root = load_subject_root(subject_id)
    loader = SubjectLoaderService(subject_root)
    loader.load_subject()
    return loader.get_node_ids()


def load_learning_bundle(subject_id: str, target_node_id: str) -> Dict[str, Any]:
    """Load a subject and return a learning bundle for the target node.

    This is the intended single engine entry point for app-level callers that do
    not need to know about internal service composition.
    """

    subject_root = load_subject_root(subject_id)
    loader = SubjectLoaderService(subject_root)
    loader.load_subject()

    bundle_service = BundleService(loader)
    return bundle_service.build_learning_bundle(target_node_id)
