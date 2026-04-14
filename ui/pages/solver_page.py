from engine.execution.run_dispatch import run
from engine.input.ocr_loader import extract_text_from_image
from engine.input.pdf_loader import extract_text_from_pdf
from engine.problem_parser.problem_structurer import structure


PLACEHOLDER = "-"


def render():
    import streamlit as st

    _left, center, _right = st.columns([1, 3, 1])
    with center:
        _render_content(st)


def _render_content(st):
    st.title("문제 풀이 엔진")

    st.subheader("입력")
    with st.form("solver_form"):
        text_input = st.text_area("문제 입력")
        submitted = st.form_submit_button("풀이 시작")

    uploaded = st.file_uploader("문제 업로드", type=["png", "jpg", "pdf"])

    text = text_input.strip() if submitted else ""
    if not text and uploaded:
        try:
            if uploaded.type == "application/pdf":
                text = extract_text_from_pdf(uploaded)
            else:
                st.image(uploaded)
                text = extract_text_from_image(uploaded)
        except Exception as exc:
            st.error("문제 추출 중 오류 발생")
            st.write(str(exc))

    if not text:
        return

    st.subheader("추출된 텍스트")
    st.text(text)

    try:
        with st.spinner("문제 분석 중..."):
            structured = structure(text)
    except Exception as exc:
        st.warning("아직 이 유형의 문제는 지원하지 않습니다.")
        st.write(str(exc))
        st.info("현재는 물리 개념/인과관계 중심 문제를 우선 지원합니다.")
        st.stop()

    st.subheader("1. 문제 해석")
    st.write("분석 완료")

    if not structured.get("target_node"):
        st.warning("아직 이 유형의 문제는 지원하지 않습니다.")
        st.info("현재는 물리 개념/인과관계 중심 문제를 우선 지원합니다.")
        st.stop()

    if not structured.get("execution_type"):
        st.warning("아직 이 유형의 문제는 지원하지 않습니다.")
        st.info("현재는 물리 개념/인과관계 중심 문제를 우선 지원합니다.")
        st.stop()

    try:
        with st.spinner("풀이 생성 중..."):
            result = run(structured)
    except Exception as exc:
        st.error("풀이 중 오류 발생")
        st.write(str(exc))
        return

    validation = _safe_dict(result.get("validation"))
    depth = _safe_dict(result.get("depth"))
    concepts = _safe_list(result.get("concepts"))
    concept_chain = _safe_list(result.get("concept_chain"))
    steps = _safe_list(result.get("steps"))
    issues = _safe_list(validation.get("issues"))
    related_lecture_materials = _safe_list(result.get("related_lecture_materials"))
    answer = result.get("answer")
    unit = result.get("unit") or ""
    confidence = validation.get("confidence", 0.0)

    st.subheader("2. 개념 연결")
    st.write(concept_chain or PLACEHOLDER)

    st.subheader("3. 최종 강의")
    st.markdown("## 문제")
    st.write(_safe_text(result.get("question")))

    st.markdown("## 분류")
    st.write(f"과목: {_safe_text(result.get('subject'))}")
    st.write(f"주제: {_safe_text(result.get('topic'))}")
    st.write(f"개념: {concepts if concepts else PLACEHOLDER}")

    st.markdown("## 답")
    if answer is None or answer == "":
        st.write(PLACEHOLDER)
    elif unit:
        st.write(f"{answer} {unit}")
    else:
        st.write(answer)

    st.markdown("## 강의")
    st.markdown(_safe_text(result.get("explanation")))

    st.markdown("## 개념 사슬")
    st.write(concept_chain or PLACEHOLDER)

    st.markdown("## 개념 Depth")
    st.write(f"[Level 1] {_safe_text(depth.get('level1'))}")
    st.write(f"[Level 2] {_safe_text(depth.get('level2'))}")
    st.write(f"[Level 3] {_safe_text(depth.get('level3'))}")

    st.markdown("## 풀이 단계")
    if steps:
        for step in steps:
            st.write(f"- {step}")
    else:
        st.write(PLACEHOLDER)

    st.markdown("## 검증")
    st.write(f"Confidence: {confidence}")
    st.write(f"Issues: {issues if issues else PLACEHOLDER}")
    st.write(f"Fallback used: {bool(result.get('used_fallback', False))}")

    if related_lecture_materials:
        st.markdown("## 관련 강의 자료")
        for material in related_lecture_materials:
            material = _safe_dict(material)
            title = _safe_text(material.get("title"))
            summary = _safe_text(material.get("summary"))
            material_concepts = _safe_list(material.get("concepts"))
            st.write(f"**{title}**")
            st.write(summary)
            st.write(f"개념: {material_concepts if material_concepts else PLACEHOLDER}")

    with st.expander("상세 보기 (JSON)"):
        st.json(_stable_result_view(result))


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


def _safe_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _safe_text(value):
    if value is None or value == "":
        return PLACEHOLDER
    return str(value)


def _stable_result_view(result):
    validation = _safe_dict(result.get("validation"))
    depth = _safe_dict(result.get("depth"))
    return {
        "question": result.get("question") or "",
        "subject": result.get("subject") or "",
        "topic": result.get("topic") or "",
        "answer": result.get("answer"),
        "unit": result.get("unit") or "",
        "steps": _safe_list(result.get("steps")),
        "concept_chain": _safe_list(result.get("concept_chain")),
        "depth": {
            "level1": depth.get("level1") or "",
            "level2": depth.get("level2") or "",
            "level3": depth.get("level3") or "",
        },
        "explanation": result.get("explanation") or "",
        "validation": {
            "confidence": validation.get("confidence", 0.0),
            "issues": _safe_list(validation.get("issues")),
        },
        "related_lecture_materials": _safe_list(result.get("related_lecture_materials")),
        "used_fallback": bool(result.get("used_fallback", False)),
    }
