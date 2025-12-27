# Smart Lab Management System - Backend

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Faculty Users

```bash
python manage.py create_faculty
```

This creates the following faculty accounts:
- **FAC001** / password123 (Shireen)
- **FAC002** / admin123 (John Doe)
- **admin** / admin (Admin User)
- **test** / test (Test User)

### 4. Load Mock Data

```bash
python manage.py loaddata fixtures/initial_data.json
```

This loads:
- 3 Semesters (Sem 1, 2, 3)
- 2 Batches per semester
- 6 Students in Batch 1
- PC mappings (PC-01 to PC-06)

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Backend will be available at: **http://localhost:8000**

---

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Faculty login
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/profile/` - Get current faculty profile

### Core
- `GET /api/semesters/` - List semesters
- `GET /api/batches/?semester={id}` - List batches
- `GET /api/pc-mappings/?batch={id}` - List PC mappings

### Students
- `GET /api/students/?batch={id}` - List students
- `GET /api/students/{id}/` - Get student details
- `POST /api/students/{id}/mark_online/` - Mark student online
- `POST /api/students/{id}/mark_offline/` - Mark student offline
- `POST /api/students/{id}/set_mode/` - Change student mode

### Sessions
- `GET /api/sessions/?batch={id}` - List lab sessions
- `POST /api/sessions/` - Start new session
- `POST /api/sessions/{id}/end_session/` - End session
- `GET /api/sessions/{id}/attendance/` - Get attendance

### Evaluation
- `GET /api/viva/?session={id}` - List viva records
- `POST /api/viva/` - Submit viva marks
- `POST /api/exams/` - Start exam session
- `GET /api/tasks/?batch={id}` - List tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/submissions/` - Get submissions

### Reports
- `GET /api/evaluation/reports/attendance/?batch={id}&date={date}` - Attendance report
- `GET /api/evaluation/reports/viva/?batch={id}` - Viva marks report
- `GET /api/evaluation/reports/submissions/?batch={id}` - Submission report

### WebSocket
- `ws://localhost:8000/ws/monitor/{batch_id}/?token={jwt_token}` - Live monitoring

---

## Testing the API

### 1. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"faculty_id": "test", "password": "test"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1Qi...",
  "refresh": "eyJ0eXAiOiJKV1Qi...",
  "faculty": {
    "id": 5,
    "faculty_id": "test",
    "name": "Test User",
    "email": "test@test.com"
  }
}
```

### 2. Get Students (with JWT)

```bash
curl -X GET "http://localhost:8000/api/students/?batch=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Start Lab Session

```bash
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"batch": 1, "session_type": "regular"}'
```

---

## Django Admin

Access at: **http://localhost:8000/admin/**

Create superuser first:
```bash
python manage.py createsuperuser
```

---

## Database

Using SQLite for development: `db.sqlite3`

To switch to PostgreSQL (production):
1. Install: `pip install psycopg2-binary`
2. Update `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lab_management',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Project Structure

```
backend/
├── apps/
│   ├── accounts/       # Faculty authentication
│   ├── core/           # Semesters, Batches, PC Mappings
│   ├── students/       # Students, Attendance
│   ├── sessions/       # Lab Sessions
│   ├── evaluation/     # Viva, Exams, Tasks
│   └── monitor/        # WebSocket consumers
├── config/             # Django settings
├── fixtures/           # Mock data
├── manage.py
└── requirements.txt
```

---

## Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt
```

### Migration Errors
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### WebSocket Connection Issues
Make sure you're using Daphne ASGI server:
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

---

## Next Steps

1. Run backend: `python manage.py runserver`
2. Test API endpoints with Postman or curl
3. Connect PyQt6 frontend (see Phase 3)
