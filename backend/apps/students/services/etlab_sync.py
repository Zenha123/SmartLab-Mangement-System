import requests
from django.conf import settings
from apps.students.models import Student
from apps.core.models import Batch, Semester
from django.contrib.auth import get_user_model
from django.db import transaction

ETLAB_API = "http://127.0.0.1:8001/api/students/"
ETLAB_FACULTY_API = "http://127.0.0.1:8001/api/faculty/"

UserModel = get_user_model()

def semester_to_year(semester_name):
    try:
        sem_no = int(semester_name.split()[-1])
        return (sem_no + 1) // 2
    except Exception:
        return 1

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

    for s in response.json():
        reg_no = s["reg_number"].strip().upper()
        name = s["name"].strip()
        semester_name = s["semester"]
        semester_no = int(semester_name.split()[-1])

        semester_obj, _ = Semester.objects.get_or_create(
            number=semester_no,
            defaults={"name": semester_name}
        )

        batch, _ = Batch.objects.get_or_create(
            semester=semester_obj,
            name="Batch 1",
            defaults={"year": semester_to_year(semester_name)}
        )

        user, created = UserModel.objects.get_or_create(
            faculty_id=reg_no,
            defaults={
                "name": name,
                "email": f"{reg_no.lower()}@student.local",
                "is_active": True,
            }
        )

        if created or not user.has_usable_password():
            default_password = f"{name}_{reg_no}".replace(" ", "").lower()
            user.set_password(default_password)
            user.save()

        _, created_student = Student.objects.update_or_create(
            student_id=reg_no,
            defaults={
                "name": name,
                "batch": batch,
                "user":user,
            }
        )

        if created_student:
            created_count += 1
        else:
            updated_count += 1

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


'''student default password format:
{name}_{reg_number} all in lowercase and spaces removed.
E.g., for a student named "John Doe" with reg_number "CS2023001
the default password will be "johndoe_cs2023001"
'''
