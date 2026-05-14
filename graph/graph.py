from typing import Literal
from typing_extensions import Annotated, TypedDict

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from agents.scheduler import scheduler_tools
from agents.evaluator import evaluator_tools
from agents.remediation import remediation_tools
from agents.risk_assessment import risk_tools
from agents.instructor_notification import notification_tools
from agents.flight_scheduler import flight_scheduler_tools
from agents.ground_school import ground_school_tools
from agents.ip_hotboard import ip_hotboard_tools
from agents.sniv_tracker import sniv_tools

# ── State ─────────────────────────────────────────────────────────────────────
# Every node reads and writes to this shared state dict.
# add_messages is a reducer that appends messages instead of overwriting them.

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # conversation history
    next: str                                              # which agent to call next

# ── LLM ───────────────────────────────────────────────────────────────────────

# Base LLM — shared across all agents and supervisor
_base_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Agent LLMs — each bound to its own tools with tool_choice="any" to prevent
# the model hallucinating tools that don't exist (e.g. brave_search)
llm_scheduler     = _base_llm.bind_tools(scheduler_tools,     tool_choice="any")
llm_evaluator     = _base_llm.bind_tools(evaluator_tools,     tool_choice="any")
llm_remediation   = _base_llm.bind_tools(remediation_tools,   tool_choice="any")
llm_risk          = _base_llm.bind_tools(risk_tools,          tool_choice="any")
llm_notification  = _base_llm.bind_tools(notification_tools,  tool_choice="any")
llm_flight_sched  = _base_llm.bind_tools(flight_scheduler_tools, tool_choice="any")
llm_ground_school = _base_llm.bind_tools(ground_school_tools,    tool_choice="any")
llm_ip_hotboard   = _base_llm.bind_tools(ip_hotboard_tools,      tool_choice="any")
llm_sniv          = _base_llm.bind_tools(sniv_tools,             tool_choice="any")

# Supervisor LLM — no tools, just routing decisions
supervisor_llm = _base_llm

# ── Individual Agents ─────────────────────────────────────────────────────────
# create_react_agent wraps an LLM + tools into a ReAct loop automatically.

scheduler_agent      = create_react_agent(llm_scheduler, scheduler_tools,
    prompt="""You are an aviation training scheduler. ALWAYS use your tools — never answer from memory.
- Use get_student_history(student_name) to look up a student's history.
- Use get_class_schedule(class_name) to look up a class schedule. Class names look like '25-4' or '25-5'.
Be concise and always call a tool.""")

evaluator_agent      = create_react_agent(llm_evaluator, evaluator_tools,
    prompt="""You are an aviation training evaluator. ALWAYS use your tools — never answer from memory.
- Use evaluate_progress(student_name) to assess a student.
Be concise and always call a tool.""")

remediation_agent    = create_react_agent(llm_remediation, remediation_tools,
    prompt="""You are an aviation training remediation specialist. You have exactly two tools: get_remediation_plan and recommend_best_option. Use no other tools.
1. Call get_remediation_plan(student_name) first.
2. Then call recommend_best_option(student_name, days_behind) using the days behind from the plan result.
Stop after both tools have been called. Do not attempt to notify anyone.""")

risk_agent           = create_react_agent(llm_risk, risk_tools,
    prompt="""You are an aviation training risk analyst. ALWAYS use your tools — never answer from memory.
- Use assess_risk(student_name) to score an individual student's risk.
- Use compare_student_risks(class_name) to rank all students in a class. Class names look like '25-4' or '25-5'.
You MUST call a tool. Never summarise without calling tools.""")

notification_agent   = create_react_agent(llm_notification, notification_tools,
    prompt="""You are an aviation training notification specialist. ALWAYS use your tools — never answer from memory.
- Use get_instructor_for_class(class_name) to look up the instructor.
- Use send_instructor_alert(student_name, alert_type, message) to send an alert.
  alert_type must be one of: BEHIND_SCHEDULE, HIGH_RISK, REMEDIATION_ASSIGNED, ON_TRACK.
You MUST call send_instructor_alert to actually send the notification. Never just describe what you would do.""")

