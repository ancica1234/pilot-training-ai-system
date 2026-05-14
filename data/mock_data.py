# ---------------------------------------------------------------------------
# mock_data.py
# ---------------------------------------------------------------------------
# All names, callsigns, and organisations are entirely fictional.
# Domain vocabulary mirrors the real scheduling spreadsheet observed in the
# customer walkthrough (Weekly sheet, IP Hotboard, Enviro Data, Ground School)
# but contains no real people, units, or sensitive information.
# ---------------------------------------------------------------------------

import datetime

# ── 1. SYLLABUS SCHEDULES ───────────────────────────────────────────────────
# Two active training classes.  Event codes mirror a simplified syllabus.

MOCK_SCHEDULES = {
    '26-1': {
        'className': '26-1',
        'startDate': '2026-03-02',
        'events': [
            {'eventCode': '0100', 'scheduledDate': '2026-03-02', 'description': 'Introduction Flight',      'type': 'FLIGHT'},
            {'eventCode': '0101', 'scheduledDate': '2026-03-09', 'description': 'Basic Maneuvers',          'type': 'FLIGHT'},
            {'eventCode': '0102', 'scheduledDate': '2026-03-16', 'description': 'Navigation',               'type': 'FLIGHT'},
            {'eventCode': '0103', 'scheduledDate': '2026-03-23', 'description': 'Formation Flying',         'type': 'FLIGHT'},
            {'eventCode': '0104', 'scheduledDate': '2026-03-30', 'description': 'Night Operations',         'type': 'FLIGHT'},
            {'eventCode': 'S101', 'scheduledDate': '2026-03-04', 'description': 'Systems SIM',              'type': 'SIM'},
            {'eventCode': 'S102', 'scheduledDate': '2026-03-11', 'description': 'Emergency Procedures SIM', 'type': 'SIM'},
            {'eventCode': 'G101', 'scheduledDate': '2026-03-03', 'description': 'Aerodynamics Ground',      'type': 'GROUND'},
            {'eventCode': 'G102', 'scheduledDate': '2026-03-10', 'description': 'Engine Systems Ground',    'type': 'GROUND'},
        ]
    },
    '26-2': {
        'className': '26-2',
        'startDate': '2026-04-06',
        'events': [
            {'eventCode': '0100', 'scheduledDate': '2026-04-06', 'description': 'Introduction Flight',      'type': 'FLIGHT'},
            {'eventCode': '0101', 'scheduledDate': '2026-04-13', 'description': 'Basic Maneuvers',          'type': 'FLIGHT'},
            {'eventCode': '0102', 'scheduledDate': '2026-04-20', 'description': 'Navigation',               'type': 'FLIGHT'},
            {'eventCode': '0103', 'scheduledDate': '2026-04-27', 'description': 'Formation Flying',         'type': 'FLIGHT'},
            {'eventCode': '0104', 'scheduledDate': '2026-05-04', 'description': 'Night Operations',         'type': 'FLIGHT'},
            {'eventCode': 'S101', 'scheduledDate': '2026-04-08', 'description': 'Systems SIM',              'type': 'SIM'},
            {'eventCode': 'S102', 'scheduledDate': '2026-04-15', 'description': 'Emergency Procedures SIM', 'type': 'SIM'},
            {'eventCode': 'G101', 'scheduledDate': '2026-04-07', 'description': 'Aerodynamics Ground',      'type': 'GROUND'},
            {'eventCode': 'G102', 'scheduledDate': '2026-04-14', 'description': 'Engine Systems Ground',    'type': 'GROUND'},
        ]
    }
}

# ── 2. STUDENT HISTORY ──────────────────────────────────────────────────────
# priority: AF = Air Force exchange (tight timeline)
#           REFRESH = refresher pilot
#           STANDARD = normal syllabus student
# colour mirrors the whiteboard colour coding described in the walkthrough.

