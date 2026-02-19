from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0003_tasksubmission_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasksubmission',
            name='submission_file',
            field=models.FileField(blank=True, null=True, upload_to='submissions/'),
        ),
    ]
