
from langchain_core.tools import tool
from data.mock_data import (
    MOCK_FLIGHT_LINES, MOCK_AIRCRAFT, MOCK_DAILY_STATUS,
    MOCK_STUDENT_HISTORY, MOCK_PERSONNEL, MOCK_SNIVS, MOCK_ENVIRO_DATA
)

@tool
def get_daily_flight_schedule(date: str) -> str:
    """Return the full flight line schedule for a given date.
    Shows each mission: MSN number, period (AM/PM/EVE), brief time,
    event type, aircraft, IP, student, and any notes.
    date format: YYYY-MM-DD"""
    lines = MOCK_FLIGHT_LINES.get(date)
    if not lines:
        return f'No flight lines scheduled for {date}'
    out = f'Flight Schedule for {date} ({len(lines)} missions):'
    for line in lines:
        student = line.get('student') or 'TBD'
        out += (f' | MSN {line["msn"]} [{line["period"]}]'
                f' Brief:{line["brief"]}'
                f' {line["event_type"]} AC:{line["aircraft"]}'
                f' IP:{line["ip"]} STU:{student}'
                f' FT:{line["flight_time"]}hrs')
        if line.get('notes'):
            out += f' ({line["notes"]})'
    return out

@tool
def get_daily_whiteboard(date: str) -> str:
    """Return the daily status whiteboard for a given date.
    Shows all personnel categorised as: ODO, FCF, FLIGHT EVENT, SIM EVENT,
    SNIVED, DOUBLE SCHEDULE, MED DOWN, GRND EVENT.
    Mirrors the colour-coded rows on the Weekly spreadsheet.
    date format: YYYY-MM-DD"""
    status = MOCK_DAILY_STATUS.get(date)
    enviro = MOCK_ENVIRO_DATA.get(date, {})
    if not status:
        return f'No whiteboard data for {date}'
    out = f'Daily Whiteboard — {date}:'
    if enviro:
        out += (f' | ENVIRO: Sunset {enviro.get("sunset","?")}'
                f' EENT {enviro.get("eent","?")}'
                f' HLL {enviro.get("hll","?")}'
                f' Highlight {enviro.get("highlight_window","?")}'
                f' | Field Hrs: {enviro.get("field_hours","?")}'
                f' | Flt Window: {enviro.get("flt_window","?")}'
        )
    categories = [
        ('ODO',             'ODO'),
        ('FCF',             'FCF'),
        ('FLIGHT_EVENT',    'FLIGHT EVENT'),
        ('SIM_EVENT',       'SIM EVENT'),
        ('SNIVED',          'SNIVED'),
        ('DOUBLE_SCHEDULE', 'DOUBLE SCHEDULE'),
        ('MED_DOWN',        'MED DOWN'),
        ('GRND_EVENT',      'GRND EVENT'),
    ]
    for key, label in categories:
        people = status.get(key, [])
        if people:
            out += f' | {label}: {", ".join(people)}'
        else:
            out += f' | {label}: —'
    return out

@tool
def get_priority_students(date: str) -> str:
    """Return students ranked by scheduling priority for a given date.
    Priority order: AF exchange students first, then Refreshers, then Standard.
    Filters out students who are SNIVED or med-down.
    date format: YYYY-MM-DD"""
    snived_today = {s['person'] for s in MOCK_SNIVS if s['date'] == date}
    priority_order = {'AF': 1, 'REFRESH': 2, 'STANDARD': 3}
    students = []
    for name, data in MOCK_STUDENT_HISTORY.items():
        if name in snived_today:
            continue
        priority = data.get('priority', 'STANDARD')
        behind = data.get('workdaysBehind', 0)
        incomplete = len(data.get('incompleteEvents', []))
        students.append((name, priority, behind, incomplete, data.get('className','?')))
    students.sort(key=lambda x: (priority_order.get(x[1], 9), -x[2]))
    out = f'Student Priority List for {date}:'
    for rank, (name, priority, behind, incomplete, cls) in enumerate(students, 1):
        behind_str = f'{behind}d behind' if behind > 0 else 'on track'
        out += f' | #{rank} {name} [{priority}] Class:{cls} {behind_str} {incomplete} events pending'
    return out

@tool
def get_aircraft_status() -> str:
    """Return the current status of all aircraft in the fleet.
    Shows tail number, type (CAL/FAM), mission capability (FMC/PMC/NMC),
    and available flight periods."""
    out = 'Aircraft Fleet Status:'
    for tail, data in MOCK_AIRCRAFT.items():
        periods = ', '.join(data['periods']) if data['periods'] else 'NONE'
        out += f' | {tail} [{data["type"]}] {data["status"]} — Periods: {periods}'
    fmc = sum(1 for d in MOCK_AIRCRAFT.values() if d['status'] == 'FMC')
    pmc = sum(1 for d in MOCK_AIRCRAFT.values() if d['status'] == 'PMC')
    nmc = sum(1 for d in MOCK_AIRCRAFT.values() if d['status'] == 'NMC')
    out += f' | Summary: {fmc} FMC, {pmc} PMC, {nmc} NMC of {len(MOCK_AIRCRAFT)} total'
    return out

@tool
def get_enviro_data(date: str) -> str:
    """Return environmental data for a given date: sunset time, EENT, HLL,
    highlight window, field hours, quiet hours, and flight window.
    date format: YYYY-MM-DD"""
    e = MOCK_ENVIRO_DATA.get(date)
    if not e:
        return f'No environmental data found for {date}'
    out = f'Environment Data for {date}:'
    out += f' | Sunset: {e["sunset"]}'
    out += f' | EENT: {e["eent"]}'
    out += f' | HLL: {e["hll"]}'
    out += f' | Highlight Window: {e["highlight_window"]}'
    out += f' | Field Hours: {e["field_hours"]}'
    out += f' | Quiet Hours: {e.get("quiet_hours") or "None"}'
    out += f' | Flt Window: {e["flt_window"]}'
    out += f' | SDO/GDO: {e.get("sdo_gdo") or "None"}'
    return out

flight_scheduler_tools = [
    get_daily_flight_schedule,
    get_daily_whiteboard,
    get_priority_students,
    get_aircraft_status,
    get_enviro_data,
]
