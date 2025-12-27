"""
Management command to create faculty users with proper password hashing.
Run with: python manage.py create_faculty
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Create faculty users with hashed passwords'

    def handle(self, *args, **options):
        faculty_data = [
            {'faculty_id': 'FAC001', 'email': 'shireen@university.edu', 'name': 'Shireen', 'password': 'password123'},
            {'faculty_id': 'FAC002', 'email': 'john.doe@university.edu', 'name': 'John Doe', 'password': 'admin123'},
            {'faculty_id': 'FAC003', 'email': 'jane.smith@university.edu', 'name': 'Jane Smith', 'password': 'faculty123'},
            {'faculty_id': 'admin', 'email': 'admin@test.com', 'name': 'Admin User', 'password': 'admin'},
            {'faculty_id': 'test', 'email': 'test@test.com', 'name': 'Test User', 'password': 'test'},
        ]

        for data in faculty_data:
            user, created = User.objects.get_or_create(
                faculty_id=data['faculty_id'],
                defaults={
                    'email': data['email'],
                    'name': data['name'],
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created faculty: {user.faculty_id}'))
            else:
                self.stdout.write(self.style.WARNING(f'Faculty already exists: {user.faculty_id}'))
