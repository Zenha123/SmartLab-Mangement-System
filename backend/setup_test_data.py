import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.core.models import Semester, Batch
from apps.students.models import Student
from apps.lab_sessions.models import LabSession

User = get_user_model()

def create_test_data():
    print("🚀 Creating Test Data...")

    # 1. Create Faculty
    faculty, created = User.objects.get_or_create(
        faculty_id="F001",
        defaults={
            "email": "faculty@test.com",
            "name": "Dr. Smith",
            "is_active": True,
            "is_staff": True
        }
    )
    if created:
        faculty.set_password("pass1234")
        faculty.save()
        print(f"✅ Faculty created: {faculty.faculty_id} / pass1234")
    else:
        print(f"ℹ️ Faculty already exists: {faculty.faculty_id}")

    # 2. Create Semester & Batch
    semester, _ = Semester.objects.get_or_create(name="Sem 1", number=1)
    batch, created = Batch.objects.get_or_create(
        semester=semester,
        name="Batch A",
        defaults={"year": 2026}
    )
    if created:
        print(f"✅ Batch created: {batch}")
    else:
        print(f"ℹ️ Batch exists: {batch}")

    # 3. Create Student User & Profile
    student_user, created = User.objects.get_or_create(
        faculty_id="S001",  # Reusing User model for student auth as per existing system
        defaults={
            "email": "student@test.com",
            "name": "John Doe",
            "is_active": True
        }
    )
    if created:
        student_user.set_password("1234")
        student_user.save()
        print(f"✅ Student User created: S001 / 1234")
    else:
        print(f"ℹ️ Student User exists: S001")

    # Ensure Student Profile exists
    student_profile, created = Student.objects.get_or_create(
        user=student_user,
        defaults={
            "student_id": "S001",
            "name": "John Doe",
            "batch": batch,
            "email": "student@test.com"
        }
    )
    if created:
        print(f"✅ Student Profile created linked to {batch}")
    else:
        print(f"ℹ️ Student Profile exists linked to {batch}")

    print("\n🎉 Test Data Setup Complete!")
    print(f"👉 Use this Student Username: S001")
    print(f"👉 Use this Student Password: 1234")

if __name__ == "__main__":
    create_test_data()
