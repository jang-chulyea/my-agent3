from core.lecture_material_loader import get_lecture_by_subject_topic
from core.rag_retriever import retrieve_context


def test_retrieve_context_excludes_lecture_materials() -> None:
    result = retrieve_context(
        query="constant volume temperature pressure",
        subject="physics",
        topic="gas_pressure",
        concepts=["temperature", "pressure", "constant_volume"],
    )

    lecture_matches = [
        match
        for match in result["matches"]
        if match.get("source_type") == "lecture_material"
    ]

    print(lecture_matches)

    assert lecture_matches == []


def test_get_lecture_by_subject_topic_loads_matching_material() -> None:
    materials = get_lecture_by_subject_topic("physics", "gas_pressure")

    assert materials
    assert materials[0]["id"] == "sample_lecture_material_001"
    assert materials[0]["subject"] == "physics"
    assert materials[0]["topic"] == "gas_pressure"
    assert "source" in materials[0]
