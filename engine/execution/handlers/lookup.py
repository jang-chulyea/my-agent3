from engine.execution.registry import build_execution_output, find_execution_node


def _build_lecture_text(definition: str, depth_info: dict, history_info: dict) -> str:
    sections = [
        ("개념 정의", definition),
        ("직관", depth_info.get("intuition", "")),
        ("원리", depth_info.get("principle", "")),
        ("공식", depth_info.get("formula", "")),
        ("활용", depth_info.get("application", "")),
        (
            "역사",
            " ".join(
                value
                for value in [
                    history_info.get("origin_problem", ""),
                    history_info.get("historical_context", ""),
                    history_info.get("evolution", ""),
                ]
                if value
            ),
        ),
    ]
    return "\n\n".join(f"[{title}]\n{content}" for title, content in sections if content)


def basic_concept_lookup(target_node: str) -> dict:
    entry = find_execution_node(target_node)
    if entry is not None:
        depth_info = entry.get("depth", {})
        history_info = entry.get("history", {})
        definition = entry.get("definition", "")
        return build_execution_output(
            target_node,
            entry,
            execution_type="lookup",
            extra={
                "depth_info": depth_info,
                "history_info": history_info,
                "explanation_bundle": {
                    "core_concept": {
                        "definition": entry.get("definition", ""),
                        "formula": entry.get("formula", ""),
                    },
                    "depth": depth_info,
                    "history": history_info,
                },
                "lecture_text": _build_lecture_text(definition, depth_info, history_info),
            },
        )

    definition = f"{target_node}에 대한 기본 개념 설명이 아직 등록되지 않았다."
    return {
        "node": target_node,
        "execution_type": "lookup",
        "definition": definition,
        "formula": "",
        "causal_relations": [],
        "depth_info": {},
        "history_info": {},
        "explanation_bundle": {
            "core_concept": {
                "definition": definition,
                "formula": "",
            },
            "depth": {},
            "history": {},
        },
        "lecture_text": _build_lecture_text(definition, {}, {}),
    }
