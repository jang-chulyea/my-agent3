from typing import Any

from pydantic import BaseModel


class LectureMaterialSchema(BaseModel):
    id: str
    subject: str
    topic: str
    title: str
    concepts: list[str]
    summary: str
    lecture_text: str
    visual_hints: list[str]
    examples: list[dict[str, Any]]
    tags: list[str]
