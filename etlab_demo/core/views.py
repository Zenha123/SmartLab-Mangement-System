from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.views.decorators.http import require_POST

from .utils import faculty_sidebar_context
from .models import Student, Timetable, Faculty, Semester, Subject, AttendanceSession, AttendanceRecord
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta, datetime

@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


# LOGIN VIEW
def login_view(request):
    error = None

    if request.method == "POST":
        faculty_id = request.POST.get("faculty_id")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=faculty_id,   # Faculty ID used as username
            password=password
        )

        if user is None:
            error = "Invalid Faculty ID or password"
        else:
            faculty = user.faculty
            login(request, user)

            if faculty.is_admin():
                return redirect("semester_list")
            else:
                return redirect("faculty_dashboard")

    return render(request, "auth/login.html", {"error": error})

def logout_view(request):
    logout(request)
    return redirect("login")


# ADMIN: semester list
@login_required
def semester_list(request):
    semesters = Semester.objects.all()
    return render(request, 'admin/semester_list.html', {'semesters': semesters})


# ADMIN: semester detail

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
HOURS = [1, 2, 3, 4, 5, 6]

def semester_detail(request, sem):
    semester = get_object_or_404(Semester, number=sem)
    subjects = Subject.objects.all()
    students = Student.objects.filter(semester=semester)
    faculties = Faculty.objects.all()

    timetable_slots = Timetable.objects.filter(semester=semester)
    timetable_exists = timetable_slots.exists()

    if request.method == 'POST':

        # ADD STUDENT
        if 'add_student' in request.POST:
            Student.objects.create(
                roll_no=request.POST['roll'],
                name=request.POST['name'],
                semester=semester   # ✅ instance
            )
            return redirect('semester_detail', sem=semester.id)

        # ADD / EDIT TIMETABLE
        if 'save_timetable' in request.POST:
            for day in DAYS:
                for hour in HOURS:
                    subject_id = request.POST.get(f'{day}_{hour}_subject')
                    faculty_id = request.POST.get(f'{day}_{hour}_faculty')

                    if not subject_id and not faculty_id:
                        Timetable.objects.filter(
                            semester=semester,
                            day_of_week=day,
                            hour_slot=hour
                        ).delete()
                    else:
                        Timetable.objects.update_or_create(
                            semester=semester,   # ✅ instance
                            day_of_week=day,
                            hour_slot=hour,
                            defaults={
                                'subject_id': subject_id or None,
                                'faculty_id': faculty_id or None
                            }
                        )

            return redirect('semester_detail', sem=semester.id)

    # BUILD GRID
    grid = {}
    for day in DAYS:
        grid[day] = []
        for hour in HOURS:
            slot = timetable_slots.filter(
                day_of_week=day,
                hour_slot=hour
            ).first()
            grid[day].append(slot)

    return render(request, 'admin/semester_detail.html', {
        'semester': semester,
        'students': students,
        'faculties': faculties,
        'subjects': subjects,
        'grid': grid,
        'timetable_exists': timetable_exists,
        'hours': HOURS
    })


DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
HOURS = [1, 2, 3, 4, 5, 6]

@login_required
def faculty_dashboard(request):
    faculty = get_object_or_404(Faculty, user=request.user)

    view_mode = request.GET.get('view', 'timetable')

    semesters = Semester.objects.filter(
        timetable__faculty=faculty
    ).distinct()

    context = {
        'faculty': faculty,
        'semesters': semesters,
        'view_mode': view_mode,
        'hours': HOURS
    }

    # ---------------- TIMETABLE VIEW ----------------
    if view_mode == 'timetable':
        slots = Timetable.objects.filter(
            faculty=faculty
        ).select_related('semester', 'subject')

        grid = {}
        for day in DAYS:
            grid[day] = []
            for hour in HOURS:
                slot = slots.filter(
                    day_of_week=day,
                    hour_slot=hour
                ).first()
                grid[day].append(slot)

        context['timetable_grid'] = grid

    # ---------------- SEMESTER / SUBJECT VIEW ----------------
    if view_mode == 'semester':
        sem_id = request.GET.get('semester')
        selected_semester = get_object_or_404(Semester, id=sem_id)

        subjects = Subject.objects.filter(
            timetable__faculty=faculty,
            timetable__semester=selected_semester
        ).distinct()

        context.update({
            'selected_semester': selected_semester,
            'subjects': subjects
        })

    return render(request, 'faculty/dashboard.html', context)



DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
HOURS = [1, 2, 3, 4, 5, 6]

