"""
Generate comprehensive fixture data for Smart Lab Management System
This script creates realistic, demo-ready data for all models
"""

import json
from datetime import datetime, timedelta

# Initialize fixture data list
fixtures = []
pk_counter = {
    'user': 1,
    'semester': 1,
    'batch': 1,
    'student': 1,
    'pcmapping': 1,
    'labsession': 1,
    'attendance': 1,
    'vivarecord': 1,
    'task': 1,
    'tasksubmission': 1,
    'examsession': 1,
    'examresult': 1
}

# 1. FACULTY USERS
faculty_users = [
    {"faculty_id": "test", "name": "Admin User", "email": "admin@university.edu", "is_superuser": True, "is_staff": True},
    {"faculty_id": "FAC001", "name": "Dr. Shireen Khan", "email": "shireen@university.edu", "is_superuser": False, "is_staff": True},
    {"faculty_id": "FAC002", "name": "Prof. Rajesh Kumar", "email": "rajesh.kumar@university.edu", "is_superuser": False, "is_staff": True},
    {"faculty_id": "FAC003", "name": "Dr. Priya Sharma", "email": "priya.sharma@university.edu", "is_superuser": False, "is_staff": True},
]

for user in faculty_users:
    fixtures.append({
        "model": "accounts.user",
        "pk": pk_counter['user'],
        "fields": {
            "password": "pbkdf2_sha256$600000$test$dummyhash",
            "last_login": None,
            "is_superuser": user["is_superuser"],
            "faculty_id": user["faculty_id"],
            "email": user["email"],
            "name": user["name"],
            "is_active": True,
            "is_staff": user["is_staff"],
            "created_at": "2024-01-01T00:00:00Z",
            "groups": [],
            "user_permissions": []
        }
    })
    pk_counter['user'] += 1

