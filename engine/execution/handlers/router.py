from engine.execution.handlers.calculation import basic_calculation
from engine.execution.handlers.judgement import causal_judgement
from engine.execution.handlers.lookup import basic_concept_lookup


HANDLER_REGISTRY = {
    "concept_explanation": basic_concept_lookup,
    "basic_concept_lookup": basic_concept_lookup,
    "basic_calculation": basic_calculation,
    "efficiency_calculation": basic_calculation,
    "causal_judgement": causal_judgement,
}


def run_execution_handler(execution_path: str, target_node: str, problem_text: str = "") -> dict:
    handler = HANDLER_REGISTRY.get(execution_path)
    if handler is not None:
        if execution_path in {"basic_calculation", "efficiency_calculation"}:
            return handler(target_node, problem_text)
        return handler(target_node)

    if execution_path == "no_target":
        return {
            "node": "",
            "execution_type": "error",
            "definition": "No target_node was selected.",
            "formula": "",
            "causal_relations": [],
        }
    return {
        "node": target_node,
        "execution_type": "unmapped",
        "definition": f"No handler registered for execution path: {execution_path}",
        "formula": "",
        "causal_relations": [],
    }
