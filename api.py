import json
import os
import shutil
from uuid import uuid4
from pathlib import Path

import requests
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from engine.ingestion.run_pdf_to_exam_json import run_pipeline as run_exam_pipeline


app = FastAPI()
UPLOAD_TMP_ROOT = Path("solve_tmp")


@app.post("/solve")
def solve(
    file: UploadFile = File(...),
    module: str = "exam",
    exam_name: str = "",
    subject: str = "",
    round: str = "",
) -> dict:
    """Run exam ingestion from an uploaded PDF/image file."""

    suffix = Path(file.filename or "").suffix
    temp_dir: Path | None = None

    try:
        UPLOAD_TMP_ROOT.mkdir(parents=True, exist_ok=True)
        temp_dir = UPLOAD_TMP_ROOT / f"exam_solve_{uuid4().hex}"
        temp_dir.mkdir()

        input_path = temp_dir / f"upload{suffix}"
        output_path = temp_dir / "exam.json"

        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        payload = run_exam_pipeline(
            input_path=str(input_path),
            output_path=str(output_path),
            module=module,
            exam_name=exam_name,
            subject=subject,
            round=round,
        )
        return _apply_visual_llm_policy(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if temp_dir is not None:
            shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/")
def index() -> FileResponse:
    return FileResponse("ui_mock/index.html")


def _apply_visual_llm_policy(payload: dict) -> dict:
    for problem in payload.get("problems", []):
        if problem.get("visual_required") is True:
            problem["solve_status"] = "llm_visual_solved"
            problem["visual_solution"] = _solve_visual_problem_with_llm(problem)
            problem["concept_nodes"] = _extract_concept_nodes(problem)
            problem.pop("explanation", None)
            problem["warning"] = "AI interpreted visual problem"
    return payload


def _solve_visual_problem_with_llm(problem: dict) -> dict:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    request_body = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Solve this visual-required exam problem in Korean. Return only "
                            "valid JSON. Do not wrap the JSON in markdown. The JSON object must "
                            "have exactly these keys: interpretation, formula, steps, answer. "
                            "interpretation must be a short Korean summary. formula must be a "
                            "plain text formula or an empty string. steps must be an array of "
                            "short Korean strings with only core calculation steps. answer must "
                            "be the final value only. Do not include an explanation field or any "
                            "other fields. Never use LaTeX or math markup: do not use \\frac, "
                            "\\times, \\sum, superscript syntax, subscript syntax, display "
                            "equations, or markdown math. Use plain text formulas only, for "
                            "example: W = (P2 - P1)(V2 - V1) / 2.\n\n"
                            f"{json.dumps(problem, ensure_ascii=False)}"
                        ),
                    }
                ],
            }
        ],
    }

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
    output_text = _extract_openai_output_text(response_body)
    try:
        visual_solution = json.loads(_extract_json_object(output_text))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"OpenAI visual solution was not valid JSON: {output_text}") from exc

    return _validate_visual_solution(visual_solution)


def _extract_openai_output_text(response_body: dict) -> str:
    if isinstance(response_body.get("output_text"), str):
        return response_body["output_text"].strip()

    texts = []
    for output_item in response_body.get("output", []):
        for content_item in output_item.get("content", []):
            if content_item.get("type") == "output_text":
                texts.append(content_item.get("text", ""))

    output_text = "".join(texts).strip()
    if not output_text:
        raise RuntimeError("OpenAI response did not include output text.")
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
        raise RuntimeError(f"OpenAI visual solution did not include a JSON object: {text}")
    return stripped[start : end + 1]


def _validate_visual_solution(value: dict) -> dict:
    if not isinstance(value, dict):
        raise RuntimeError("OpenAI visual solution must be a JSON object.")

    allowed_keys = {"interpretation", "formula", "steps", "answer"}
    extra_keys = set(value) - allowed_keys
    missing_keys = allowed_keys - set(value)
    if extra_keys or missing_keys:
        raise RuntimeError(
            "OpenAI visual solution keys must be exactly: interpretation, formula, steps, answer."
        )

    if not isinstance(value["steps"], list):
        raise RuntimeError("OpenAI visual solution steps must be an array.")

    return {
        "interpretation": str(value["interpretation"]),
        "formula": str(value["formula"]),
        "steps": [str(step) for step in value["steps"]],
        "answer": str(value["answer"]),
    }


CONCEPT_NODE_RULES = [
    {
        "node_key": "pressure",
        "label": "압력",
        "keywords": ["pressure", "압력", "p1", "p2", " kpa", "pa"],
    },
    {
        "node_key": "volume",
        "label": "부피",
        "keywords": ["volume", "부피", "체적", "v1", "v2", " m3", "m^3"],
    },
    {
        "node_key": "work",
        "label": "일",
        "keywords": ["work", "일", "w =", "경계일", "면적", "area under"],
    },
    {
        "node_key": "area",
        "label": "면적",
        "keywords": ["area", "면적", "삼각형", "사각형", "그래프 면적"],
    },
    {
        "node_key": "temperature",
        "label": "온도",
        "keywords": ["temperature", "온도", "t1", "t2", "delta t"],
    },
    {
        "node_key": "heat",
        "label": "열",
        "keywords": ["heat", "열", "q =", "열량"],
    },
    {
        "node_key": "energy",
        "label": "에너지",
        "keywords": ["energy", "에너지", "내부에너지"],
    },
    {
        "node_key": "efficiency",
        "label": "효율",
        "keywords": ["efficiency", "효율", "cop", "성능계수"],
    },
    {
        "node_key": "power",
        "label": "동력",
        "keywords": ["power", "동력", "kw", "watt"],
    },
    {
        "node_key": "force",
        "label": "힘",
        "keywords": ["force", "힘", "f ="],
    },
]


def _extract_concept_nodes(problem: dict) -> list[dict]:
    visual_solution = problem.get("visual_solution") or {}
    steps = visual_solution.get("steps") if isinstance(visual_solution, dict) else []
    if not isinstance(steps, list):
        steps = []

    weighted_texts = [
        (str(visual_solution.get("formula", "")), 0.9),
        (" ".join(str(step) for step in steps), 0.84),
        (str(visual_solution.get("interpretation", "")), 0.82),
        (str(problem.get("question", "")), 0.78),
        (" ".join(str(tag) for tag in problem.get("tags", [])), 0.76),
        (str(problem.get("topic", "")), 0.74),
        (str(problem.get("minor_subject", "")), 0.72),
    ]

    matches: dict[str, dict] = {}
    for rule in CONCEPT_NODE_RULES:
        for text, confidence in weighted_texts:
            normalized_text = f" {text.casefold()} "
            if any(keyword.casefold() in normalized_text for keyword in rule["keywords"]):
                existing = matches.get(rule["node_key"])
                if existing is None or confidence > existing["confidence"]:
                    matches[rule["node_key"]] = {
                        "node_key": rule["node_key"],
                        "label": rule["label"],
                        "source": "visual_solution_extractor",
                        "confidence": confidence,
                    }

    return sorted(matches.values(), key=lambda item: (-item["confidence"], item["node_key"]))
