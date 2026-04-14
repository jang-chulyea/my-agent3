import json
import logging
from typing import Any

import ollama
from pydantic import ValidationError

from schemas.llm_output_schema import LLMOutputSchema


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "Return ONLY valid JSON. No explanation."
MAX_ATTEMPTS = 3


def solve_with_llm(structured_problem: dict) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Solve this structured problem and return JSON matching the "
                "required output schema:\n"
                f"{json.dumps(structured_problem, ensure_ascii=False)}"
            ),
        },
    ]

    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        response_text = _call_llm(messages)

        try:
            payload = json.loads(response_text)
        except json.JSONDecodeError as exc:
            last_error = exc
            logger.warning("invalid JSON from LLM on attempt %s: %s", attempt, exc)
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "The previous response was invalid JSON. "
                        f"JSON parsing error: {exc}. "
                        "Return ONLY valid JSON. No explanation."
                    ),
                }
            )
            continue

        try:
            validated_output = LLMOutputSchema.model_validate(payload)
        except ValidationError as exc:
            last_error = exc
            logger.warning("LLM output validation error on attempt %s: %s", attempt, exc)
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "The previous JSON did not match the required schema. "
                        f"Validation error: {exc}. "
                        "Return corrected JSON only."
                    ),
                }
            )
            continue

        return validated_output.model_dump()

    raise ValueError("LLM failed to return valid schema-compliant JSON") from last_error


def _call_llm(messages: list[dict[str, str]]) -> str:
    response: dict[str, Any] = ollama.chat(
        model="llama3",
        messages=messages,
    )
    return response["message"]["content"]
