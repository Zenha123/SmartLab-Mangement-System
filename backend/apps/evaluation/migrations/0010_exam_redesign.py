from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0009_alter_vivarecord_is_published'),
        ('core', '0001_initial'),
        ('accounts', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        # Drop old tables first (they may not exist if DB was fresh)
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    "DROP TABLE IF EXISTS exam_results;",
                    reverse_sql="",
                ),
                migrations.RunSQL(
                    "DROP TABLE IF EXISTS exam_sessions;",
                    reverse_sql="",
                ),
            ],
            state_operations=[
                migrations.DeleteModel(name='ExamResult'),
                migrations.DeleteModel(name='ExamSession'),
            ],
        ),

        # Create new ExamSession
        migrations.CreateModel(
            name='ExamSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Lab Exam', max_length=200)),
                ('duration_minutes', models.IntegerField(default=120)),
                ('status', models.CharField(
                    choices=[('scheduled', 'Scheduled'), ('active', 'Active'), ('completed', 'Completed')],
                    default='scheduled', max_length=15
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                            related_name='exam_sessions', to='core.batch')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='exam_sessions', to='accounts.user')),
            ],
            options={'db_table': 'exam_sessions', 'ordering': ['-created_at']},
        ),

        # Create ExamQuestion
        migrations.CreateModel(
            name='ExamQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField()),
                ('marks', models.IntegerField(default=10)),
                ('difficulty', models.CharField(
                    blank=True,
                    choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
                    default='medium', max_length=10
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='questions', to='evaluation.examsession')),
            ],
            options={'db_table': 'exam_questions', 'ordering': ['created_at']},
        ),

        # Create StudentExam
        migrations.CreateModel(
            name='StudentExam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submission_file', models.FileField(blank=True, null=True, upload_to='exam_submissions/')),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('marks', models.IntegerField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True)),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('submitted', 'Submitted'), ('evaluated', 'Evaluated')],
                    default='pending', max_length=15
                )),
                ('is_published', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='student_exams', to='evaluation.examsession')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='student_exams', to='students.student')),
                ('assigned_questions', models.ManyToManyField(
                    blank=True, related_name='student_exams', to='evaluation.examquestion'
                )),
            ],
            options={'db_table': 'student_exams', 'ordering': ['-created_at'],
                     'unique_together': {('session', 'student')}},
        ),
    ]
