from langchain_core.tools import tool
from data.mock_data import MOCK_SCHEDULES, MOCK_STUDENT_HISTORY

@tool
def get_class_schedule(class_name: str) -> str:
    """Fetch the training schedule for a given class including all events and dates."""
    s = MOCK_SCHEDULES.get(class_name)
    if not s: return 'No schedule found for class ' + class_name
    out = 'Class ' + class_name + ' started ' + s['startDate']
    for e in s['events']:
        out += ' | ' + e['eventCode'] + ' ' + e['description'] + ' ' + e['scheduledDate']
    return out

@tool
def get_class_students(class_name: str) -> str:
    """Return all student names enrolled in a given class."""
    students = []
    for name, data in MOCK_STUDENT_HISTORY.items():
        if data.get('className') == class_name:
            students.append(name)
    if not students:
        return 'No students found for class ' + class_name
    return 'Class ' + class_name + ' students: ' + ' | '.join(students)


@tool
def get_student_history(student_name: str) -> str:
    """Fetch student event completion history including completed and incomplete events and workdays behind."""
    h = MOCK_STUDENT_HISTORY.get(student_name)
    if not h: return 'No history found for ' + student_name
    out = 'Student: ' + student_name
    out += ' | Workdays Behind: ' + str(h['workdaysBehind'])
    for e in h['completedEvents']:
        out += ' || DONE ' + e['eventCode'] + ' ' + e['status']
    for e in h['incompleteEvents']:
        out += ' || PENDING ' + e
    return out

scheduler_tools = [get_class_schedule, get_student_history, get_class_students]
