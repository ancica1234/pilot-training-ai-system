"""
tests/test_tools.py
-------------------
Unit tests for every agent tool function.
These tests call tools directly — no LLM involved, no API key needed.
"""

import pytest
from data.mock_data import MOCK_STUDENT_HISTORY, MOCK_SCHEDULES


# ── Scheduler tools ────────────────────────────────────────────────────────────

class TestSchedulerTools:
    def test_get_class_schedule_known_class(self):
        from agents.scheduler import get_class_schedule
        result = get_class_schedule.invoke({"class_name": "25-4"})
        assert "25-4" in result
        assert "Introduction Flight" in result
        assert "01-01-25" in result

    def test_get_class_schedule_unknown_class(self):
        from agents.scheduler import get_class_schedule
        result = get_class_schedule.invoke({"class_name": "99-9"})
        assert "No schedule found" in result

    def test_get_student_history_known_student(self):
        from agents.scheduler import get_student_history
        result = get_student_history.invoke({"student_name": "John Smith"})
        assert "John Smith" in result
        assert "Workdays Behind: 5" in result
        assert "PENDING" in result

    def test_get_student_history_unknown_student(self):
        from agents.scheduler import get_student_history
        result = get_student_history.invoke({"student_name": "Ghost Person"})
        assert "No history found" in result

    def test_get_class_schedule_class_25_5(self):
        from agents.scheduler import get_class_schedule
        result = get_class_schedule.invoke({"class_name": "25-5"})
        assert "25-5" in result
        assert "Night Operations" in result

    def test_get_class_students_known_class(self):
        from agents.scheduler import get_class_students
        result = get_class_students.invoke({"class_name": "25-4"})
        assert "John Smith" in result
        assert "Marcus Webb" in result

    def test_get_class_students_unknown_class(self):
        from agents.scheduler import get_class_students
        result = get_class_students.invoke({"class_name": "99-9"})
        assert "No students found" in result

    def test_get_class_students_25_5(self):
        from agents.scheduler import get_class_students
        result = get_class_students.invoke({"class_name": "25-5"})
        assert "Carlos Rivera" in result


# ── Evaluator tools ────────────────────────────────────────────────────────────

class TestEvaluatorTools:
    def test_evaluate_progress_behind_student(self):
        from agents.evaluator import evaluate_progress
        result = evaluate_progress.invoke({"student_name": "John Smith"})
        assert "BEHIND" in result
        assert "REMEDIATION REQUIRED" in result
        assert "40%" in result

    def test_evaluate_progress_on_track_student(self):
        from agents.evaluator import evaluate_progress
        result = evaluate_progress.invoke({"student_name": "Jane Doe"})
        assert "ON TRACK" in result
        assert "REMEDIATION REQUIRED" not in result

    def test_evaluate_progress_unknown_student(self):
        from agents.evaluator import evaluate_progress
        result = evaluate_progress.invoke({"student_name": "Ghost Person"})
        assert "No data found" in result

    def test_evaluate_progress_class_25_5_students(self):
        from agents.evaluator import evaluate_progress
        for name in ["Carlos Rivera", "Priya Patel"]:
            result = evaluate_progress.invoke({"student_name": name})
            assert name in result


# ── Remediation tools ──────────────────────────────────────────────────────────

class TestRemediationTools:
    def test_get_remediation_plan_behind_student(self):
        from agents.remediation import get_remediation_plan
        result = get_remediation_plan.invoke({"student_name": "John Smith"})
        assert "John Smith" in result
        assert "Option" in result
        assert "5 days behind" in result

    def test_get_remediation_plan_on_track_student(self):
        from agents.remediation import get_remediation_plan
        result = get_remediation_plan.invoke({"student_name": "Jane Doe"})
        assert "on track" in result.lower()
        assert "no remediation needed" in result.lower()

    def test_get_remediation_plan_unknown_student(self):
        from agents.remediation import get_remediation_plan
        result = get_remediation_plan.invoke({"student_name": "Ghost Person"})
        assert "No data found" in result

    def test_recommend_best_option_minor_delay(self):
        from agents.remediation import recommend_best_option
        result = recommend_best_option.invoke({"student_name": "Jane Doe", "days_behind": 1})
        assert "Option 1" in result
        assert "makeup sessions" in result.lower()

    def test_recommend_best_option_moderate_delay(self):
        from agents.remediation import recommend_best_option
        result = recommend_best_option.invoke({"student_name": "John Smith", "days_behind": 5})
        assert "Option 3" in result
        assert "simulator" in result.lower()

    def test_recommend_best_option_severe_delay(self):
        from agents.remediation import recommend_best_option
        result = recommend_best_option.invoke({"student_name": "Carlos Rivera", "days_behind": 8})
        assert "Option 2" in result
        assert "tutoring" in result.lower()


