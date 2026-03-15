import requests
from django.conf import settings
from apps.students.models import Student
from apps.core.models import Batch, Semester, FacultyTimetableSlot
from django.contrib.auth import get_user_model
from django.db import transaction
from collections import defaultdict

ETLAB_API = "http://127.0.0.1:8001/api/students/"
ETLAB_FACULTY_API = "http://127.0.0.1:8001/api/faculty/"
ETLAB_TIMETABLE_API = "http://127.0.0.1:8001/api/timetable/"

UserModel = get_user_model()

def semester_to_year(semester_name):
    try:
        sem_no = int(semester_name.split()[-1])
        return (sem_no + 1) // 2
    except Exception:
        return 1


def _default_batches_for_semester(semester_obj, semester_name):
    year = semester_to_year(semester_name)
    batch_1, _ = Batch.objects.get_or_create(
        semester=semester_obj,
        name="Batch 1",
        defaults={"year": year},
    )
    batch_2, _ = Batch.objects.get_or_create(
        semester=semester_obj,
        name="Batch 2",
        defaults={"year": year},
    )

    dirty_fields = []
    if batch_1.year != year:
        batch_1.year = year
        dirty_fields.append("year")
    if batch_2.year != year:
        batch_2.year = year
        dirty_fields.append("year")
    if dirty_fields:
        batch_1.save(update_fields=dirty_fields)
        batch_2.save(update_fields=dirty_fields)

    return batch_1, batch_2

@transaction.atomic
def sync_students_from_etlab():
    headers = {
        "Authorization": f"Bearer {settings.ETLAB_SERVICE_TOKEN}"
    }

    response = requests.get(
        ETLAB_API,
        headers=headers,
        timeout=10
    )
    response.raise_for_status()

    created_count = 0
    updated_count = 0
    students_by_semester = defaultdict(list)

    for s in response.json():
        reg_no = s["reg_number"].strip().upper()
        name = s["name"].strip()
        semester_name = s["semester"]
        semester_no = int(semester_name.split()[-1])

        semester_obj, _ = Semester.objects.get_or_create(
            number=semester_no,
            defaults={"name": semester_name}
        )
        if semester_obj.name != semester_name:
            semester_obj.name = semester_name
            semester_obj.save(update_fields=["name"])

        students_by_semester[semester_obj].append(
            {
                "reg_no": reg_no,
                "name": name,
                "semester_name": semester_name,
            }
        )

    for semester_obj, semester_students in students_by_semester.items():
        semester_students.sort(key=lambda item: item["reg_no"])
        batch_1, batch_2 = _default_batches_for_semester(
            semester_obj,
            semester_students[0]["semester_name"],
        )
        split_index = (len(semester_students) + 1) // 2

        for index, student_payload in enumerate(semester_students):
            reg_no = student_payload["reg_no"]
            name = student_payload["name"]
            batch = batch_1 if index < split_index else batch_2

            user, created = UserModel.objects.get_or_create(
                faculty_id=reg_no,
                defaults={
                    "name": name,
                    "email": f"{reg_no.lower()}@student.local",
                    "is_active": True,
                }
            )

            user_dirty_fields = []
            if user.name != name:
                user.name = name
                user_dirty_fields.append("name")
            expected_email = f"{reg_no.lower()}@student.local"
            if not user.email:
                user.email = expected_email
                user_dirty_fields.append("email")
            if not user.is_active:
                user.is_active = True
                user_dirty_fields.append("is_active")
            if created or not user.has_usable_password():
                default_password = f"{name}_{reg_no}".replace(" ", "").lower()
                user.set_password(default_password)
                user_dirty_fields.append("password")
            if user_dirty_fields:
                user.save(update_fields=user_dirty_fields)

            _, created_student = Student.objects.update_or_create(
                student_id=reg_no,
                defaults={
                    "name": name,
                    "batch": batch,
                    "user": user,
                }
            )

            if created_student:
                created_count += 1
            else:
                updated_count += 1

        batch_1.total_students = split_index
        batch_1.save(update_fields=["total_students"])
        batch_2.total_students = len(semester_students) - split_index
        batch_2.save(update_fields=["total_students"])

    return {
        "synced": created_count + updated_count,
        "created": created_count,
        "updated": updated_count,
    }


@transaction.atomic
def sync_faculty_from_etlab():
    headers = {
        "Authorization": f"Bearer {settings.ETLAB_SERVICE_TOKEN}"
    }

    response = requests.get(
        ETLAB_FACULTY_API,
        headers=headers,
        timeout=10
    )
    response.raise_for_status()

    created_count = 0
    updated_count = 0

    for f in response.json():
        faculty_id = f["faculty_id"].strip().upper()
        name = f["name"].strip()
        email = (f.get("email") or f"{faculty_id.lower()}@faculty.local").strip().lower()
        role = (f.get("role") or "FACULTY").strip().upper()

        defaults = {
            "name": name,
            "email": email,
            "is_active": True,
            "is_staff": role == "ADMIN",
        }

        user, created = UserModel.objects.update_or_create(
            faculty_id=faculty_id,
            defaults=defaults,
        )

        if created:
            created_count += 1
            user.set_password(f"{faculty_id.lower()}@123")
            user.save(update_fields=["password"])
        else:
            updated_count += 1

    return {
        "synced": created_count + updated_count,
        "created": created_count,
        "updated": updated_count,
    }


@transaction.atomic
def sync_timetable_from_etlab():
    headers = {
        "Authorization": f"Bearer {settings.ETLAB_SERVICE_TOKEN}"
    }

    response = requests.get(
        ETLAB_TIMETABLE_API,
        headers=headers,
        timeout=10
    )
    response.raise_for_status()

    timetable_rows = response.json()

    FacultyTimetableSlot.objects.all().delete()

    created_count = 0
    skipped_count = 0

    for row in timetable_rows:
        faculty_id = (row.get("faculty_id") or "").strip().upper()
        subject_name = (row.get("subject_name") or "").strip()
        day_of_week = (row.get("day_of_week") or "").strip()
        hour_slot = row.get("hour_slot")
        semester_no = row.get("semester_number")
        semester_name = (row.get("semester_name") or f"Sem {semester_no}").strip()

        if not (faculty_id and subject_name and day_of_week and hour_slot and semester_no):
            skipped_count += 1
            continue

        faculty = UserModel.objects.filter(faculty_id=faculty_id).first()
        if not faculty:
            skipped_count += 1
            continue

        semester_obj, _ = Semester.objects.get_or_create(
            number=int(semester_no),
            defaults={"name": semester_name}
        )

        FacultyTimetableSlot.objects.create(
            faculty=faculty,
            semester=semester_obj,
            day_of_week=day_of_week,
            hour_slot=int(hour_slot),
            subject_name=subject_name
        )
        created_count += 1

    return {
        "synced": created_count,
        "created": created_count,
        "updated": 0,
        "skipped": skipped_count,
    }


'''student default password format:
{name}_{reg_number} all in lowercase and spaces removed.
E.g., for a student named "John Doe" with reg_number "CS2023001
the default password will be "johndoe_cs2023001"
'''
