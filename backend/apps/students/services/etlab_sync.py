import requests
from ..models import Student
from apps.core.models import Batch, Semester

ETLAB_API = "http://127.0.0.1:8000/api/students/"


def semester_to_year(semester_name):
    try:
        sem_no = int(semester_name.split()[-1])
        return (sem_no + 1) // 2
    except Exception:
        return 1


def sync_students_from_etlab():
    response = requests.get(ETLAB_API, timeout=10)
    response.raise_for_status()

    for s in response.json():
        semester_name = s["semester"]          # "Semester 3"
        semester_no = int(semester_name.split()[-1])

        # 1️⃣ Get or create Semester
        semester_obj, _ = Semester.objects.get_or_create(
            number=semester_no,
            defaults={"name": semester_name}
        )

        # 2️⃣ Get or create Batch (WITH semester!)
        batch, _ = Batch.objects.get_or_create(
            name=semester_name,
            semester=semester_obj,
            defaults={
                "year": semester_to_year(semester_name)
            }
        )

        # 3️⃣ Create / update Student
        Student.objects.update_or_create(
            student_id=s['reg_number'],
            defaults={
                'name': s['name'],
                'batch': batch,
            }
        )

    print("✅ Students synced successfully from eTLab")
