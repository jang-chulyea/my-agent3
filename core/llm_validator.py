from typing import Any


def validate_llm_output(llm_result: dict, rag_result: dict) -> dict:
    issues = []
    validated_output = {}

    try:
        validated_output = _validate_with_pydantic(llm_result)
    except ImportError:
        try:
            validated_output = _validate_manually(llm_result)
        except Exception as exc:
            issues.append(str(exc))
            return {
                "valid": False,
                "confidence": 0.0,
                "issues": issues,
                "validated_output": {},
            }
    except Exception as exc:
        issues.append(str(exc))
        return {
            "valid": False,
            "confidence": 0.0,
            "issues": issues,
            "validated_output": {},
        }

    rag_concepts = _rag_concepts(rag_result)
    output_concepts = {str(concept).casefold() for concept in validated_output.get("concept_chain", [])}
    hallucinated_concepts = sorted(output_concepts - rag_concepts) if rag_concepts else []

    confidence = 1.0
    if hallucinated_concepts:
        issues.append(
            "low_confidence: concept_chain references concepts not found in RAG context: "
            + ", ".join(hallucinated_concepts)
        )
        confidence = 0.5

    return {
        "valid": True,
        "confidence": confidence,
        "issues": issues,
        "validated_output": validated_output,
    }


def _validate_with_pydantic(llm_result: dict) -> dict:
    from schemas.llm_output_schema import LLMOutputSchema

    return LLMOutputSchema.model_validate(llm_result).model_dump()


def _validate_manually(llm_result: Any) -> dict:
    if not isinstance(llm_result, dict):
        raise ValueError("llm_result must be a dict")

    required_keys = {"answer", "unit", "steps", "concept_chain", "depth"}
    missing_keys = required_keys - llm_result.keys()
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"llm_result missing required keys: {missing}")

    if not isinstance(llm_result["answer"], (float, int, str)):
        raise ValueError("llm_result answer must be a float or string")
    if llm_result["unit"] is not None and not isinstance(llm_result["unit"], str):
        raise ValueError("llm_result unit must be a string or None")
    if not isinstance(llm_result["steps"], list) or not llm_result["steps"]:
        raise ValueError("steps must not be empty")
    if not isinstance(llm_result["concept_chain"], list) or not llm_result["concept_chain"]:
        raise ValueError("concept_chain must have at least 1 item")
    if not isinstance(llm_result["depth"], dict):
        raise ValueError("depth must be a dict")

    missing_depth_keys = {"level1", "level2", "level3"} - llm_result["depth"].keys()
    if missing_depth_keys:
        missing = ", ".join(sorted(missing_depth_keys))
        raise ValueError(f"depth is missing required keys: {missing}")

    return dict(llm_result)


def _rag_concepts(rag_result: dict) -> set[str]:
    concepts = set()

    if not isinstance(rag_result, dict):
        return concepts

    matches = rag_result.get("matches", [])
    if not isinstance(matches, list):
        return concepts

    for match in matches:
        if not isinstance(match, dict):
            continue

        data = match.get("data", {})
        if not isinstance(data, dict):
            continue

        item_concepts = data.get("concepts", [])
        if not isinstance(item_concepts, list):
            continue

        concepts.update(str(concept).casefold() for concept in item_concepts)

    return concepts
