import sys
import types

from core import rag_retriever
from engine.execution import run_dispatch
from engine.execution.run_dispatch import run


def test_rag_llm_pipeline_e2e_smoke(monkeypatch) -> None:
    def fake_solve_with_llm(payload: dict) -> dict:
        assert payload["problem"]["subject"] == "physics"
        assert payload["context"]["matches"]

        return {
            "answer": "Pressure increases.",
            "unit": None,
            "steps": [
                "Retrieve the constant-volume pressure and temperature context.",
                "Apply the direct relationship between temperature and pressure.",
            ],
            "concept_chain": [
                "temperature",
                "pressure",
            ],
            "depth": {
                "level1": "Temperature is increasing.",
                "level2": "Volume is constant.",
                "level3": "Pressure increases when temperature rises at constant volume.",
            },
        }

    fake_llm_solver = types.ModuleType("core.llm_solver")
    fake_llm_solver.solve_with_llm = fake_solve_with_llm
    monkeypatch.setitem(sys.modules, "core.llm_solver", fake_llm_solver)

    structured = {
        "question": "At constant volume, how does increasing temperature affect gas pressure?",
        "subject": "physics",
        "topic": "gas_pressure",
        "concepts": ["temperature", "pressure", "constant_volume"],
        "target_node": "temperature",
        "related_nodes": ["pressure", "volume"],
        "conditions": ["constant_volume"],
        "execution_type": "judgement",
    }

    result = run(structured)

    assert result
    assert "rag_result" in result
    assert result["rag_result"]["matches"]
    assert "llm_result" in result
    assert result["llm_result"]["answer"] == "Pressure increases."
    assert any(key in result for key in ("concept_chain", "explanation", "depth"))


def test_rag_llm_pipeline_continues_with_problem_only_when_rag_is_empty(monkeypatch) -> None:
    captured_payload = {}

    def fake_solve_with_llm(payload: dict) -> dict:
        captured_payload.update(payload)
        return {
            "answer": "Use the problem statement only.",
            "unit": None,
            "steps": ["No retrieved context was available.", "Solve from the structured problem."],
            "concept_chain": ["pressure"],
            "depth": {
                "level1": "Read the question.",
                "level2": "Identify the requested concept.",
                "level3": "Answer using known pressure behavior.",
            },
        }

    fake_llm_solver = types.ModuleType("core.llm_solver")
    fake_llm_solver.solve_with_llm = fake_solve_with_llm
    monkeypatch.setitem(sys.modules, "core.llm_solver", fake_llm_solver)
    monkeypatch.setattr(
        rag_retriever,
        "retrieve_context",
        lambda **_kwargs: {"query": "missing context", "matches": []},
    )

    structured = {
        "question": "A question with no matching local context.",
        "target_node": "pressure",
        "related_nodes": [],
        "execution_type": "concept",
    }

    result = run(structured)

    assert "context" not in captured_payload
    assert captured_payload["problem"] == structured
    assert result["rag_result"]["matches"] == []
    assert result["llm_result"]["answer"] == "Use the problem statement only."
    assert "lecture_text" in result


def test_invalid_mocked_llm_result_falls_back_to_engine(monkeypatch) -> None:
    def fake_solve_with_llm(_payload: dict) -> dict:
        return {"answer": "missing required schema fields"}

    fake_llm_solver = types.ModuleType("core.llm_solver")
    fake_llm_solver.solve_with_llm = fake_solve_with_llm
    monkeypatch.setitem(sys.modules, "core.llm_solver", fake_llm_solver)
    monkeypatch.setattr(
        rag_retriever,
        "retrieve_context",
        lambda **_kwargs: {"query": "pressure", "matches": [{"source": "sample", "score": 1.0, "data": {}}]},
    )

    result = run(
        {
            "question": "What is pressure?",
            "target_node": "pressure",
            "related_nodes": [],
            "execution_type": "concept",
        }
    )

    assert result["llm_result"] == {"answer": "missing required schema fields"}
    assert "fallback_reason" in result
    assert "llm_result missing required keys" in result["fallback_reason"]
    assert "lecture_text" in result
    assert any(key in result for key in ("concept_chain", "explanation", "depth"))


def test_fallback_path_is_triggered_when_llm_raises(monkeypatch) -> None:
    fallback_called = {"value": False}

    def fake_solve_with_llm(_payload: dict) -> dict:
        raise RuntimeError("LLM unavailable")

    def fake_run_execution_handler(_execution_path: str, target_node: str) -> dict:
        fallback_called["value"] = True
        return {
            "node": target_node,
            "execution_type": "lookup",
            "definition": "Fallback pressure explanation.",
            "formula": "",
            "causal_relations": [],
            "depth_info": {"intuition": "fallback depth"},
            "history_info": {},
            "explanation_bundle": {
                "core_concept": {
                    "definition": "Fallback pressure explanation.",
                    "formula": "",
                },
                "depth": {"intuition": "fallback depth"},
                "history": {},
            },
            "lecture_text": "Fallback pressure explanation.",
        }

    fake_llm_solver = types.ModuleType("core.llm_solver")
    fake_llm_solver.solve_with_llm = fake_solve_with_llm
    monkeypatch.setitem(sys.modules, "core.llm_solver", fake_llm_solver)
    monkeypatch.setattr(
        rag_retriever,
        "retrieve_context",
        lambda **_kwargs: {"query": "pressure", "matches": [{"source": "sample", "score": 1.0, "data": {}}]},
    )
    monkeypatch.setattr(run_dispatch, "run_execution_handler", fake_run_execution_handler)

    result = run(
        {
            "question": "What is pressure?",
            "target_node": "pressure",
            "related_nodes": [],
            "execution_type": "concept",
        }
    )

    assert fallback_called["value"] is True
    assert result["fallback_reason"] == "LLM unavailable"
    assert result["definition"] == "Fallback pressure explanation."
    assert "rag_result" in result
    assert "llm_result" in result