# 2. SEMESTERS (1-8)
for i in range(1, 9):
    fixtures.append({
        "model": "core.semester",
        "pk": pk_counter['semester'],
        "fields": {
            "name": f"Sem {i}",
            "number": i,
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    })
    pk_counter['semester'] += 1

# 3. BATCHES (2 batches per semester for Sem 1-6)
batch_mapping = {}  # To track batch IDs for later use
for sem_num in range(1, 7):
    for batch_num in range(1, 3):
        batch_id = pk_counter['batch']
        batch_mapping[(sem_num, batch_num)] = batch_id
        fixtures.append({
            "model": "core.batch",
            "pk": batch_id,
            "fields": {
                "semester": sem_num,
                "name": f"Batch {batch_num}",
                "year": 2024,
                "total_students": 30,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        })
        pk_counter['batch'] += 1

# 4. STUDENTS (30 students per batch for first 3 batches)
student_names = [
    "Andrea John", "Decca Thomas", "Krishna Kumar", "John Doe", "Mike Harry",
    "Chen Zung", "Sarah Williams", "David Brown", "Emily Davis", "Michael Wilson",
    "Jessica Moore", "Christopher Taylor", "Ashley Anderson", "Matthew Thomas",
    "Amanda Jackson", "Daniel White", "Stephanie Harris", "Joshua Martin",
    "Jennifer Thompson", "Andrew Garcia", "Elizabeth Martinez", "Ryan Robinson",
    "Nicole Clark", "Brandon Rodriguez", "Samantha Lewis", "Justin Lee",
    "Rachel Walker", "Kevin Hall", "Lauren Allen", "Tyler Young"
]

student_mapping = {}  # To track student IDs
for batch_key in [(1, 1), (1, 2), (2, 1)]:  # First 3 batches
    batch_id = batch_mapping[batch_key]
    for i, name in enumerate(student_names):
        student_id = pk_counter['student']
        student_mapping[(batch_id, i)] = student_id
        
        status = "online" if i % 3 != 0 else "offline"
        modes = ["normal", "exam", "viva", "locked"]
        mode = modes[i % 4]
        
        # Make email unique by including student_id
        email_name = name.lower().replace(' ', '.')
        unique_email = f"{email_name}.{student_id}@student.edu"
        
        fixtures.append({
            "model": "students.student",
            "pk": student_id,
            "fields": {
                "student_id": f"87{65000 + student_id:05d}",
                "name": name,
                "email": unique_email,
                "batch": batch_id,
                "status": status,
                "current_mode": mode,
                "last_seen": "2024-12-27T08:00:00Z" if status == "online" else "2024-12-26T18:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-12-27T08:00:00Z"
            }
        })
        pk_counter['student'] += 1

# 5. PC MAPPINGS (one per student)
for batch_key in [(1, 1), (1, 2), (2, 1)]:
    batch_id = batch_mapping[batch_key]
    for i in range(30):
        if (batch_id, i) in student_mapping:
            student_id = student_mapping[(batch_id, i)]
            fixtures.append({
                "model": "core.pcmapping",
                "pk": pk_counter['pcmapping'],
                "fields": {
                    "pc_id": f"PC-{pk_counter['pcmapping']:02d}",
                    "student": student_id,
                    "batch": batch_id,
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            })
            pk_counter['pcmapping'] += 1

# 6. LAB SESSIONS (past sessions for first 2 batches)
session_mapping = {}
for batch_key in [(1, 1), (1, 2)]:
    batch_id = batch_mapping[batch_key]
    for session_num in range(1, 4):  # 3 past sessions per batch
        session_id = pk_counter['labsession']
        session_mapping[(batch_id, session_num)] = session_id
        
        start_date = datetime(2024, 12, 20 + session_num)
        end_date = start_date + timedelta(hours=2)
        
        fixtures.append({
            "model": "lab_sessions.labsession",
            "pk": session_id,
            "fields": {
                "batch": batch_id,
                "faculty": 2,  # Dr. Shireen Khan
                "session_type": "regular",
                "status": "completed",
                "start_time": start_date.isoformat() + "Z",
                "end_time": end_date.isoformat() + "Z",
                "created_at": start_date.isoformat() + "Z",
                "updated_at": end_date.isoformat() + "Z"
            }
        })
        pk_counter['labsession'] += 1

# 7. ATTENDANCE RECORDS
for batch_key in [(1, 1), (1, 2)]:
    batch_id = batch_mapping[batch_key]
    for session_num in range(1, 4):
        session_id = session_mapping[(batch_id, session_num)]
        
        # Create attendance for 25 out of 30 students (some absent)
        for i in range(25):
            if (batch_id, i) in student_mapping:
                student_id = student_mapping[(batch_id, i)]
                
                start_date = datetime(2024, 12, 20 + session_num, 9, 0)
                end_date = start_date + timedelta(hours=2)
                
                fixtures.append({
                    "model": "students.attendance",
                    "pk": pk_counter['attendance'],
                    "fields": {
                        "student": student_id,
                        "session": session_id,
                        "status": "present",
                        "login_time": start_date.isoformat() + "Z",
                        "logout_time": end_date.isoformat() + "Z",
                        "created_at": start_date.isoformat() + "Z",
                        "updated_at": end_date.isoformat() + "Z"
                    }
                })
                pk_counter['attendance'] += 1

# 8. VIVA RECORDS
for batch_key in [(1, 1)]:
    batch_id = batch_mapping[batch_key]
    session_id = session_mapping[(batch_id, 1)]
    
    # Viva marks for 20 students
    for i in range(20):
        if (batch_id, i) in student_mapping:
            student_id = student_mapping[(batch_id, i)]
            marks = 60 + (i * 2)  # Marks from 60 to 98
            
            fixtures.append({
                "model": "evaluation.vivarecord",
                "pk": pk_counter['vivarecord'],
                "fields": {
                    "student": student_id,
                    "session": session_id,
                    "faculty": 2,
                    "marks": marks,
                    "notes": f"Good performance. Answered {marks}% of questions correctly.",
                    "status": "completed",
                    "conducted_at": "2024-12-21T10:00:00Z",
                    "created_at": "2024-12-21T10:00:00Z",
                    "updated_at": "2024-12-21T10:00:00Z"
                }
            })
            pk_counter['vivarecord'] += 1

# 9. TASKS
task_mapping = {}
for batch_key in [(1, 1), (1, 2), (2, 1)]:
    batch_id = batch_mapping[batch_key]
    
    tasks = [
        {"title": "Python Assignment 1", "desc": "Create a calculator using OOP principles"},
        {"title": "Database Project", "desc": "Design and implement a library management system"},
        {"title": "Web Development Task", "desc": "Build a responsive portfolio website using HTML/CSS/JS"}
    ]
    
    for task_num, task_data in enumerate(tasks, 1):
        task_id = pk_counter['task']
        task_mapping[(batch_id, task_num)] = task_id
        
        fixtures.append({
            "model": "evaluation.task",
            "pk": task_id,
            "fields": {
                "batch": batch_id,
                "faculty": 2,
                "title": task_data["title"],
                "description": task_data["desc"],
                "deadline": "2024-12-30T23:59:59Z",
                "auto_delete": False,
                "created_at": "2024-12-15T00:00:00Z",
                "updated_at": "2024-12-15T00:00:00Z"
            }
        })
        pk_counter['task'] += 1

# 10. TASK SUBMISSIONS
for batch_key in [(1, 1)]:
    batch_id = batch_mapping[batch_key]
    task_id = task_mapping[(batch_id, 1)]
    
    # 15 students submitted the first task
    for i in range(15):
        if (batch_id, i) in student_mapping:
            student_id = student_mapping[(batch_id, i)]
            
            fixtures.append({
                "model": "evaluation.tasksubmission",
                "pk": pk_counter['tasksubmission'],
                "fields": {
                    "task": task_id,
                    "student": student_id,
                    "file_path": f"/submissions/task1/student_{student_id}_calculator.py",
                    "submitted_at": "2024-12-20T10:00:00Z",
                    "marks": 70 + (i * 2),
                    "feedback": "Good work. Code is clean and functional.",
                    "created_at": "2024-12-20T10:00:00Z",
                    "updated_at": "2024-12-20T10:00:00Z"
                }
            })
            pk_counter['tasksubmission'] += 1

# 11. EXAM SESSIONS
for batch_key in [(1, 1), (1, 2)]:
    batch_id = batch_mapping[batch_key]
    session_id = session_mapping[(batch_id, 2)]
    
    fixtures.append({
        "model": "evaluation.examsession",
        "pk": pk_counter['examsession'],
        "fields": {
            "lab_session": session_id,
            "exam_type": "practical",
            "duration_minutes": 120,
            "allowed_apps": "VS Code, Chrome, Terminal",
            "created_at": "2024-12-22T00:00:00Z",
            "updated_at": "2024-12-22T00:00:00Z"
        }
    })
    exam_session_id = pk_counter['examsession']
    pk_counter['examsession'] += 1
    
    # 12. EXAM RESULTS
    for i in range(25):
        if (batch_id, i) in student_mapping:
            student_id = student_mapping[(batch_id, i)]
            marks = 55 + (i * 1.5)
            
            fixtures.append({
                "model": "evaluation.examresult",
                "pk": pk_counter['examresult'],
                "fields": {
                    "student": student_id,
                    "exam_session": exam_session_id,
                    "marks": int(marks),
                    "duration_minutes": 110 + (i % 10),
                    "started_at": "2024-12-22T09:00:00Z",
                    "submitted_at": "2024-12-22T11:00:00Z",
                    "created_at": "2024-12-22T11:00:00Z",
                    "updated_at": "2024-12-22T11:00:00Z"
                }
            })
            pk_counter['examresult'] += 1

# Write to file
output_file = "fixtures/complete_data.json"
with open(output_file, 'w') as f:
    json.dump(fixtures, f, indent=2)

print(f"✅ Generated {len(fixtures)} fixture records")
print(f"📁 Saved to: {output_file}")
print("\nSummary:")
print(f"  - Faculty Users: {pk_counter['user'] - 1}")
print(f"  - Semesters: {pk_counter['semester'] - 1}")
print(f"  - Batches: {pk_counter['batch'] - 1}")
print(f"  - Students: {pk_counter['student'] - 1}")
print(f"  - PC Mappings: {pk_counter['pcmapping'] - 1}")
print(f"  - Lab Sessions: {pk_counter['labsession'] - 1}")
print(f"  - Attendance Records: {pk_counter['attendance'] - 1}")
print(f"  - Viva Records: {pk_counter['vivarecord'] - 1}")
print(f"  - Tasks: {pk_counter['task'] - 1}")
print(f"  - Task Submissions: {pk_counter['tasksubmission'] - 1}")
print(f"  - Exam Sessions: {pk_counter['examsession'] - 1}")
print(f"  - Exam Results: {pk_counter['examresult'] - 1}")
print("\nTo load: python manage.py loaddata fixtures/complete_data.json")
