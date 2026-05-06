"""
tests/test_data.py
------------------
Tests that validate the mock data is internally consistent.
Catches issues like students referencing classes that don't exist.
"""

import pytest
from data.mock_data import MOCK_SCHEDULES, MOCK_STUDENT_HISTORY, MOCK_REMEDIATION


class TestMockSchedules:
    def test_all_required_classes_present(self):
        assert "25-4" in MOCK_SCHEDULES
        assert "25-5" in MOCK_SCHEDULES

    def test_each_class_has_required_fields(self):
        for class_name, data in MOCK_SCHEDULES.items():
            assert "className" in data,  f"{class_name} missing className"
            assert "startDate" in data,  f"{class_name} missing startDate"
            assert "events"    in data,  f"{class_name} missing events"
            assert len(data["events"]) > 0, f"{class_name} has no events"

    def test_each_event_has_required_fields(self):
        for class_name, data in MOCK_SCHEDULES.items():
            for event in data["events"]:
                assert "eventCode"     in event, f"{class_name} event missing eventCode"
                assert "scheduledDate" in event, f"{class_name} event missing scheduledDate"
                assert "description"   in event, f"{class_name} event missing description"

    def test_event_codes_are_unique_within_class(self):
        for class_name, data in MOCK_SCHEDULES.items():
            codes = [e["eventCode"] for e in data["events"]]
            assert len(codes) == len(set(codes)), f"{class_name} has duplicate event codes"


class TestMockStudentHistory:
    def test_all_expected_students_present(self):
        assert "John Smith"    in MOCK_STUDENT_HISTORY
        assert "Jane Doe"      in MOCK_STUDENT_HISTORY
        assert "Carlos Rivera" in MOCK_STUDENT_HISTORY
        assert "Priya Patel"   in MOCK_STUDENT_HISTORY
        assert "Marcus Webb"   in MOCK_STUDENT_HISTORY


    def test_each_student_has_required_fields(self):
        for name, data in MOCK_STUDENT_HISTORY.items():
            assert "className"        in data, f"{name} missing className"
            assert "workdaysBehind"   in data, f"{name} missing workdaysBehind"
            assert "incompleteEvents" in data, f"{name} missing incompleteEvents"
            assert "completedEvents"  in data, f"{name} missing completedEvents"

    def test_student_classes_exist_in_schedules(self):
        for name, data in MOCK_STUDENT_HISTORY.items():
            class_name = data["className"]
            assert class_name in MOCK_SCHEDULES, \
                f"{name} references class {class_name} which doesn't exist in MOCK_SCHEDULES"

    def test_workdays_behind_is_non_negative(self):
        for name, data in MOCK_STUDENT_HISTORY.items():
            assert data["workdaysBehind"] >= 0, f"{name} has negative workdaysBehind"

    def test_completed_events_have_required_fields(self):
        for name, data in MOCK_STUDENT_HISTORY.items():
            for event in data["completedEvents"]:
                assert "eventCode"     in event, f"{name} completed event missing eventCode"
                assert "completedDate" in event, f"{name} completed event missing completedDate"
                assert "status"        in event, f"{name} completed event missing status"

    def test_no_event_in_both_complete_and_incomplete(self):
        for name, data in MOCK_STUDENT_HISTORY.items():
            completed_codes = {e["eventCode"] for e in data["completedEvents"]}
            incomplete_codes = set(data["incompleteEvents"])
            overlap = completed_codes & incomplete_codes
            assert not overlap, f"{name} has events in both complete and incomplete: {overlap}"

    def test_john_smith_is_behind(self):
        assert MOCK_STUDENT_HISTORY["John Smith"]["workdaysBehind"] > 0

    def test_jane_doe_is_on_track(self):
        assert MOCK_STUDENT_HISTORY["Jane Doe"]["workdaysBehind"] == 0

    def test_carlos_rivera_is_most_behind(self):
        days = {n: d["workdaysBehind"] for n, d in MOCK_STUDENT_HISTORY.items()}
        assert days["Carlos Rivera"] == max(days.values())

    def test_marcus_webb_is_behind(self):
        assert "Marcus Webb" in MOCK_STUDENT_HISTORY
        assert MOCK_STUDENT_HISTORY["Marcus Webb"]["workdaysBehind"] > 0
        assert MOCK_STUDENT_HISTORY["Marcus Webb"]["className"] == "25-4"
        assert len(MOCK_STUDENT_HISTORY["Marcus Webb"]["incompleteEvents"]) == 2

    def test_marcus_web_is_behind(self):
        assert "Marcus Webb"   in MOCK_STUDENT_HISTORY
        assert MOCK_STUDENT_HISTORY["Marcus Webb"]["workdaysBehind"] > 0
        assert MOCK_STUDENT_HISTORY["Marcus Webb"]["className"] == "25-4"
        assert len(MOCK_STUDENT_HISTORY["Marcus Webb"]["incompleteEvents"]) == 2

class TestMockRemediation:
    def test_remediation_options_present(self):
        assert len(MOCK_REMEDIATION) >= 3

    def test_all_options_are_non_empty_strings(self):
        for key, value in MOCK_REMEDIATION.items():
            assert isinstance(value, str) and len(value) > 0, \
                f"Remediation option '{key}' is empty"