MOCK_STUDENT_HISTORY = {
    # ── Class 26-1 ──
    'Tara Voss': {
        'className': '26-1', 'workdaysBehind': 8, 'priority': 'STANDARD',
        'incompleteEvents': ['0101', '0102', '0103', '0104', 'S102'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '2026-03-02', 'status': 'Satisfactory'},
            {'eventCode': 'S101', 'completedDate': '2026-03-04', 'status': 'Satisfactory'},
            {'eventCode': 'G101', 'completedDate': '2026-03-03', 'status': 'Satisfactory'},
            {'eventCode': 'G102', 'completedDate': '2026-03-10', 'status': 'Unsatisfactory'},
        ]},
    'Leon Marsh': {
        'className': '26-1', 'workdaysBehind': 2, 'priority': 'REFRESH',
        'incompleteEvents': ['0103', '0104'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '2026-03-02', 'status': 'Satisfactory'},
            {'eventCode': '0101', 'completedDate': '2026-03-09', 'status': 'Satisfactory'},
            {'eventCode': '0102', 'completedDate': '2026-03-17', 'status': 'Unsatisfactory'},
            {'eventCode': 'S101', 'completedDate': '2026-03-04', 'status': 'Satisfactory'},
            {'eventCode': 'S102', 'completedDate': '2026-03-11', 'status': 'Satisfactory'},
            {'eventCode': 'G101', 'completedDate': '2026-03-03', 'status': 'Satisfactory'},
            {'eventCode': 'G102', 'completedDate': '2026-03-10', 'status': 'Satisfactory'},
        ]},
    'Dana Quirke': {
        'className': '26-1', 'workdaysBehind': 0, 'priority': 'AF',
        'incompleteEvents': ['0104'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '2026-03-02', 'status': 'Satisfactory'},
            {'eventCode': '0101', 'completedDate': '2026-03-09', 'status': 'Satisfactory'},
            {'eventCode': '0102', 'completedDate': '2026-03-16', 'status': 'Satisfactory'},
            {'eventCode': '0103', 'completedDate': '2026-03-23', 'status': 'Satisfactory'},
            {'eventCode': 'S101', 'completedDate': '2026-03-04', 'status': 'Satisfactory'},
            {'eventCode': 'S102', 'completedDate': '2026-03-11', 'status': 'Satisfactory'},
            {'eventCode': 'G101', 'completedDate': '2026-03-03', 'status': 'Satisfactory'},
            {'eventCode': 'G102', 'completedDate': '2026-03-10', 'status': 'Satisfactory'},
        ]},
    # ── Class 26-2 ──
    'Bram Okafor': {
        'className': '26-2', 'workdaysBehind': 5, 'priority': 'AF',
        'incompleteEvents': ['0102', '0103', '0104', 'S102'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '2026-04-06', 'status': 'Satisfactory'},
            {'eventCode': '0101', 'completedDate': '2026-04-14', 'status': 'Satisfactory'},
            {'eventCode': 'S101', 'completedDate': '2026-04-08', 'status': 'Satisfactory'},
            {'eventCode': 'G101', 'completedDate': '2026-04-07', 'status': 'Satisfactory'},
            {'eventCode': 'G102', 'completedDate': '2026-04-14', 'status': 'Satisfactory'},
        ]},
    'Yuki Tanaka': {
        'className': '26-2', 'workdaysBehind': 3, 'priority': 'REFRESH',
        'incompleteEvents': ['0103', '0104'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '2026-04-06', 'status': 'Satisfactory'},
            {'eventCode': '0101', 'completedDate': '2026-04-13', 'status': 'Satisfactory'},
            {'eventCode': '0102', 'completedDate': '2026-04-21', 'status': 'Satisfactory'},
            {'eventCode': 'S101', 'completedDate': '2026-04-08', 'status': 'Satisfactory'},
            {'eventCode': 'S102', 'completedDate': '2026-04-15', 'status': 'Satisfactory'},
            {'eventCode': 'G101', 'completedDate': '2026-04-07', 'status': 'Satisfactory'},
            {'eventCode': 'G102', 'completedDate': '2026-04-14', 'status': 'Satisfactory'},
        ]},
    'Petra Holst': {
        'className': '26-2', 'workdaysBehind': 0, 'priority': 'STANDARD',
        'incompleteEvents': ['0104'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '2026-04-06', 'status': 'Satisfactory'},
            {'eventCode': '0101', 'completedDate': '2026-04-13', 'status': 'Satisfactory'},
            {'eventCode': '0102', 'completedDate': '2026-04-20', 'status': 'Satisfactory'},
            {'eventCode': '0103', 'completedDate': '2026-04-27', 'status': 'Satisfactory'},
            {'eventCode': 'S101', 'completedDate': '2026-04-08', 'status': 'Satisfactory'},
            {'eventCode': 'S102', 'completedDate': '2026-04-15', 'status': 'Satisfactory'},
            {'eventCode': 'G101', 'completedDate': '2026-04-07', 'status': 'Satisfactory'},
            {'eventCode': 'G102', 'completedDate': '2026-04-14', 'status': 'Satisfactory'},
        ]},
}


