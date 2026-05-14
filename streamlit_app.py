import os
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from graph.graph import graph
from data.mock_data import (MOCK_STUDENT_HISTORY, MOCK_SCHEDULES, MOCK_DAILY_STATUS,
    MOCK_FLIGHT_LINES, MOCK_ENVIRO_DATA, MOCK_GROUND_SCHOOL, MOCK_IP_HOTBOARD,
    MOCK_PERSONNEL, MOCK_SNIVS, MOCK_AIRCRAFT)
from agents.instructor_notification import NOTIFICATION_LOG

st.set_page_config(page_title="Aviation Training Multi-Agent System", page_icon="✈️", layout="wide")

EXAMPLE_QUERIES = [
    "Evaluate Tara Voss training progress and assess her risk level.",
    "Compare risk levels for all students in class 26-1.",
    "Build a remediation plan for Bram Okafor, assess his risk, then notify his instructor.",
    "Show me the flight whiteboard for 2026-04-06.",
    "Show me the ground school schedule and CSI availability for 2026-04-07.",
    "Show me the IP hotboard for 2026-04-06.",
    "Show me all SNIVs and check for double schedule conflicts on 2026-04-06.",
    "What is the aircraft status and enviro data for 2026-04-06?",
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
    "flight_scheduler":        "✈️",
    "ground_school":           "🎓",
    "ip_hotboard":             "📋",
    "sniv_tracker":            "🚫",
}

