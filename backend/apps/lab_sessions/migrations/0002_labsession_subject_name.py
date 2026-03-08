# Generated manually for subject sync

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab_sessions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='labsession',
            name='subject_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