flight_sched_agent  = create_react_agent(llm_flight_sched, flight_scheduler_tools,
    prompt="""You are an aviation flight scheduling officer. ALWAYS use your tools — never answer from memory.
- Use get_daily_flight_schedule(date) to retrieve missions for a date.
- Use get_daily_whiteboard(date) to get the full daily status board.
- Use get_priority_students(date) to get student priority order for scheduling.
- Use get_aircraft_status() to check aircraft availability.
- Use get_enviro_data(date) to get sunset, EENT, HLL and flight window data.
Always call a tool. Dates use format YYYY-MM-DD.""")

ground_school_agent = create_react_agent(llm_ground_school, ground_school_tools,
    prompt="""You are a ground school scheduling coordinator. ALWAYS use your tools — never answer from memory.
- Use get_ground_school_schedule(date) to get events for a specific date.
- Use check_csi_availability(date) to verify CSI coverage for simulator events.
- Use get_ground_school_week(start_date) to get a full week view.
Always call a tool. Dates use format YYYY-MM-DD.""")

ip_hotboard_agent   = create_react_agent(llm_ip_hotboard, ip_hotboard_tools,
    prompt="""You are an IP scheduling coordinator managing the instructor hotboard. ALWAYS use your tools — never answer from memory.
- Use get_ip_hotboard(date) to rank available instructors by least flight hours.
- Use get_instructor_availability(date) to see full availability for all instructors.
- Use get_qualified_ips(event_type, date) to find qualified available IPs for CAL, FAM, or FCF events.
Always call a tool. Dates use format YYYY-MM-DD.""")

sniv_agent          = create_react_agent(llm_sniv, sniv_tools,
    prompt="""You are a personnel availability tracker managing SNIVs and scheduling conflicts. ALWAYS use your tools — never answer from memory.
- Use get_snivs_for_date(date) to list all SNIVs for a date.
- Use check_double_schedule(date) to detect conflicts between SNIVs and flight assignments.
- Use get_personnel_availability_summary(date) to get a full availability summary.
Always call a tool. Dates use format YYYY-MM-DD.""")


# ── Supervisor ────────────────────────────────────────────────────────────────
# The supervisor reads the conversation and decides which agent to call next,
# or whether we are done.

MEMBERS = ["scheduler", "evaluator", "remediation", "risk_assessment", "instructor_notification", "flight_scheduler", "ground_school", "ip_hotboard", "sniv_tracker"]

