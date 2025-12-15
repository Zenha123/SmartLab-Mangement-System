semesters = {
    f"Sem {i}": [f"Batch {b}" for b in (1, 2)] for i in range(1, 9)
}

students = [
    {"name": "Andrea John", "pc": "PC-01", "status": "Online", "mode": "Normal"},
    {"name": "Decca Thomas", "pc": "PC-02", "status": "Offline", "mode": "Locked"},
    {"name": "Krishna Kumar", "pc": "PC-03", "status": "Online", "mode": "Exam"},
    {"name": "John Doe", "pc": "PC-04", "status": "Online", "mode": "Viva"},
    {"name": "Mike Harry", "pc": "PC-05", "status": "Offline", "mode": "Normal"},
    {"name": "Chen Zung", "pc": "PC-06", "status": "Online", "mode": "Normal"},
]

progress_rows = [
    {"name": "Andrea John", "id": "8765766", "visited": 79, "progress": 70, "grade": "76/100", "goal": "B+", "performance": "Great"},
    {"name": "Decca Thomas", "id": "8767786", "visited": 21, "progress": 20, "grade": "32/100", "goal": "D", "performance": "At risk"},
    {"name": "Krishna Kumar", "id": "8799486", "visited": 63, "progress": 60, "grade": "65/100", "goal": "B", "performance": "Good"},
    {"name": "John Doe", "id": "8765766", "visited": 79, "progress": 70, "grade": "76/100", "goal": "B+", "performance": "Great"},
]

evaluation_rows = [
    {"name": "Andrea John", "id": "8765766", "submitted": "Apr 06, 2022 9:00 am", "file": "Andrea_john_Assignment5.zip", "grade": "92", "feedback": "Don’t change background color"},
    {"name": "Decca Thomas", "id": "8767786", "submitted": "Apr 06, 2022 1:00 pm", "file": "Decca_Thomas_Assignment5.zip", "grade": "", "feedback": ""},
    {"name": "Krishna Kumar", "id": "8799486", "submitted": "-", "file": "-", "grade": "", "feedback": ""},
    {"name": "John Doe", "id": "8798583", "submitted": "-", "file": "-", "grade": "", "feedback": ""},
]

viva_rows = [
    {"name": "Andrea John", "status": "Completed", "marks": 18},
    {"name": "Decca Thomas", "status": "Waiting", "marks": None},
    {"name": "Krishna Kumar", "status": "Waiting", "marks": None},
]

task_rows = [
    {"student": "Andrea John", "file": "task1.py", "time": "10:30", "auto": "Yes"},
    {"student": "Decca Thomas", "file": "task1.py", "time": "10:35", "auto": "No"},
]

reports_attendance = [
    {"date": "2024-07-12", "present": 24, "absent": 6},
    {"date": "2024-07-13", "present": 28, "absent": 2},
]

