from typing import Any


def format_final_output(
    structured: dict,
    rag_result: dict | None,
    llm_result: dict | None,
    llm_checked: dict | None,
    fallback_result: dict | None = None,
) -> dict:
    safe_rag_result = _safe_rag_result(rag_result)
    validation = _safe_validation(llm_checked)
    validated_output = validation.get("validated_output", {})
    used_fallback = fallback_result is not None
    source = fallback_result if used_fallback else validated_output
    source = source if isinstance(source, dict) else {}
    concept_nodes = _output_concept_nodes(structured, source)
    importance = _safe_importance(structured.get("importance") or source.get("importance"))

    depth = _safe_depth(source.get("depth") or source.get("depth_info"))
    concept_chain = _safe_list(source.get("concept_chain"))
    steps = _safe_list(source.get("steps"))
    answer = source.get("answer", source.get("definition"))
    unit = source.get("unit") or ""
    explanation = _safe_text(
        source.get("explanation")
        or source.get("lecture_text")
        or "\n".join(str(step) for step in steps)
    )

    output = {
        "question": _safe_text(structured.get("question") or structured.get("target_node")),
        "question_type": _safe_text(
            structured.get("question_type") or structured.get("execution_type")
        ),
        "subject": _safe_text(structured.get("subject")),
        "topic": _safe_text(structured.get("topic")),
        "concepts": _safe_list(structured.get("concepts")),
        "concept_nodes": concept_nodes,
        "importance": importance,
        "rag_result": safe_rag_result,
        "llm_result": llm_result if isinstance(llm_result, dict) else {},
        "validation": {
            "valid": bool(validation.get("valid", False)),
            "confidence": float(validation.get("confidence", 0.0)),
            "issues": _safe_list(validation.get("issues")),
        },
        "concept_chain": concept_chain,
        "depth": depth,
        "steps": steps,
        "answer": answer,
        "unit": unit,
        "explanation": explanation,
        "related_lecture_materials": _related_lecture_materials(
            safe_rag_result,
            structured.get("concepts"),
        ),
        "used_fallback": used_fallback,
    }

    # Keep current UI-facing keys stable until the UI is intentionally migrated.
    output["lecture_text"] = explanation
    output["explanation_bundle"] = source.get("explanation_bundle", {})
    for key in (
        "node",
        "execution_type",
        "definition",
        "formula",
        "depth_info",
        "history_info",
        "chain_reason",
        "chain_explanation",
    ):
        if key in source:
            output[key] = source[key]
    if "fallback_reason" in source:
        output["fallback_reason"] = source["fallback_reason"]

    return output


def _safe_rag_result(rag_result: dict | None) -> dict:
    if not isinstance(rag_result, dict):
        return {"query": "", "matches": []}

    matches = rag_result.get("matches")
    if not isinstance(matches, list):
        matches = []

    return {
        "query": _safe_text(rag_result.get("query")),
        "matches": matches,
    }


def _safe_validation(llm_checked: dict | None) -> dict:
    if not isinstance(llm_checked, dict):
        return {
            "valid": False,
            "confidence": 0.0,
            "issues": [],
            "validated_output": {},
        }

    return {
        "valid": bool(llm_checked.get("valid", False)),
        "confidence": float(llm_checked.get("confidence", 0.0)),
        "issues": _safe_list(llm_checked.get("issues")),
        "validated_output": llm_checked.get("validated_output", {}),
    }


def _safe_depth(depth: Any) -> dict:
    depth = depth if isinstance(depth, dict) else {}
    return {
        "level1": _safe_text(depth.get("level1") or depth.get("intuition")),
        "level2": _safe_text(depth.get("level2") or depth.get("principle")),
        "level3": _safe_text(depth.get("level3") or depth.get("formula")),
    }


def _safe_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _safe_importance(value: Any) -> dict:
    importance = value if isinstance(value, dict) else {}
    return {
        "score": float(importance.get("score", 0.0) or 0.0),
        "frequency": int(importance.get("frequency", 0) or 0),
        "difficulty": int(importance.get("difficulty", 0) or 0),
        "recency": int(importance.get("recency", 0) or 0),
    }


def _output_concept_nodes(structured: dict, source: dict) -> list[str]:
    concept_nodes = _normalize_concept_node_strings(structured.get("concept_nodes"))
    if concept_nodes:
        return concept_nodes

    concept_nodes = _normalize_concept_node_strings(structured.get("concepts"))
    if concept_nodes:
        return concept_nodes

    concept_nodes = _normalize_concept_node_strings(structured.get("related_nodes"))
    if concept_nodes:
        return concept_nodes

    concept_nodes = _normalize_concept_node_strings(source.get("concept_nodes"))
    if concept_nodes:
        return concept_nodes

    return []


def _normalize_concept_node_strings(value: Any) -> list[str]:
    normalized: list[str] = []
    for item in _safe_list(value):
        if isinstance(item, str):
            text = item.strip()
            if text:
                normalized.append(text)
        elif isinstance(item, dict):
            for key in ("node_key", "label", "text"):
                raw = item.get(key)
                if isinstance(raw, str) and raw.strip():
                    normalized.append(raw.strip())
                    break
    return normalized


def _related_lecture_materials(rag_result: dict, concepts: list | None = None) -> list[dict]:
    materials = []
    requested_concepts = {str(concept).casefold() for concept in _safe_list(concepts)}
    for match in rag_result.get("matches", []):
        if not isinstance(match, dict) or match.get("source_type") != "lecture_material":
            continue
        score = float(match.get("score", 0.0))
        if score < 5:
            continue

        data = match.get("data", {})
        if not isinstance(data, dict):
            continue
        material_concepts = _safe_list(data.get("concepts"))
        material_concept_set = {str(concept).casefold() for concept in material_concepts}
        if requested_concepts and not requested_concepts.intersection(material_concept_set):
            continue

        materials.append(
            {
                "id": _safe_text(data.get("id")),
                "title": _safe_text(data.get("title")),
                "summary": _safe_text(data.get("summary")),
                "concepts": material_concepts,
                "source": _safe_text(match.get("source")),
                "score": score,
            }
        )

    return sorted(materials, key=lambda material: material["score"], reverse=True)[:2]