SUPERVISOR_PROMPT = """
You are an aviation training supervisor. Your ONLY job is to decide which agent to call next.

Available agents:
- scheduler              : looks up syllabus class schedules and student event history
- evaluator              : assesses whether a student is on track or behind
- remediation            : creates remediation plans for students who are behind
- risk_assessment        : scores a student's risk of failing to complete training
- instructor_notification: sends alerts to instructors about student status
- flight_scheduler       : daily flight lines, whiteboard, aircraft status, enviro data, student priority
- ground_school          : ground school calendar, CSI availability, weekly ground school view
- ip_hotboard            : instructor hotboard ranked by flight hours, instructor availability
- sniv_tracker           : SNIV list, double-schedule conflicts, personnel availability summary

Critical rules:
1. Determine EXACTLY which agents are needed by looking for these keywords in the user request:
   - "schedule", "list", "history", "syllabus"   → scheduler
   - "evaluate", "progress"                      → evaluator
   - "risk", "risk level"                        → risk_assessment
   - "remediation plan"                          → remediation
   - "notify", "alert", "alert instructor"       → instructor_notification
   - "flight", "whiteboard", "aircraft", "enviro", "flight line", "msn", "priority students" → flight_scheduler
   - "ground school", "csi", "ground event"      → ground_school
   - "hotboard", "ip availability", "instructor hours", "qualified ip" → ip_hotboard
   - "sniv", "availability", "double schedule", "personnel availability" → sniv_tracker
   If a keyword is NOT present, do NOT call that agent.
2. An agent is DONE when its result prefix appears in the conversation:
   - scheduler        → "Schedule lookup:"
   - evaluator        → "Evaluation for"
   - remediation      → "Remediation plan for"
   - risk_assessment  → "Risk assessment for" or "Class risk comparison for"
   - notification     → "Instructor notified:"
   - flight_scheduler → "Flight Schedule for" or "Daily Whiteboard" or "Aircraft Fleet" or "Environment Data" or "Student Priority List"
   - ground_school    → "Ground School Schedule for" or "CSI Availability" or "Ground School Week"
   - ip_hotboard      → "IP Hotboard for" or "Instructor availability for" or "Qualified IPs for"
   - sniv_tracker     → "SNIVs for" or "DOUBLE SCHEDULE" or "Personnel Availability Summary"
3. Never call an agent that is already done.
4. Once all needed agents are done, respond with FINISH immediately.

Respond with ONLY one word from: scheduler, evaluator, remediation, risk_assessment, instructor_notification, flight_scheduler, ground_school, ip_hotboard, sniv_tracker, FINISH.
"""

# Keywords that must appear in the user request to allow each agent
AGENT_KEYWORDS = {
    "scheduler":              ["schedule", "list", "history", "class", "events", "syllabus"],
    "evaluator":              ["evaluate", "progress", "status", "on track", "behind"],
    "remediation":            ["remediation", "remediate", "plan"],
    "risk_assessment":        ["risk"],
    "instructor_notification":["notify", "alert", "notification", "full status report"],
    "flight_scheduler":       ["flight", "whiteboard", "aircraft", "enviro", "flight line", "msn", "priority student", "takeoff", "land", "brief"],
    "ground_school":          ["ground school", "csi", "ground event", "sim event", "aeromed", "nightlab"],
    "ip_hotboard":            ["hotboard", "ip availability", "instructor hours", "qualified ip", "least hours", "flight hours"],
    "sniv_tracker":           ["sniv", "availability", "double schedule", "personnel availability", "drill"],
}

# Result prefixes that indicate an agent has already completed its work
AGENT_DONE_PREFIXES = {
    "scheduler":               "Schedule lookup:",
    "evaluator":               "Evaluation for",
    "remediation":             "Remediation plan for",
    "risk_assessment":         ["Risk assessment for", "Class risk comparison for"],
    "instructor_notification": "Instructor notified:",
    "flight_scheduler":        ["Flight Schedule for", "Daily Whiteboard", "Aircraft Fleet Status", "Environment Data for", "Student Priority List"],
    "ground_school":           ["Ground School Schedule for", "CSI Availability check", "Ground School Week"],
    "ip_hotboard":             ["IP Hotboard for", "Instructor availability for", "Qualified IPs for"],
    "sniv_tracker":            ["SNIVs for", "DOUBLE SCHEDULE", "Personnel Availability Summary"],
}


def _allowed_agents(user_query: str, messages: list) -> list:
    """Return agents that are (a) relevant to the query and (b) not yet done."""
    query_lower = user_query.lower()
    all_content = " ".join(m.content for m in messages if m.content)

    allowed = []
    for agent in MEMBERS:
        # Check if agent is relevant to this query
        keywords = AGENT_KEYWORDS.get(agent, [])
        if not any(kw in query_lower for kw in keywords):
            continue
        # Check if agent already produced output
        done_prefix = AGENT_DONE_PREFIXES.get(agent, "")
        if isinstance(done_prefix, list):
            already_done = any(p in all_content for p in done_prefix)
        else:
            already_done = done_prefix in all_content
        if not already_done:
            allowed.append(agent)
    return allowed


