import sys
import logging
from typing import Any

from chain_builder import ChainBuilder
from engine.execution.dispatcher import dispatch_target_node
from engine.execution.handlers import run_execution_handler
from engine.problem_parser.execution_intent_selector import select_execution_intent
from engine.problem_parser.node_mapping_entry import parse_problem_text
from engine.problem_parser.problem_structurer import structure_problem_text
from relation_resolver import RelationResolver


logger = logging.getLogger(__name__)


def build_chain_explanation(chain: list[str]) -> str | None:
    if not chain:
        return None

    text = "이 문제는 다음 개념 흐름으로 이해된다.\n"
    for c in chain:
        text += f"{c}\n"
    text += "즉, 개념들이 연결되어 결과가 결정된다."
    return text


def build_problem_interpretation(structured: dict) -> str:
    return f"이 문제는 '{structured.get('target_node')}' 개념을 중심으로 해석된다."


def build_solution_process(chain: list[str], execution_type: str) -> str:
    if execution_type == "calculation":
        return "주어진 값을 이용하여 계산을 수행한다."
    if execution_type == "judgement":
        return "조건을 기반으로 변화 방향을 판단한다."
    return "개념을 기반으로 설명을 구성한다."


def build_conclusion(chain: list[str]) -> str | None:
    if not chain:
        return None
    return f"따라서 최종적으로 '{chain[-1]}'의 결과에 도달한다."


def attach_chain_explanation_to_lecture(lecture_text: str, chain_text: str) -> str:
    formula_section = "\n\n[공식]"
    chain_section = f"\n\n[개념 연결 설명]\n{chain_text}"
    if formula_section in lecture_text:
        return lecture_text.replace(formula_section, chain_section + formula_section, 1)
    return lecture_text + chain_section


def attach_concept_chain(
    final_output: dict,
    target_node: str,
    related_nodes: list[str],
    context: dict | None = None,
) -> dict:
    resolver = RelationResolver("data/relations.json")
    builder = ChainBuilder()
    relations = resolver.resolve(target_node, related_nodes, context=context)
    chain, reason = builder.build(relations)
    structured = {"target_node": target_node}
    execution_type = final_output.get("execution_type", "")
    chain_text = build_chain_explanation(chain)
    problem_interpretation = build_problem_interpretation(structured)
    solution_process = build_solution_process(chain, execution_type)
    conclusion = build_conclusion(chain)
    final_output["concept_chain"] = chain
    final_output["chain_reason"] = reason
    final_output["chain_explanation"] = chain_text
    explanation_bundle = final_output.setdefault("explanation_bundle", {})
    explanation_bundle["concept_chain"] = chain
    explanation_bundle["chain_reason"] = reason
    explanation_bundle["chain_explanation"] = chain_text
    explanation_bundle["problem_interpretation"] = problem_interpretation
    explanation_bundle["solution_process"] = solution_process
    explanation_bundle["conclusion"] = conclusion
    if chain_text and final_output.get("lecture_text"):
        final_output["lecture_text"] = attach_chain_explanation_to_lecture(
            final_output["lecture_text"],
            chain_text,
        )
    if reason and final_output.get("lecture_text"):
        final_output["lecture_text"] += "\n\n[추론 이유]\n" + reason
    lecture_parts = [
        "[문제 해석]",
        problem_interpretation,
        "[해결 과정]",
        solution_process,
    ]
    if chain_text:
        lecture_parts += ["[개념 연결 설명]", chain_text]
    if conclusion:
        lecture_parts += ["[결론]", conclusion]
    lecture_block = "\n".join(lecture_parts)
    if final_output.get("lecture_text"):
        final_output["lecture_text"] += "\n\n" + lecture_block
    else:
        final_output["lecture_text"] = lecture_block
    return final_output


def _safe_concepts(structured: dict) -> list[str] | None:
    concepts = structured.get("concepts")
    if concepts is None:
        return None
    if isinstance(concepts, list):
        return [str(concept) for concept in concepts if str(concept).strip()]
    return [str(concepts)]


def _normalize_rag_result(rag_result: Any, query: str) -> dict:
    if not isinstance(rag_result, dict):
        return {"query": query, "matches": []}

    matches = rag_result.get("matches")
    if not isinstance(matches, list):
        matches = []

    return {
        "query": rag_result.get("query") or query,
        "matches": matches,
    }


def _rag_has_matches(rag_result: dict) -> bool:
    return bool(rag_result.get("matches"))


def _validate_llm_result(llm_result: Any) -> dict:
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
        raise ValueError("llm_result steps must be a non-empty list")
    if not isinstance(llm_result["concept_chain"], list) or not llm_result["concept_chain"]:
        raise ValueError("llm_result concept_chain must be a non-empty list")
    if not isinstance(llm_result["depth"], dict):
        raise ValueError("llm_result depth must be a dict")

    missing_depth_keys = {"level1", "level2", "level3"} - llm_result["depth"].keys()
    if missing_depth_keys:
        missing = ", ".join(sorted(missing_depth_keys))
        raise ValueError(f"llm_result depth missing required keys: {missing}")

    return llm_result


