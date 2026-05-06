from langchain_core.tools import tool
from data.mock_data import MOCK_STUDENT_HISTORY

@tool
def assess_risk(student_name: str) -> str:
    """Assess the risk level of a student failing to complete training on time. Returns LOW, MEDIUM, or HIGH risk with justification."""
    h = MOCK_STUDENT_HISTORY.get(student_name)
    if not h:
        return 'No data found for ' + student_name

    behind      = h['workdaysBehind']
    incomplete  = len(h['incompleteEvents'])
    completed   = len(h['completedEvents'])
    total       = completed + incomplete
    pct_done    = round((completed / total) * 100) if total > 0 else 0
    pct_remain  = 100 - pct_done

    # Risk scoring
    score = 0
    reasons = []

    if behind == 0:
        reasons.append('on track with schedule')
    elif behind <= 2:
        score += 1
        reasons.append(str(behind) + ' workdays behind (minor)')
    elif behind <= 5:
        score += 2
        reasons.append(str(behind) + ' workdays behind (moderate)')
    else:
        score += 3
        reasons.append(str(behind) + ' workdays behind (severe)')

    if pct_remain <= 20:
        reasons.append('nearly complete (' + str(pct_done) + '% done)')
    elif pct_remain <= 50:
        score += 1
        reasons.append(str(incomplete) + ' events remaining (' + str(pct_remain) + '%)')
    else:
        score += 2
        reasons.append('majority of training remaining (' + str(pct_remain) + '%)')

    if incomplete >= 3:
        score += 1
        reasons.append(str(incomplete) + ' incomplete events is concerning')

    # Determine risk level
    if score <= 1:
        risk = 'LOW'
    elif score <= 3:
        risk = 'MEDIUM'
    else:
        risk = 'HIGH'

    out  = 'Risk Assessment for ' + student_name + ':'
    out += ' Risk Level: ' + risk
    out += ' | Score: ' + str(score) + '/6'
    out += ' | Factors: ' + ', '.join(reasons)

    if risk == 'HIGH':
        out += ' | ACTION REQUIRED: Immediate intervention recommended'
    elif risk == 'MEDIUM':
        out += ' | MONITOR: Close monitoring and proactive support advised'
    else:
        out += ' | STATUS: No immediate action required'

    return out


@tool
def compare_student_risks(class_name: str) -> str:
    """Compare risk levels of all students in a class and rank them from highest to lowest risk."""
    from data.mock_data import MOCK_STUDENT_HISTORY

    # Find all students in the class
    class_students = [
        name for name, data in MOCK_STUDENT_HISTORY.items()
        if data.get('className') == class_name
    ]

    if not class_students:
        return 'No students found for class ' + class_name

    results = []
    for name in class_students:
        h = MOCK_STUDENT_HISTORY[name]
        behind     = h['workdaysBehind']
        incomplete = len(h['incompleteEvents'])
        completed  = len(h['completedEvents'])
        total      = completed + incomplete
        pct_done   = round((completed / total) * 100) if total > 0 else 0

        score = 0
        if behind > 5:   score += 3
        elif behind > 2: score += 2
        elif behind > 0: score += 1

        pct_remain = 100 - pct_done
        if pct_remain > 50:   score += 2
        elif pct_remain > 20: score += 1

        if incomplete >= 3: score += 1

        risk = 'HIGH' if score > 3 else ('MEDIUM' if score > 1 else 'LOW')
        results.append((name, risk, score, behind, pct_done))

    # Sort by score descending (highest risk first)
    results.sort(key=lambda x: x[2], reverse=True)

    out = 'Class ' + class_name + ' Risk Ranking:'
    for rank, (name, risk, score, behind, pct) in enumerate(results, 1):
        out += ' | #' + str(rank) + ' ' + name
        out += ' [' + risk + '] score=' + str(score)
        out += ' behind=' + str(behind) + 'days'
        out += ' complete=' + str(pct) + '%'

    return out


risk_tools = [assess_risk, compare_student_risks]