def supervisor_node(state: AgentState) -> AgentState:
    """Supervisor decides which agent to call next or whether to finish."""
    messages = state["messages"]

    # Find original user query
    user_query = ""
    for m in messages:
        if isinstance(m, HumanMessage):
            user_query = m.content
            break

    # Enforce keyword-based allow-list in Python before asking the LLM
    allowed = _allowed_agents(user_query, messages)
    if not allowed:
        print(f"\n[Supervisor] → finish (all needed agents done)")
        return {"messages": messages, "next": "finish"}

    # Build conversation summary for the LLM
    conversation = "\n".join(
        f"[{m.__class__.__name__}]: {m.content[:300] if m.content else '(no content)'}"
        for m in messages
    )

    allowed_str = "/".join(allowed + ["FINISH"])
    response = supervisor_llm.invoke([
        HumanMessage(content=SUPERVISOR_PROMPT + "\n\nConversation:\n" + conversation +
                     f"\n\nAllowed choices for this query: {allowed_str}"
                     f"\n\nWhich agent should act next? ({allowed_str})")
    ])

    decision = response.content.strip().lower()
    decision = decision.replace("-", "_").strip(".,!?'\"")

    # Must be in the allowed list
    if decision not in allowed + ["finish"]:
        decision = allowed[0]  # pick the first allowed agent

    print(f"\n[Supervisor] → {decision}")
    return {"messages": messages, "next": decision}

# ── Agent Node Wrappers ───────────────────────────────────────────────────────
# Each wrapper runs the agent and appends its response to the message history.

def _first_human_message(state: AgentState) -> list:
    """Return only the original human request so agents aren't confused by prior agent outputs."""
    for m in state["messages"]:
        if isinstance(m, HumanMessage):
            return [m]
    return state["messages"][-1:]


def _extract_class_name(text: str) -> str | None:
    """Extract a class name like 25-4 or 25-5 from a query string."""
    import re
    # Match 'class 25-4' or just '25-4' anywhere
    m = re.search(r'(?:class\s+)?(\d{2}-\d+)', text)
    return m.group(1) if m else None


def _extract_student_name(text: str) -> str | None:
    """Extract a student name from a query string, handling 'for Name', 'Name's', etc."""
    import re
    # Match 'for FirstName LastName'
    m = re.search(r'for ([A-Z][a-z]+ [A-Z][a-z]+)', text)
    if m:
        return m.group(1)
    # Match possessive 'FirstName LastName's'
    m = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)\'s', text)
    if m:
        return m.group(1)
    # Match plain 'FirstName LastName' anywhere
    m = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', text)
    if m:
        return m.group(1)
    return None


def run_scheduler(state: AgentState) -> AgentState:
    print("[scheduler] running...")
    import re
    human_msg = _first_human_message(state)[0]
    student_name  = _extract_student_name(human_msg.content)
    class_name    = _extract_class_name(human_msg.content)

    from agents.scheduler import get_student_history, get_class_schedule
    from langchain_core.messages import AIMessage
    parts = []
    if student_name:
        parts.append(get_student_history.invoke({"student_name": student_name}))
    if class_name:
        parts.append(get_class_schedule.invoke({"class_name": class_name}))
    if not parts:
        parts.append("No student or class name found in request.")

    summary = AIMessage(content="Schedule lookup: " + " | ".join(parts))
    print("[scheduler] done")
    return {"messages": [summary]}


