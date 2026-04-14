from engine.execution.dispatcher import dispatch_target_node
from engine.execution.handlers import basic_calculation, causal_judgement, run_execution_handler
from engine.execution.handlers.calculation import _execute_formula
from engine.execution.handlers.router import HANDLER_REGISTRY


def test_dispatcher_covers_execution_registry_nodes() -> None:
    assert dispatch_target_node("efficiency") == "efficiency_calculation"
    assert dispatch_target_node("power") == "basic_calculation"
    assert dispatch_target_node("volume") == "basic_calculation"


def test_handler_router_uses_registered_handlers() -> None:
    assert "basic_calculation" in HANDLER_REGISTRY
    assert "causal_judgement" in HANDLER_REGISTRY

    output = run_execution_handler("basic_calculation", "pressure")

    assert output["node"] == "pressure"
    assert output["execution_type"] == "calculation"
    assert output["formula"] == "P = F / A"
    assert output["calculation_ready"] is True
    assert output["required_inputs"] == ["force", "area"]


def test_basic_calculation_returns_registry_backed_plan() -> None:
    output = basic_calculation("efficiency")

    assert output["execution_type"] == "calculation"
    assert output["calculation_ready"] is True
    assert output["required_inputs"] == ["useful_output", "input"]
    assert output["output_node"] == "efficiency"
    assert output["calculation_steps"]
    assert output["calculation_executed"] is False


def test_basic_calculation_executes_pressure_formula_from_problem_text() -> None:
    output = basic_calculation("pressure", "압력을 계산하라. 힘 10 면적 2")

    assert output["execution_type"] == "calculation"
    assert output["calculation_ready"] is True
    assert output["input_values"] == {"force": 10.0, "area": 2.0}
    assert output["calculation_executed"] is True
    assert output["result"] == 5.0
    assert output["result_node"] == "pressure"
    assert output["calculation_error"] == ""


def test_basic_calculation_reports_missing_input_values() -> None:
    output = basic_calculation("pressure", "압력을 계산하라. 힘 10")

    assert output["calculation_executed"] is False
    assert output["result"] is None
    assert output["calculation_error"] == "Missing input values: area"


def test_basic_calculation_reports_division_by_zero() -> None:
    output = basic_calculation("pressure", "압력을 계산하라. 힘 10 면적 0")

    assert output["calculation_executed"] is False
    assert output["result"] is None
    assert output["calculation_error"] == "Cannot divide by zero: area"


def test_calculation_execution_reports_unknown_operation() -> None:
    result, error = _execute_formula(
        {"inputs": ["force", "area"], "operation": "unknown_operation"},
        {"force": 10.0, "area": 2.0},
    )

    assert result is None
    assert error == "Unknown calculation operation: unknown_operation"


def test_handler_router_passes_problem_text_to_calculation_handler() -> None:
    output = run_execution_handler("basic_calculation", "pressure", "압력을 계산하라. 힘 12 면적 3")

    assert output["calculation_executed"] is True
    assert output["result"] == 4.0


def test_causal_judgement_builds_judgement_points_from_registry_relations() -> None:
    output = causal_judgement("pressure")

    assert output["execution_type"] == "judgement"
    assert output["judgement_ready"] is True
    assert output["judgement_points"]
    assert output["judgement_points"][0]["target"] == "pressure"
    assert output["judgement_result"] == "possible"
    assert output["reasoning_steps"]
    assert output["rule_evaluations"][0]["judgement_result"] == "increase"
    assert output["rule_evaluations"][1]["judgement_result"] == "decrease"


def test_causal_judgement_selects_relevant_increase_rule_from_problem_text() -> None:
    output = causal_judgement("pressure", "힘이 증가하고 면적은 일정하면 압력은 가능한가?")

    assert output["judgement_result"] == "increase"
    assert len(output["rule_evaluations"]) == 1
    assert output["rule_evaluations"][0]["condition"] == "force increases while area stays the same"
    assert output["reasoning_steps"] == [
        "Condition: force increases while area stays the same -> increase",
        "Pressure is calculated as force divided by area.",
        "If area is unchanged, increasing force increases the numerator.",
        "Therefore pressure increases.",
    ]


def test_causal_judgement_selects_relevant_decrease_rule_from_problem_text() -> None:
    output = causal_judgement("pressure", "면적이 증가하고 힘은 동일하면 압력은 가능한가?")

    assert output["judgement_result"] == "decrease"
    assert len(output["rule_evaluations"]) == 1
    assert output["rule_evaluations"][0]["condition"] == "area increases while force stays the same"


def test_causal_judgement_returns_structured_impossible_result_for_missing_node() -> None:
    output = causal_judgement("missing_node")

    assert output["execution_type"] == "judgement"
    assert output["judgement_ready"] is False
    assert output["judgement_points"] == []
    assert output["judgement_result"] == "impossible"
    assert output["reasoning_steps"] == [
        "No execution registry entry found for node: missing_node",
    ]
    assert output["rule_evaluations"] == []


def test_unknown_execution_path_returns_structured_unmapped_output() -> None:
    output = run_execution_handler("missing_path", "pressure")

    assert output["node"] == "pressure"
    assert output["execution_type"] == "unmapped"
    assert output["formula"] == ""
    assert output["causal_relations"] == []
