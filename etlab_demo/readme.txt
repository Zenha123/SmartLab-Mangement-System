run etlab demo on port 8000
 and smartlab on port 8001
etlab/ run python manage.py import_students to load STUDENT data in csv to etlab(same for faculty)
in smartlab backend
    python manage.py shell
        from apps.students.services.etlab_sync import sync_students_from_etlab
        >>> sync_students_from_etlab()
        studnet sync done






------------------------------------

When running on LAN:

What IP does backend run on?

127.0.0.1? ❌ (won't work across devices)

0.0.0.0? ✅