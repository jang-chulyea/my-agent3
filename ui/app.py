import streamlit as st

from engine.loader import (
    get_subject_problem_map,
    group_by_minor_subject,
    load_exam,
    list_minor_subjects,
)


EXAM_PATH = "data/exams/ac_refrigeration_engineer/2024_1/exam_2024_1.json"


def main():
    st.title("Exam Problems")

    lecture_tab, core_tab, exam_tab, solve_tab = st.tabs(["Lecture", "Core", "Exam", "Solve"])

    with lecture_tab:
        st.write("Lecture placeholder")

    with core_tab:
        st.write("Core placeholder")

    with exam_tab:
        problems = load_exam(EXAM_PATH)
        group_by_minor_subject(problems)
        subject_map = get_subject_problem_map()
        subjects = list_minor_subjects()

        if not subjects:
            st.write("No subjects found.")
            return

        selected_subject = st.selectbox("Subject", subjects)
        selected_problems = subject_map.get(selected_subject, [])

        st.write(f"Problem count: {len(selected_problems)}")
        for problem in selected_problems:
            st.write(f"{problem['problem_no']}. {problem['question']}")

    with solve_tab:
        st.write("Solve placeholder")


if __name__ == "__main__":
    main()
