from core.llm_validator import validate_llm_output


def _valid_llm_output() -> dict:
    return {
        "answer": "Pressure increases.",
        "unit": None,
        "steps": ["Identify constant volume.", "Apply the pressure-temperature relationship."],
        "concept_chain": ["temperature", "pressure"],
        "depth": {
            "level1": "Temperature changes.",
            "level2": "Volume is fixed.",
            "level3": "Pressure increases.",
        },
    }


def _rag_result() -> dict:
    return {
        "query": "temperature pressure",
        "matches": [
            {
                "source": "sample",
                "score": 10.0,
                "data": {
                    "concepts": ["temperature", "pressure", "constant_volume"],
                },
            }
        ],
    }


def test_validate_llm_output_accepts_valid_output() -> None:
    result = validate_llm_output(_valid_llm_output(), _rag_result())

    assert result["valid"] is True
    assert result["confidence"] == 1.0
    assert result["issues"] == []
    assert result["validated_output"]["answer"] == "Pressure increases."


def test_validate_llm_output_reports_missing_fields() -> None:
    result = validate_llm_output({"answer": "Pressure increases."}, _rag_result())

    assert result["valid"] is False
    assert result["confidence"] == 0.0
    assert result["issues"]
    assert result["validated_output"] == {}


def test_validate_llm_output_marks_hallucinated_concepts_low_confidence() -> None:
    llm_output = _valid_llm_output()
    llm_output["concept_chain"] = ["temperature", "entropy"]

    result = validate_llm_output(llm_output, _rag_result())

    assert result["valid"] is True
    assert result["confidence"] < 1.0
    assert any("low_confidence" in issue for issue in result["issues"])
    assert any("entropy" in issue for issue in result["issues"])


def test_validate_llm_output_reports_empty_steps() -> None:
    llm_output = _valid_llm_output()
    llm_output["steps"] = []

    result = validate_llm_output(llm_output, _rag_result())

    assert result["valid"] is False
    assert result["confidence"] == 0.0
    assert result["issues"]
    assert result["validated_output"] == {}
