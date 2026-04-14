EXECUTION_PATHS = {
    "pressure": "concept_explanation",
    "force": "concept_explanation",
    "area": "concept_explanation",
    "temperature": "concept_explanation",
    "heat": "basic_calculation",
    "energy": "concept_explanation",
    "work": "basic_calculation",
    "efficiency": "efficiency_calculation",
    "power": "basic_calculation",
    "volume": "basic_calculation",
    "number": "basic_concept_lookup",
    "heat_engine": "efficiency_calculation",
}

INTENT_EXECUTION_PATHS = {
    "concept_explanation": "concept_explanation",
    "calculation": "basic_calculation",
    "judgement": "causal_judgement",
}


def dispatch_target_node(target_node: str, execution_intent: str | None = None) -> str:
    if not target_node:
        return "no_target"
    if execution_intent in INTENT_EXECUTION_PATHS:
        return INTENT_EXECUTION_PATHS[execution_intent]
    return EXECUTION_PATHS.get(target_node, "unmapped_execution")
