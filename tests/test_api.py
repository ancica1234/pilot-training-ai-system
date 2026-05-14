"""
tests/test_api.py - FastAPI endpoint tests. No LLM calls.
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_returns_agent_count(self):
        response = client.get("/health")
        assert response.json()["agents"] == 9


class TestStudentsEndpoint:
    def test_list_students_returns_200(self):
        assert client.get("/students").status_code == 200

    def test_list_students_returns_list(self):
        data = client.get("/students").json()
        assert isinstance(data, list) and len(data) > 0

    def test_list_students_has_required_fields(self):
        student = client.get("/students").json()[0]
        for field in ["name","className","workdaysBehind","status","incompleteCount"]:
            assert field in student

    def test_list_students_includes_bram_okafor(self):
        names = [s["name"] for s in client.get("/students").json()]
        assert "Bram Okafor" in names

    def test_list_students_includes_tara_voss(self):
        names = [s["name"] for s in client.get("/students").json()]
        assert "Tara Voss" in names

    def test_get_student_known(self):
        response = client.get("/students/Bram Okafor")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Bram Okafor"
        assert data["className"] == "26-2"
        assert data["workdaysBehind"] == 5
        assert data["status"] == "BEHIND"

    def test_get_student_on_track(self):
        response = client.get("/students/Petra Holst")
        assert response.status_code == 200
        assert response.json()["status"] == "ON TRACK"
        assert response.json()["workdaysBehind"] == 0

    def test_get_student_unknown_returns_404(self):
        response = client.get("/students/Ghost Person")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_student_yuki_tanaka(self):
        response = client.get("/students/Yuki Tanaka")
        assert response.status_code == 200
        data = response.json()
        assert data["className"] == "26-2"
        assert data["workdaysBehind"] == 3
        assert data["status"] == "BEHIND"


class TestClassesEndpoint:
    def test_list_classes_returns_200(self):
        assert client.get("/classes").status_code == 200

    def test_list_classes_returns_both_classes(self):
        names = [c["className"] for c in client.get("/classes").json()]
        assert "26-1" in names
        assert "26-2" in names

    def test_class_has_students(self):
        classes = {c["className"]: c for c in client.get("/classes").json()}
        assert len(classes["26-1"]["students"]) > 0
        assert len(classes["26-2"]["students"]) > 0

    def test_class_26_1_has_correct_event_count(self):
        classes = {c["className"]: c for c in client.get("/classes").json()}
        assert classes["26-1"]["eventCount"] == 9

    def test_class_26_2_includes_bram_okafor(self):
        classes = {c["className"]: c for c in client.get("/classes").json()}
        names = [s["name"] for s in classes["26-2"]["students"]]
        assert "Bram Okafor" in names


class TestNotificationsEndpoint:
    def test_notifications_returns_200(self):
        assert client.get("/notifications").status_code == 200

    def test_notifications_returns_list(self):
        assert isinstance(client.get("/notifications").json(), list)

    def test_notifications_has_required_fields_when_populated(self):
        from agents.instructor_notification import send_instructor_alert, NOTIFICATION_LOG
        NOTIFICATION_LOG.clear()
        send_instructor_alert.invoke({
            "student_name": "Bram Okafor",
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
        assert entry["student_name"] == "Bram Okafor"
        assert entry["alert_type"]   == "HIGH_RISK"
