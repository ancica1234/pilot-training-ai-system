
from langchain_core.tools import tool
from data.mock_data import MOCK_SNIVS, MOCK_PERSONNEL, MOCK_FLIGHT_LINES

@tool
def get_snivs_for_date(date: str) -> str:
    """Return all SNIV (unavailability) records for a given date.
    A SNIV means the person has requested NOT to be scheduled.
    date format: YYYY-MM-DD"""
    snivs = [s for s in MOCK_SNIVS if s['date'] == date]
    if not snivs:
        return f'No SNIVs recorded for {date}'
    out = f'SNIVs for {date} ({len(snivs)} total):'
    for s in snivs:
        out += f' | {s["person"]} — Reason: {s["reason"]} — Source: {s["source"]}'
    return out

@tool
def check_double_schedule(date: str) -> str:
    """Check if any person is both SNIV'd and still scheduled for a flight on a given date.
    Returns a list of conflicts (double-schedule flags).
    date format: YYYY-MM-DD"""
    snived = {s['person'] for s in MOCK_SNIVS if s['date'] == date}
    lines = MOCK_FLIGHT_LINES.get(date, [])
    scheduled_people = set()
    for line in lines:
        if line.get('ip'):      scheduled_people.add(line['ip'])
        if line.get('student'): scheduled_people.add(line['student'])

    conflicts = snived & scheduled_people
    if not conflicts:
        return f'No double-schedule conflicts found for {date}'
    out = f'DOUBLE SCHEDULE CONFLICTS for {date}:'
    for person in conflicts:
        out += f' | {person} is SNIVED but appears on the flight schedule — NEEDS RESOLUTION'
    return out

@tool
def get_personnel_availability_summary(date: str) -> str:
    """Return a full daily availability summary for all personnel.
    Combines SNIV data, med-down status, and reservist drill-day availability.
    Mirrors the Personnel Availability tab on the Weekly spreadsheet.
    date format: YYYY-MM-DD"""
    snived_today = {s['person'] for s in MOCK_SNIVS if s['date'] == date}
    out = f'Personnel Availability Summary for {date}:'

    for category in ['Instructor', 'Student']:
        people = MOCK_PERSONNEL.get(category, {})
        for name, data in people.items():
            flags = []
            if name in snived_today:
                flags.append('SNIVED')
            if data.get('med_down'):
                flags.append('MED DOWN')
            if data.get('snived'):
                flags.append('SNIVED(sys)')
            if data.get('type') == 'RESERVIST':
                drill = data.get('drill_days', [])
                flags.append('DRILL' if date in drill else 'NO-DRILL')
            status = 'UNAVAILABLE' if any(f in flags for f in ['SNIVED','SNIVED(sys)','MED DOWN']) else 'AVAILABLE'
            if data.get('type') == 'RESERVIST' and 'DRILL' not in flags:
                status = 'UNAVAILABLE'
            flags_str = ' [' + ', '.join(flags) + ']' if flags else ''
            out += f' | {category}: {name} ({data.get("type","?")}) — {status}{flags_str}'
    return out

sniv_tools = [get_snivs_for_date, check_double_schedule, get_personnel_availability_summary]