def run_evaluator(state: AgentState) -> AgentState:
    print("[evaluator] running...")
    import re
    from langchain_core.messages import AIMessage
    human_msg = _first_human_message(state)[0]
    student_name = _extract_student_name(human_msg.content)

    # If no individual student was named, check if all students in a class were requested
    if not student_name:
        class_name = _extract_class_name(human_msg.content)
        if class_name:
            from data.mock_data import MOCK_STUDENT_HISTORY
            from agents.evaluator import evaluate_progress
            students = [n for n, d in MOCK_STUDENT_HISTORY.items() if d.get('className') == class_name]
            if students:
                parts = [evaluate_progress.invoke({"student_name": s}) for s in students]
                summary = AIMessage(content="Evaluation for " + class_name + ": " + " | ".join(parts))
                print("[evaluator] done")
                return {"messages": [summary]}
        summary = AIMessage(content="Evaluation for unknown: No student name found in request.")
        print("[evaluator] done")
        return {"messages": [summary]}

    from agents.evaluator import evaluate_progress
    result = evaluate_progress.invoke({"student_name": student_name})
    summary = AIMessage(content="Evaluation for " + student_name + ": " + result)
    print("[evaluator] done")
    return {"messages": [summary]}

def run_remediation(state: AgentState) -> AgentState:
    print("[remediation] running...")
    from langchain_core.messages import AIMessage
    human_msg = _first_human_message(state)[0]
    student_name = _extract_student_name(human_msg.content)
    if not student_name:
        # No individual student named — skip remediation
        print("[remediation] skipped — no individual student named")
        return {"messages": [AIMessage(content="Remediation plan for unknown: No individual student named in request.")]}

    # Call tools directly — bypass ReAct to avoid hallucination
    from agents.remediation import get_remediation_plan, recommend_best_option
    plan_result    = get_remediation_plan.invoke({"student_name": student_name})
    # Extract days behind from mock data
    from data.mock_data import MOCK_STUDENT_HISTORY
    days_behind    = MOCK_STUDENT_HISTORY.get(student_name, {}).get("workdaysBehind", 0)
    option_result  = recommend_best_option.invoke({"student_name": student_name, "days_behind": days_behind})

    from langchain_core.messages import AIMessage
    summary = AIMessage(content=f"Remediation plan for {student_name}: {plan_result} | Best option: {option_result}")
    print("[remediation] done")
    return {"messages": [summary]}

def run_risk_assessment(state: AgentState) -> AgentState:
    print("[risk_assessment] running...")
    import re
    from langchain_core.messages import AIMessage
    human_msg = _first_human_message(state)[0]
    content = human_msg.content

    # Class-wide comparison requested?
    class_name = _extract_class_name(content)
    if class_name:
        from agents.risk_assessment import compare_student_risks
        risk_result = compare_student_risks.invoke({"class_name": class_name})
        summary = AIMessage(content=f"Class risk comparison for {class_name}: {risk_result}")
    else:
        # Individual student assessment
        student_name = _extract_student_name(content) or "John Smith"
        from agents.risk_assessment import assess_risk
        risk_result = assess_risk.invoke({"student_name": student_name})
        summary = AIMessage(content=f"Risk assessment for {student_name}: {risk_result}")

    print("[risk_assessment] done")
    return {"messages": [summary]}

def run_instructor_notification(state: AgentState) -> AgentState:
    print("[instructor_notification] running...")
    import re
    from langchain_core.messages import AIMessage
    from agents.instructor_notification import send_instructor_alert
    from data.mock_data import MOCK_STUDENT_HISTORY

    human_msg = _first_human_message(state)[0]
    content = human_msg.content

    # Collect prior agent outputs for context
    prior = "\n".join(m.content for m in state["messages"] if m.content)

    # Determine alert type from risk results
    alert_type = "BEHIND_SCHEDULE"
    if "HIGH" in prior:
        alert_type = "HIGH_RISK"

    # Check if this is a class-wide notification or individual
    class_name   = _extract_class_name(content)
    student_name = _extract_student_name(content)

    results = []
    if class_name:
        # Notify about every high-risk student in the class
        high_risk_students = [
            name for name, data in MOCK_STUDENT_HISTORY.items()
            if data.get('className') == class_name and data.get('workdaysBehind', 0) > 0
        ]
        if not high_risk_students:
            high_risk_students = [
                name for name, data in MOCK_STUDENT_HISTORY.items()
                if data.get('className') == class_name
            ]
        for student_name in high_risk_students:
            result = send_instructor_alert.invoke({
                "student_name": student_name,
                "alert_type":   alert_type,
                "message":      f"Status report: {prior[:600]}"
            })
            results.append(result)
    elif student_name:
        result = send_instructor_alert.invoke({
            "student_name": student_name,
            "alert_type":   alert_type,
            "message":      prior[:600]
        })
        results.append(result)
    else:
        results.append("No student or class identified for notification.")

    summary = AIMessage(content="Instructor notified: " + " | ".join(results))
    print("[instructor_notification] done")
    return {"messages": [summary]}

