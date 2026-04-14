import pytest

from engine import load_subject_root
from engine.registry import SubjectNotFoundError


def test_load_subject_root_resolves_registered_subject() -> None:
    subject_root = load_subject_root("subject_02_hvac")

    assert subject_root == "data/subject_02_hvac"


def test_load_subject_root_raises_for_unknown_subject() -> None:
    with pytest.raises(SubjectNotFoundError, match="subject_id not found in registry"):
        load_subject_root("subject_99_missing")
