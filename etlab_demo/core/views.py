from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login
from .models import Student, Timetable, Faculty, Semester, Subject
from django.contrib.auth.decorators import login_required

# LOGIN VIEW
def login_view(request):
    error = None

    if request.method == 'POST':
        role = request.POST['role']
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            if role == 'admin' and user.is_staff:
                return redirect('semester_list')
            if role == 'faculty' and not user.is_staff:
                return redirect('faculty_dashboard')  # Placeholder for faculty dashboard
            else:
                error = "Invalid role selection"
        else:
            error = "Invalid credentials"

    return render(request, 'auth/login.html', {'error': error})


# ADMIN: semester list
def semester_list(request):
    semesters = Semester.objects.all()
    return render(request, 'admin/semester_list.html', {'semesters': semesters})


# ADMIN: semester detail

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
HOURS = [1, 2, 3, 4, 5, 6]

def semester_detail(request, sem):
    semester = get_object_or_404(Semester, id=sem)
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