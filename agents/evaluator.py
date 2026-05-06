from langchain_core.tools import tool
from data.mock_data import MOCK_STUDENT_HISTORY

@tool
def evaluate_progress(student_name: str) -> str:
    """Evaluate if a student is on track or behind schedule and summarize their training status."""
    h = MOCK_STUDENT_HISTORY.get(student_name)
    if not h: return 'No data found for ' + student_name
    behind = h['workdaysBehind']
    completed = len(h['completedEvents'])
    incomplete = len(h['incompleteEvents'])
    total = completed + incomplete
    pct = round((completed / total) * 100) if total > 0 else 0
    status = 'BEHIND' if behind > 0 else 'ON TRACK'
    out = 'Evaluation for ' + student_name + ':'
    out += ' Status: ' + status
    out += ' | Progress: ' + str(completed) + '/' + str(total) + ' events (' + str(pct) + '%)'
    out += ' | Workdays Behind: ' + str(behind)
    if behind > 0:
        out += ' | REMEDIATION REQUIRED'
    return out

evaluator_tools = [evaluate_progress]
