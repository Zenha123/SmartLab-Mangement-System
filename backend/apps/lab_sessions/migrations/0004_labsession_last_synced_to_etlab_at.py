from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lab_sessions", "0003_labsession_scheduled_date_and_hour"),
    ]

    operations = [
        migrations.AddField(
            model_name="labsession",
            name="last_synced_to_etlab_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
