"""
tests/test_data.py
------------------
Tests that validate the mock data is internally consistent.
"""
import pytest
from data.mock_data import MOCK_SCHEDULES, MOCK_STUDENT_HISTORY, MOCK_REMEDIATION


class TestMockSchedules:
    def test_all_required_classes_present(self):
        assert "26-1" in MOCK_SCHEDULES
        assert "26-2" in MOCK_SCHEDULES

    def test_each_class_has_required_fields(self):
        for class_name, data in MOCK_SCHEDULES.items():
            assert "className" in data
            assert "startDate" in data
            assert "events"    in data
            assert len(data["events"]) > 0

    def test_each_event_has_required_fields(self):
        for class_name, data in MOCK_SCHEDULES.items():
            for event in data["events"]:
                assert "eventCode"     in event
                assert "scheduledDate" in event
                assert "description"   in event

    def test_event_codes_are_unique_within_class(self):
        for class_name, data in MOCK_SCHEDULES.items():
            codes = [e["eventCode"] for e in data["events"]]
            assert len(codes) == len(set(codes))

    def test_classes_have_mixed_event_types(self):
        for class_name, data in MOCK_SCHEDULES.items():
            types = {e.get("type") for e in data["events"]}
            assert "FLIGHT" in types
            assert "SIM" in types
            assert "GROUND" in types


class TestMockStudentHistory:
    def test_all_expected_students_present(self):
        for name in ["Tara Voss", "Leon Marsh", "Dana Quirke",
                     "Bram Okafor", "Yuki Tanaka", "Petra Holst"]:
            assert name in MOCK_STUDENT_HISTORY

    def test_each_student_has_required_fields(self):
        for name, data in MOCK_STUDENT_HISTORY.items():
            assert "className"        in data
            assert "workdaysBehind"   in data
            assert "incompleteEvents" in data
            assert "completedEvents"  in data
            assert "priority"         in data

    def test_student_classes_exist_in_schedules(self):
        for name, data in MOCK_STUDENT_HISTORY.items():
            assert data["className"] in MOCK_SCHEDULES

    def test_workdays_behind_is_non_negative(self):
        for name, data in MOCK_STUDENT_HISTORY.items():
            assert data["workdaysBehind"] >= 0

    def test_completed_events_have_required_fields(self):
        for name, data in MOCK_STUDENT_HISTORY.items():
            for event in data["completedEvents"]:
                assert "eventCode"     in event
                assert "completedDate" in event
                assert "status"        in event

    def test_no_event_in_both_complete_and_incomplete(self):
        for name, data in MOCK_STUDENT_HISTORY.items():
            completed = {e["eventCode"] for e in data["completedEvents"]}
            incomplete = set(data["incompleteEvents"])
            assert not (completed & incomplete)

    def test_tara_voss_is_most_behind(self):
        days = {n: d["workdaysBehind"] for n, d in MOCK_STUDENT_HISTORY.items()}
        assert days["Tara Voss"] == max(days.values())

    def test_petra_holst_is_on_track(self):
        assert MOCK_STUDENT_HISTORY["Petra Holst"]["workdaysBehind"] == 0

    def test_bram_okafor_is_behind(self):
        assert MOCK_STUDENT_HISTORY["Bram Okafor"]["workdaysBehind"] > 0
        assert MOCK_STUDENT_HISTORY["Bram Okafor"]["className"] == "26-2"

    def test_dana_quirke_is_af_priority(self):
        assert MOCK_STUDENT_HISTORY["Dana Quirke"]["priority"] == "AF"

    def test_leon_marsh_is_refresh_priority(self):
        assert MOCK_STUDENT_HISTORY["Leon Marsh"]["priority"] == "REFRESH"

    def test_priority_values_are_valid(self):
        valid = {"AF", "REFRESH", "STANDARD"}
        for name, data in MOCK_STUDENT_HISTORY.items():
            assert data["priority"] in valid


class TestMockRemediation:
    def test_remediation_options_present(self):
        assert len(MOCK_REMEDIATION) >= 3

    def test_all_options_are_non_empty_strings(self):
        for key, value in MOCK_REMEDIATION.items():
            assert isinstance(value, str) and len(value) > 0
