
from langchain_core.tools import tool
from data.mock_data import MOCK_IP_HOTBOARD, MOCK_PERSONNEL, MOCK_SNIVS

@tool
def get_ip_hotboard(date: str) -> str:
    """Return instructors ranked by least flight hours (hotboard order).
    Only includes instructors available on the given date (not SNIV'd or med-down).
    date format: YYYY-MM-DD"""
    snived_today = {s['person'] for s in MOCK_SNIVS if s['date'] == date}
    med_down = {
        name for name, data in MOCK_PERSONNEL['Instructor'].items()
        if data.get('med_down')
    }
    blocked = snived_today | med_down

    available = [ip for ip in MOCK_IP_HOTBOARD if ip['name'] not in blocked]
    unavailable = [ip for ip in MOCK_IP_HOTBOARD if ip['name'] in blocked]

    available.sort(key=lambda x: x['flight_hours_ytd'])

    out = f'IP Hotboard for {date} (ranked by least flight hours):'
    for rank, ip in enumerate(available, 1):
        out += f' | #{rank} {ip["name"]} — {ip["flight_hours_ytd"]}hrs YTD — last flew {ip["last_flight"]} — AVAILABLE'
    for ip in unavailable:
        reason = 'MED DOWN' if ip['name'] in med_down else 'SNIVED'
        out += f' | {ip["name"]} — {ip["flight_hours_ytd"]}hrs YTD — {reason} (not available)'
    return out

@tool
def get_instructor_availability(date: str) -> str:
    """Return full availability status for all instructors on a given date.
    Shows type (Active/AF/Reservist/Non-Perm), SNIV status, med status, and drill days.
    date format: YYYY-MM-DD"""
    snived_today = {s['person'] for s in MOCK_SNIVS if s['date'] == date}
    out = f'Instructor availability for {date}:'
    for name, data in MOCK_PERSONNEL['Instructor'].items():
        status_flags = []
        if data.get('snived') or name in snived_today:
            status_flags.append('SNIVED')
        if data.get('med_down'):
            status_flags.append('MED DOWN')
        if data['type'] == 'RESERVIST':
            drill = data.get('drill_days', [])
            if date in drill:
                status_flags.append('DRILL DAY')
            else:
                status_flags.append('NOT DRILL DAY')
        availability = 'UNAVAILABLE' if status_flags else 'AVAILABLE'
        flags_str = '(' + ', '.join(status_flags) + ')' if status_flags else ''
        out += f' | {name} [{data["type"]}] {data["flight_hours_ytd"]}hrs — {availability} {flags_str}'
    return out

@tool
def get_qualified_ips(event_type: str, date: str) -> str:
    """Return instructors qualified for a specific event type (CAL, FAM, FCF)
    who are available on the given date, ranked by least flight hours.
    date format: YYYY-MM-DD"""
    snived_today = {s['person'] for s in MOCK_SNIVS if s['date'] == date}
    out = f'Qualified IPs for {event_type} on {date}:'
    candidates = []
    for name, data in MOCK_PERSONNEL['Instructor'].items():
        if event_type not in data.get('qualifications', []):
            continue
        if data.get('med_down') or name in snived_today or data.get('snived'):
            continue
        if data['type'] == 'RESERVIST' and date not in data.get('drill_days', []):
            continue
        # find hotboard hours
        hrs = next((h['flight_hours_ytd'] for h in MOCK_IP_HOTBOARD if h['name'] == name), 0)
        candidates.append((name, data['type'], hrs))
    candidates.sort(key=lambda x: x[2])
    if not candidates:
        return out + ' | No qualified available IPs found'
    for rank, (name, itype, hrs) in enumerate(candidates, 1):
        out += f' | #{rank} {name} [{itype}] {hrs}hrs YTD'
    return out

ip_hotboard_tools = [get_ip_hotboard, get_instructor_availability, get_qualified_ips]