# ── Risk assessment tools ──────────────────────────────────────────────────────

class TestRiskAssessmentTools:
    def test_assess_risk_high_risk_student(self):
        from agents.risk_assessment import assess_risk
        result = assess_risk.invoke({"student_name": "John Smith"})
        assert "HIGH" in result
        assert "ACTION REQUIRED" in result
        assert "Score" in result

    def test_assess_risk_low_risk_student(self):
        from agents.risk_assessment import assess_risk
        result = assess_risk.invoke({"student_name": "Jane Doe"})
        assert "LOW" in result
        assert "No immediate action" in result

    def test_assess_risk_unknown_student(self):
        from agents.risk_assessment import assess_risk
        result = assess_risk.invoke({"student_name": "Ghost Person"})
        assert "No data found" in result

    def test_compare_student_risks_known_class(self):
        from agents.risk_assessment import compare_student_risks
        result = compare_student_risks.invoke({"class_name": "25-4"})
        assert "25-4" in result
        assert "John Smith" in result
        assert "Jane Doe" in result
        # John Smith should be ranked higher risk than Jane Doe
        assert result.index("John Smith") < result.index("Jane Doe")

    def test_compare_student_risks_class_25_5(self):
        from agents.risk_assessment import compare_student_risks
        result = compare_student_risks.invoke({"class_name": "25-5"})
        assert "Carlos Rivera" in result
        assert "Priya Patel" in result
        # Carlos (8 days behind) should rank higher than Priya (2 days behind)
        assert result.index("Carlos Rivera") < result.index("Priya Patel")

    def test_compare_student_risks_unknown_class(self):
        from agents.risk_assessment import compare_student_risks
        result = compare_student_risks.invoke({"class_name": "99-9"})
        assert "No students found" in result


# ── Instructor notification tools ──────────────────────────────────────────────

class TestNotificationTools:
    def test_get_instructor_for_known_class(self):
        from agents.instructor_notification import get_instructor_for_class
        result = get_instructor_for_class.invoke({"class_name": "25-4"})
        assert "Lt. Commander Williams" in result
        assert "williams@navy.mil" in result

    def test_get_instructor_for_class_25_5(self):
        from agents.instructor_notification import get_instructor_for_class
        result = get_instructor_for_class.invoke({"class_name": "25-5"})
        assert "Lt. Commander Chen" in result
        assert "chen@navy.mil" in result

    def test_get_instructor_for_unknown_class(self):
        from agents.instructor_notification import get_instructor_for_class
        result = get_instructor_for_class.invoke({"class_name": "99-9"})
        assert "No instructor found" in result

    def test_send_instructor_alert_success(self):
        from agents.instructor_notification import send_instructor_alert, NOTIFICATION_LOG
        initial_count = len(NOTIFICATION_LOG)
        result = send_instructor_alert.invoke({
            "student_name": "John Smith",
            "alert_type":   "HIGH_RISK",
            "message":      "Test alert"
        })
        assert "NOTIFICATION SENT" in result
        assert "Lt. Commander Williams" in result
        assert "HIGH_RISK" in result
        assert len(NOTIFICATION_LOG) == initial_count + 1

    def test_send_instructor_alert_unknown_student(self):
        from agents.instructor_notification import send_instructor_alert
        result = send_instructor_alert.invoke({
            "student_name": "Ghost Person",
            "alert_type":   "HIGH_RISK",
            "message":      "Test"
        })
        assert "No student data found" in result

    def test_get_notification_log_empty(self):
        from agents.instructor_notification import get_notification_log, NOTIFICATION_LOG
        NOTIFICATION_LOG.clear()
        result = get_notification_log.invoke({})
        assert "No notifications" in result

    def test_get_notification_log_with_entries(self):
        from agents.instructor_notification import get_notification_log, NOTIFICATION_LOG, send_instructor_alert
        NOTIFICATION_LOG.clear()
        send_instructor_alert.invoke({
            "student_name": "John Smith",
            "alert_type":   "BEHIND_SCHEDULE",
            "message":      "Test"
        })
        result = get_notification_log.invoke({})
        assert "1 total" in result
        assert "BEHIND_SCHEDULE" in result
