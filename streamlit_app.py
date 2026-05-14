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

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["🤖 Agent Query", "👷‍✈️ Students", "📋 Notifications", "✈️ Flight Schedule", "🎓 Ground School", "📋 IP Hotboard", "🚫 SNIVs", "❓ Help"])

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

with tab8:
    st.title("How to Use This System")
    st.markdown("""
    This system replaces multiple Excel spreadsheets and SharePoint trackers with a single
    AI-powered interface for aviation flight training scheduling and student management.
    """)

    with st.expander("🤖  Agent Query — Ask the AI anything", expanded=True):
        st.markdown("""
        **What it does:**
        Type a plain-English question and the system automatically routes it to the right
        specialist agents, runs the tools, and returns a structured answer.

        **How to use it:**
        - Type your question in the text box and click **Run**, or click one of the pre-built example buttons
        - The system will show which agents were called and what each one found
        - If the query involves sending an instructor alert, you will be asked to **Approve or Reject** before anything is sent

        **Example queries you can type:**
        | Query | Agents used |
        |---|---|
        | `Show me the flight whiteboard for 2026-04-06` | Flight Scheduler |
        | `Show me the IP hotboard for 2026-04-06` | IP Hotboard |
        | `Show me all SNIVs and check for double schedule conflicts on 2026-04-06` | SNIV Tracker |
        | `Show me the ground school schedule and CSI availability for 2026-04-07` | Ground School |
        | `What is the aircraft status and enviro data for 2026-04-06?` | Flight Scheduler |
        | `Evaluate Tara Voss training progress and assess her risk level` | Evaluator + Risk |
        | `Build a remediation plan for Bram Okafor and notify his instructor` | Remediation + Notification |
        | `Compare risk levels for all students in class 26-1` | Risk Assessment |

        **Tip:** Always include a date in YYYY-MM-DD format for flight/schedule queries.
        Available demo dates: 2026-04-06, 2026-04-07, 2026-04-08, 2026-04-13, 2026-04-20, 2026-04-27
        """)

    with st.expander("✈️  Flight Schedule Tab"):
        st.markdown("""
        **What it shows:**
        The daily operational picture — equivalent to the Weekly spreadsheet whiteboard.

        **How to use it:**
        1. Select a date from the dropdown
        2. The **Environmental Data bar** shows: Sunset time, EENT (End of Evening Nautical Twilight),
           HLL (High Light Level), Highlight Window, and Flight Window for that day
        3. The **Daily Status Board** shows every person colour-coded by their status:

        | Row | Meaning |
        |---|---|
        | **ODO** | Officer of the Day |
        | **FCF** | Functional Check Flight crew |
        | **FLIGHT EVENT** | Scheduled for a flight today |
        | **SIM EVENT** | Scheduled for simulator today |
        | **SNIVED** | Submitted unavailability — should NOT be scheduled |
        | **DOUBLE SCHEDULE** | Conflict: person is both SNIVED and on the flight schedule |
        | **MED DOWN** | Medically grounded — cannot fly |
        | **GRND EVENT** | Ground event only — no flight |

        4. The **Flight Lines** section shows each mission: mission number, period (AM/PM/EVE),
           brief time, event type (CAL/FAM/FCF), aircraft tail number, IP, and student

        **Tip:** CAL = Calibration flight, FAM = Familiarisation flight, FCF = Functional Check Flight
        """)

    with st.expander("🎓  Ground School Tab"):
        st.markdown("""
        **What it shows:**
        The daily ground school calendar — equivalent to the Excel-generated ground school spreadsheet.

        **How to use it:**
        1. Select a date from the dropdown
        2. Each event card shows: event code, title, start time, and duration
        3. Look for these badges:
           - **CSI REQUIRED** 🔬 — A Certified Simulator Instructor must be present for this event.
             If no CSI is available that day, the system will flag a warning in the Agent Query tab
           - **OUTSIDE AGENCY** 🏢 — This event involves an external organisation (e.g. Aeromed,
             Night Lab, Course Rules brief) and requires advance coordination

        **Tip:** Use the Agent Query tab with `check CSI availability for 2026-04-07` to
        automatically verify whether a qualified CSI is available before the duty day.
        """)

    with st.expander("📋  IP Hotboard Tab"):
        st.markdown("""
        **What it shows:**
        Instructors ranked from least to most Year-to-Date flight hours — this determines who
        should fly next. Replaces the broken IP Hotboard Product tab in the Excel spreadsheet.

        **How to use it:**
        1. Select a date from the dropdown
        2. **Available** instructors are ranked #1 (least hours) to last — the scheduler should
           assign the top-ranked available IP to the next flight
        3. **Unavailable** instructors are listed separately with their reason (SNIVED or MED DOWN)
        4. Instructor type is shown in brackets:
           - **ACTIVE** — Full-time staff instructor
           - **AF** — Air Force exchange instructor
           - **RESERVIST** — Part-time; only available on their drill days
           - **NON_PERM** — Non-permanent attached pilot

        **Tip:** Use the Agent Query tab with `show qualified IPs for CAL on 2026-04-06` to
        filter the hotboard to only instructors qualified for a specific event type.
        """)

    with st.expander("🚫  SNIVs Tab"):
        st.markdown("""
        **What it shows:**
        Unavailability requests (SNIVs) for a selected date, plus a full personnel availability
        summary. Replaces the manual copy-paste from MSharp into the Personnel Availability
        and SNIV tabs on the Weekly spreadsheet.

        **What is a SNIV?**
        A SNIV is a request by a person to **not be scheduled** on a given date. It is submitted
        in the scheduling system (MSharp) or entered manually. A person who is SNIVED should
        not appear on the flight schedule.

        **How to use it:**
        1. Select a date from the dropdown
        2. **SNIVs section** — lists everyone who has requested unavailability and why
        3. **Personnel Availability Summary** — shows every instructor and student with their status:
           - 🟢 **AVAILABLE** — cleared to be scheduled
           - 🔴 **UNAVAILABLE** — SNIVED, medically grounded, or (for reservists) not a drill day

        **Tip:** Use the Agent Query tab with
        `check for double schedule conflicts on 2026-04-06` to automatically detect anyone
        who is SNIVED but still appears on the flight schedule.
        """)

    with st.expander("👷‍✈️  Students Tab"):
        st.markdown("""
        **What it shows:**
        All students grouped by class, sorted from most days behind to on track.

        **Status indicators:**
        - 🔴 **BEHIND** — more than 3 workdays behind schedule
        - 🟡 **BEHIND** — 1–3 workdays behind schedule
        - 🟢 **ON TRACK** — no days behind

        **Student priority tiers** (relevant for flight scheduling priority):
        - **AF** — Air Force exchange student with a fixed departure deadline — highest priority
        - **REFRESH** — Refresher pilot returning to currency — high priority
        - **STANDARD** — Normal syllabus student
        """)

    with st.expander("📋  Notifications Tab"):
        st.markdown("""
        **What it shows:**
        A log of all instructor alerts sent during this session.

        Alerts are only sent after you explicitly **approve** them in the Agent Query tab.
        Each alert includes: instructor name, student name, class, alert type, timestamp, and message.

        **Alert types:**
        - **HIGH_RISK** — Student is at high risk of not completing training on time
        - **BEHIND_SCHEDULE** — Student is behind their syllabus schedule
        - **REMEDIATION_ASSIGNED** — A remediation plan has been created for the student
        - **ON_TRACK** — Positive status update
        """)

    st.divider()
    st.markdown("### Available Demo Data")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Classes:** 26-1, 26-2")
        st.markdown("**Students:** Tara Voss, Leon Marsh, Dana Quirke (class 26-1)")
        st.markdown("**Students:** Bram Okafor, Yuki Tanaka, Petra Holst (class 26-2)")
        st.markdown("**Instructors:** Gale Rynder, Otto Finch, Selma Varga, Noel Drax, Preet Aulakh, Bex Torrance")
    with col2:
        st.markdown("**Flight/Schedule dates:** 2026-04-06, 2026-04-07, 2026-04-08, 2026-04-13, 2026-04-20, 2026-04-27")
        st.markdown("**SNIVed on 2026-04-06:** Otto Finch (personal), Preet Aulakh (medical)")
        st.markdown("**Aircraft:** T-001 (CAL/FMC), T-002 (FAM/FMC), T-003 (CAL/FMC), T-004 (FAM/PMC), T-005 (CAL/NMC)")
        st.markdown("**Priority students:** Dana Quirke (AF/26-1), Bram Okafor (AF/26-2)")
