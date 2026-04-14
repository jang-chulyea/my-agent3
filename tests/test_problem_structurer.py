from engine.problem_parser.problem_structurer import structure_problem_text
from engine.execution.run_dispatch import run


def test_problem_structurer_extracts_condition_execution_type_and_nodes() -> None:
    structured = structure_problem_text("부피가 일정할 때 온도가 상승하면 압력은 어떻게 되는가?")

    assert structured == {
        "target_node": "temperature",
        "related_nodes": ["pressure"],
        "conditions": ["constant_volume"],
        "execution_type": "judgement",
    }


def test_structured_input_runs_existing_pipeline() -> None:
    result = run({
        "target_node": "temperature",
        "related_nodes": ["pressure"],
        "conditions": ["constant_volume"],
        "execution_type": "judgement",
    })

    assert "lecture_text" in result
    assert result["concept_chain"] == ["온도 ↑ → 압력 ↑", "압력 ↑ → 끓는점 ↑"]


def test_problem_structurer_marks_unsupported_input_without_target_node() -> None:
    structured = structure_problem_text("5곱하기 6은?")

    assert structured["target_node"] == ""
    assert structured["execution_type"] == "concept"
