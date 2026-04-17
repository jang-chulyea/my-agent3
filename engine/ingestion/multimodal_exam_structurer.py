import base64
import json
import mimetypes
import os
from pathlib import Path
from typing import Any

import requests


def extract_problems_from_file(input_path: str, module: str) -> list[dict]:
    """Structure a PDF/image exam with a multimodal LLM.

    The provider integration is intentionally isolated in _call_multimodal_llm
    so the ingestion pipeline can switch providers without changing writer,
    validator, loader, or indexer code.
    """

    prompt = _build_prompt(module)
    raw_result = _call_multimodal_llm(input_path, prompt)
    raw_problems = _extract_raw_problems(raw_result)

    return [
        _normalize_llm_problem(raw_problem, index, module)
        for index, raw_problem in enumerate(raw_problems, start=1)
    ]


def _build_prompt(module: str) -> str:
    return (
        "Read the full input exam PDF/image as one complete exam round and return only valid JSON. "
        "Do not wrap the JSON in markdown. Return an object with a problems array. "
        "The input may contain 20 to 100 numbered problems. Preserve every detected problem in order. "
        "Do not skip problems. If a problem is partially unreadable, still include it with empty strings "
        "for uncertain fields and set review_status to low_confidence. "
        "Each problem must include problem_no, major_subject, minor_subject, topic, "
        "tags, question, choices, answer, explanation, visual_required, and review_status. "
        "Keep explanation brief and avoid free-form commentary. "
        "Use review_status only from: auto, manual_reviewed, manual_or_llm_review, "
        "low_confidence, fallback_generated. "
        f"Use module={module!r} unless a problem explicitly requires another module. "
        "Do not merge separate numbered problems. Do not treat circled choice "
        "numbers as problem starts. If an answer is uncertain, set review_status "
        "to low_confidence and explain the uncertainty."
    )


def _call_multimodal_llm(input_path: str, prompt: str) -> dict:
    """Provider boundary for OpenAI multimodal LLM calls.

    Tests can monkeypatch this function to return a dict shaped like:
    {"problems": [{...}, {...}]}. This implementation uses the Responses API
    over requests.
    """

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    model = "gpt-4.1-mini"
    path = Path(input_path)
    image_data_url = _build_image_data_url(path)
    extraction_prompt = (
        f"{prompt}\n\n"
        "Return JSON only. Do not include markdown fences, comments, or any text "
        "outside the JSON object. The JSON schema must be exactly:\n"
        "{\n"
        '  "problems": [\n'
        "    {\n"
        '      "problem_no": 1,\n'
        '      "question": "string",\n'
        '      "choices": ["string"],\n'
        '      "answer": "string",\n'
        '      "explanation": "string",\n'
        '      "tags": ["string"],\n'
        '      "visual_required": false,\n'
        '      "review_status": "manual_or_llm_review"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "Preserve all numbered problems from the source in the same order."
    )
    request_body = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": extraction_prompt,
                    },
                    {
                        "type": "input_image",
                        "image_url": image_data_url,
                    },
                ],
            }
        ],
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=request_body,
            timeout=120,
        )
        response.raise_for_status()
        response_body = response.json()
    except requests.exceptions.HTTPError as exc:
        response_text = exc.response.text if exc.response is not None else str(exc)
        raise RuntimeError(
            f"OpenAI Responses API request failed: HTTP "
            f"{exc.response.status_code if exc.response is not None else 'unknown'}: "
            f"{response_text}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"OpenAI Responses API request failed: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("OpenAI Responses API returned non-JSON response.") from exc

    output_text = _extract_openai_output_text(response_body)
    try:
        result = json.loads(_extract_json_object(output_text))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"OpenAI response did not contain valid JSON: {output_text}") from exc

    if not isinstance(result, dict) or "problems" not in result:
        raise RuntimeError("OpenAI response JSON must be an object with a problems field.")
    return result


def _encode_image_base64(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input image not found: {path}")

    mime_type = mimetypes.guess_type(path.name)[0] or ""
    if not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported image input type: {mime_type or 'unknown'}")

    return base64.b64encode(path.read_bytes()).decode("ascii")


def _build_image_data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime_type};base64,{_encode_image_base64(path)}"


def _extract_openai_output_text(response_body: dict) -> str:
    if isinstance(response_body.get("output_text"), str):
        return response_body["output_text"]

    texts = []
    for output_item in response_body.get("output", []):
        for content_item in output_item.get("content", []):
            if content_item.get("type") == "output_text":
                texts.append(content_item.get("text", ""))

    output_text = "".join(texts).strip()
    if not output_text:
        raise ValueError("OpenAI response did not include output text.")
    return output_text


