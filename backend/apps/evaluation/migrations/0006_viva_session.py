from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('core', '0001_initial'),
        ('lab_sessions', '0001_initial'),
        ('students', '0001_initial'),
        ('evaluation', '0005_tasksubmission_is_published'),
    ]

    operations = [
        migrations.CreateModel(
            name='VivaSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('viva_type', models.CharField(choices=[('offline', 'Offline (Face-to-Face)'), ('online', 'Online (Platform Based)')], default='offline', max_length=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('live', 'Live'), ('completed', 'Completed')], default='pending', max_length=15)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('platform_name', models.CharField(blank=True, max_length=100, null=True)),
                ('join_code', models.CharField(blank=True, max_length=50, null=True)),
                ('join_link', models.URLField(blank=True, max_length=500, null=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('instructions', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viva_sessions', to='core.batch')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='viva_sessions', to='accounts.user')),
            ],
            options={
                'db_table': 'viva_sessions',
                'ordering': ['-date', '-created_at'],
            },
        ),
        migrations.AddField(
            model_name='vivarecord',
            name='viva_session',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='records', to='evaluation.vivasession'),
        ),
        migrations.AlterField(
            model_name='vivarecord',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='viva_records', to='lab_sessions.labsession'),
        ),
        migrations.AlterUniqueTogether(
            name='vivarecord',
            unique_together={('student', 'viva_session')},
        ),
    ]
