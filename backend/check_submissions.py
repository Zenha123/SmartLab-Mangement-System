import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.evaluation.models import TaskSubmission, Task
from apps.students.models import Student

print("=" * 60)
print("CHECKING SUBMISSIONS")
print("=" * 60)

submissions = TaskSubmission.objects.all()
print(f"\nTotal submissions: {submissions.count()}")

if submissions.exists():
    for s in submissions:
        print(f"\n--- Submission {s.id} ---")
        print(f"Student: {s.student.name} (ID: {s.student.student_id})")
        print(f"Task: {s.task.title}")
        print(f"Batch: {s.task.batch.name} (ID: {s.task.batch.id})")
        print(f"Status: {s.status}")
        print(f"File: {s.file_path}")
        print(f"Submitted: {s.submitted_at}")
else:
    print("\n❌ NO SUBMISSIONS FOUND!")
    print("\nChecking tasks...")
    tasks = Task.objects.all()
    print(f"Total tasks: {tasks.count()}")
    if tasks.exists():
        for t in tasks:
            print(f"  - Task {t.id}: {t.title} (Batch: {t.batch.name})")
    
    print("\nChecking students...")
    students = Student.objects.all()
    print(f"Total students: {students.count()}")
    if students.exists():
        for st in students[:5]:  # First 5
            print(f"  - {st.name} ({st.student_id}) - Batch: {st.batch.name if st.batch else 'NO BATCH'}")

print("\n" + "=" * 60)
