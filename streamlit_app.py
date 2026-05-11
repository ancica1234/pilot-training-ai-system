import os
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph.graph import graph
from data.mock_data import MOCK_STUDENT_HISTORY, MOCK_SCHEDULES
from agents.instructor_notification import NOTIFICATION_LOG

st.set_page_config(page_title="Aviation Training Multi-Agent System", page_icon="✈️", layout="wide")

EXAMPLE_QUERIES = [
    "Evaluate John Smith's training progress and assess his risk level.",
    "Compare risk levels for all students in class 25-4.",
    "Build a remediation plan for John Smith, assess his risk, then notify his instructor.",
    "Give me a full status report on class 25-5 and alert the instructor about any high-risk students.",
]

if "thread_id" not in st.session_state:
    st.session_state.thread_id = "streamlit-1"
if "awaiting_approval" not in st.session_state:
    st.session_state.awaiting_approval = False
if "steps" not in st.session_state:
    st.session_state.steps = []

AGENT_ICONS = {
    "scheduler":               "📅",
    "evaluator":               "📊",
    "remediation":             "🔧",
    "risk_assessment":         "⚠️",
    "instructor_notification": "📨",
}

AGENT_PREFIXES = {
    "Schedule lookup:":          "scheduler",
    "Evaluation for":            "evaluator",
    "Remediation plan for":      "remediation",
    "Risk assessment for":       "risk_assessment",
    "Class risk comparison for": "risk_assessment",
    "Instructor notified:":      "instructor_notification",
}

def extract_steps(messages):
    steps = []
    for m in messages:
        if not isinstance(m, AIMessage) or not m.content:
            continue
        for prefix, agent in AGENT_PREFIXES.items():
            if m.content.startswith(prefix):
                steps.append({"agent": agent, "output": m.content})
                break
    return steps

def run_query(query: str):
    import uuid
    st.session_state.thread_id = str(uuid.uuid4())[:8]
    st.session_state.steps = []
    st.session_state.awaiting_approval = False
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    inputs = {"messages": [HumanMessage(content=query)]}
    with st.spinner("Running agents..."):
        try:
            for _ in graph.stream(inputs, config=config, stream_mode="values", recursion_limit=25):
                pass
        except Exception as e:
            st.error(f"Error: {e}")
            return
    state = graph.get_state(config)
    st.session_state.steps = extract_steps(state.values.get("messages", []))
    if state.next and "instructor_notification" in state.next:
        st.session_state.awaiting_approval = True

def approve_notification(approved: bool):
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    if approved:
        with st.spinner("Sending notification..."):
            try:
                for _ in graph.stream(None, config=config, stream_mode="values", recursion_limit=10):
                    pass
            except Exception as e:
                st.error(f"Error: {e}")
                return
        state = graph.get_state(config)
        st.session_state.steps = extract_steps(state.values.get("messages", []))
    st.session_state.awaiting_approval = False

# ── UI ─────────────────────────────────────────────────────────────────────────
st.title("✈️ Aviation Training Multi-Agent System")
st.caption("LangGraph · Groq LLaMA 3.3 · FastAPI · LangSmith")

tab1, tab2, tab3 = st.tabs(["🤖 Agent Query", "👨‍✈️ Students", "📋 Notifications"])

with tab1:
    st.subheader("Ask the Multi-Agent System")
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Enter your query:", placeholder="e.g. Evaluate John Smith's training progress")
    with col2:
        st.write("")
        st.write("")
        run_btn = st.button("▶ Run", type="primary", use_container_width=True)

    st.write("**Or pick an example:**")
    cols = st.columns(2)
    for i, q in enumerate(EXAMPLE_QUERIES):
        if cols[i % 2].button(f"Query {i+1}", key=f"ex_{i}", use_container_width=True):
            run_query(q)
            st.rerun()

    if run_btn and query:
        run_query(query)
        st.rerun()

    if st.session_state.awaiting_approval:
        st.warning("⚠️ The system wants to send instructor notifications. Approve?")
        c1, c2 = st.columns(2)
        if c1.button("✅ Approve", type="primary", use_container_width=True):
            approve_notification(True)
            st.rerun()
        if c2.button("❌ Reject", use_container_width=True):
            approve_notification(False)
            st.rerun()

    if st.session_state.steps:
        st.divider()
        st.subheader("Agent Execution")
        for step in st.session_state.steps:
            icon = AGENT_ICONS.get(step["agent"], "🤖")
            with st.expander(f"{icon} {step['agent'].replace('_', ' ').title()}", expanded=True):
                st.write(step["output"])

with tab2:
    st.subheader("Student Status")
    for class_name in sorted(MOCK_SCHEDULES.keys()):
        st.markdown(f"### Class {class_name}")
        students = [(n, d) for n, d in MOCK_STUDENT_HISTORY.items() if d["className"] == class_name]
        for name, data in sorted(students, key=lambda x: -x[1]["workdaysBehind"]):
            behind = data["workdaysBehind"]
            status = "🔴 BEHIND" if behind > 3 else "🟡 BEHIND" if behind > 0 else "🟢 ON TRACK"
            incomplete = len(data["incompleteEvents"])
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            col1.write(f"**{name}**")
            col2.write(status)
            col3.write(f"{behind} days behind")
            col4.write(f"{incomplete} events pending")
        st.divider()

with tab3:
    st.subheader("Notification Log")
    if not NOTIFICATION_LOG:
        st.info("No notifications sent this session.")
    else:
        for n in reversed(NOTIFICATION_LOG):
            alert = n["alert_type"]
            color = "🔴" if alert == "HIGH_RISK" else "🟡"
            with st.expander(f"{color} {n['student_name']} — {alert} — {n['timestamp']}"):
                st.write(f"**To:** {n['instructor']} ({n['email']})")
                st.write(f"**Class:** {n['class_name']}")
                st.write(f"**Message:** {n['message'][:300]}")