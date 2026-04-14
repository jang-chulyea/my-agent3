"""Public engine entry points for application-facing usage.

This module keeps the app-facing import surface small while the internal engine
structure is still evolving.
"""

from engine.bundle_service import BundleService
from engine.entrypoint import get_node_ids, infer_subject_and_target, load_learning_bundle
from engine.registry import load_subject_root
from engine.subject_loader import SubjectLoaderService


def create_subject_loader(subject_root: str) -> SubjectLoaderService:
    """Return the engine loader service for a subject root."""
    return SubjectLoaderService(subject_root)


__all__ = [
    "BundleService",
    "SubjectLoaderService",
    "create_subject_loader",
    "get_node_ids",
    "infer_subject_and_target",
    "load_learning_bundle",
    "load_subject_root",
]
