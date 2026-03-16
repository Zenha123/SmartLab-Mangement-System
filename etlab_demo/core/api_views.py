from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Student, Faculty, Timetable, Semester, Subject, AttendanceSession, AttendanceRecord
from .serializers import studentSerializer, facultySerializer, timetableSyncSerializer
from django.conf import settings

def check_service_token(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return False

    try:
        scheme, token = auth_header.split()
        return scheme == "Bearer" and token == settings.ETLAB_SERVICE_TOKEN
    except ValueError:
        return False


@api_view(['GET'])
def student_list(request):
    if not check_service_token(request):
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    students = Student.objects.all()
    serializer = studentSerializer(students, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def faculty_list(request):
    if not check_service_token(request):
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    faculties = Faculty.objects.all().select_related("user")
    serializer = facultySerializer(faculties, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def timetable_list(request):
    if not check_service_token(request):
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    slots = (
        Timetable.objects
        .filter(faculty__isnull=False, subject__isnull=False)
        .select_related("semester", "subject", "faculty")
    )
    serializer = timetableSyncSerializer(slots, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def attendance_sync(request):
    if not check_service_token(request):
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    sessions = request.data.get("sessions") or []
    if not isinstance(sessions, list) or not sessions:
        return Response({"detail": "No attendance sessions provided."}, status=status.HTTP_400_BAD_REQUEST)

    sessions_synced = 0
    records_synced = 0
    not_available_records = 0

    with transaction.atomic():
        for session_payload in sessions:
            faculty_id = (session_payload.get("faculty_id") or "").strip().upper()
            subject_name = (session_payload.get("subject_name") or "").strip()
            semester_number = session_payload.get("semester_number")
            semester_name = (session_payload.get("semester_name") or f"Semester {semester_number}").strip()
            session_date = session_payload.get("date")
            period = session_payload.get("period")
            source_batch = (session_payload.get("source_batch") or "").strip()
            record_payloads = session_payload.get("records") or []

            if not (faculty_id and subject_name and semester_number and session_date and period):
                return Response({"detail": "Attendance session payload is missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

            faculty = Faculty.objects.filter(faculty_id=faculty_id).first()
            if not faculty:
                return Response({"detail": f"Faculty '{faculty_id}' not found in ETLab."}, status=status.HTTP_400_BAD_REQUEST)

            semester, _ = Semester.objects.get_or_create(
                number=int(semester_number),
                defaults={"semester_name": semester_name},
            )
            if semester.semester_name != semester_name:
                semester.semester_name = semester_name
                semester.save(update_fields=["semester_name"])

            subject, _ = Subject.objects.get_or_create(subject_name=subject_name)
            attendance_session, created = AttendanceSession.objects.get_or_create(
                subject=subject,
                semester=semester,
                date=session_date,
                period=int(period),
                faculty=faculty,
                defaults={
                    "remarks": f"Synced from SmartLab batch {source_batch}" if source_batch else "Synced from SmartLab",
                },
            )
            if not created and source_batch:
                attendance_session.remarks = f"Synced from SmartLab batch {source_batch}"
                attendance_session.save(update_fields=["remarks", "updated_at"])

            AttendanceRecord.objects.filter(session=attendance_session).delete()

            for record_payload in record_payloads:
                reg_number = (record_payload.get("reg_number") or "").strip().upper()
                student_name = (record_payload.get("name") or "").strip()
                attendance_status = (record_payload.get("status") or "absent").strip().lower()

                if attendance_status not in {"present", "absent", "not_available"}:
                    attendance_status = "absent"

                student = Student.objects.filter(reg_number=reg_number).first()
                if not student:
                    continue

                if student_name and student.name != student_name:
                    student.name = student_name
                    student.save(update_fields=["name"])
                if student.semester_id != semester.id:
                    student.semester = semester
                    student.save(update_fields=["semester"])

                AttendanceRecord.objects.create(
                    session=attendance_session,
                    student=student,
                    is_present=attendance_status == "present",
                    status=attendance_status,
                )
                records_synced += 1
                if attendance_status == "not_available":
                    not_available_records += 1

            sessions_synced += 1

    return Response(
        {
            "sessions_synced": sessions_synced,
            "records_synced": records_synced,
            "not_available_records": not_available_records,
        },
        status=status.HTTP_200_OK,
    )