# ── New Agent Node Runners ────────────────────────────────────────────────────

def _extract_date(text: str) -> str:
    """Extract a YYYY-MM-DD date from text, defaulting to 2026-04-06 for demos."""
    import re
    m = re.search(r'(\d{4}-\d{2}-\d{2})', text)
    return m.group(1) if m else '2026-04-06'


def run_flight_scheduler(state: AgentState) -> AgentState:
    print("[flight_scheduler] running...")
    from langchain_core.messages import AIMessage
    human_msg = _first_human_message(state)[0]
    content = human_msg.content
    date = _extract_date(content)

    from agents.flight_scheduler import (
        get_daily_flight_schedule, get_daily_whiteboard,
        get_priority_students, get_aircraft_status, get_enviro_data
    )
    parts = []
    cl = content.lower()
    if any(k in cl for k in ['whiteboard', 'status board', 'daily board']):
        parts.append(get_daily_whiteboard.invoke({'date': date}))
    if any(k in cl for k in ['flight line', 'flight schedule', 'msn', 'mission']):
        parts.append(get_daily_flight_schedule.invoke({'date': date}))
    if any(k in cl for k in ['aircraft', 'fleet', 'plane']):
        parts.append(get_aircraft_status.invoke({}))
    if any(k in cl for k in ['enviro', 'sunset', 'eent', 'hll', 'highlight']):
        parts.append(get_enviro_data.invoke({'date': date}))
    if any(k in cl for k in ['priority student', 'student priority', 'who flies']):
        parts.append(get_priority_students.invoke({'date': date}))
    if not parts:
        parts.append(get_daily_whiteboard.invoke({'date': date}))
        parts.append(get_daily_flight_schedule.invoke({'date': date}))
    summary = AIMessage(content='Flight Schedule for ' + date + ': ' + ' | '.join(parts))
    print("[flight_scheduler] done")
    return {'messages': [summary]}


def run_ground_school(state: AgentState) -> AgentState:
    print("[ground_school] running...")
    from langchain_core.messages import AIMessage
    human_msg = _first_human_message(state)[0]
    content = human_msg.content
    date = _extract_date(content)
    cl = content.lower()

    from agents.ground_school import (
        get_ground_school_schedule, check_csi_availability, get_ground_school_week
    )
    parts = []
    if 'week' in cl:
        parts.append(get_ground_school_week.invoke({'start_date': date}))
    if 'csi' in cl:
        parts.append(check_csi_availability.invoke({'date': date}))
    if not parts:
        parts.append(get_ground_school_schedule.invoke({'date': date}))
        parts.append(check_csi_availability.invoke({'date': date}))
    summary = AIMessage(content='Ground School Schedule for ' + date + ': ' + ' | '.join(parts))
    print("[ground_school] done")
    return {'messages': [summary]}


