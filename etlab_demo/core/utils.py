from .models import Semester

def faculty_sidebar_context(faculty, view_mode='timetable', selected_semester=None):
    semesters = Semester.objects.filter(
        timetable__faculty=faculty
    ).distinct()

    return {
        'faculty': faculty,
        'semesters': semesters,
        'view_mode': view_mode,
        'selected_semester': selected_semester
    }
