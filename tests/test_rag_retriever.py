import json

from core import rag_retriever


def test_retrieve_context_loads_sample_json_files(monkeypatch, tmp_path) -> None:
    exams_dir = tmp_path / "data" / "exams" / "json"
    core_problems_dir = tmp_path / "data" / "core_problems"
    subjects_dir = tmp_path / "data" / "subjects"

    exams_dir.mkdir(parents=True)
    core_problems_dir.mkdir(parents=True)
    subjects_dir.mkdir(parents=True)

    (exams_dir / "area_exam.json").write_text(
        json.dumps(
            {
                "id": "exam-001",
                "subject": "basic_math",
                "topic": "area",
                "question": "Find the area of a rectangle.",
                "concepts": ["rectangle", "area"],
            }
        ),
        encoding="utf-8",
    )
    (core_problems_dir / "pressure_problem.json").write_text(
        json.dumps(
            {
                "id": "problem-001",
                "subject": "hvac",
                "topic": "pressure",
                "question": "Calculate pressure from force and area.",
                "concepts": ["pressure", "force", "area"],
            }
        ),
        encoding="utf-8",
    )
    (subjects_dir / "math_subject.json").write_text(
        json.dumps(
            {
                "subject_id": "basic_math",
                "topic": "number",
                "description": "Basic number operations.",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        rag_retriever,
        "SEARCH_ROOTS",
        [exams_dir, core_problems_dir, subjects_dir],
    )

    result = rag_retriever.retrieve_context(
        query="rectangle area",
        subject="basic_math",
        topic="area",
        concepts=["rectangle"],
    )

    print(result["matches"])

    assert result["query"] == "rectangle area"
    assert result["matches"]
    assert len(result["matches"]) <= 5
    assert result["matches"][0]["data"]["id"] == "exam-001"
    assert result["matches"][0]["score"] > 0
