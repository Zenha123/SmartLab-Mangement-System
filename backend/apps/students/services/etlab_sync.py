import requests
from django.conf import settings
from apps.students.models import Student
from apps.core.models import Batch, Semester
from django.contrib.auth import get_user_model
from django.db import transaction

ETLAB_API = "http://127.0.0.1:8000/api/students/"

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

        Student.objects.update_or_create(
            student_id=reg_no,
            defaults={
                "name": name,
                "batch": batch,
                "user":user,
            }
        )

    print("✅ Secure student synced with default passwords")


'''student default password format:
{name}_{reg_number} all in lowercase and spaces removed.
E.g., for a student named "John Doe" with reg_number "CS2023001
the default password will be "johndoe_cs2023001"
'''