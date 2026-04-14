from engine.loader import get_problems_by_tag, group_by_minor_subject, load_exam


EXAM_PATH = "data/exams/ac_refrigeration_engineer/2024_1/exam_2024_1.json"


def test_filtering_by_second_law_tag_returns_correct_problems() -> None:
    problems = load_exam(EXAM_PATH)
    group_by_minor_subject(problems)

    filtered = get_problems_by_tag("second_law")

    assert [problem["problem_id"] for problem in filtered] == ["2024_1_001"]
    assert all("second_law" in problem["tags"] for problem in filtered)
