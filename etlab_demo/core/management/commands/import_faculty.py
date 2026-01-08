import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Faculty

class Command(BaseCommand):
    help = "Import faculty users from CSV"

    def handle(self, *args, **kwargs):
        with open("faculty_data.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                faculty_id = row["faculty_id"].strip()
                name = row["name"].strip()
                email = row["email"].strip()
                role = row["role"].strip()
                password = row["password"].strip()

                user, created = User.objects.get_or_create(
                    username=faculty_id,
                    defaults={"email": email}
                )

                if created:
                    user.set_password(password)  # 🔐 hash password
                    user.save()

                faculty, _ = Faculty.objects.get_or_create(
                    user=user,
                    defaults={
                        "faculty_id": faculty_id,
                        "name": name,
                        "role": role,
                    }
                )

                self.stdout.write(
                    self.style.SUCCESS(f"Imported {faculty_id}")
                )
