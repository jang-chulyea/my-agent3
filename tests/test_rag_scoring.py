import json

from core import rag_retriever


def test_rag_scoring_ranks_more_relevant_items_first(monkeypatch, tmp_path) -> None:
    data_dir = tmp_path / "data" / "exams" / "json"
    data_dir.mkdir(parents=True)

    (data_dir / "high_relevance.json").write_text(
        json.dumps(
            {
                "id": "high",
                "subject": "physics",
                "topic": "gas_pressure",
                "question": "At constant volume, temperature increases gas pressure.",
                "concepts": ["temperature", "pressure", "constant_volume"],
            }
        ),
        encoding="utf-8",
    )
    (data_dir / "medium_relevance.json").write_text(
        json.dumps(
            {
                "id": "medium",
                "subject": "physics",
                "topic": "gas_pressure",
                "question": "Pressure can be calculated from force and area.",
                "concepts": ["pressure"],
            }
        ),
        encoding="utf-8",
    )
    (data_dir / "low_relevance.json").write_text(
        json.dumps(
            {
                "id": "low",
                "subject": "biology",
                "topic": "cells",
                "question": "Cells contain organelles.",
                "concepts": ["cell"],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(rag_retriever, "SEARCH_ROOTS", [data_dir])

    result = rag_retriever.retrieve_context(
        query="temperature pressure constant volume",
        subject="physics",
        topic="gas_pressure",
        concepts=["temperature", "pressure", "constant_volume"],
    )

    ranked_ids = [match["data"]["id"] for match in result["matches"]]

    assert ranked_ids == ["high", "medium"]
    assert result["matches"][0]["score"] > result["matches"][1]["score"]
    assert all(match["score"] >= 2 for match in result["matches"])
