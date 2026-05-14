"""
tests/test_tools.py
---------------
Unit tests for every agent tool. No LLM, no API key needed.
"""
import pytest
from data.mock_data import MOCK_STUDENT_HISTORY, MOCK_SCHEDULES


# Scheduler tools
class TestSchedulerTools:
    def test_get_class_schedule_known_class(self):
        from agents.scheduler import get_class_schedule
        result = get_class_schedule.invoke({"class_name": "26-1"})
        assert "26-1" in result
        assert "Introduction Flight" in result

    def test_get_class_schedule_unknown_class(self):
        from agents.scheduler import get_class_schedule
        result = get_class_schedule.invoke({"class_name": "99-9"})
        assert "No schedule found" in result

    def test_get_student_history_known_student(self):
        from agents.scheduler import get_student_history
        result = get_student_history.invoke({"student_name": "Bram Okafor"})
        assert "Bram Okafor" in result
        assert "Workdays Behind: 5" in result
        assert "PENDING" in result

    def test_get_student_history_unknown_student(self):
        from agents.scheduler import get_student_history
        result = get_student_history.invoke({"student_name": "Ghost Person"})
        assert "No history found" in result

    def test_get_class_schedule_class_26_2(self):
        from agents.scheduler import get_class_schedule
        result = get_class_schedule.invoke({"class_name": "26-2"})
        assert "26-2" in result
        assert "Night Operations" in result

    def test_get_class_students_known_class(self):
        from agents.scheduler import get_class_students
        result = get_class_students.invoke({"class_name": "26-2"})
        assert "Bram Okafor" in result
        assert "Yuki Tanaka" in result

    def test_get_class_students_unknown_class(self):
        from agents.scheduler import get_class_students
        result = get_class_students.invoke({"class_name": "99-9"})
        assert "No students found" in result

    def test_get_class_students_26_1(self):
        from agents.scheduler import get_class_students
        result = get_class_students.invoke({"class_name": "26-1"})
        assert "Tara Voss" in result


# Evaluator tools
class TestEvaluatorTools:
    def test_evaluate_progress_behind_student(self):
        from agents.evaluator import evaluate_progress
        result = evaluate_progress.invoke({"student_name": "Bram Okafor"})
        assert "BEHIND" in result
        assert "REMEDIATION REQUIRED" in result

    def test_evaluate_progress_on_track_student(self):
        from agents.evaluator import evaluate_progress
        result = evaluate_progress.invoke({"student_name": "Petra Holst"})
        assert "ON TRACK" in result
        assert "REMEDIATION REQUIRED" not in result

    def test_evaluate_progress_unknown_student(self):
        from agents.evaluator import evaluate_progress
        result = evaluate_progress.invoke({"student_name": "Ghost Person"})
        assert "No data found" in result

    def test_evaluate_progress_class_26_1_students(self):
        from agents.evaluator import evaluate_progress
        for name in ["Tara Voss", "Leon Marsh"]:
            result = evaluate_progress.invoke({"student_name": name})
            assert name in result


# Remediation tools
class TestRemediationTools:
    def test_get_remediation_plan_behind_student(self):
        from agents.remediation import get_remediation_plan
        result = get_remediation_plan.invoke({"student_name": "Bram Okafor"})
        assert "Bram Okafor" in result
        assert "Option" in result
        assert "5 days behind" in result

    def test_get_remediation_plan_on_track_student(self):
        from agents.remediation import get_remediation_plan
        result = get_remediation_plan.invoke({"student_name": "Petra Holst"})
        assert "on track" in result.lower()

    def test_get_remediation_plan_unknown_student(self):
        from agents.remediation import get_remediation_plan
        result = get_remediation_plan.invoke({"student_name": "Ghost Person"})
        assert "No data found" in result

    def test_recommend_best_option_minor_delay(self):
        from agents.remediation import recommend_best_option
        result = recommend_best_option.invoke({"student_name": "Leon Marsh", "days_behind": 2})
        assert "Option 1" in result
        assert "makeup" in result.lower()

    def test_recommend_best_option_moderate_delay(self):
        from agents.remediation import recommend_best_option
        result = recommend_best_option.invoke({"student_name": "Bram Okafor", "days_behind": 5})
        assert "Option 3" in result
        assert "simulator" in result.lower()

    def test_recommend_best_option_severe_delay(self):
        from agents.remediation import recommend_best_option
        result = recommend_best_option.invoke({"student_name": "Tara Voss", "days_behind": 8})
        assert "Option 2" in result
        assert "tutoring" in result.lower()