with tab8:
    st.title("How to Use This System")
    st.markdown("This system replaces multiple Excel spreadsheets and SharePoint trackers with a single AI-powered interface for aviation flight training scheduling and student management.")

    with st.expander("Agent Query — Ask the AI anything", expanded=True):
        st.markdown("""**What it does:** Type a plain-English question and the system routes it to the right specialist agents.\n\n**How to use it:**\n- Type your question and click Run, or click an example button\n- The system shows which agents were called and what each found\n- If the query involves sending an instructor alert, you must Approve or Reject before anything is sent\n\n**Tip:** Always include a date in YYYY-MM-DD format for flight/schedule queries. Available demo dates: 2026-04-06, 2026-04-07, 2026-04-08, 2026-04-13, 2026-04-20, 2026-04-27""")

    with st.expander("Flight Schedule Tab"):
        st.markdown("""**What it shows:** The daily operational picture equivalent to the Weekly spreadsheet whiteboard.\n\n**How to use it:**\n1. Select a date from the dropdown\n2. The Environmental Data bar shows Sunset, EENT (End of Evening Nautical Twilight), HLL (High Light Level), Highlight Window, and Flight Window\n3. The Daily Status Board shows every person colour-coded by status:\n   - ODO: Officer of the Day\n   - FCF: Functional Check Flight crew\n   - FLIGHT EVENT: Scheduled for a flight today\n   - SIM EVENT: Scheduled for simulator today\n   - SNIVED: Submitted unavailability - should NOT be scheduled\n   - DOUBLE SCHEDULE: Conflict - person is SNIVED but still on the flight schedule\n   - MED DOWN: Medically grounded - cannot fly\n   - GRND EVENT: Ground event only\n4. Flight Lines section shows each mission: MSN number, period (AM/PM/EVE), brief time, event type (CAL/FAM/FCF), aircraft tail, IP, and student\n\n**Tip:** CAL = Calibration flight, FAM = Familiarisation flight, FCF = Functional Check Flight""")

    with st.expander("Ground School Tab"):
        st.markdown("""**What it shows:** The daily ground school calendar equivalent to the Excel-generated ground school spreadsheet.\n\n**How to use it:**\n1. Select a date from the dropdown\n2. Each event card shows: event code, title, start time, and duration\n3. Look for these badges:\n   - CSI REQUIRED: A Certified Simulator Instructor must be present. If no CSI is available the system will flag a warning in the Agent Query tab\n   - OUTSIDE AGENCY: This event involves an external organisation (Aeromed, Night Lab, Course Rules brief) and requires advance coordination\n\n**Tip:** Use the Agent Query tab with: Show me the ground school schedule and CSI availability for 2026-04-07""")

    with st.expander("IP Hotboard Tab"):
        st.markdown("""**What it shows:** Instructors ranked from least to most Year-to-Date flight hours. This determines who should fly next. Replaces the broken IP Hotboard Product tab in the Excel spreadsheet.\n\n**How to use it:**\n1. Select a date from the dropdown\n2. Available instructors are ranked #1 (least hours) to last - assign the top-ranked available IP to the next flight\n3. Unavailable instructors are listed separately with their reason (SNIVED or MED DOWN)\n4. Instructor types:\n   - ACTIVE: Full-time staff instructor\n   - AF: Air Force exchange instructor\n   - RESERVIST: Part-time, only available on their drill days\n   - NON_PERM: Non-permanent attached pilot\n\n**Tip:** Use Agent Query with: Show qualified IPs for CAL on 2026-04-06 to filter by event type qualification""")

    with st.expander("SNIVs Tab"):
        st.markdown("""**What it shows:** Unavailability requests for a selected date plus a full personnel availability summary. Replaces the manual copy-paste from the scheduling system into the Personnel Availability and SNIV tabs on the Weekly spreadsheet.\n\n**What is a SNIV?**\nA SNIV is a request by a person to NOT be scheduled on a given date. A person who is SNIVED should not appear on the flight schedule.\n\n**How to use it:**\n1. Select a date from the dropdown\n2. SNIVs section lists everyone who has requested unavailability and why\n3. Personnel Availability Summary shows every instructor and student with status:\n   - Green AVAILABLE: cleared to be scheduled\n   - Red UNAVAILABLE: SNIVED, medically grounded, or for reservists not a drill day\n\n**Tip:** Use Agent Query with: Check for double schedule conflicts on 2026-04-06 to detect anyone SNIVED but still on the flight schedule""")

    with st.expander("Students Tab"):
        st.markdown("""**What it shows:** All students grouped by class, sorted from most days behind to on track.\n\n**Status indicators:**\n- Red BEHIND: more than 3 workdays behind schedule\n- Yellow BEHIND: 1-3 workdays behind schedule\n- Green ON TRACK: no days behind\n\n**Student priority tiers:**\n- AF: Air Force exchange student with a fixed departure deadline - highest scheduling priority\n- REFRESH: Refresher pilot returning to currency - high priority\n- STANDARD: Normal syllabus student""")

    with st.expander("Notifications Tab"):
        st.markdown("""**What it shows:** A log of all instructor alerts sent during this session. Alerts are only sent after you explicitly Approve them in the Agent Query tab.\n\n**Alert types:**\n- HIGH_RISK: Student is at high risk of not completing training on time\n- BEHIND_SCHEDULE: Student is behind their syllabus schedule\n- REMEDIATION_ASSIGNED: A remediation plan has been created\n- ON_TRACK: Positive status update""")

    st.divider()
    st.markdown("### Available Demo Data")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Classes:** 26-1, 26-2")
        st.markdown("**Class 26-1 students:** Tara Voss, Leon Marsh, Dana Quirke")
        st.markdown("**Class 26-2 students:** Bram Okafor, Yuki Tanaka, Petra Holst")
        st.markdown("**Instructors:** Gale Rynder, Otto Finch, Selma Varga, Noel Drax, Preet Aulakh, Bex Torrance")
    with col2:
        st.markdown("**Schedule dates:** 2026-04-06, 2026-04-07, 2026-04-08, 2026-04-13, 2026-04-20, 2026-04-27")
        st.markdown("**SNIVed on 2026-04-06:** Otto Finch (personal), Preet Aulakh (medical)")
        st.markdown("**Aircraft:** T-001 CAL/FMC, T-002 FAM/FMC, T-003 CAL/FMC, T-004 FAM/PMC, T-005 CAL/NMC")
        st.markdown("**Priority students:** Dana Quirke (AF/26-1), Bram Okafor (AF/26-2)")
