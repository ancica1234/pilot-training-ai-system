MOCK_SCHEDULES = {
    '25-5' : {
        'className' : '25-5',
        'startDate' : '06-01-25',
        'events' : [
            {'eventCode' : '0100', 'scheduledDate' : '06-01-25', 'description' : 'Introduction Flight'},
            {'eventCode' : '0101', 'scheduledDate' : '13-01-25', 'description' : 'Basic Maneuvers'},
            {'eventCode' : '0102', 'scheduledDate' : '20-01-25', 'description' : 'Navigation'},
            {'eventCode' : '0103', 'scheduledDate' : '27-01-25', 'description' : 'Formation Flying'},
            {'eventCode' : '0104', 'scheduledDate' : '03-02-25', 'description' : 'Night Operations'},
        ]
    },
    '25-4' : {
        'className' : '25-4'  ,
        'startDate' : '01-01-25'  ,
        'events' : [
            {'eventCode' : '0100' , 'scheduledDate' : '01-01-25' , 'description' : 'Introduction Flight'} ,
            {'eventCode' : '0101' , 'scheduledDate' : '08-01-25' , 'description' : 'Basic Maneuvers'} ,
            {'eventCode' : '0102' , 'scheduledDate' : '15-01-25' , 'description' : 'Navigation'} ,
            {'eventCode' : '0103' , 'scheduledDate' : '22-01-25' , 'description' : 'Formation Flying'} ,
            {'eventCode' : '0104' , 'scheduledDate' : '29-01-25' , 'description' : 'Night Operations'} ,
        ]
    }
}

MOCK_STUDENT_HISTORY = {
    'Carlos Rivera': {'className': '25-5', 'workdaysBehind': 8,
        'incompleteEvents': ['0101', '0102', '0103', '0104'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '06-01-25', 'status': 'Satisfactory'},
        ]},
    'Priya Patel': {'className': '25-5', 'workdaysBehind': 2,
        'incompleteEvents': ['0103', '0104'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '06-01-25', 'status': 'Satisfactory'},
            {'eventCode': '0101', 'completedDate': '13-01-25', 'status': 'Satisfactory'},
            {'eventCode': '0102', 'completedDate': '21-01-25', 'status': 'Unsatisfactory'},
        ]},
    'John Smith': {'className': '25-4', 'workdaysBehind': 5,
        'incompleteEvents': ['0102','0103','0104'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '01-01-25', 'status': 'Satisfactory'},
            {'eventCode': '0101', 'completedDate': '09-01-25', 'status': 'Satisfactory'},
        ]},
    'Marcus Webb': {'className': '25-4', 'workdaysBehind': 3,
        'incompleteEvents': ['0103','0104'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '01-01-25', 'status': 'Satisfactory'},
            {'eventCode': '0101', 'completedDate': '09-01-25', 'status': 'Satisfactory'},
            {'eventCode': '0102', 'completedDate': '19-01-25', 'status': 'Satisfactory'},
        ]},
    'Jane Doe': {'className': '25-4', 'workdaysBehind': 0,
        'incompleteEvents': ['0104'],
        'completedEvents': [
            {'eventCode': '0100', 'completedDate': '01-01-25', 'status': 'Satisfactory'},
            {'eventCode': '0101', 'completedDate': '08-01-25', 'status': 'Satisfactory'},
            {'eventCode': '0102', 'completedDate': '15-01-25', 'status': 'Satisfactory'},
            {'eventCode': '0103', 'completedDate': '22-01-25', 'status': 'Satisfactory'},
        ]},
}

MOCK_REMEDIATION = {
    'makeup': 'Schedule makeup sessions on weekends to cover missed events 0102 and 0103',
    'tutoring': 'Pair with a high-performing student for guided practice on Navigation',
    'simulator': 'Add 4 extra simulator hours to build confidence before live events',
}