MOCK_REMEDIATION = {
    'makeup':    'Schedule makeup sessions on non-duty days to cover missed flight events',
    'tutoring':  'Pair with a high-performing peer for guided practice on Navigation',
    'simulator': 'Add 4 extra simulator hours to build proficiency before live events',
}

# ── 3. PERSONNEL TRACKER ─────────────────────────────────────────────────────
MOCK_PERSONNEL = {
    'Instructor': {
        'Gale Rynder': {
            'type': 'ACTIVE', 'role': 'IP',
            'snived': False, 'med_down': False,
            'flight_hours_ytd': 142.5,
            'qualifications': ['CAL', 'FAM', 'FCF'],
            'email': 'g.rynder@aviationtraining.aero',
        },
        'Otto Finch': {
            'type': 'ACTIVE', 'role': 'IP',
            'snived': True, 'med_down': False,
            'flight_hours_ytd': 98.0,
            'qualifications': ['CAL', 'FAM'],
            'email': 'o.finch@aviationtraining.aero',
        },
        'Selma Varga': {
            'type': 'AF', 'role': 'IP',
            'snived': False, 'med_down': False,
            'flight_hours_ytd': 210.0,
            'qualifications': ['CAL', 'FAM', 'FCF'],
            'email': 's.varga@af-exchange.aero',
        },
        'Noel Drax': {
            'type': 'RESERVIST', 'role': 'IP',
            'snived': False, 'med_down': False,
            'flight_hours_ytd': 44.0,
            'qualifications': ['CAL'],
            'email': 'n.drax@reserve.aero',
            'drill_days': ['2026-04-06', '2026-04-07', '2026-04-20', '2026-04-21'],
        },
        'Preet Aulakh': {
            'type': 'RESERVIST', 'role': 'IP',
            'snived': False, 'med_down': True,
            'flight_hours_ytd': 61.5,
            'qualifications': ['CAL', 'FAM'],
            'email': 'p.aulakh@reserve.aero',
            'drill_days': ['2026-04-06', '2026-04-13', '2026-04-27'],
        },
        'Bex Torrance': {
            'type': 'NON_PERM', 'role': 'IP',
            'snived': False, 'med_down': False,
            'flight_hours_ytd': 77.0,
            'qualifications': ['CAL', 'FAM'],
            'email': 'b.torrance@aviationtraining.aero',
        },
    },
    'Student': {
        'Tara Voss':   {'type': 'ACTIVE', 'role': 'STUDENT', 'class': '26-1'},
        'Leon Marsh':  {'type': 'ACTIVE', 'role': 'STUDENT', 'class': '26-1'},
        'Dana Quirke': {'type': 'AF',     'role': 'STUDENT', 'class': '26-1'},
        'Bram Okafor': {'type': 'AF',     'role': 'STUDENT', 'class': '26-2'},
        'Yuki Tanaka': {'type': 'ACTIVE', 'role': 'STUDENT', 'class': '26-2'},
        'Petra Holst': {'type': 'ACTIVE', 'role': 'STUDENT', 'class': '26-2'},
    },
}

