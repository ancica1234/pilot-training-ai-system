"""
tests/test_api.py
-----------------
Tests for the FastAPI endpoints.
Uses FastAPI's TestClient — no server needed, no LLM calls made.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


# ── Health ─────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_returns_agent_count(self):
        response = client.get("/health")
        assert response.json()["agents"] == 5


# ── Students ───────────────────────────────────────────────────────────────────

class TestStudentsEndpoint:
    def test_list_students_returns_200(self):
        response = client.get("/students")
        assert response.status_code == 200

    def test_list_students_returns_list(self):
        response = client.get("/students")
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_list_students_has_required_fields(self):
        response = client.get("/students")
        student = response.json()[0]
        assert "name"            in student
        assert "className"       in student
        assert "workdaysBehind"  in student
        assert "status"          in student
        assert "incompleteCount" in student

    def test_list_students_includes_john_smith(self):
        response = client.get("/students")
        names = [s["name"] for s in response.json()]
        assert "John Smith" in names

    def test_list_students_includes_marcus_webb(self):
        response = client.get("/students")
        names = [s["name"] for s in response.json()]
        assert "Marcus Webb" in names

    def test_get_student_known(self):
        response = client.get("/students/John Smith")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Smith"
        assert data["className"] == "25-4"
        assert data["workdaysBehind"] == 5
        assert data["status"] == "BEHIND"

    def test_get_student_on_track(self):
        response = client.get("/students/Jane Doe")
        assert response.status_code == 200
        assert response.json()["status"] == "ON TRACK"
        assert response.json()["workdaysBehind"] == 0

    def test_get_student_unknown_returns_404(self):
        response = client.get("/students/Ghost Person")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_student_marcus_webb(self):
        response = client.get("/students/Marcus Webb")
        assert response.status_code == 200
        data = response.json()
        assert data["className"] == "25-4"
        assert data["workdaysBehind"] == 3
        assert data["status"] == "BEHIND"
        assert data["incompleteCount"] == 2


# ── Classes ────────────────────────────────────────────────────────────────────

class TestClassesEndpoint:
    def test_list_classes_returns_200(self):
        response = client.get("/classes")
        assert response.status_code == 200

    def test_list_classes_returns_both_classes(self):
        response = client.get("/classes")
        names = [c["className"] for c in response.json()]
        assert "25-4" in names
        assert "25-5" in names

    def test_class_has_students(self):
        response = client.get("/classes")
        classes = {c["className"]: c for c in response.json()}
        assert len(classes["25-4"]["students"]) > 0
        assert len(classes["25-5"]["students"]) > 0

    def test_class_25_4_has_correct_event_count(self):
        response = client.get("/classes")
        classes = {c["className"]: c for c in response.json()}
        assert classes["25-4"]["eventCount"] == 5

    def test_class_25_4_includes_marcus_webb(self):
        response = client.get("/classes")
        classes = {c["className"]: c for c in response.json()}
        names = [s["name"] for s in classes["25-4"]["students"]]
        assert "Marcus Webb" in names


# ── Notifications ──────────────────────────────────────────────────────────────

class TestNotificationsEndpoint:
    def test_notifications_returns_200(self):
        response = client.get("/notifications")
        assert response.status_code == 200

    def test_notifications_returns_list(self):
        response = client.get("/notifications")
        assert isinstance(response.json(), list)

    def test_notifications_has_required_fields_when_populated(self):
        from agents.instructor_notification import send_instructor_alert, NOTIFICATION_LOG
        NOTIFICATION_LOG.clear()
        send_instructor_alert.invoke({
            "student_name": "John Smith",
            "alert_type":   "HIGH_RISK",
            "message":      "Test"
        })
        response = client.get("/notifications")
        data = response.json()
        assert len(data) == 1
        entry = data[0]
        assert "timestamp"    in entry
        assert "student_name" in entry
        assert "alert_type"   in entry
        assert entry["student_name"] == "John Smith"
        assert entry["alert_type"]   == "HIGH_RISK"