import sys
import types

from engine.input import input_structurer
from engine.problem_parser.llm_structurer import llm_structure, structure
from utils.json_extractor import extract_json


PROBLEM_TEXT = "부피가 일정할 때 온도가 상승하면 압력은 어떻게 되는가?"
EXPECTED = {
    "target_node": "temperature",
    "related_nodes": ["pressure"],
    "conditions": ["constant_volume"],
    "execution_type": "judgement",
}


def test_llm_structurer_falls_back_to_rule_based_structure(monkeypatch) -> None:
    def fail_llm(_text: str) -> dict:
        raise RuntimeError("llm unavailable")

    monkeypatch.setattr("engine.problem_parser.llm_structurer.llm_structure", fail_llm)

    assert structure(PROBLEM_TEXT) == EXPECTED


def test_llm_structurer_uses_deepseek_ollama_json(monkeypatch) -> None:
    fake_ollama = types.SimpleNamespace(
        chat=lambda model, messages: {"message": {"content": '{"target_node": "temperature", "related_nodes": ["pressure"], "conditions": ["constant_volume"], "execution_type": "judgement"}'}}
    )
    monkeypatch.setitem(sys.modules, "ollama", fake_ollama)

    assert llm_structure(PROBLEM_TEXT) == EXPECTED


def test_llm_structurer_falls_back_from_deepseek_to_llama3(monkeypatch) -> None:
    calls = []

    def fake_chat(model, messages):
        calls.append(model)
        if model == "deepseek-r1:32b":
            raise RuntimeError("deepseek unavailable")
        return {"message": {"content": '{"target_node": "temperature", "related_nodes": ["pressure"], "conditions": ["constant_volume"], "execution_type": "judgement"}'}}

    monkeypatch.setitem(sys.modules, "ollama", types.SimpleNamespace(chat=fake_chat))

    assert llm_structure(PROBLEM_TEXT) == EXPECTED
    assert calls == ["deepseek-r1:32b", "llama3"]


def test_json_extractor_parses_json_inside_explanatory_text() -> None:
    content = '다음과 같습니다:\n{"target_node": "temperature", "related_nodes": ["pressure"], "conditions": ["constant_volume"], "execution_type": "judgement"}'

    assert extract_json(content) == EXPECTED


def test_llm_structurer_parses_json_inside_explanatory_text(monkeypatch) -> None:
    fake_ollama = types.SimpleNamespace(
        chat=lambda model, messages: {"message": {"content": '다음과 같습니다:\n{"target_node": "temperature", "related_nodes": ["pressure"], "conditions": ["constant_volume"], "execution_type": "judgement"}'}}
    )
    monkeypatch.setitem(sys.modules, "ollama", fake_ollama)

    assert llm_structure(PROBLEM_TEXT) == EXPECTED


def test_image_input_extracts_text_then_structures(monkeypatch) -> None:
    monkeypatch.setattr(input_structurer, "extract_text_from_image", lambda _path: PROBLEM_TEXT)
    monkeypatch.setattr(input_structurer, "structure", lambda text: EXPECTED)

    assert input_structurer.structure_input("image", "problem.png") == EXPECTED


def test_pdf_input_extracts_text_then_structures(monkeypatch) -> None:
    monkeypatch.setattr(input_structurer, "extract_text_from_pdf", lambda _path: PROBLEM_TEXT)
    monkeypatch.setattr(input_structurer, "structure", lambda text: EXPECTED)

    assert input_structurer.structure_input("pdf", "problem.pdf") == EXPECTED
