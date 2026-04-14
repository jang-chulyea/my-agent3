from dataclasses import dataclass
import sys

from engine.node_mapping.extractor import extract_candidate_terms
from engine.node_mapping.mapper import load_node_registry, map_problem_to_nodes
from engine.node_mapping.normalizer import normalize_text


@dataclass(frozen=True)
class TestCase:
    label: str
    problem_text: str
    expected_target: str


TEST_CASES = [
    TestCase("concept_query_pressure_definition", "압력의 정의는?", "pressure"),
    TestCase("causal_query_pressure_increase", "압력이 증가하는 경우는?", "pressure"),
    TestCase("causal_query_force_to_pressure", "힘이 커지면 압력은 어떻게 변하나?", "pressure"),
    TestCase("intuition_query_needle_vs_plate", "왜 바늘은 아프고 넓은 판은 덜 아플까?", "area"),
    TestCase("calculation_like_pressure_formula", "압력 계산은 어떻게 하지?", "pressure"),
    TestCase("concept_query_force_definition", "힘이란 무엇인가?", "force"),
    TestCase("concept_query_area_definition", "면적의 뜻은?", "area"),
    TestCase("causal_query_temperature_to_pressure", "온도가 올라가면 압력은?", "pressure"),
    TestCase("math_query_number_definition", "number의 의미는?", "number"),
    TestCase("mixed_query_force_area_pressure", "힘과 면적이 압력에 어떤 영향을 주나?", "pressure"),
    TestCase("mixed_query_pressure_what_changes", "힘과 면적이 바뀌면 압력은 무엇이 되나?", "pressure"),
    TestCase("mixed_query_force_target", "압력과 면적이 주어질 때 힘은 얼마인가?", "force"),
    TestCase("mixed_query_area_target", "힘과 압력이 주어질 때 면적은 어떻게 구하나?", "area"),
    TestCase("mixed_query_pressure_target", "힘, 면적, 압력 중에서 무엇을 계산해야 하나?", "pressure"),
    TestCase("mixed_query_pressure_focus", "힘과 면적이 함께 변하면 결국 압력은 어떻게 달라지나?", "pressure"),
    TestCase("concept_query_efficiency_definition", "효율은 무엇인가?", "efficiency"),
    TestCase("concept_query_pressure_short", "압력의 정의", "pressure"),
    TestCase("causal_query_force_increase_short", "힘이 증가하면?", "force"),
]


RULES_ADDED = [
    "mixed-question target preference when pressure/force/area co-occur",
    "question focus proximity scoring",
    "asked-about node bonus using topic particles near focus markers",
]


def legacy_map_problem_to_nodes(problem_text: str) -> tuple[str, str]:
    registry = load_node_registry()
    candidates = extract_candidate_terms(problem_text)
    normalized_candidates = {normalize_text(candidate) for candidate in candidates}
    score_by_node: dict[str, float] = {}
    matched_nodes: set[str] = set()

    for entry in registry:
        best_score = 0.0
        for alias in entry.aliases:
            normalized_alias = normalize_text(alias)
            if normalized_alias in normalized_candidates:
                best_score = max(best_score, 1.0 + (len(normalized_alias) * 0.01))
            elif normalized_alias and normalized_alias in normalize_text(problem_text):
                best_score = max(best_score, 0.6 + (len(normalized_alias) * 0.01))

        if best_score > 0.0:
            score_by_node[entry.canonical_name] = best_score
            matched_nodes.add(entry.canonical_name)

    if not score_by_node:
        return "", "failure"

    target_node = max(score_by_node, key=lambda node: (score_by_node[node], len(node)))
    if len(matched_nodes) > 1:
        return target_node, "ambiguous"
    return target_node, "success"


def classify_case(result, expected_target: str) -> str:
    competing_nodes = {item.mapped_to for item in result.matched_terms}
    if result.target_node != expected_target:
        return "failure"
    if len(competing_nodes) > 1 and result.confidence < 0.75:
        return "ambiguous"
    return "success"


def run() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    before_counts = {"success": 0, "failure": 0, "ambiguous": 0}
    after_counts = {"success": 0, "failure": 0, "ambiguous": 0}

    success_cases: list[str] = []
    failure_cases: list[str] = []
    ambiguous_cases: list[str] = []

    for case in TEST_CASES:
        before_target, before_status = legacy_map_problem_to_nodes(case.problem_text)
        before_counts[before_status] += 1

        result = map_problem_to_nodes(case.problem_text)
        status = classify_case(result, case.expected_target)
        after_counts[status] += 1

        if status == "success":
            success_cases.append(case.label)
        elif status == "failure":
            failure_cases.append(case.label)
        else:
            ambiguous_cases.append(case.label)

        print("=" * 60)
        print(f"label: {case.label}")
        print(f"input: {case.problem_text}")
        print(f"expected_target: {case.expected_target}")
        print(f"before_target: {before_target}")
        print(f"before_status: {before_status}")
        print(f"target_node: {result.target_node}")
        print(f"related_nodes: {result.related_nodes}")
        print(f"confidence: {result.confidence}")
        print(f"score_breakdown: {result.score_breakdown}")
        print("selection_reasons:")
        for reason in result.selection_reasons:
            print(f"  - {reason}")
        print(f"after_status: {status}")

    solved = "mixed_query_force_area_pressure" not in failure_cases and "mixed_query_force_area_pressure" not in ambiguous_cases

    print("=" * 60)
    print("updated_counts")
    print(f"before: {before_counts}")
    print(f"after: {after_counts}")
    print(f"remaining_weak_case_solved: {solved}")
    print(f"success_cases ({len(success_cases)}): {success_cases}")
    print(f"failure_cases ({len(failure_cases)}): {failure_cases}")
    print(f"ambiguous_cases ({len(ambiguous_cases)}): {ambiguous_cases}")
    print("new_rules_added:")
    for rule in RULES_ADDED:
        print(f"  - {rule}")


if __name__ == "__main__":
    run()
