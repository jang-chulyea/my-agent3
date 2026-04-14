import streamlit as st

from engine import get_node_ids, infer_subject_and_target, load_learning_bundle
from engine.registry import load_subject_ids


def render_bundle(bundle: dict) -> None:
    subject = bundle.get("subject", {})
    target_node = bundle.get("target_node", {})
    prerequisites = bundle.get("prerequisite_nodes", [])
    definition = target_node.get("definition", {})
    tags = target_node.get("tags", [])

    st.subheader("Subject")
    st.write(f"ID: {subject.get('subject_id', '')}")
    st.write(f"Title: {subject.get('title', '')}")

    st.subheader("Target Node")
    st.write(f"ID: {target_node.get('node_id', '')}")
    st.write(f"Title: {target_node.get('title', '')}")

    st.subheader("Definition")
    st.markdown(f"**Short**: {definition.get('short', '')}")
    st.markdown(f"**Full**: {definition.get('full', '')}")

    st.subheader("Prerequisites")
    if prerequisites:
        for node in prerequisites:
            st.write(f"- {node.get('title', '')} ({node.get('node_id', '')})")
    else:
        st.write("None")

    st.subheader("Knowledge Chain")
    render_chain(target_node, prerequisites, max_depth=3)

    st.subheader("Tags")
    if tags:
        st.write(", ".join(tags))
    else:
        st.write("None")

    if st.checkbox("Debug JSON"):
        st.json(bundle)


def render_chain(target_node: dict, prerequisite_nodes: list[dict], max_depth: int = 3) -> None:
    node_map = {node.get("node_id"): node for node in prerequisite_nodes}
    relation_map = {
        ("TD-00-FORCE", "TD-01-PRESSURE"): "힘이 증가하면 압력이 증가한다. (면적 일정)",
        ("TD-00-AREA", "TD-01-PRESSURE"): "면적이 증가하면 압력이 감소한다. (힘 일정)",
    }

    def walk(node: dict, depth: int) -> None:
        if not node or depth > max_depth:
            return

        prefix = "&nbsp;" * (depth * 8)
        connector = "|-- " if depth == 1 else "`-- "
        title = node.get("title", "")
        node_id = node.get("node_id", "")
        st.markdown(f"{prefix}{connector}{title} ({node_id})", unsafe_allow_html=True)

        source_node_id = node_id
        target_node_id = target_node.get("node_id", "")
        relation_text = relation_map.get((source_node_id, target_node_id))
        if relation_text is None:
            relation_text = relation_map.get((target_node_id, source_node_id), "relation missing")
        st.markdown(f"{prefix}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-> {relation_text}", unsafe_allow_html=True)
        st.markdown("<div style='height:0.35rem;'></div>", unsafe_allow_html=True)

        if depth >= max_depth:
            return

        for child_id in node.get("prerequisites", []):
            child_node = node_map.get(child_id)
            if child_node is not None:
                walk(child_node, depth + 1)
            else:
                child_prefix = "&nbsp;" * ((depth + 1) * 8)
                st.markdown(f"{child_prefix}`-- {child_id}", unsafe_allow_html=True)
                st.markdown(
                    f"{child_prefix}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-> relation missing",
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:0.35rem;'></div>", unsafe_allow_html=True)

    root_title = target_node.get("title", "")
    root_node_id = target_node.get("node_id", "")
    st.write(f"{root_title} ({root_node_id})")
    st.markdown("<div style='height:0.35rem;'></div>", unsafe_allow_html=True)

    for node in prerequisite_nodes:
        walk(node, 1)


def render() -> None:
    _left, center, _right = st.columns([1, 3, 1])
    with center:
        _render_content()


def _render_content() -> None:
    st.title("My_Agent 3.0")

    subject_ids = load_subject_ids()
    if "subject_id" not in st.session_state:
        st.session_state.subject_id = subject_ids[0]
    if "problem_input" not in st.session_state:
        st.session_state.problem_input = ""
    if "bundle" not in st.session_state:
        st.session_state.bundle = None

    st.text_area("Problem Input", key="problem_input")

    if st.button("Analyze Problem"):
        inferred = infer_subject_and_target(st.session_state.problem_input)
        if inferred is not None:
            inferred_subject_id, inferred_target_node_id = inferred
            st.session_state.subject_id = inferred_subject_id
            st.session_state.target_node_id = inferred_target_node_id
            try:
                st.session_state.bundle = load_learning_bundle(
                    inferred_subject_id,
                    inferred_target_node_id,
                )
            except Exception as exc:
                st.session_state.bundle = None
                st.error(str(exc))
        else:
            st.session_state.bundle = None
            st.error("Could not infer subject_id and target_node_id from the input.")

    subject_id = st.selectbox("Subject ID", subject_ids, key="subject_id")
    node_ids = get_node_ids(subject_id)
    if "target_node_id" not in st.session_state or st.session_state.target_node_id not in node_ids:
        st.session_state.target_node_id = node_ids[0]
    target_node_id = st.selectbox("Target Node ID", node_ids, key="target_node_id")

    if st.button("Load Bundle"):
        try:
            st.session_state.bundle = load_learning_bundle(subject_id, target_node_id)
        except Exception as exc:
            st.session_state.bundle = None
            st.error(str(exc))

    if st.session_state.bundle is not None:
        render_bundle(st.session_state.bundle)
