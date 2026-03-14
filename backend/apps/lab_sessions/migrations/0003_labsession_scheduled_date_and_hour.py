from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab_sessions', '0002_labsession_subject_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='labsession',
            name='scheduled_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='labsession',
            name='scheduled_hour',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