AGENT_PREFIXES = {
    "Schedule lookup:":          "scheduler",
    "Evaluation for":            "evaluator",
    "Remediation plan for":      "remediation",
    "Risk assessment for":       "risk_assessment",
    "Class risk comparison for": "risk_assessment",
    "Instructor notified:":      "instructor_notification",
    "Flight Schedule for":       "flight_scheduler",
    "Daily Whiteboard":          "flight_scheduler",
    "Aircraft Fleet Status":     "flight_scheduler",
    "Environment Data for":      "flight_scheduler",
    "Student Priority List":     "flight_scheduler",
    "Ground School Schedule for": "ground_school",
    "CSI Availability check":    "ground_school",
    "Ground School Week":        "ground_school",
    "IP Hotboard for":           "ip_hotboard",
    "Instructor availability for": "ip_hotboard",
    "Qualified IPs for":         "ip_hotboard",
    "SNIVs for":                 "sniv_tracker",
    "DOUBLE SCHEDULE":           "sniv_tracker",
    "Personnel Availability":    "sniv_tracker",
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

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🤖 Agent Query", "👷‍✈️ Students", "📋 Notifications", "✈️ Flight Schedule", "🎓 Ground School", "📋 IP Hotboard", "🚫 SNIVs"])

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
        label = q[:55] + "..." if len(q) > 55 else q
        if cols[i % 2].button(label, key=f"ex_{i}", use_container_width=True):
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
with tab4:
    st.subheader("Daily Flight Schedule")
    dates = sorted(MOCK_FLIGHT_LINES.keys())
    selected_date = st.selectbox("Select date", dates, key="flt_date")
    enviro = MOCK_ENVIRO_DATA.get(selected_date, {})
    if enviro:
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Sunset", enviro.get("sunset","—"))
        c2.metric("EENT", enviro.get("eent","—"))
        c3.metric("HLL", enviro.get("hll","—"))
        c4.metric("Highlight Window", enviro.get("highlight_window","—"))
        c5.metric("Flt Window", enviro.get("flt_window","—"))
    st.divider()
    status = MOCK_DAILY_STATUS.get(selected_date, {})
    if status:
        st.markdown("### Daily Status Board")
        STATUS_COLORS = {
            "ODO":             "#d4edda",
            "FCF":             "#f8d7da",
            "FLIGHT_EVENT":    "#fff3cd",
            "SIM_EVENT":       "#d1ecf1",
            "SNIVED":          "#ffe5b4",
            "DOUBLE_SCHEDULE": "#f8d7da",
            "MED_DOWN":        "#e8b4f8",
            "GRND_EVENT":      "#d8b4f8",
        }
        STATUS_LABELS = {
            "ODO": "ODO", "FCF": "FCF", "FLIGHT_EVENT": "FLIGHT EVENT",
            "SIM_EVENT": "SIM EVENT", "SNIVED": "SNIVED",
            "DOUBLE_SCHEDULE": "DOUBLE SCHEDULE", "MED_DOWN": "MED DOWN",
            "GRND_EVENT": "GRND EVENT",
        }
        for key, label in STATUS_LABELS.items():
            people = status.get(key, [])
            col_label, col_people = st.columns([2, 8])
            col_label.markdown(f"**{label}**")
            if people:
                tags = "".join(f'<span style="background:{STATUS_COLORS[key]};padding:2px 8px;margin:2px;border-radius:4px;font-size:0.85em">{p}</span>' for p in people)
                col_people.markdown(tags, unsafe_allow_html=True)
            else:
                col_people.markdown("—")
    st.divider()
    st.markdown("### Flight Lines")
    lines = MOCK_FLIGHT_LINES.get(selected_date, [])
    if lines:
        for line in lines:
            period_color = "🌅" if line["period"]=="AM" else ("🌆" if line["period"]=="PM" else "🌙")
            with st.expander(f"{period_color} MSN {line['msn']} — {line['event_type']} — {line['aircraft']} — Brief: {line['brief']}", expanded=True):
                c1,c2,c3,c4 = st.columns(4)
                c1.write(f"**IP:** {line.get('ip','TBD')}")
                c2.write(f"**Student:** {line.get('student','TBD')}")
                c3.write(f"**Takeoff:** {line.get('takeoff','TBD')}")
                c4.write(f"**Land:** {line.get('land','TBD')}")
                if line.get("notes"):
                    st.caption(line["notes"])
    else:
        st.info("No flight lines for this date.")

with tab5:
    st.subheader("Ground School Calendar")
    gs_dates = sorted(MOCK_GROUND_SCHOOL.keys())
    sel_gs_date = st.selectbox("Select date", gs_dates, key="gs_date")
    day = MOCK_GROUND_SCHOOL.get(sel_gs_date, {})
    if day:
        st.markdown(f"### Day {day['day_number']} — {sel_gs_date}")
        if day.get("holiday"):
            st.warning("HOLIDAY — no events scheduled")
        else:
            for ev in day["events"]:
                csi_badge = " 🔬 CSI REQUIRED" if ev["csi_required"] else ""
                agency_badge = " 🏢 OUTSIDE AGENCY" if ev["outside_agency"] else ""
                with st.expander(f"{ev['code']} — {ev['title']} @ {ev['start']}{csi_badge}{agency_badge}"):
                    st.write(f"**Duration:** {ev['duration_hrs']} hrs")
                    if ev["csi_required"]:
                        st.warning("Requires CSI present")
                    if ev["outside_agency"]:
                        st.info("Coordinated with outside agency")
            if day.get("notes"):
                st.caption(f"Note: {day['notes']}")
    else:
        st.info("No ground school data for this date.")

with tab6:
    st.subheader("IP Hotboard")
    hb_dates = sorted(MOCK_ENVIRO_DATA.keys())
    sel_hb_date = st.selectbox("Select date", hb_dates, key="hb_date")
    from data.mock_data import MOCK_SNIVS
    snived_today = {s["person"] for s in MOCK_SNIVS if s["date"] == sel_hb_date}
    med_down_today = {n for n, d in MOCK_PERSONNEL["Instructor"].items() if d.get("med_down")}
    blocked = snived_today | med_down_today
    available = [ip for ip in MOCK_IP_HOTBOARD if ip["name"] not in blocked]
    unavailable = [ip for ip in MOCK_IP_HOTBOARD if ip["name"] in blocked]
    available.sort(key=lambda x: x["flight_hours_ytd"])
    st.markdown("#### Available (ranked by least flight hours)")
    for rank, ip in enumerate(available, 1):
        idata = MOCK_PERSONNEL["Instructor"].get(ip["name"], {})
        c1,c2,c3,c4 = st.columns([1,3,2,2])
        c1.markdown(f"**#{rank}**")
        c2.write(f"{ip['name']} [{idata.get('type','?')}]")
        c3.metric("YTD Hours", f"{ip['flight_hours_ytd']}")
        c4.write(f"Last flew: {ip['last_flight']}")
    if unavailable:
        st.divider()
        st.markdown("#### Unavailable")
        for ip in unavailable:
            reason = "MED DOWN" if ip["name"] in med_down_today else "SNIVED"
            st.write(f"🚫 {ip['name']} — {ip['flight_hours_ytd']}hrs — {reason}")

with tab7:
    st.subheader("SNIV Tracker")
    sniv_dates = sorted(set(s["date"] for s in MOCK_SNIVS))
    all_dates = sorted(MOCK_ENVIRO_DATA.keys())
    sel_sniv_date = st.selectbox("Select date", all_dates, key="sniv_date")
    day_snivs = [s for s in MOCK_SNIVS if s["date"] == sel_sniv_date]
    st.markdown(f"#### SNIVs for {sel_sniv_date} ({len(day_snivs)} total)")
    if day_snivs:
        for s in day_snivs:
            st.warning(f"🚫 **{s['person']}** — {s['reason']} (source: {s['source']})")
    else:
        st.success("No SNIVs recorded for this date")
    st.divider()
    st.markdown("#### Personnel Availability Summary")
    snived_set = {s["person"] for s in MOCK_SNIVS if s["date"] == sel_sniv_date}
    for category in ["Instructor", "Student"]:
        st.markdown(f"**{category}s**")
        people = MOCK_PERSONNEL.get(category, {})
        for name, data in people.items():
            flags = []
            if name in snived_set: flags.append("SNIVED")
            if data.get("med_down"): flags.append("MED DOWN")
            if data.get("snived"): flags.append("SNIVED(sys)")
            if data.get("type") == "RESERVIST":
                drill = data.get("drill_days", [])
                flags.append("DRILL" if sel_sniv_date in drill else "NO-DRILL")
            is_unavailable = any(f in flags for f in ["SNIVED","SNIVED(sys)","MED DOWN"])                 or (data.get("type")=="RESERVIST" and "DRILL" not in flags)
            icon = "🔴" if is_unavailable else "🟢"
            flags_str = " | " + ", ".join(flags) if flags else ""
            st.write(f"{icon} {name} [{data.get('type','?')}]{flags_str}")
        st.write("")
