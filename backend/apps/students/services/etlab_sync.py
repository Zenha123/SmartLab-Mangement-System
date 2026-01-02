import requests
from django.conf import settings
from apps.students.models import Student
from apps.core.models import Batch, Semester

ETLAB_API = "http://127.0.0.1:8000/api/students/"


def semester_to_year(semester_name):
    try:
        sem_no = int(semester_name.split()[-1])
        return (sem_no + 1) // 2
    except Exception:
        return 1


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

        Student.objects.update_or_create(
            student_id=reg_no,
            defaults={
                "name": name,
                "batch": batch,
            }
        )

    print("✅ Secure student sync completed")
