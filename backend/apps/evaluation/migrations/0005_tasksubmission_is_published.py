from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0004_tasksubmission_submission_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasksubmission',
            name='is_published',
            field=models.BooleanField(default=False),
        ),
    ]