# Risk assessment tools
class TestRiskAssessmentTools:
    def test_assess_risk_high_risk_student(self):
        from agents.risk_assessment import assess_risk
        result = assess_risk.invoke({"student_name": "Tara Voss"})
        assert "HIGH" in result
        assert "ACTION REQUIRED" in result
        assert "Score" in result

    def test_assess_risk_low_risk_student(self):
        from agents.risk_assessment import assess_risk
        result = assess_risk.invoke({"student_name": "Petra Holst"})
        assert "LOW" in result
        assert "No immediate action" in result

    def test_assess_risk_unknown_student(self):
        from agents.risk_assessment import assess_risk
        result = assess_risk.invoke({"student_name": "Ghost Person"})
        assert "No data found" in result

    def test_compare_student_risks_known_class(self):
        from agents.risk_assessment import compare_student_risks
        result = compare_student_risks.invoke({"class_name": "26-2"})
        assert "26-2" in result
        assert "Bram Okafor" in result
        assert "Petra Holst" in result
        assert result.index("Bram Okafor") < result.index("Petra Holst")

    def test_compare_student_risks_class_26_1(self):
        from agents.risk_assessment import compare_student_risks
        result = compare_student_risks.invoke({"class_name": "26-1"})
        assert "Tara Voss" in result
        assert "Dana Quirke" in result
        assert result.index("Tara Voss") < result.index("Dana Quirke")

    def test_compare_student_risks_unknown_class(self):
        from agents.risk_assessment import compare_student_risks
        result = compare_student_risks.invoke({"class_name": "99-9"})
        assert "No students found" in result


# Notification tools
class TestNotificationTools:
    def test_get_instructor_for_known_class(self):
        from agents.instructor_notification import get_instructor_for_class
        result = get_instructor_for_class.invoke({"class_name": "26-1"})
        assert "Instructor" in result

    def test_get_instructor_for_unknown_class(self):
        from agents.instructor_notification import get_instructor_for_class
        result = get_instructor_for_class.invoke({"class_name": "99-9"})
        assert "No instructor found" in result

    def test_send_instructor_alert_success(self):
        from agents.instructor_notification import send_instructor_alert, NOTIFICATION_LOG
        initial_count = len(NOTIFICATION_LOG)
        result = send_instructor_alert.invoke({
            "student_name": "Bram Okafor",
            "alert_type":   "HIGH_RISK",
            "message":      "Test alert"
        })
        assert "NOTIFICATION SENT" in result
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
            "student_name": "Bram Okafor",
            "alert_type":   "BEHIND_SCHEDULE",
            "message":      "Test"
        })
        result = get_notification_log.invoke({})
        assert "1 total" in result
        assert "BEHIND_SCHEDULE" in result


# IP Hotboard tools
class TestIPHotboardTools:
    def test_get_ip_hotboard(self):
        from agents.ip_hotboard import get_ip_hotboard
        result = get_ip_hotboard.invoke({"date": "2026-04-06"})
        assert "IP Hotboard for 2026-04-06" in result
        assert "Noel Drax" in result
        assert "AVAILABLE" in result

    def test_get_ip_hotboard_excludes_snived(self):
        from agents.ip_hotboard import get_ip_hotboard
        result = get_ip_hotboard.invoke({"date": "2026-04-06"})
        assert "SNIVED" in result or "MED DOWN" in result

    def test_get_instructor_availability(self):
        from agents.ip_hotboard import get_instructor_availability
        result = get_instructor_availability.invoke({"date": "2026-04-06"})
        assert "Instructor availability for 2026-04-06" in result
        assert "Gale Rynder" in result

    def test_get_qualified_ips_cal(self):
        from agents.ip_hotboard import get_qualified_ips
        result = get_qualified_ips.invoke({"event_type": "CAL", "date": "2026-04-06"})
        assert "Qualified IPs for CAL" in result

    def test_get_qualified_ips_fcf(self):
        from agents.ip_hotboard import get_qualified_ips
        result = get_qualified_ips.invoke({"event_type": "FCF", "date": "2026-04-06"})
        assert "Qualified IPs for FCF" in result
        assert "Gale Rynder" in result or "Selma Varga" in result


