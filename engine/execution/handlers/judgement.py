import json
from pathlib import Path
import re
from typing import Any

from engine.execution.registry import build_execution_output, find_execution_node


JUDGEMENT_REGISTRY_PATH = Path("data/execution_judgement_registry.json")
CONDITION_KEYWORDS = {
    "increase": ("increase", "increases", "increased", "증가", "커지면", "커진다", "상승"),
    "decrease": ("decrease", "decreases", "decreased", "감소", "작아지면", "줄면", "하락"),
    "same": ("same", "constant", "unchanged", "일정", "동일", "같", "유지"),
}
INPUT_ALIASES = {
    "force": ("force", "힘", "작용력", "하중"),
    "area": ("area", "면적", "단면적", "넓이"),
    "work": ("work", "일량"),
    "time": ("time", "시간"),
    "mass": ("mass", "질량"),
    "acceleration": ("acceleration", "가속도"),
}


def load_judgement_registry(
    registry_path: Path | str = JUDGEMENT_REGISTRY_PATH,
) -> dict[str, dict[str, Any]]:
    path = Path(registry_path)
    with path.open("r", encoding="utf-8") as file:
        registry = json.load(file)

    if not isinstance(registry, dict):
        raise ValueError("execution judgement registry must be an object")

    return registry


def find_judgement_plan(target_node: str) -> dict[str, Any]:
    return load_judgement_registry().get(target_node, {})


def _relation_matches_target(relation: dict[str, Any], target_node: str) -> bool:
    return relation.get("from") == target_node or relation.get("to") == target_node


def _build_reasoning_steps(plan: dict[str, Any]) -> list[str]:
    reasoning_steps: list[str] = []
    for rule in plan.get("rules", []):
        condition = rule.get("condition", "")
        judgement_result = rule.get("judgement_result", "")
        if condition and judgement_result:
            reasoning_steps.append(f"Condition: {condition} -> {judgement_result}")
        reasoning_steps.extend(rule.get("reasoning_steps", []))
    return reasoning_steps


def _build_rule_evaluations(plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "condition": rule.get("condition", ""),
            "judgement_result": rule.get("judgement_result", ""),
            "reasoning_steps": rule.get("reasoning_steps", []),
        }
        for rule in plan.get("rules", [])
    ]


def _parse_problem_condition(problem_text: str) -> dict[str, set[str]]:
    normalized_text = problem_text.lower()
    clauses = [
        clause.strip()
        for clause in re.split(r"하고|,|\.|;|\bwhile\b|\band\b|\bif\b", normalized_text)
        if clause.strip()
    ]
    parsed = {
        "directions": {
            direction
            for direction, keywords in CONDITION_KEYWORDS.items()
            if any(keyword in normalized_text for keyword in keywords)
        },
        "inputs": {
            input_name
            for input_name, aliases in INPUT_ALIASES.items()
            if any(alias in normalized_text for alias in aliases)
        },
        "input_directions": set(),
    }
    for clause in clauses:
        clause_inputs = [
            input_name
            for input_name, aliases in INPUT_ALIASES.items()
            if any(alias in clause for alias in aliases)
        ]
        clause_directions = [
            direction
            for direction, keywords in CONDITION_KEYWORDS.items()
            if any(keyword in clause for keyword in keywords)
        ]
        for input_name in clause_inputs:
            for direction in clause_directions:
                parsed["input_directions"].add((input_name, direction))
    return parsed


def _rule_matches_condition(rule: dict[str, Any], parsed_condition: dict[str, set[str]]) -> bool:
    condition = rule.get("condition", "").lower()
    judgement_result = rule.get("judgement_result", "")
    directions = parsed_condition.get("directions", set())
    inputs = parsed_condition.get("inputs", set())
    input_directions = parsed_condition.get("input_directions", set())

    if input_directions:
        rule_input_directions = _parse_problem_condition(condition).get("input_directions", set())
        return input_directions.issubset(rule_input_directions)

    direction_matches = not directions or judgement_result in directions or any(
        direction in condition for direction in directions
    )
    input_matches = not inputs or any(input_name in condition for input_name in inputs)

    return direction_matches and input_matches


def _select_relevant_rules(plan: dict[str, Any], problem_text: str) -> list[dict[str, Any]]:
    if not problem_text:
        return plan.get("rules", [])

    parsed_condition = _parse_problem_condition(problem_text)
    for rule in plan.get("rules", []):
        if _rule_matches_condition(rule, parsed_condition):
            return [rule]

    return []


def causal_judgement(target_node: str, problem_text: str = "") -> dict:
    entry = find_execution_node(target_node)
    plan = find_judgement_plan(target_node)
    if entry is None:
        return build_execution_output(
            target_node,
            None,
            execution_type="judgement",
            definition=f"No execution registry entry found for node: {target_node}",
            extra={
                "judgement_ready": False,
                "judgement_points": [],
                "judgement_result": "impossible",
                "reasoning_steps": [
                    f"No execution registry entry found for node: {target_node}",
                ],
                "rule_evaluations": [],
            },
        )

    causal_relations = entry.get("causal_relations", [])
    judgement_points = [
        {
            "source": relation.get("from", ""),
            "target": relation.get("to", ""),
            "relation": relation.get("relation", ""),
            "directly_about_target": _relation_matches_target(relation, target_node),
        }
        for relation in causal_relations
    ]
    selected_plan = {
        **plan,
        "rules": _select_relevant_rules(plan, problem_text),
    }
    selected_rules = selected_plan.get("rules", [])

    return build_execution_output(
        target_node,
        entry,
        execution_type="judgement",
        extra={
            "judgement_ready": bool(judgement_points),
            "judgement_points": judgement_points,
            "judgement_result": (
                selected_rules[0].get("judgement_result", "")
                if problem_text and selected_rules
                else plan.get("judgement_result", "possible" if judgement_points else "impossible")
            ),
            "reasoning_steps": _build_reasoning_steps(selected_plan),
            "rule_evaluations": _build_rule_evaluations(selected_plan),
        },
    )
