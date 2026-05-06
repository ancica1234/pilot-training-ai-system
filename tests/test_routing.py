"""
tests/test_routing.py
---------------------
Unit tests for the supervisor routing logic.
Tests the Python-level keyword filtering without making any LLM calls.
"""

import pytest
from langchain_core.messages import HumanMessage, AIMessage


# ── _allowed_agents ────────────────────────────────────────────────────────────

class TestAllowedAgents:
    """Test the keyword-based agent allow-list enforced in Python."""

    def setup_method(self):
        # Import fresh each test so AGENT_KEYWORDS changes don't leak
        from graph.graph import _allowed_agents
        self._allowed_agents = _allowed_agents

    def _msgs(self, *contents):
        return [AIMessage(content=c) for c in contents]

    def test_risk_query_allows_only_risk(self):
        allowed = self._allowed_agents(
            "Assess the risk level for John Smith",
            [HumanMessage(content="Assess the risk level for John Smith")]
        )
        assert "risk_assessment" in allowed
        assert "remediation" not in allowed
        assert "instructor_notification" not in allowed

    def test_remediation_query_allows_remediation(self):
        allowed = self._allowed_agents(
            "Build a remediation plan for John Smith",
            [HumanMessage(content="Build a remediation plan for John Smith")]
        )
        assert "remediation" in allowed

    def test_notify_query_allows_notification(self):
        allowed = self._allowed_agents(
            "Alert the instructor about John Smith",
            [HumanMessage(content="Alert the instructor about John Smith")]
        )
        assert "instructor_notification" in allowed

    def test_schedule_query_allows_scheduler(self):
        allowed = self._allowed_agents(
            "List students in class 25-4",
            [HumanMessage(content="List students in class 25-4")]
        )
        assert "scheduler" in allowed

    def test_done_agent_excluded(self):
        """An agent whose result prefix is already in messages should be excluded."""
        msgs = [
            HumanMessage(content="Assess the risk level for John Smith"),
            AIMessage(content="Risk assessment for John Smith: Risk Level: HIGH"),
        ]
        allowed = self._allowed_agents("Assess the risk level for John Smith", msgs)
        assert "risk_assessment" not in allowed

    def test_all_done_returns_empty(self):
        """When all relevant agents are done, allowed list should be empty."""
        msgs = [
            HumanMessage(content="Assess the risk level for John Smith"),
            AIMessage(content="Risk assessment for John Smith: Risk Level: HIGH"),
        ]
        allowed = self._allowed_agents("Assess the risk level for John Smith", msgs)
        assert allowed == []

    def test_full_pipeline_query_allows_all(self):
        allowed = self._allowed_agents(
            "Build a remediation plan for John Smith, assess his risk, then notify his instructor.",
            [HumanMessage(content="Build a remediation plan for John Smith, assess his risk, then notify his instructor.")]
        )
        assert "remediation" in allowed
        assert "risk_assessment" in allowed
        assert "instructor_notification" in allowed

    def test_students_query_routes_to_scheduler(self):
        allowed = self._allowed_agents(
            "Who are the students in class 25-4?",
            [HumanMessage(content="Who are the students in class 25-4?")]
        )
        assert "scheduler" in allowed
        assert "risk_assessment" not in allowed
        assert "remediation" not in allowed

    def test_partial_completion_excludes_done_agents(self):
        msgs = [
            HumanMessage(content="Build a remediation plan for John Smith, assess his risk, then notify his instructor."),
            AIMessage(content="Remediation plan for John Smith: Option 3..."),
        ]
        allowed = self._allowed_agents(
            "Build a remediation plan for John Smith, assess his risk, then notify his instructor.",
            msgs
        )
        assert "remediation" not in allowed
        assert "risk_assessment" in allowed
        assert "instructor_notification" in allowed

    def test_students_query_routes_to_scheduler(self):
        allowed = self._allowed_agents(
            "Who are the students in class 25-4?",
            [HumanMessage(content="Who are the students in class 25-4?")]
        )
        assert "scheduler"  in allowed
        assert "risk_assessment"  not in allowed
        assert "remediation"  not in allowed

# ── _extract_student_name ──────────────────────────────────────────────────────

class TestExtractStudentName:
    def setup_method(self):
        from graph.graph import _extract_student_name
        self._extract = _extract_student_name

    def test_for_firstname_lastname(self):
        assert self._extract("Build a plan for John Smith") == "John Smith"

    def test_possessive(self):
        assert self._extract("Evaluate John Smith's progress") == "John Smith"

    def test_plain_name(self):
        assert self._extract("John Smith is behind schedule") == "John Smith"

    def test_no_name_returns_none(self):
        assert self._extract("List all students in class 25-4") is None

    def test_class_25_5_students(self):
        assert self._extract("Assess risk for Carlos Rivera") == "Carlos Rivera"
        assert self._extract("Priya Patel's remediation plan") == "Priya Patel"


# ── _extract_class_name ────────────────────────────────────────────────────────

class TestExtractClassName:
    def setup_method(self):
        from graph.graph import _extract_class_name
        self._extract = _extract_class_name

    def test_with_class_keyword(self):
        assert self._extract("List students in class 25-4") == "25-4"

    def test_without_class_keyword(self):
        assert self._extract("Compare risks in 25-5") == "25-5"

    def test_typo_clss(self):
        assert self._extract("List students in clss 25-4") == "25-4"

    def test_no_class_returns_none(self):
        assert self._extract("Evaluate John Smith's progress") is None

    def test_class_25_5(self):
        assert self._extract("Full status report on class 25-5") == "25-5"
