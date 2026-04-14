import json
from pathlib import Path


SUBJECT_ROOT = Path("data/subject_02_hvac")


def test_subject_json_is_readable_and_has_required_fields() -> None:
    subject_data = json.loads((SUBJECT_ROOT / "subject.json").read_text(encoding="utf-8"))

    assert subject_data["subject_id"] == "subject_02_hvac"
    assert subject_data["node_folder"] == "nodes"
    assert subject_data["relation_folder"] == "relations"
    assert "TD-01-PRESSURE" in subject_data["entry_nodes"]


def test_nodes_and_relations_files_are_readable_and_connected() -> None:
    nodes_dir = SUBJECT_ROOT / "nodes"
    relations_file = SUBJECT_ROOT / "relations" / "prerequisite_edges.json"

    node_files = sorted(nodes_dir.glob("*.json"))
    assert node_files, "Expected at least one node file"

    nodes = [json.loads(path.read_text(encoding="utf-8")) for path in node_files]
    node_ids = {node["node_id"] for node in nodes}

    assert "TD-01-PRESSURE" in node_ids

    relations = json.loads(relations_file.read_text(encoding="utf-8"))
    assert relations, "Expected at least one prerequisite edge"

    pressure_edges = [
        edge
        for edge in relations
        if edge["target_node_id"] == "TD-01-PRESSURE" and edge["relation"] == "prerequisite"
    ]

    assert len(pressure_edges) == 2
    assert {edge["source_node_id"] for edge in pressure_edges} == {"TD-00-FORCE", "TD-00-AREA"}
    assert all(edge["source_node_id"] in node_ids for edge in relations)
    assert all(edge["target_node_id"] in node_ids for edge in relations)