# ── 4. SNIV LIST ─────────────────────────────────────────────────────────────
# SNIV = request NOT to be scheduled. Sourced from scheduling system.
MOCK_SNIVS = [
    {'person': 'Otto Finch',   'date': '2026-04-06', 'reason': 'Personal appointment', 'source': 'MSHARP'},
    {'person': 'Preet Aulakh', 'date': '2026-04-06', 'reason': 'Medical grounding',    'source': 'MSHARP'},
    {'person': 'Preet Aulakh', 'date': '2026-04-07', 'reason': 'Medical grounding',    'source': 'MSHARP'},
    {'person': 'Tara Voss',    'date': '2026-04-10', 'reason': 'Admin appointment',    'source': 'MANUAL'},
]

# ── 5. AIRCRAFT FLEET ────────────────────────────────────────────────────────
# Each aircraft has a tail number, mission type, and availability per period.
# periods: AM (morning line), PM (afternoon line), EVE (evening/night)
MOCK_AIRCRAFT = {
    'T-001': {'type': 'CAL', 'status': 'FMC', 'periods': ['AM', 'PM']},
    'T-002': {'type': 'FAM', 'status': 'FMC', 'periods': ['AM', 'PM']},
    'T-003': {'type': 'CAL', 'status': 'FMC', 'periods': ['AM', 'PM', 'EVE']},
    'T-004': {'type': 'FAM', 'status': 'PMC', 'periods': ['AM']},
    'T-005': {'type': 'CAL', 'status': 'NMC', 'periods': []},
}
# FMC = Fully Mission Capable, PMC = Partially, NMC = Non-Mission Capable

# ── 6. DAILY FLIGHT LINES ────────────────────────────────────────────────────
# Mirrors the bottom template section of the Weekly spreadsheet.
# Each line has a mission number, brief time, event type, and crew slots.
MOCK_FLIGHT_LINES = {
    '2026-04-06': [
        {
            'msn': '0-1', 'period': 'AM', 'brief': '0700',
            'takeoff': 'TBD', 'land': 'TBD', 'flight_time': 0.0,
            'event_type': 'FCF', 'aircraft': 'T-001',
            'ip': 'Gale Rynder', 'student': None, 'notes': 'FCF/FERRY'
        },
        {
            'msn': '0-2', 'period': 'AM', 'brief': '0700',
            'takeoff': 'TBD', 'land': 'TBD', 'flight_time': 0.0,
            'event_type': 'CAL', 'aircraft': 'T-003',
            'ip': 'Selma Varga', 'student': 'Dana Quirke', 'notes': ''
        },
        {
            'msn': '0-3', 'period': 'AM', 'brief': '0730',
            'takeoff': 'TBD', 'land': 'TBD', 'flight_time': 0.0,
            'event_type': 'FAM', 'aircraft': 'T-002',
            'ip': 'Bex Torrance', 'student': 'Bram Okafor', 'notes': 'AF priority'
        },
        {
            'msn': '0-4', 'period': 'PM', 'brief': '1300',
            'takeoff': 'TBD', 'land': 'TBD', 'flight_time': 0.0,
            'event_type': 'CAL', 'aircraft': 'T-001',
            'ip': 'Gale Rynder', 'student': 'Leon Marsh', 'notes': 'Hot seat AM->PM'
        },
        {
            'msn': '0-5', 'period': 'PM', 'brief': '1300',
            'takeoff': 'TBD', 'land': 'TBD', 'flight_time': 0.0,
            'event_type': 'FAM', 'aircraft': 'T-002',
            'ip': 'Noel Drax', 'student': 'Yuki Tanaka', 'notes': 'Reservist drill day'
        },
    ]
}

