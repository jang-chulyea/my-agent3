import json
from pathlib import Path

from engine.ingestion import multimodal_exam_structurer, run_pdf_to_exam_json
from engine.loader.exam_indexer import (
    get_problems_by_subject,
    get_problems_by_tag,
    group_by_minor_subject,
    list_minor_subjects,
)
from engine.loader.exam_loader import load_exam
from engine.validation.exam_validator import validate_exam_payload


def test_fake_multimodal_llm_output_runs_full_exam_pipeline(monkeypatch) -> None:
    def fake_llm(_input_path: str, _prompt: str) -> dict:
        return {
            "problems": [
                {
                    "problem_no": 1,
                    "module": "exam",
                    "major_subject": "thermodynamics",
                    "minor_subject": "closed_system_work",
                    "topic": "constant_pressure_boundary_work",
                    "tags": ["thermodynamics", "boundary_work"],
                    "question": "A gas expands at constant pressure. Find the boundary work.",
                    "choices": ["150 kJ", "250 kJ", "350 kJ", "450 kJ"],
                    "answer": "250 kJ",
                    "explanation": "Boundary work is W = P(V2 - V1).",
                    "visual_required": False,
                    "review_status": "auto",
                },
                {
                    "problem_no": 2,
                    "module": "exam",
                    "major_subject": "thermodynamics",
                    "minor_subject": "p_v_diagram_work",
                    "topic": "pressure_volume_work",
                    "tags": ["thermodynamics", "p_v_diagram", "boundary_work"],
                    "question": "Use the P-V diagram to find the expansion work.",
                    "choices": ["30 kJ", "200 kJ", "3000 kJ", "6000 kJ"],
                    "answer": "6000 kJ",
                    "explanation": "The graph area gives the pressure-volume work.",
                    "visual_required": True,
                    "review_status": "manual_or_llm_review",
                },
            ]
        }

    monkeypatch.setattr(multimodal_exam_structurer, "_call_multimodal_llm", fake_llm)

    output_path = Path("data/exams/sample/problem_sample_fake_llm_pipeline_test.json")
    try:
        payload = run_pdf_to_exam_json.run_pipeline(
            input_path="problem_sample.png",
            output_path=str(output_path),
            module="exam",
        )

        assert validate_exam_payload(payload) is True
        assert payload["exam_info"] == {
            "exam_name": "",
            "subject": "",
            "round": "",
            "source_file": "problem_sample.png",
            "ingestion_mode": "multimodal_llm",
        }
        assert [problem["problem_id"] for problem in payload["problems"]] == [
            "problem_001",
            "problem_002",
        ]

        first_write = output_path.read_text(encoding="utf-8")
        assert first_write == json.dumps(payload, ensure_ascii=False, indent=2)

        second_payload = run_pdf_to_exam_json.run_pipeline(
            input_path="problem_sample.png",
            output_path=str(output_path),
            module="exam",
        )
        assert second_payload == payload
        assert output_path.read_text(encoding="utf-8") == first_write

        loaded_problems = load_exam(str(output_path))
        assert loaded_problems == payload["problems"]

        grouped = group_by_minor_subject(loaded_problems)
        assert list_minor_subjects() == ["closed_system_work", "p_v_diagram_work"]
        assert [problem["problem_no"] for problem in grouped["closed_system_work"]] == [1]
        assert [problem["problem_no"] for problem in grouped["p_v_diagram_work"]] == [2]
        assert [problem["problem_no"] for problem in get_problems_by_subject("p_v_diagram_work")] == [2]
        assert [problem["problem_no"] for problem in get_problems_by_tag("boundary_work")] == [1, 2]
    finally:
        try:
            output_path.unlink(missing_ok=True)
        except PermissionError:
            pass
