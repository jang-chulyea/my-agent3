import json

from engine.ingestion import run_pdf_to_exam_json


def test_pdf_to_exam_json_pipeline_with_mocked_text(monkeypatch) -> None:
    raw_text = """
1. question: Heat engine efficiency question?
major_subject: AC refrigeration design
minor_subject: thermodynamics
topic: second law
tags: thermodynamics, second_law
A) Choice A
B) Choice B
C) Choice C
D) Choice D
answer: A
explanation: Test explanation.

2. question: Compressor role question?
major_subject: AC refrigeration design
minor_subject: refrigeration_cycle
topic: compressor
tags: refrigeration_cycle, compressor
A) Choice A
B) Choice B
C) Choice C
D) Choice D
answer: B
explanation: Compressor test explanation.

3. question: Refer to the following table and choose the correct refrigerant state.
major_subject: AC refrigeration design
minor_subject: refrigeration_cycle
topic: refrigerant table
tags: refrigeration_cycle, table
A) Choice A
B) Choice B
C) Choice C
D) Choice D
answer: C
explanation: Table-based test explanation.
"""
    monkeypatch.setattr(run_pdf_to_exam_json, "extract_text", lambda _path: raw_text)
    monkeypatch.setattr(
        run_pdf_to_exam_json,
        "extract_problems_from_file",
        lambda _path, _module: (_ for _ in ()).throw(RuntimeError("mock multimodal unavailable")),
    )
    monkeypatch.setattr(
        run_pdf_to_exam_json,
        "write_exam_json",
        lambda problems, _output_path, exam_info=None: {
            "exam_info": exam_info or {},
            "problems": problems,
        },
    )

    result = run_pdf_to_exam_json.run_pipeline(
        input_path="mock.pdf",
        output_path="mock_output.json",
        module="exam",
    )

    written = json.loads(json.dumps(result))
    assert result == written
    assert written["exam_info"] == {
        "exam_name": "",
        "subject": "",
        "round": "",
        "source_file": "mock.pdf",
        "ingestion_mode": "selectable_text_fallback",
        "multimodal_error": "RuntimeError: mock multimodal unavailable",
        "fallback_reason": "multimodal_exception",
    }
    assert len(written["problems"]) == 3
    assert written["problems"][0]["problem_id"] == "problem_001"
    assert written["problems"][0]["problem_no"] == 1
    assert written["problems"][0]["module"] == "exam"
    assert written["problems"][0]["major_subject"] == "AC refrigeration design"
    assert written["problems"][0]["minor_subject"] == "thermodynamics"
    assert written["problems"][0]["topic"] == "second law"
    assert written["problems"][0]["tags"] == ["thermodynamics", "second_law"]
    assert written["problems"][0]["question"] == "Heat engine efficiency question?"
    assert written["problems"][0]["answer"] == "A"
    assert written["problems"][0]["explanation"] == "Test explanation."
    assert written["problems"][0]["visual_required"] is False
    assert written["problems"][0]["ingestion_status"] == "structured"
    assert written["problems"][0]["solve_status"] == "not_started"
    assert written["problems"][0]["review_status"] == "auto"
    assert written["problems"][2]["visual_required"] is True
    assert written["problems"][2]["ingestion_status"] == "visual_required"
    assert written["problems"][2]["solve_status"] == "not_started"
    assert written["problems"][2]["review_status"] == "manual_or_llm_review"