def run_ip_hotboard(state: AgentState) -> AgentState:
    print("[ip_hotboard] running...")
    from langchain_core.messages import AIMessage
    human_msg = _first_human_message(state)[0]
    content = human_msg.content
    date = _extract_date(content)
    cl = content.lower()

    from agents.ip_hotboard import (
        get_ip_hotboard, get_instructor_availability, get_qualified_ips
    )
    parts = []
    if any(k in cl for k in ['qualified', 'cal', 'fam', 'fcf']):
        event_type = 'FCF' if 'fcf' in cl else ('FAM' if 'fam' in cl else 'CAL')
        parts.append(get_qualified_ips.invoke({'event_type': event_type, 'date': date}))
    if any(k in cl for k in ['availability', 'available']):
        parts.append(get_instructor_availability.invoke({'date': date}))
    if not parts:
        parts.append(get_ip_hotboard.invoke({'date': date}))
    summary = AIMessage(content='IP Hotboard for ' + date + ': ' + ' | '.join(parts))
    print("[ip_hotboard] done")
    return {'messages': [summary]}


def run_sniv_tracker(state: AgentState) -> AgentState:
    print("[sniv_tracker] running...")
    from langchain_core.messages import AIMessage
    human_msg = _first_human_message(state)[0]
    content = human_msg.content
    date = _extract_date(content)
    cl = content.lower()

    from agents.sniv_tracker import (
        get_snivs_for_date, check_double_schedule, get_personnel_availability_summary
    )
    parts = []
    if 'double' in cl or 'conflict' in cl:
        parts.append(check_double_schedule.invoke({'date': date}))
    if any(k in cl for k in ['personnel', 'all staff', 'summary']):
        parts.append(get_personnel_availability_summary.invoke({'date': date}))
    if not parts:
        parts.append(get_snivs_for_date.invoke({'date': date}))
        parts.append(check_double_schedule.invoke({'date': date}))
    summary = AIMessage(content='SNIVs for ' + date + ': ' + ' | '.join(parts))
    print("[sniv_tracker] done")
    return {'messages': [summary]}


# ── Routing Function ──────────────────────────────────────────────────────────
# After the supervisor runs, this function reads state["next"] and returns
# the name of the next node to visit.

def route(state: AgentState) -> Literal["scheduler", "evaluator", "remediation", "risk_assessment", "instructor_notification", "flight_scheduler", "ground_school", "ip_hotboard", "sniv_tracker", "__end__"]:
    nxt = state.get("next", "finish")
    if nxt == "finish":
        return END
    return nxt

# ── Build the Graph ───────────────────────────────────────────────────────────

builder = StateGraph(AgentState)

# Add all nodes
builder.add_node("supervisor",              supervisor_node)
builder.add_node("scheduler",               run_scheduler)
builder.add_node("evaluator",               run_evaluator)
builder.add_node("remediation",             run_remediation)
builder.add_node("risk_assessment",         run_risk_assessment)
builder.add_node("instructor_notification", run_instructor_notification)
builder.add_node("flight_scheduler",        run_flight_scheduler)
builder.add_node("ground_school",           run_ground_school)
builder.add_node("ip_hotboard",             run_ip_hotboard)
builder.add_node("sniv_tracker",            run_sniv_tracker)

# Entry point — always start at supervisor
builder.add_edge(START, "supervisor")

# Supervisor decides where to go
builder.add_conditional_edges("supervisor", route)

# After each agent runs, return to supervisor for next decision
builder.add_edge("scheduler",               "supervisor")
builder.add_edge("evaluator",               "supervisor")
builder.add_edge("remediation",             "supervisor")
builder.add_edge("risk_assessment",         "supervisor")
builder.add_edge("instructor_notification", "supervisor")
builder.add_edge("flight_scheduler",        "supervisor")
builder.add_edge("ground_school",           "supervisor")
builder.add_edge("ip_hotboard",             "supervisor")
builder.add_edge("sniv_tracker",            "supervisor")

# Compile into a runnable graph
# MemorySaver is required for interrupt_before and get_state to work.
# interrupt_before="instructor_notification" pauses the graph and surfaces state
# to the caller before any notification is sent, allowing a human to confirm.
memory = MemorySaver()
graph = builder.compile(checkpointer=memory, interrupt_before=["instructor_notification"])
