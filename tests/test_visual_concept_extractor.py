import api


def test_extract_concept_nodes_from_visual_solution() -> None:
    problem = {
        "question": "P-V graph work problem",
        "topic": "pressure_volume_work",
        "tags": ["p_v_diagram"],
        "visual_solution": {
            "interpretation": "P-V 그래프의 면적으로 일을 구합니다.",
            "formula": "W = (P2 - P1)(V2 - V1) / 2",
            "steps": ["압력 변화와 부피 변화를 확인합니다.", "그래프 면적을 계산합니다."],
            "answer": "3000 kJ",
        },
    }

    concept_nodes = api._extract_concept_nodes(problem)
    node_keys = {node["node_key"] for node in concept_nodes}

    assert {"pressure", "volume", "work", "area"}.issubset(node_keys)
    assert all(node["source"] == "visual_solution_extractor" for node in concept_nodes)
    assert all(isinstance(node["confidence"], float) for node in concept_nodes)


def test_visual_llm_policy_attaches_concept_nodes(monkeypatch) -> None:
    monkeypatch.setattr(
        api,
        "_solve_visual_problem_with_llm",
        lambda _problem: {
            "interpretation": "P-V 그래프의 면적으로 일을 구합니다.",
            "formula": "W = (P2 - P1)(V2 - V1) / 2",
            "steps": ["압력 변화와 부피 변화를 확인합니다."],
            "answer": "3000 kJ",
        },
    )

    payload = {
        "problems": [
            {
                "problem_id": "problem_001",
                "question": "P-V graph work problem",
                "tags": ["p_v_diagram"],
                "visual_required": True,
                "solve_status": "not_started",
                "explanation": "old explanation",
            }
        ]
    }

    result = api._apply_visual_llm_policy(payload)
    problem = result["problems"][0]

    assert problem["solve_status"] == "llm_visual_solved"
    assert "explanation" not in problem
    assert problem["visual_solution"]["answer"] == "3000 kJ"
    assert problem["concept_nodes"]
    assert {"node_key", "label", "source", "confidence"} <= set(problem["concept_nodes"][0])
