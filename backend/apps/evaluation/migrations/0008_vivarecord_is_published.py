from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0007_alter_vivarecord_viva_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='vivarecord',
            name='is_published',
            field=models.BooleanField(default=False, help_text='Faculty publishes for student to see'),
        ),
    ]
