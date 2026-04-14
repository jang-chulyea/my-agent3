from engine import load_learning_bundle, load_subject_root


def test_registry_resolves_different_subject_ids_to_different_roots() -> None:
    hvac_root = load_subject_root("subject_02_hvac")
    math_root = load_subject_root("subject_03_basic_math")

    assert hvac_root == "data/subject_02_hvac"
    assert math_root == "data/subject_03_basic_math"
    assert hvac_root != math_root


def test_engine_entrypoint_builds_bundle_for_second_subject() -> None:
    bundle = load_learning_bundle("subject_03_basic_math", "BM-01-NUMBER")

    assert bundle["subject"]["subject_id"] == "subject_03_basic_math"
    assert bundle["target_node"]["node_id"] == "BM-01-NUMBER"
    assert bundle["prerequisite_nodes"] == []