def _extract_json_object(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError(f"OpenAI response did not contain a JSON object: {text}")

    return stripped[start : end + 1]


def _extract_raw_problems(raw_result: Any) -> list[dict]:
    if isinstance(raw_result, dict):
        raw_problems = raw_result.get("problems")
    elif isinstance(raw_result, list):
        raw_problems = raw_result
    else:
        raise ValueError("Multimodal result must be a dict or list.")

    if not isinstance(raw_problems, list):
        raise ValueError("Multimodal result must include a problems list.")

    if not raw_problems:
        raise ValueError("Multimodal result included no problems.")

    for raw_problem in raw_problems:
        if not isinstance(raw_problem, dict):
            raise ValueError("Each multimodal problem must be a dict.")
        if "problem_no" not in raw_problem:
            raise ValueError("Each multimodal problem must include problem_no.")

    return raw_problems


def _normalize_llm_problem(raw_problem: dict, index: int, module: str) -> dict:
    def normalize_token(value: Any) -> str:
        return (
            str(value or "")
            .strip()
            .lower()
            .replace("-", "_")
            .replace("/", "_")
            .replace(" ", "_")
        )

    def add_tag(value: str) -> None:
        if value and value not in normalized_tags:
            normalized_tags.append(value)

    tags = raw_problem.get("tags", [])
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    if not isinstance(tags, list):
        tags = []

    choices = raw_problem.get("choices", [])
    if not isinstance(choices, list):
        choices = []

    problem_no = raw_problem["problem_no"]
    module_value = str(raw_problem.get("module") or module or "exam")
    review_status = str(raw_problem.get("review_status") or "manual_or_llm_review")

    text_for_labels = " ".join(
        [
            str(raw_problem.get("major_subject", "")),
            str(raw_problem.get("minor_subject", "")),
            str(raw_problem.get("topic", "")),
            str(raw_problem.get("question", "")),
            " ".join(str(tag) for tag in tags),
        ]
    ).lower()

    major_subject = normalize_token(raw_problem.get("major_subject"))
    if "thermodynamic" in text_for_labels or "압력" in text_for_labels:
        major_subject = "thermodynamics"

    is_pv_diagram = any(
        marker in text_for_labels
        for marker in ("p_v", "pressure_volume", "pressure-volume", "graph", "diagram", "cylinder", "실린더", "그림")
    )
    is_constant_pressure = any(
        marker in text_for_labels
        for marker in ("constant_pressure", "constant pressure", "일정", "500kpa", "500 kpa")
    )

    if major_subject == "thermodynamics" and is_pv_diagram:
        minor_subject = "p_v_diagram_work"
        topic = "pressure_volume_work"
    elif major_subject == "thermodynamics" and is_constant_pressure:
        minor_subject = "closed_system_work"
        topic = "constant_pressure_boundary_work"
    else:
        minor_subject = normalize_token(raw_problem.get("minor_subject"))
        topic = normalize_token(raw_problem.get("topic"))

    normalized_tags = []
    tag_aliases = {
        "thermodynamics": "thermodynamics",
        "work": "boundary_work",
        "energy": "energy",
        "pressure": "pressure",
        "volume": "volume",
        "pressure_volume": "p_v_diagram",
        "pressure_volume_work": "p_v_diagram",
        "pressure_volume_": "p_v_diagram",
        "p_v_diagram": "p_v_diagram",
        "graph": "graph",
        "cylinder": "cylinder",
    }
    for tag in tags:
        normalized = normalize_token(tag)
        add_tag(tag_aliases.get(normalized, normalized))

    if major_subject == "thermodynamics":
        add_tag("thermodynamics")
    if minor_subject == "closed_system_work":
        add_tag("closed_system")
        add_tag("constant_pressure_process")
        add_tag("boundary_work")
        add_tag("expansion_work")
    elif minor_subject == "p_v_diagram_work":
        add_tag("p_v_diagram")
        add_tag("graph")
        add_tag("boundary_work")
        add_tag("expansion_work")
    if review_status == "low_confidence":
        add_tag("low_confidence")

    return {
        "problem_id": str(raw_problem.get("problem_id") or f"problem_{index:03d}"),
        "problem_no": problem_no,
        "module": module_value,
        "major_subject": major_subject,
        "minor_subject": minor_subject,
        "topic": topic,
        "tags": normalized_tags,
        "question": raw_problem.get("question", ""),
        "choices": choices,
        "answer": str(raw_problem.get("answer", "")),
        "explanation": raw_problem.get("explanation", ""),
        "visual_required": bool(raw_problem.get("visual_required", False)),
        "review_status": review_status,
    }
