from core.output_formatter import format_final_output


def _structured() -> dict:
    return {
        "question": "What happens to pressure when temperature rises?",
        "question_type": "judgement",
        "subject": "physics",
        "topic": "gas_pressure",
        "concepts": ["temperature", "pressure"],
    }


def _rag_result() -> dict:
    return {
        "query": "pressure temperature",
        "matches": [{"source": "sample", "score": 10.0, "data": {}}],
    }


def _llm_result() -> dict:
    return {
        "answer": "Pressure increases.",
        "unit": None,
        "steps": ["Read the condition.", "Apply the concept."],
        "concept_chain": ["temperature", "pressure"],
        "depth": {
            "level1": "Temperature rises.",
            "level2": "Volume is fixed.",
            "level3": "Pressure increases.",
        },
    }


def _llm_checked() -> dict:
    return {
        "valid": True,
        "confidence": 1.0,
        "issues": [],
        "validated_output": _llm_result(),
    }


def test_format_final_output_valid_llm_path() -> None:
    output = format_final_output(
        structured=_structured(),
        rag_result=_rag_result(),
        llm_result=_llm_result(),
        llm_checked=_llm_checked(),
    )

    assert output["question"] == "What happens to pressure when temperature rises?"
    assert output["question_type"] == "judgement"
    assert output["subject"] == "physics"
    assert output["topic"] == "gas_pressure"
    assert output["concepts"] == ["temperature", "pressure"]
    assert output["rag_result"]["matches"]
    assert output["llm_result"]["answer"] == "Pressure increases."
    assert output["validation"]["valid"] is True
    assert output["concept_chain"] == ["temperature", "pressure"]
    assert output["depth"]["level3"] == "Pressure increases."
    assert output["steps"] == ["Read the condition.", "Apply the concept."]
    assert output["answer"] == "Pressure increases."
    assert output["unit"] == ""
    assert output["explanation"] == "Read the condition.\nApply the concept."
    assert output["related_lecture_materials"] == []
    assert output["used_fallback"] is False


def test_format_final_output_fallback_path() -> None:
    fallback_result = {
        "definition": "Fallback explanation.",
        "lecture_text": "Fallback lecture.",
        "concept_chain": ["temperature", "pressure"],
        "depth_info": {"intuition": "Intuition text."},
        "fallback_reason": "LLM unavailable",
    }

    output = format_final_output(
        structured=_structured(),
        rag_result=_rag_result(),
        llm_result=None,
        llm_checked=None,
        fallback_result=fallback_result,
    )

    assert output["used_fallback"] is True
    assert output["answer"] == "Fallback explanation."
    assert output["explanation"] == "Fallback lecture."
    assert output["concept_chain"] == ["temperature", "pressure"]
    assert output["depth"]["level1"] == "Intuition text."
    assert output["fallback_reason"] == "LLM unavailable"
    assert output["validation"]["valid"] is False


def test_format_final_output_empty_rag_path() -> None:
    output = format_final_output(
        structured=_structured(),
        rag_result=None,
        llm_result=_llm_result(),
        llm_checked=_llm_checked(),
    )

    assert output["rag_result"] == {"query": "", "matches": []}
    assert output["related_lecture_materials"] == []
    assert output["used_fallback"] is False


def test_format_final_output_missing_optional_fields() -> None:
    output = format_final_output(
        structured={},
        rag_result={"query": None, "matches": None},
        llm_result=None,
        llm_checked={"valid": False},
    )

    assert output["question"] == ""
    assert output["question_type"] == ""
    assert output["subject"] == ""
    assert output["topic"] == ""
    assert output["concepts"] == []
    assert output["rag_result"] == {"query": "", "matches": []}
    assert output["llm_result"] == {}
    assert output["validation"] == {"valid": False, "confidence": 0.0, "issues": []}
    assert output["concept_chain"] == []
    assert output["depth"] == {"level1": "", "level2": "", "level3": ""}
    assert output["steps"] == []
    assert output["answer"] is None
    assert output["unit"] == ""
    assert output["explanation"] == ""
    assert output["related_lecture_materials"] == []
    assert output["used_fallback"] is False


def test_format_final_output_adds_related_lecture_materials() -> None:
    rag_result = {
        "query": "pressure temperature",
        "matches": [
            {
                "source": "data/lecture_materials/sample_lecture_material_001.json",
                "source_type": "lecture_material",
                "score": 12.0,
                "data": {
                    "id": "sample_lecture_material_001",
                    "title": "Constant Volume Gas Pressure",
                    "summary": "Pressure rises with temperature at constant volume.",
                    "concepts": ["temperature", "pressure", "constant_volume"],
                    "lecture_text": "Internal text should not be copied into related material summary.",
                },
            },
            {
                "source": "data/lecture_materials/stronger.json",
                "source_type": "lecture_material",
                "score": 14.0,
                "data": {
                    "id": "stronger",
                    "title": "Stronger Match",
                    "summary": "A stronger lecture material match.",
                    "concepts": ["temperature"],
                },
            },
            {
                "source": "data/lecture_materials/weak.json",
                "source_type": "lecture_material",
                "score": 4.0,
                "data": {
                    "id": "weak",
                    "title": "Weak Match",
                    "summary": "This should be filtered by score.",
                    "concepts": ["temperature"],
                },
            },
            {
                "source": "data/lecture_materials/no_overlap.json",
                "source_type": "lecture_material",
                "score": 20.0,
                "data": {
                    "id": "no_overlap",
                    "title": "No Concept Overlap",
                    "summary": "This should be filtered by concept overlap.",
                    "concepts": ["entropy"],
                },
            },
            {
                "source": "data/exams/json/sample_exam_001.json",
                "source_type": "exam",
                "score": 10.0,
                "data": {"id": "sample_exam_001"},
            },
        ],
    }

    output = format_final_output(
        structured=_structured(),
        rag_result=rag_result,
        llm_result=_llm_result(),
        llm_checked=_llm_checked(),
    )

    assert output["related_lecture_materials"] == [
        {
            "id": "stronger",
            "title": "Stronger Match",
            "summary": "A stronger lecture material match.",
            "concepts": ["temperature"],
            "source": "data/lecture_materials/stronger.json",
            "score": 14.0,
        },
        {
            "id": "sample_lecture_material_001",
            "title": "Constant Volume Gas Pressure",
            "summary": "Pressure rises with temperature at constant volume.",
            "concepts": ["temperature", "pressure", "constant_volume"],
            "source": "data/lecture_materials/sample_lecture_material_001.json",
            "score": 12.0,
        }
    ]
