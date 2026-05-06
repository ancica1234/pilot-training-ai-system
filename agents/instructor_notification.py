from langchain_core.tools import tool
from data.mock_data import MOCK_STUDENT_HISTORY

# Mock instructor registry
MOCK_INSTRUCTORS = {
    '25-4': {
        'name': 'Lt. Commander Williams',
        'email': 'williams@navy.mil',
        'phone': '555-0101'
    },
    '25-5': {
        'name': 'Lt. Commander Chen',
        'email': 'chen@navy.mil',
        'phone': '555-0202'
    }
}

# Mock notification log (simulates sent notifications)
NOTIFICATION_LOG = []


@tool
def get_instructor_for_class(class_name: str) -> str:
    """Look up the assigned instructor for a given class."""
    instructor = MOCK_INSTRUCTORS.get(class_name)
    if not instructor:
        return 'No instructor found for class ' + class_name
    out  = 'Instructor for class ' + class_name + ':'
    out += ' Name: ' + instructor['name']
    out += ' | Email: ' + instructor['email']
    out += ' | Phone: ' + instructor['phone']
    return out


@tool
def send_instructor_alert(student_name: str, alert_type: str, message: str) -> str:
    """Send an alert to the instructor assigned to a student's class. alert_type should be one of: BEHIND_SCHEDULE, HIGH_RISK, REMEDIATION_ASSIGNED, ON_TRACK."""
    h = MOCK_STUDENT_HISTORY.get(student_name)
    if not h:
        return 'No student data found for ' + student_name

    class_name = h.get('className', 'Unknown')
    instructor = MOCK_INSTRUCTORS.get(class_name)
    if not instructor:
        return 'No instructor found for class ' + class_name

    # Log the notification (simulates sending)
    from datetime import datetime
    notification = {
        'timestamp':    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'student_name': student_name,
        'class_name':   class_name,
        'instructor':   instructor['name'],
        'email':        instructor['email'],
        'alert_type':   alert_type,
        'message':      message,
        'status':       'SENT'
    }
    NOTIFICATION_LOG.append(notification)

    out  = 'NOTIFICATION SENT'
    out += ' | To: ' + instructor['name'] + ' (' + instructor['email'] + ')'
    out += ' | Student: ' + student_name
    out += ' | Class: ' + class_name
    out += ' | Type: ' + alert_type
    out += ' | Message: ' + message
    return out


@tool
def get_notification_log() -> str:
    """Retrieve the log of all notifications that have been sent during this session."""
    if not NOTIFICATION_LOG:
        return 'No notifications have been sent this session.'
    out = 'Notification Log (' + str(len(NOTIFICATION_LOG)) + ' total):'
    for i, n in enumerate(NOTIFICATION_LOG, 1):
        out += ' | #' + str(i)
        out += ' [' + n['alert_type'] + ']'
        out += ' To: ' + n['instructor']
        out += ' Re: ' + n['student_name']
        out += ' Status: ' + n['status']
    return out


notification_tools = [get_instructor_for_class, send_instructor_alert, get_notification_log]
