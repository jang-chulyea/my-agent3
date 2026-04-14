from engine.execution.dispatcher import dispatch_target_node
from engine.execution.run_dispatch import attach_concept_chain
from engine.execution.handlers import run_execution_handler
from chain_builder import ChainBuilder
from relation_resolver import RelationResolver


def test_execution_routing_concept_explanation_case() -> None:
    execution_path = dispatch_target_node("pressure")
    output = run_execution_handler(execution_path, "pressure")

    assert execution_path == "concept_explanation"
    assert output["node"] == "pressure"
    assert output["execution_type"] == "lookup"
    assert output["definition"]
    assert output["formula"] == "P = F / A"
    assert output["depth_info"]["intuition"]
    assert set(output["depth_info"]) == {"intuition", "principle", "formula", "application"}
    assert output["history_info"]["origin_problem"]
    assert set(output["history_info"]) == {"origin_problem", "historical_context", "evolution"}
    assert output["explanation_bundle"]["core_concept"]["definition"] == output["definition"]
    assert output["explanation_bundle"]["core_concept"]["formula"] == output["formula"]
    assert output["explanation_bundle"]["depth"] == output["depth_info"]
    assert output["explanation_bundle"]["history"] == output["history_info"]
    assert "[개념 정의]\n압력은 단위 면적당 작용하는 힘이다." in output["lecture_text"]
    assert "[공식]\nP = F / A" in output["lecture_text"]
    assert "[역사]\n" in output["lecture_text"]


def test_concept_chain_is_added_to_final_concept_output() -> None:
    resolver = RelationResolver("data/relations.json")
    builder = ChainBuilder()
    assert resolver.resolve("temperature", ["pressure"]) == []

    relations = resolver.resolve(
        "temperature",
        ["pressure", "volume"],
        context={"conditions": ["constant_volume"]},
    )

    assert relations == [
        {"source": "temperature", "target": "pressure", "text": "온도 ↑ → 압력 ↑"},
        {"source": "temperature", "target": "volume", "text": "온도 ↑ → 부피 ↑"},
        {"source": "pressure", "target": "boiling_point", "text": "압력 ↑ → 끓는점 ↑"},
    ]
    chain, reason = builder.build(relations)
    assert chain == ["온도 ↑ → 압력 ↑", "압력 ↑ → 끓는점 ↑"]
    assert reason == "가장 긴 인과 경로 선택 (length=2)"
    assert len(chain) == 2
    assert chain.count("온도 ↑ → 압력 ↑") == 1
    assert chain.count("압력 ↑ → 끓는점 ↑") == 1
    assert chain.count("온도 ↑ → 부피 ↑") == 0

    output = run_execution_handler("concept_explanation", "temperature")
    final_output = attach_concept_chain(
        output,
        "temperature",
        ["pressure", "volume"],
        context={"conditions": ["constant_volume"]},
    )

    assert final_output["concept_chain"] == ["온도 ↑ → 압력 ↑", "압력 ↑ → 끓는점 ↑"]
    assert final_output["chain_reason"] == "가장 긴 인과 경로 선택 (length=2)"
    assert final_output["explanation_bundle"]["concept_chain"] == ["온도 ↑ → 압력 ↑", "압력 ↑ → 끓는점 ↑"]
    assert final_output["explanation_bundle"]["chain_reason"] == "가장 긴 인과 경로 선택 (length=2)"
    assert final_output["explanation_bundle"]["chain_explanation"] == (
        "이 문제는 다음 개념 흐름으로 이해된다.\n"
        "온도 ↑ → 압력 ↑\n"
        "압력 ↑ → 끓는점 ↑\n"
        "즉, 개념들이 연결되어 결과가 결정된다."
    )
    assert final_output["explanation_bundle"]["problem_interpretation"] == (
        "이 문제는 'temperature' 개념을 중심으로 해석된다."
    )
    assert final_output["explanation_bundle"]["solution_process"] == "개념을 기반으로 설명을 구성한다."
    assert final_output["explanation_bundle"]["conclusion"] == (
        "따라서 최종적으로 '압력 ↑ → 끓는점 ↑'의 결과에 도달한다."
    )
    assert (
        "[개념 연결 설명]\n"
        "이 문제는 다음 개념 흐름으로 이해된다.\n"
        "온도 ↑ → 압력 ↑\n"
        "압력 ↑ → 끓는점 ↑\n"
        "즉, 개념들이 연결되어 결과가 결정된다."
    ) in final_output["lecture_text"]
    assert "[추론 이유]\n가장 긴 인과 경로 선택 (length=2)" in final_output["lecture_text"]
    assert "[문제 해석]\n이 문제는 'temperature' 개념을 중심으로 해석된다." in final_output["lecture_text"]
    assert "[해결 과정]\n개념을 기반으로 설명을 구성한다." in final_output["lecture_text"]
    assert "[결론]\n따라서 최종적으로 '압력 ↑ → 끓는점 ↑'의 결과에 도달한다." in final_output["lecture_text"]
    assert "온도 ↑ → 부피 ↑" not in final_output["lecture_text"]


def test_judgement_final_output_gets_problem_solution_conclusion_flow() -> None:
    output = run_execution_handler("causal_judgement", "temperature")
    final_output = attach_concept_chain(
        output,
        "temperature",
        ["pressure", "volume"],
        context={"conditions": ["constant_volume"]},
    )

    assert final_output["explanation_bundle"]["problem_interpretation"] == (
        "이 문제는 'temperature' 개념을 중심으로 해석된다."
    )
    assert final_output["explanation_bundle"]["solution_process"] == "조건을 기반으로 변화 방향을 판단한다."
    assert final_output["explanation_bundle"]["conclusion"] == (
        "따라서 최종적으로 '압력 ↑ → 끓는점 ↑'의 결과에 도달한다."
    )
    assert "[해결 과정]\n조건을 기반으로 변화 방향을 판단한다." in final_output["lecture_text"]


def test_execution_routing_calculation_planning_case() -> None:
    execution_path = dispatch_target_node("power")
    output = run_execution_handler(execution_path, "power")

    assert execution_path == "basic_calculation"
    assert output["node"] == "power"
    assert output["execution_type"] == "calculation"
    assert output["calculation_ready"] is True
    assert output["required_inputs"] == ["work", "time"]
    assert output["calculation_steps"]


def test_execution_routing_judgement_case() -> None:
    output = run_execution_handler("causal_judgement", "pressure")

    assert output["node"] == "pressure"
    assert output["execution_type"] == "judgement"
    assert output["judgement_ready"] is True
    assert output["judgement_points"]


def test_execution_routing_no_target_and_fallback_cases() -> None:
    no_target_path = dispatch_target_node("")
    no_target_output = run_execution_handler(no_target_path, "")

    assert no_target_path == "no_target"
    assert no_target_output["node"] == ""
    assert no_target_output["execution_type"] == "error"

    fallback_path = dispatch_target_node("unknown_node")
    fallback_output = run_execution_handler(fallback_path, "unknown_node")

    assert fallback_path == "unmapped_execution"
    assert fallback_output["node"] == "unknown_node"
    assert fallback_output["execution_type"] == "unmapped"
