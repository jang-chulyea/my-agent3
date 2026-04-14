from engine.execution.dispatcher import dispatch_target_node
from engine.execution.handlers import run_execution_handler
from engine.problem_parser.execution_intent_selector import (
    INTENT_CALCULATION,
    INTENT_CONCEPT_EXPLANATION,
    INTENT_JUDGEMENT,
    INTENT_UNKNOWN,
    select_execution_intent,
)
from engine.problem_parser.node_mapping_entry import parse_problem_text


def _route_problem(problem_text: str) -> tuple[str, str, str, dict]:
    parsed = parse_problem_text(problem_text)
    execution_intent = select_execution_intent(problem_text)
    execution_path = dispatch_target_node(parsed.target_node, execution_intent)
    output = run_execution_handler(execution_path, parsed.target_node)
    return parsed.target_node, execution_intent, execution_path, output


def test_concept_explanation_intent_routes_to_concept_path() -> None:
    target_node, execution_intent, execution_path, output = _route_problem("압력의 정의는?")

    assert target_node == "pressure"
    assert execution_intent == INTENT_CONCEPT_EXPLANATION
    assert execution_path == "concept_explanation"
    assert output["execution_type"] == "lookup"


def test_calculation_intent_routes_to_calculation_related_path() -> None:
    target_node, execution_intent, execution_path, output = _route_problem("압력을 계산하라")

    assert target_node == "pressure"
    assert execution_intent == INTENT_CALCULATION
    assert execution_path == "basic_calculation"
    assert output["execution_type"] == "calculation"
    assert output["calculation_ready"] is True


def test_judgement_intent_routes_to_judgement_path() -> None:
    _target_node, execution_intent, execution_path, output = _route_problem("이 과정이 가능한가?")

    assert execution_intent == INTENT_JUDGEMENT
    assert execution_path == "causal_judgement"
    assert output["execution_type"] == "judgement"


def test_unknown_or_ambiguous_intent_falls_back_to_target_node_routing() -> None:
    assert select_execution_intent("압력은?") == INTENT_UNKNOWN
    assert select_execution_intent("압력의 정의와 값을 계산하라") == INTENT_UNKNOWN

    target_node, execution_intent, execution_path, output = _route_problem("압력은?")

    assert target_node == "pressure"
    assert execution_intent == INTENT_UNKNOWN
    assert execution_path == "concept_explanation"
    assert output["execution_type"] == "lookup"
