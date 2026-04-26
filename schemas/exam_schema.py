from typing import Any, Literal

from pydantic import BaseModel, Field


ReviewStatus = Literal[
    "auto",
    "manual_reviewed",
    "manual_or_llm_review",
    "low_confidence",
    "fallback_generated",
]

IngestionMode = Literal[
    "multimodal_llm",
    "selectable_text_fallback",
    "manual_text_assumption",
    "manual_input",
]


class ExamInfoSchema(BaseModel):
    source_file: str | None = None
    ingestion_mode: IngestionMode | None = None
    language: str | None = None
    version: str | None = None


class ExamProblemSchema(BaseModel):
    problem_id: str
    problem_no: int
    module: str
    major_subject: str
    minor_subject: str
    topic: str
    question: str
    choices: list[str]
    answer: str
    explanation: str
    tags: list[str]
    visual_required: bool
    review_status: ReviewStatus
    concept_nodes: list[str] = Field(default_factory=list)
    topic_id: str = ""
    importance: dict[str, Any] = Field(
        default_factory=lambda: {
            "score": 0.0,
            "frequency": 0,
            "difficulty": 0,
            "recency": 0,
        }
    )
    answer_choice: int | None = None
    source_page: int | None = None
    ingestion_mode: IngestionMode | None = None


class ExamPayloadSchema(BaseModel):
    exam_info: ExamInfoSchema
    problems: list[ExamProblemSchema]


# Backward-compatible alias for imports that still refer to ExamSchema.
ExamSchema = ExamPayloadSchema
