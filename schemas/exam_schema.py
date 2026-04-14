from typing import Any, Literal

from pydantic import BaseModel


class ExamSchema(BaseModel):
    id: str
    subject: str
    topic: str
    question: str
    question_type: Literal["calculation", "concept", "judgement"]
    given: dict[str, Any]
    asked: str
    concepts: list[str]
