
from langchain_core.tools import tool
from data.mock_data import MOCK_GROUND_SCHOOL, MOCK_PERSONNEL, MOCK_SNIVS

@tool
def get_ground_school_schedule(date: str) -> str:
    """Return the ground school events scheduled for a given date.
    Includes event codes, titles, times, CSI requirements, and outside-agency flags.
    date format: YYYY-MM-DD"""
    day = MOCK_GROUND_SCHOOL.get(date)
    if not day:
        return f'No ground school events found for {date}'
    out = f'Ground School Schedule for {date} (Day {day["day_number"]}):'
    if day['holiday']:
        out += ' | HOLIDAY — no events scheduled'
        return out
    for ev in day['events']:
        csi = ' [CSI REQUIRED]' if ev['csi_required'] else ''
        agency = ' [OUTSIDE AGENCY]' if ev['outside_agency'] else ''
        out += f' | {ev["code"]} {ev["title"]} @ {ev["start"]} ({ev["duration_hrs"]}hrs){csi}{agency}'
    if day['notes']:
        out += f' | NOTE: {day["notes"]}'
    return out

@tool
def check_csi_availability(date: str) -> str:
    """Check whether a CSI (Certified Simulator Instructor) is available on a given date.
    Flags a warning if CSI events are scheduled but no CSI is available.
    date format: YYYY-MM-DD"""
    day = MOCK_GROUND_SCHOOL.get(date)
    if not day:
        return f'No ground school data for {date}'
    csi_events = [ev for ev in day['events'] if ev['csi_required']]
    if not csi_events:
        return f'No CSI-required events on {date} — no CSI needed'

    snived_today = {s['person'] for s in MOCK_SNIVS if s['date'] == date}
    # IPs with FCF qualification are treated as CSI-capable in this mock
    csi_capable = [
        name for name, data in MOCK_PERSONNEL['Instructor'].items()
        if 'FCF' in data.get('qualifications', [])
        and not data.get('med_down')
        and not data.get('snived')
        and name not in snived_today
    ]

    out = f'CSI Availability check for {date}:'
    out += f' | CSI-required events: {len(csi_events)}'
    if csi_capable:
        out += f' | CSI available: {", ".join(csi_capable)} — OK'
    else:
        out += ' | WARNING: No CSI available — CSI-required events are at risk'
    for ev in csi_events:
        out += f' | Needs CSI: {ev["code"]} {ev["title"]} @ {ev["start"]}'
    return out

@tool
def get_ground_school_week(start_date: str) -> str:
    """Return ground school events for the full week starting from start_date.
    Useful for weekly planning and identifying CSI conflicts in advance.
    date format: YYYY-MM-DD"""
    from datetime import datetime, timedelta
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        return f'Invalid date format: {start_date}. Use YYYY-MM-DD'
    out = f'Ground School Week starting {start_date}:'
    found = False
    for i in range(7):
        d = (start + timedelta(days=i)).strftime('%Y-%m-%d')
        day = MOCK_GROUND_SCHOOL.get(d)
        if day:
            found = True
            event_titles = [ev["title"] for ev in day["events"]]
            csi_needed = any(ev["csi_required"] for ev in day["events"])
            csi_flag = ' [CSI NEEDED]' if csi_needed else ''
            out += f' | {d} (Day {day["day_number"]}): {len(day["events"])} events — {chr(10).join(event_titles) if len(event_titles) <= 2 else str(len(event_titles)) + " events"}{csi_flag}'
    if not found:
        out += ' | No ground school events found for this week'
    return out

ground_school_tools = [get_ground_school_schedule, check_csi_availability, get_ground_school_week]