# SNIV tracker tools
class TestSnivTrackerTools:
    def test_get_snivs_for_date(self):
        from agents.sniv_tracker import get_snivs_for_date
        result = get_snivs_for_date.invoke({"date": "2026-04-06"})
        assert "Otto Finch" in result
        assert "Preet Aulakh" in result

    def test_get_snivs_no_snivs(self):
        from agents.sniv_tracker import get_snivs_for_date
        result = get_snivs_for_date.invoke({"date": "2026-01-01"})
        assert "No SNIVs" in result

    def test_check_double_schedule(self):
        from agents.sniv_tracker import check_double_schedule
        result = check_double_schedule.invoke({"date": "2026-04-06"})
        assert isinstance(result, str)

    def test_get_personnel_availability_summary(self):
        from agents.sniv_tracker import get_personnel_availability_summary
        result = get_personnel_availability_summary.invoke({"date": "2026-04-06"})
        assert "Personnel Availability Summary" in result
        assert "Gale Rynder" in result


# Ground school tools
class TestGroundSchoolTools:
    def test_get_ground_school_schedule(self):
        from agents.ground_school import get_ground_school_schedule
        result = get_ground_school_schedule.invoke({"date": "2026-04-06"})
        assert "Ground School Schedule for 2026-04-06" in result
        assert "Course Rules Brief" in result

    def test_get_ground_school_schedule_unknown_date(self):
        from agents.ground_school import get_ground_school_schedule
        result = get_ground_school_schedule.invoke({"date": "2026-01-01"})
        assert "No ground school events" in result

    def test_check_csi_availability(self):
        from agents.ground_school import check_csi_availability
        result = check_csi_availability.invoke({"date": "2026-04-07"})
        assert "CSI Availability check" in result
        assert "CSI-required events" in result

    def test_get_ground_school_week(self):
        from agents.ground_school import get_ground_school_week
        result = get_ground_school_week.invoke({"start_date": "2026-04-06"})
        assert "Ground School Week" in result


# Flight scheduler tools
class TestFlightSchedulerTools:
    def test_get_daily_flight_schedule(self):
        from agents.flight_scheduler import get_daily_flight_schedule
        result = get_daily_flight_schedule.invoke({"date": "2026-04-06"})
        assert "Flight Schedule for 2026-04-06" in result
        assert "MSN" in result
        assert "Gale Rynder" in result

    def test_get_daily_flight_schedule_unknown_date(self):
        from agents.flight_scheduler import get_daily_flight_schedule
        result = get_daily_flight_schedule.invoke({"date": "2026-01-01"})
        assert "No flight lines" in result

    def test_get_daily_whiteboard(self):
        from agents.flight_scheduler import get_daily_whiteboard
        result = get_daily_whiteboard.invoke({"date": "2026-04-06"})
        assert "Daily Whiteboard" in result
        assert "FLIGHT EVENT" in result
        assert "SNIVED" in result

    def test_get_priority_students(self):
        from agents.flight_scheduler import get_priority_students
        result = get_priority_students.invoke({"date": "2026-04-06"})
        assert "Student Priority List" in result
        assert "AF" in result
        assert result.index("AF") < result.index("STANDARD")

    def test_get_aircraft_status(self):
        from agents.flight_scheduler import get_aircraft_status
        result = get_aircraft_status.invoke({})
        assert "Aircraft Fleet Status" in result
        assert "FMC" in result
        assert "NMC" in result

    def test_get_enviro_data(self):
        from agents.flight_scheduler import get_enviro_data
        result = get_enviro_data.invoke({"date": "2026-04-06"})
        assert "Environment Data for 2026-04-06" in result
        assert "Sunset" in result
        assert "EENT" in result
        assert "1935" in result
