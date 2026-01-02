import csv
from django.core.management.base import BaseCommand, CommandError
from core.models import Student, Semester


class Command(BaseCommand):
    help = "Import students from CSV file (reg_number,name,semester_number)"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to CSV file",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]

        try:
            with open(csv_file, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                # ✅ Validate CSV headers
                required_fields = {"reg_number", "name", "semester_number"}
                if not reader.fieldnames or not required_fields.issubset(reader.fieldnames):
                    raise CommandError(
                        "CSV must contain columns: reg_number, name, semester_number"
                    )

                created = 0
                skipped = 0

                for row in reader:
                    try:
                        reg_number = row["reg_number"].strip()
                        name = row["name"].strip()
                        semester_no = int(row["semester_number"])

                        if not reg_number or not name:
                            skipped += 1
                            continue

                        semester_name = f"Semester {semester_no}"

                        # ✅ AUTO-CREATE SEMESTER
                        semester, _ = Semester.objects.get_or_create(
                            semester_name=semester_name
                        )

                        student, is_created = Student.objects.get_or_create(
                            reg_number=reg_number,
                            defaults={
                                "name": name,
                                "semester": semester,
                            },
                        )

                        if is_created:
                            created += 1
                        else:
                            skipped += 1

                    except Exception:
                        skipped += 1
                        continue

        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_file}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed successfully: {created} created, {skipped} skipped"
            )
        )
