from engine.problem_parser.problem_structurer import structure_problem_text as rule_based_structure
from utils.json_extractor import extract_json


def llm_structure(text: str) -> dict:
    import ollama

    prompt = f"""
문제를 JSON으로 구조화:
- target_node
- related_nodes
- conditions
- execution_type

반드시 JSON만 출력.
설명, 문장, 코드블록 금지.

문제:
{text}
"""

    last_error = None
    for model in ["deepseek-r1:32b", "llama3"]:
        try:
            res = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
            )
            return extract_json(res["message"]["content"])
        except Exception as exc:
            last_error = exc

    raise last_error if last_error is not None else RuntimeError("ollama structuring failed")


def structure(text: str) -> dict:
    try:
        return llm_structure(text)
    except Exception:
        return rule_based_structure(text)
