import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Import faculty data from ETLAB CSV into SmartLab"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                faculty_id = row['faculty_id']
                name = row['name']
                email = row['email']
                role = row['role'].upper()
                password = row['password']

                is_staff = True
                is_superuser = True if role == 'ADMIN' else False

                user, created = User.objects.update_or_create(
                    faculty_id=faculty_id,
                    defaults={
                        'name': name,
                        'email': email,
                        'is_staff': is_staff,
                        'is_superuser': is_superuser,
                        'is_active': True,
                    }
                )

                if created or not user.has_usable_password():
                    user.set_password(password)
                    user.save()

        self.stdout.write(
            self.style.SUCCESS("ETLAB faculty imported successfully")
        )