@login_required
def attendance_week_view(request, subject_id):
    faculty = get_object_or_404(Faculty, user=request.user)
    subject = get_object_or_404(Subject, id=subject_id)

    # Get semester from timetable
    timetable_entries = Timetable.objects.filter(
        faculty=faculty,
        subject=subject
    )

    semester_id = request.GET.get('semester')
    semester = get_object_or_404(Semester, id=semester_id)


    # Week calculation
    today = date.today()
    selected_date_str = request.GET.get('date')

    if selected_date_str:
        selected_date = date.fromisoformat(selected_date_str)
    else:
        selected_date = today

    # Prevent future dates
    if selected_date > today:
        selected_date = today

    # Build date range: selected_date → today
    date_range = []
    current = selected_date

    while current <= today:
        date_range.append(current)
        current += timedelta(days=1)


    # Build grid
    grid = []

    for day_date in date_range:
        day_name = day_date.strftime('%A')

        row = {
            'date': day_date,
            'day': day_name,
            'periods': []
        }

        for hour in HOURS:
            is_scheduled = Timetable.objects.filter(
                faculty=faculty,
                subject=subject,
                semester=semester,
                day_of_week=day_name,
                hour_slot=hour
            ).exists()

            if not is_scheduled:
                row['periods'].append({'status': 'disabled'})
                continue

            session_exists = AttendanceSession.objects.filter(
                faculty=faculty,
                subject=subject,
                semester=semester,
                date=day_date,
                period=hour
            ).exists()

            row['periods'].append({
                'status': 'edit' if session_exists else 'add',
                'date': day_date,
                'period': hour
            })

        grid.append(row)

    context = {
        'subject': subject,
        'semester': semester,
        'grid': grid,
        'selected_date': selected_date,
        'today': today,
        'hours': HOURS,
    }

    context.update(
        faculty_sidebar_context(
            faculty=faculty,
            view_mode='attendance',
            selected_semester=semester
        )
    )

    return render(request, 'faculty/attendance_week.html', context)

from .models import Student, Timetable, Faculty, Semester, Subject, AttendanceSession, AttendanceRecord, Marks
@login_required
def mark_attendance(request):
    subject_id = request.GET.get("subject")
    semester_id = request.GET.get("semester")
    date_str = request.GET.get("date")
    period = request.GET.get("period")

    subject = Subject.objects.get(id=subject_id)
    semester = Semester.objects.get(id=semester_id)
    attendance_date = date.fromisoformat(date_str)
    faculty=request.user.faculty

    session, _ = AttendanceSession.objects.get_or_create(
        subject=subject,
        semester=semester,
        date=attendance_date,
        period=period,
        faculty=faculty
    )

    students = Student.objects.filter(semester=semester)

    if request.method == "POST":
        AttendanceRecord.objects.filter(session=session).delete()

        for student in students:
            is_present = request.POST.get(f"present_{student.reg_number}")
            AttendanceRecord.objects.create(
                session=session,
                student=student,
                is_present=bool(is_present)
            )

        messages.success(request, "Attendance saved successfully.")
        return redirect(
        f"{reverse('attendance_week', args=[subject.id])}?semester={semester.id}&date={attendance_date}"
        )

    attendance_map = {
    r.student.reg_number: r.is_present
    for r in AttendanceRecord.objects.filter(session=session)
}


    return render(request, "faculty/mark_attendance.html", {
        "subject": subject,
        "semester": semester,
        "period": period,
        "students": students,
        "attendance_map": attendance_map,
        "date": attendance_date,
    })
@login_required
def mark_marks(request, subject_id, semester_id):
    subject = get_object_or_404(Subject, id=subject_id)
    semester = get_object_or_404(Semester, id=semester_id)

    students = Student.objects.filter(semester=semester)
    faculty = request.user.faculty

    # -------- SAVE MARKS --------
    if request.method == "POST":
        for student in students:
            internal = request.POST.get(f"internal_{student.reg_number}")
            assignment = request.POST.get(f"assignment_{student.reg_number}")
            lab = request.POST.get(f"lab_{student.reg_number}")

            Marks.objects.update_or_create(
                student=student,
                subject=subject,
                semester=semester,
                defaults={
                    "internal_marks": int(internal or 0),
                    "assignment_marks": int(assignment or 0),
                    "lab_marks": int(lab or 0),
                    "faculty": faculty
                }
            )

        messages.success(request, "Marks saved successfully.")
        return redirect("faculty_dashboard")

    # -------- LOAD EXISTING MARKS --------
    marks_dict = {
        m.student.reg_number: m
        for m in Marks.objects.filter(
            subject=subject,
            semester=semester
        )
    }

    for student in students:
        student.marks = marks_dict.get(student.reg_number)

    return render(request, "faculty/mark_marks.html", {
        "students": students,
        "subject": subject,
        "semester": semester,
    })




