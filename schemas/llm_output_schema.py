from typing import Any, Optional

from pydantic import BaseModel, field_validator


class LLMOutputSchema(BaseModel):
    answer: float | str
    unit: Optional[str]
    steps: list[str]
    concept_chain: list[str]
    depth: dict[str, Any]

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("steps must not be empty")
        return value

    @field_validator("concept_chain")
    @classmethod
    def validate_concept_chain(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("concept_chain must have at least 1 item")
        return value

    @field_validator("depth")
    @classmethod
    def validate_depth(cls, value: dict[str, Any]) -> dict[str, Any]:
        required_keys = {"level1", "level2", "level3"}
        missing_keys = required_keys - value.keys()
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise ValueError(f"depth is missing required keys: {missing}")
        return value
