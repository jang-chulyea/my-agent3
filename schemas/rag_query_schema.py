from typing import Any

from pydantic import BaseModel


class RAGQuerySchema(BaseModel):
    query: str
    filters: dict[str, Any]
