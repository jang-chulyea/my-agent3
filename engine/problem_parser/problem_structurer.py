KEYWORD_NODE_MAP = {
    "온도": "temperature",
    "압력": "pressure",
    "끓는점": "boiling_point",
}


def structure_problem_text(problem_text: str) -> dict:
    conditions = []
    if "부피 일정" in problem_text or "부피가 일정" in problem_text:
        conditions.append("constant_volume")

    if any(keyword in problem_text for keyword in ["계산", "구하라"]):
        execution_type = "calculation"
    elif any(keyword in problem_text for keyword in ["증가", "감소", "변화", "상승"]):
        execution_type = "judgement"
    else:
        execution_type = "concept"

    found_nodes = [
        node
        for keyword, node in KEYWORD_NODE_MAP.items()
        if keyword in problem_text
    ]
    target_node = found_nodes[0] if found_nodes else ""
    related_nodes = [node for node in found_nodes[1:] if node != target_node]

    return {
        "target_node": target_node,
        "related_nodes": related_nodes,
        "conditions": conditions,
        "execution_type": execution_type,
    }


def structure(problem_text: str) -> dict:
    return structure_problem_text(problem_text)
