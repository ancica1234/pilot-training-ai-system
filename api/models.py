"""
api/models.py
-------------
Pydantic models for API request and response bodies.
Pydantic validates incoming JSON automatically and serialises outgoing responses.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ── Request models ─────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query to send to the agent system")
    thread_id: str = Field(default="default", description="Conversation thread ID for stateful multi-turn queries")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "query": "Evaluate John Smith's training progress and assess his risk level.",
                "thread_id": "session-1"
            }]
        }
    }


class ApproveRequest(BaseModel):
    thread_id: str = Field(..., description="Thread ID of the paused graph to resume")
    approved: bool = Field(..., description="True to send the notification, False to cancel")


# ── Response models ────────────────────────────────────────────────────────────

class AgentStep(BaseModel):
    agent: str
    output: str


class QueryResponse(BaseModel):
    thread_id:  str
    status:     str  # "complete" or "awaiting_approval"
    steps:      list[AgentStep]
    final_output: Optional[str] = None
    pending_messages: Optional[list[str]] = None  # shown when awaiting approval


class StudentSummary(BaseModel):
    name:            str
    className:       str
    workdaysBehind:  int
    status:          str  # "BEHIND" or "ON TRACK"
    incompleteCount: int


class ClassSummary(BaseModel):
    className:   str
    startDate:   str
    eventCount:  int
    students:    list[StudentSummary]


class NotificationEntry(BaseModel):
    timestamp:    str
    student_name: str
    class_name:   str
    instructor:   str
    alert_type:   str
    message:      str