# ── 7. DAILY STATUS GRID ─────────────────────────────────────────────────────
# Mirrors the colour-coded rows in the top section of the Weekly spreadsheet.
# Categories: ODO, FCF, FLIGHT_EVENT, SIM_EVENT, SNIVED, DOUBLE_SCHEDULE,
#             MED_DOWN, GRND_EVENT
MOCK_DAILY_STATUS = {
    '2026-04-06': {
        'ODO':             ['Gale Rynder'],
        'FCF':             ['Gale Rynder', 'Selma Varga'],
        'FLIGHT_EVENT':    ['Dana Quirke', 'Bram Okafor', 'Leon Marsh', 'Yuki Tanaka'],
        'SIM_EVENT':       ['Tara Voss', 'Petra Holst'],
        'SNIVED':          ['Otto Finch', 'Preet Aulakh'],
        'DOUBLE_SCHEDULE': [],
        'MED_DOWN':        ['Preet Aulakh'],
        'GRND_EVENT':      ['Tara Voss'],
    }
}

# ── 8. ENVIRONMENT DATA ──────────────────────────────────────────────────────
# Mirrors the ENVIRO DATA tab on the Weekly spreadsheet.
# EENT = End of Evening Nautical Twilight
# HLL  = High Light Level threshold
# highlight_window = period requiring special lighting/NVG rules
MOCK_ENVIRO_DATA = {
    '2026-04-06': {
        'sunset': '1935', 'eent': '2031', 'hll': '2031',
        'highlight_window': '2031-2045',
        'field_hours': '0800-0100',
        'quiet_hours': None,
        'flt_window': '0x0',
        'sdo_gdo': 'SDO/GDO',
    },
    '2026-04-07': {
        'sunset': '1936', 'eent': '2032', 'hll': '2032',
        'highlight_window': '2032-2046',
        'field_hours': '0800-0100',
        'quiet_hours': None,
        'flt_window': '2x2',
        'sdo_gdo': None,
    },
    '2026-04-08': {
        'sunset': '1937', 'eent': '2033', 'hll': '2033',
        'highlight_window': '2033-2047',
        'field_hours': '0800-0100',
        'quiet_hours': '2200-0600',
        'flt_window': '2x2',
        'sdo_gdo': None,
    },
    '2026-04-13': {
        'sunset': '1941', 'eent': '2037', 'hll': '2037',
        'highlight_window': '2037-2051',
        'field_hours': '0800-0100',
        'quiet_hours': None,
        'flt_window': '2x2',
        'sdo_gdo': None,
    },
    '2026-04-20': {
        'sunset': '1947', 'eent': '2044', 'hll': '2044',
        'highlight_window': '2044-2058',
        'field_hours': '0800-0100',
        'quiet_hours': None,
        'flt_window': '2x2',
        'sdo_gdo': None,
    },
    '2026-04-27': {
        'sunset': '1953', 'eent': '2050', 'hll': '2050',
        'highlight_window': '2050-2104',
        'field_hours': '0800-0100',
        'quiet_hours': None,
        'flt_window': '2x2',
        'sdo_gdo': None,
    },
}

