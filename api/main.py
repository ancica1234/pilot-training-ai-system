"""
api/main.py
-----------
FastAPI application for the Aviation Training Multi-Agent System.

Run with:
    GROQ_API_KEY=<key> uvicorn api.main:app --reload

Then open:
    http://localhost:8000/docs   ← interactive Swagger UI
    http://localhost:8000/redoc  ← ReDoc documentation
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage

from api.models import (
    QueryRequest, QueryResponse, ApproveRequest,
    AgentStep, StudentSummary, ClassSummary, NotificationEntry
)

# ── App setup ──────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Aviation Training Multi-Agent API",
    description="Multi-agent system for aviation flight training management",
    version="1.0.0",
)

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import graph after app setup so env vars are in place
from graph.graph import graph


# ── Helper ─────────────────────────────────────────────────────────────────────

def _extract_steps(messages: list) -> list[AgentStep]:
    """Turn agent AIMessages into AgentStep objects for the response."""
    steps = []
    for m in messages:
        if not isinstance(m, AIMessage) or not m.content:
            continue
        content = m.content
        if content.startswith("Schedule lookup:"):
            steps.append(AgentStep(agent="scheduler", output=content))
        elif content.startswith("Evaluation for"):
            steps.append(AgentStep(agent="evaluator", output=content))
        elif content.startswith("Remediation plan for"):
            steps.append(AgentStep(agent="remediation", output=content))
        elif content.startswith(("Risk assessment for", "Class risk comparison for")):
            steps.append(AgentStep(agent="risk_assessment", output=content))
        elif content.startswith("Instructor notified:"):
            steps.append(AgentStep(agent="instructor_notification", output=content))
    return steps


# ── Query endpoints ────────────────────────────────────────────────────────────

@app.post("/query", response_model=QueryResponse, tags=["Agent"])
def run_query(request: QueryRequest):
    """Send a natural language query to the multi-agent system.
    
    If the graph pauses for human approval before sending instructor notifications,
    the response will have status='awaiting_approval'. Call POST /query/approve to resume.
    """
    config = {"configurable": {"thread_id": request.thread_id}}
    inputs = {"messages": [HumanMessage(content=request.query)]}

    try:
        for _ in graph.stream(inputs, config=config, stream_mode="values", recursion_limit=25):
            pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    state = graph.get_state(config)
    steps = _extract_steps(state.values.get("messages", []))

    # Check if paused at instructor_notification interrupt
    if state.next and "instructor_notification" in state.next:
        pending = [
            m.content for m in state.values.get("messages", [])[-4:]
            if m.content and isinstance(m, AIMessage)
        ]
        return QueryResponse(
            thread_id=request.thread_id,
            status="awaiting_approval",
            steps=steps,
            pending_messages=pending
        )

    final = steps[-1].output if steps else "No output produced."
    return QueryResponse(
        thread_id=request.thread_id,
        status="complete",
        steps=steps,
        final_output=final
    )


@app.post("/query/approve", response_model=QueryResponse, tags=["Agent"])
def approve_notification(request: ApproveRequest):
    """Resume a paused graph after human review of instructor notification.
    
    Set approved=true to send the notification, approved=false to cancel.
    """
    config = {"configurable": {"thread_id": request.thread_id}}

    state = graph.get_state(config)
    if not state.next or "instructor_notification" not in state.next:
        raise HTTPException(status_code=400, detail="No pending notification for this thread_id")

    if not request.approved:
        return QueryResponse(
            thread_id=request.thread_id,
            status="complete",
            steps=_extract_steps(state.values.get("messages", [])),
            final_output="Notification cancelled by user."
        )

    try:
        for _ in graph.stream(None, config=config, stream_mode="values", recursion_limit=10):
            pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    state = graph.get_state(config)
    steps = _extract_steps(state.values.get("messages", []))
    final = steps[-1].output if steps else "No output produced."
    return QueryResponse(
        thread_id=request.thread_id,
        status="complete",
        steps=steps,
        final_output=final
    )


# ── Data endpoints ─────────────────────────────────────────────────────────────

@app.get("/students", response_model=list[StudentSummary], tags=["Data"])
def list_students():
    """List all students with their current status."""
    from data.mock_data import MOCK_STUDENT_HISTORY
    result = []
    for name, data in MOCK_STUDENT_HISTORY.items():
        result.append(StudentSummary(
            name=name,
            className=data["className"],
            workdaysBehind=data["workdaysBehind"],
            status="BEHIND" if data["workdaysBehind"] > 0 else "ON TRACK",
            incompleteCount=len(data["incompleteEvents"])
        ))
    return result


@app.get("/students/{student_name}", response_model=StudentSummary, tags=["Data"])
def get_student(student_name: str):
    """Get a single student's status by name."""
    from data.mock_data import MOCK_STUDENT_HISTORY
    data = MOCK_STUDENT_HISTORY.get(student_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"Student '{student_name}' not found")
    return StudentSummary(
        name=student_name,
        className=data["className"],
        workdaysBehind=data["workdaysBehind"],
        status="BEHIND" if data["workdaysBehind"] > 0 else "ON TRACK",
        incompleteCount=len(data["incompleteEvents"])
    )


@app.get("/classes", response_model=list[ClassSummary], tags=["Data"])
def list_classes():
    """List all classes with their schedules and enrolled students."""
    from data.mock_data import MOCK_SCHEDULES, MOCK_STUDENT_HISTORY
    result = []
    for class_name, schedule in MOCK_SCHEDULES.items():
        students = [
            StudentSummary(
                name=name,
                className=class_name,
                workdaysBehind=data["workdaysBehind"],
                status="BEHIND" if data["workdaysBehind"] > 0 else "ON TRACK",
                incompleteCount=len(data["incompleteEvents"])
            )
            for name, data in MOCK_STUDENT_HISTORY.items()
            if data["className"] == class_name
        ]
        result.append(ClassSummary(
            className=class_name,
            startDate=schedule["startDate"],
            eventCount=len(schedule["events"]),
            students=students
        ))
    return result


@app.get("/notifications", response_model=list[NotificationEntry], tags=["Data"])
def list_notifications():
    """Get the log of all notifications sent this session."""
    from agents.instructor_notification import NOTIFICATION_LOG
    return [
        NotificationEntry(
            timestamp=n["timestamp"],
            student_name=n["student_name"],
            class_name=n["class_name"],
            instructor=n["instructor"],
            alert_type=n["alert_type"],
            message=n["message"]
        )
        for n in NOTIFICATION_LOG
    ]


# ── Health check ───────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health():
    """Health check endpoint."""
    return {"status": "ok", "agents": 9, "classes": 2}