def _run_engine_fallback(
    structured: dict,
    target_node: str,
    rag_result: dict | None = None,
    llm_result: Any = None,
    fallback_reason: str | None = None,
) -> dict:
    execution_type = structured.get("execution_type", "concept")
    intent_map = {
        "concept": "concept_explanation",
        "calculation": "calculation",
        "judgement": "judgement",
    }
    execution_path = dispatch_target_node(target_node, intent_map.get(execution_type, execution_type))
    final_output = run_execution_handler(execution_path, target_node)
    final_output["rag_result"] = rag_result or {
        "query": structured.get("question") or structured.get("target_node", ""),
        "matches": [],
    }
    final_output["llm_result"] = llm_result
    if fallback_reason:
        final_output["fallback_reason"] = fallback_reason
    return final_output


def _normalize_final_output(final_output: dict) -> dict:
    final_output.setdefault("rag_result", {"query": "", "matches": []})
    final_output.setdefault("llm_result", None)
    final_output.setdefault("answer", final_output.get("definition", ""))
    final_output.setdefault("unit", None)
    final_output.setdefault("steps", [])
    final_output.setdefault("depth", final_output.get("depth_info", {}))
    final_output.setdefault("concept_chain", [])
    final_output.setdefault("lecture_text", "")
    final_output.setdefault("explanation_bundle", {})
    return final_output


def run(structured: dict) -> dict:
    target_node = structured.get("target_node", "")
    related_nodes = structured.get("related_nodes", [])
    query = structured.get("question") or structured.get("target_node", "")
    rag_result = {"query": query, "matches": []}
    llm_result = None
    llm_checked = None
    fallback_result = None

    try:
        from core.output_formatter import format_final_output
        from core.llm_solver import solve_with_llm
        from core.llm_validator import validate_llm_output
        from core.rag_retriever import retrieve_context

        rag_result = _normalize_rag_result(
            retrieve_context(
                query=query,
                subject=structured.get("subject") or None,
                topic=structured.get("topic") or None,
                concepts=_safe_concepts(structured),
            ),
            query,
        )
        llm_payload = {"problem": structured}
        if _rag_has_matches(rag_result):
            llm_payload["context"] = rag_result

        llm_result = solve_with_llm(llm_payload)
        llm_checked = validate_llm_output(llm_result, rag_result)
        if not llm_checked["valid"] or llm_checked["confidence"] < 1.0:
            raise ValueError("; ".join(llm_checked["issues"]) or "LLM output failed validation")
        llm_result = llm_checked["validated_output"]

        logger.info("structured: %s", structured)
        logger.info("rag_result: %s", rag_result)
        logger.info("llm_result: %s", llm_result)
        print("structured:", structured)
        print("rag_result:", rag_result)
        print("llm_result:", llm_result)

        final_output = dict(llm_result)
        final_output["rag_result"] = rag_result
        final_output["llm_result"] = llm_result
        final_output["validation"] = llm_checked
        final_output.setdefault("execution_type", structured.get("execution_type", "llm"))
        final_output.setdefault("lecture_text", "\n".join(llm_result.get("steps", [])))
    except Exception as exc:
        from core.output_formatter import format_final_output

        logger.warning("RAG + LLM flow failed; falling back to engine: %s", exc)
        final_output = _run_engine_fallback(
            structured,
            target_node,
            rag_result=rag_result,
            llm_result=llm_result,
            fallback_reason=str(exc),
        )
        fallback_result = final_output

    final_output = attach_concept_chain(
        final_output,
        target_node,
        related_nodes,
        context={"conditions": structured.get("conditions", [])},
    )
    if fallback_result is not None:
        fallback_result = final_output
    return format_final_output(
        structured=structured,
        rag_result=rag_result,
        llm_result=llm_result if isinstance(llm_result, dict) else None,
        llm_checked=llm_checked,
        fallback_result=fallback_result,
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

    problem_text = " ".join(sys.argv[1:]).strip()
    if not problem_text:
        problem_text = input("problem_text: ").strip()

    parsed = parse_problem_text(problem_text)
    structured = structure_problem_text(problem_text)
    execution_intent = select_execution_intent(problem_text)
    execution_path = dispatch_target_node(parsed.target_node, execution_intent)
    final_output = run_execution_handler(execution_path, parsed.target_node, problem_text)
    final_output = attach_concept_chain(
        final_output,
        parsed.target_node,
        parsed.related_nodes,
        context={"conditions": structured.get("conditions", [])},
    )

    print("target_node:", parsed.target_node)
    print("related_nodes:", parsed.related_nodes)
    print("confidence:", parsed.confidence)
    print("execution_intent:", execution_intent)
    print("execution_path:", execution_path)
    print("definition:", final_output.get("definition", ""))
    if final_output.get("formula"):
        print("formula:", final_output.get("formula", ""))
    print("causal_relations:", final_output.get("causal_relations", []))
    print("final_output:", final_output)


if __name__ == "__main__":
    main()