# ── 9. GROUND SCHOOL CALENDAR ────────────────────────────────────────────────
# Mirrors the Ground School tab / Excel-generated calendar.
# Each day has a numbered event sequence, CSI requirement flag, and
# outside_agency flag (aeromed, nightlab, course rules, briefs).
# csi_required: True = needs a Certified Simulator Instructor present
MOCK_GROUND_SCHOOL = {
    '2026-04-06': {
        'day_number': 1,
        'events': [
            {'code': 'GS-01', 'title': 'Course Rules Brief',      'start': '0800', 'duration_hrs': 1.0, 'csi_required': False, 'outside_agency': True},
            {'code': 'GS-02', 'title': 'Aerodynamics Study Hall', 'start': '0900', 'duration_hrs': 2.0, 'csi_required': False, 'outside_agency': False},
            {'code': 'GS-03', 'title': 'Engine Systems Lecture',  'start': '1300', 'duration_hrs': 1.5, 'csi_required': False, 'outside_agency': False},
        ],
        'holiday': False, 'notes': '',
    },
    '2026-04-07': {
        'day_number': 2,
        'events': [
            {'code': 'GS-04', 'title': 'SIM Orientation',         'start': '0800', 'duration_hrs': 2.0, 'csi_required': True,  'outside_agency': False},
            {'code': 'GS-05', 'title': 'Night Lab Brief',         'start': '1900', 'duration_hrs': 1.0, 'csi_required': False, 'outside_agency': True},
        ],
        'holiday': False, 'notes': 'CSI: confirm availability before 0700',
    },
    '2026-04-08': {
        'day_number': 3,
        'events': [
            {'code': 'GS-06', 'title': 'Aeromed Brief',           'start': '0800', 'duration_hrs': 1.0, 'csi_required': False, 'outside_agency': True},
            {'code': 'GS-07', 'title': 'Study Hall — Navigation', 'start': '0900', 'duration_hrs': 2.0, 'csi_required': False, 'outside_agency': False},
            {'code': 'GS-08', 'title': 'SIM Lab 1',               'start': '1300', 'duration_hrs': 2.0, 'csi_required': True,  'outside_agency': False},
        ],
        'holiday': False, 'notes': '',
    },
    '2026-04-13': {
        'day_number': 4,
        'events': [
            {'code': 'GS-09', 'title': 'Formation Flying Brief',  'start': '0800', 'duration_hrs': 1.0, 'csi_required': False, 'outside_agency': False},
            {'code': 'GS-10', 'title': 'SIM Lab 2',               'start': '1000', 'duration_hrs': 2.0, 'csi_required': True,  'outside_agency': False},
        ],
        'holiday': False, 'notes': '',
    },
    '2026-04-20': {
        'day_number': 5,
        'events': [
            {'code': 'GS-11', 'title': 'Night Ops Study Hall',    'start': '0800', 'duration_hrs': 2.0, 'csi_required': False, 'outside_agency': False},
            {'code': 'GS-12', 'title': 'Night SIM Lab',           'start': '1900', 'duration_hrs': 2.0, 'csi_required': True,  'outside_agency': False},
        ],
        'holiday': False, 'notes': 'Night SIM requires CSI on duty',
    },
    '2026-04-27': {
        'day_number': 6,
        'events': [
            {'code': 'GS-13', 'title': 'End-of-Course Brief',     'start': '0800', 'duration_hrs': 1.0, 'csi_required': False, 'outside_agency': False},
        ],
        'holiday': False, 'notes': '',
    },
}

# ── 10. IP HOTBOARD SOURCE ───────────────────────────────────────────────────
# Raw data pasted from scheduling system — instructor flight hours per period.
# Used to rank IPs from least to most flight time (hotboard = lowest hrs flies next).
MOCK_IP_HOTBOARD = [
    {'name': 'Noel Drax',    'flight_hours_ytd': 44.0,  'last_flight': '2026-03-28', 'available_today': True},
    {'name': 'Preet Aulakh', 'flight_hours_ytd': 61.5,  'last_flight': '2026-03-25', 'available_today': False},
    {'name': 'Bex Torrance', 'flight_hours_ytd': 77.0,  'last_flight': '2026-04-01', 'available_today': True},
    {'name': 'Otto Finch',   'flight_hours_ytd': 98.0,  'last_flight': '2026-04-03', 'available_today': False},
    {'name': 'Gale Rynder',  'flight_hours_ytd': 142.5, 'last_flight': '2026-04-05', 'available_today': True},
    {'name': 'Selma Varga',  'flight_hours_ytd': 210.0, 'last_flight': '2026-04-05', 'available_today': True},
]
