from langchain_core.tools import tool
from data.mock_data import MOCK_STUDENT_HISTORY, MOCK_REMEDIATION

@tool
def get_remediation_plan(student_name: str) -> str:
    """Generate a remediation plan for a student who is behind schedule. Only call this if the student is behind."""
    h = MOCK_STUDENT_HISTORY.get(student_name)
    if not h: return 'No data found for ' + student_name
    if h['workdaysBehind'] == 0: return student_name + ' is on track - no remediation needed'
    out = 'Remediation Plan for ' + student_name + ' (' + str(h['workdaysBehind']) + ' days behind):'
    for i, (k, v) in enumerate(MOCK_REMEDIATION.items()):
        out += ' | Option ' + str(i+1) + ': ' + v
    return out

@tool
def recommend_best_option(student_name: str, days_behind: int) -> str:
    """Recommend the single best remediation option based on how many days behind the student is."""
    if days_behind <= 2:
        return 'Recommendation for ' + student_name + ': Option 1 - Makeup sessions on weekends is sufficient for minor delays'
    elif days_behind <= 5:
        return 'Recommendation for ' + student_name + ': Option 3 - Add simulator hours plus makeup sessions for moderate delays'
    else:
        return 'Recommendation for ' + student_name + ': Option 2 - Peer tutoring combined with makeup sessions for significant delays'

remediation_tools = [get_remediation_plan, recommend_best_option]
