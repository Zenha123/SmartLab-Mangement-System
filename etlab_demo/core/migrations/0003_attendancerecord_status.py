from django.db import migrations, models


def populate_attendance_status(apps, schema_editor):
    AttendanceRecord = apps.get_model("core", "AttendanceRecord")
    for record in AttendanceRecord.objects.all().iterator():
        record.status = "present" if record.is_present else "absent"
        record.save(update_fields=["status"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_marks"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendancerecord",
            name="status",
            field=models.CharField(
                choices=[
                    ("present", "Present"),
                    ("absent", "Absent"),
                    ("not_available", "Not Available"),
                ],
                default="absent",
                max_length=20,
            ),
        ),
        migrations.RunPython(populate_attendance_status, migrations.RunPython.noop),
    ]
