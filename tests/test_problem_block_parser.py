from engine.ingestion.problem_block_parser import split_problem_blocks


def test_problem_block_parser_splits_real_exam_like_text() -> None:
    raw_text = """
1. 다음 중 열역학 제2법칙에 대한 설명으로 옳은 것은?
A) 보기 1
B) 보기 2
C) 보기 3
D) 보기 4

2. 냉동사이클에서 압축기의 역할로 옳은 것은?
A) 보기 1
B) 보기 2
C) 보기 3
D) 보기 4

3. 증발기의 역할에 대한 설명으로 옳은 것은?
A) 보기 1
B) 보기 2
C) 보기 3
D) 보기 4
"""

    blocks = split_problem_blocks(raw_text)

    assert len(blocks) == 3
    assert blocks[0].startswith("다음 중 열역학 제2법칙")
    assert blocks[1].startswith("냉동사이클에서 압축기")
    assert blocks[2].startswith("증발기의 역할")
    assert all("A) 보기 1" in block for block in blocks)


def test_problem_block_parser_splits_question_prefix_format() -> None:
    raw_text = """
Question 1. 공기조화 부하 계산에서 현열에 대한 설명으로 옳은 것은?
① 온도 변화와 관련된다
② 습도 변화와 관련된다
③ 압력 변화만 의미한다
④ 풍량과 무관하다

Question 2. 냉매의 응축 과정에 대한 설명으로 옳은 것은?
① 열을 방출한다
② 열을 흡수한다
③ 압축비가 0이 된다
④ 증발기에서만 발생한다
"""

    blocks = split_problem_blocks(raw_text)

    assert len(blocks) == 2
    assert blocks[0].startswith("공기조화 부하 계산")
    assert blocks[1].startswith("냉매의 응축 과정")
    assert "① 온도 변화와 관련된다" in blocks[0]
    assert "① 열을 방출한다" in blocks[1]


def test_problem_block_parser_splits_compact_number_parenthesis_format() -> None:
    raw_text = """1) 압축기 토출가스 온도가 높아지는 원인으로 옳은 것은?
가. 압축비 증가
나. 흡입압력 증가
다. 응축온도 감소
라. 냉매량 과다
2) 팽창밸브 통과 후 냉매 상태 변화로 옳은 것은?
가. 압력이 낮아진다
나. 온도가 항상 상승한다
다. 압력이 높아진다
라. 액체가 모두 기체가 된다
"""

    blocks = split_problem_blocks(raw_text)

    assert len(blocks) == 2
    assert blocks[0].startswith("압축기 토출가스")
    assert blocks[1].startswith("팽창밸브 통과 후")
    assert "가. 압축비 증가" in blocks[0]
    assert "가. 압력이 낮아진다" in blocks[1]

def test_problem_block_parser_splits_zero_padded_space_format() -> None:
    raw_text = """
01 first question text
A) 450 kJ
B) 350 kJ

02 second question text
A) 30 kJ
B) 200 kJ
"""

    blocks = split_problem_blocks(raw_text)

    assert len(blocks) == 2
    assert blocks[0].startswith("first question text")
    assert blocks[1].startswith("second question text")


def test_problem_block_parser_splits_number_dot_format() -> None:
    raw_text = """
1. first question text
A) 450 kJ
B) 350 kJ

2. second question text
A) 30 kJ
B) 200 kJ
"""

    blocks = split_problem_blocks(raw_text)

    assert len(blocks) == 2
    assert blocks[0].startswith("first question text")
    assert blocks[1].startswith("second question text")


def test_problem_block_parser_splits_number_parenthesis_format() -> None:
    raw_text = """
1) first question text
A) 450 kJ
B) 350 kJ

2) second question text
A) 30 kJ
B) 200 kJ
"""

    blocks = split_problem_blocks(raw_text)

    assert len(blocks) == 2
    assert blocks[0].startswith("first question text")
    assert blocks[1].startswith("second question text")


def test_problem_block_parser_splits_korean_prefix_format() -> None:
    raw_text = """
문제 01 first question text
A) 450 kJ
B) 350 kJ

문항 02 second question text
A) 30 kJ
B) 200 kJ
"""

    blocks = split_problem_blocks(raw_text)

    assert len(blocks) == 2
    assert blocks[0].startswith("first question text")
    assert blocks[1].startswith("second question text")


def test_problem_block_parser_does_not_split_circled_choice_numbers() -> None:
    raw_text = """
01 first question text
① 450 kJ
② 350 kJ
③ 250 kJ
④ 150 kJ

02 second question text
① 30 kJ
② 200 kJ
③ 3000 kJ
④ 6000 kJ
"""

    blocks = split_problem_blocks(raw_text)

    assert len(blocks) == 2
    assert "① 450 kJ" in blocks[0]
    assert "④ 6000 kJ" in blocks[1]
