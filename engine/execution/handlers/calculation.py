import json
from pathlib import Path
import re
from typing import Any

from engine.execution.registry import build_execution_output, find_execution_node


CALCULATION_REGISTRY_PATH = Path("data/execution_calculation_registry.json")
NUMBER_PATTERN = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"


def load_calculation_registry(
    registry_path: Path | str = CALCULATION_REGISTRY_PATH,
) -> dict[str, dict[str, Any]]:
    path = Path(registry_path)
    with path.open("r", encoding="utf-8") as file:
        registry = json.load(file)

    if not isinstance(registry, dict):
        raise ValueError("execution calculation registry must be an object")

    return registry


def find_calculation_plan(target_node: str) -> dict[str, Any]:
    return load_calculation_registry().get(target_node, {})


def _parse_input_values(problem_text: str, plan: dict[str, Any]) -> dict[str, float]:
    values: dict[str, float] = {}
    input_aliases = plan.get("input_aliases", {})

    for input_name in plan.get("inputs", []):
        aliases = input_aliases.get(input_name, [input_name])
        for alias in aliases:
            pattern = rf"(?<!\w){re.escape(alias)}\s*(?:=|:|은|는|이|가)?\s*({NUMBER_PATTERN})"
            match = re.search(pattern, problem_text, flags=re.IGNORECASE)
            if match:
                values[input_name] = float(match.group(1))
                break

    return values


def _divide(inputs: list[str], values: dict[str, float]) -> tuple[float | None, str]:
    numerator = values[inputs[0]]
    denominator = values[inputs[1]]
    if denominator == 0:
        return None, f"Cannot divide by zero: {inputs[1]}"
    return numerator / denominator, ""


def _multiply(inputs: list[str], values: dict[str, float]) -> tuple[float | None, str]:
    result = 1.0
    for input_name in inputs:
        result *= values[input_name]
    return result, ""


OPERATION_REGISTRY = {
    "divide": _divide,
    "multiply": _multiply,
}


def _execute_formula(plan: dict[str, Any], values: dict[str, float]) -> tuple[float | None, str]:
    inputs = plan.get("inputs", [])
    missing_inputs = [input_name for input_name in inputs if input_name not in values]
    if missing_inputs:
        return None, f"Missing input values: {', '.join(missing_inputs)}"

    operation = plan.get("operation", "")
    operation_handler = OPERATION_REGISTRY.get(operation)
    if operation_handler is None:
        return None, f"Unknown calculation operation: {operation}"

    return operation_handler(inputs, values)


def _build_calculation_extra(plan: dict[str, Any], problem_text: str, calculation_ready: bool) -> dict[str, Any]:
    values = _parse_input_values(problem_text, plan) if problem_text else {}
    result, error = _execute_formula(plan, values) if problem_text and calculation_ready else (None, "")

    return {
        "calculation_ready": calculation_ready,
        "required_inputs": plan.get("inputs", []),
        "output_node": plan.get("output", ""),
        "calculation_steps": plan.get("steps", []),
        "notes": plan.get("notes", []),
        "input_values": values,
        "calculation_executed": result is not None,
        "result": result,
        "result_node": plan.get("output", ""),
        "calculation_error": error,
    }


def basic_calculation(target_node: str, problem_text: str = "") -> dict:
    entry = find_execution_node(target_node)
    plan = find_calculation_plan(target_node)

    if entry is None:
        return build_execution_output(
            target_node,
            None,
            execution_type="calculation",
            definition=f"No execution registry entry found for node: {target_node}",
            extra=_build_calculation_extra(plan, problem_text, calculation_ready=False),
        )

    return build_execution_output(
        target_node,
        entry,
        execution_type="calculation",
        extra=_build_calculation_extra(
            plan,
            problem_text,
            calculation_ready=bool(entry.get("formula") and plan),
        ),
    )
