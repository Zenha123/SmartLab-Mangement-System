# Smart Lab Management System - Technical Documentation

## 1. Project Overview

Smart Lab Management System is a multi-part academic lab platform built around a Django backend and two PyQt6 desktop clients:

- `backend/`: central API, authentication, attendance, task, viva, exam, report, control, and WebSocket services
- `lab/`: faculty desktop application
- `student/`: student desktop application
- `etlab_demo/`: ETLab-style demo data source used for faculty, student, and timetable sync

The system is designed for classroom/lab supervision. Faculty can start lab sessions, monitor attendance and student status, create tasks, run viva and exams, issue control commands, and generate reports. Students log in from lab machines, receive live events, submit work, and participate in viva and exams.

## 2. Current Architecture

### 2.1 High-level components

1. `backend/` runs the main business logic and persistence layer.
2. `lab/` consumes backend REST APIs and faculty WebSocket channels.
3. `student/` consumes backend REST APIs and student WebSocket channels.
4. `etlab_demo/` exposes service-token-protected sync endpoints used by the backend.
5. Redis is required by Django Channels for group messaging.

### 2.2 Runtime ports and endpoints

- Backend HTTP API: `http://127.0.0.1:8000`
- Backend WebSocket base: `ws://127.0.0.1:8000`
- ETLab demo sync source: `http://127.0.0.1:8001`

### 2.3 Main communication paths

- Faculty desktop -> Django REST API with JWT bearer tokens
- Student desktop -> Django REST API with JWT bearer tokens
- Faculty desktop -> `ws/monitor/<batch_id>/?token=<jwt>`
- Student desktop -> `ws/student/?token=<jwt>`
- Backend -> Redis channel layer -> WebSocket groups for live events
- Backend -> ETLab demo APIs using `ETLAB_SERVICE_TOKEN`

## 3. Technology Stack

### 3.1 Backend

- Python
- Django 4.2.9
- Django REST Framework
- Simple JWT
- Django Channels 4
- Daphne
- Redis / `channels_redis`
- SQLite for local development
- ReportLab for PDF reports

### 3.2 Faculty desktop

- PyQt6
- `requests`
- `websocket-client`
- `aiortc`, `mss`, `opencv-python`, `numpy`, `av` for live monitor / screen streaming support

### 3.3 Student desktop

- PyQt6
- `requests`
- `websocket-client`
- `aiortc`, `mss`, `opencv-python`, `numpy`, `av`

### 3.4 ETLab demo

- Django app exposing demo faculty, student, and timetable APIs

## 4. Repository Structure

```text
SmartLab-Mangement-System/
├── backend/                 # Main Django backend
│   ├── apps/
│   │   ├── accounts/        # Faculty auth and timetable APIs
│   │   ├── core/            # Semester, batch, PC mapping, timetable slot models
│   │   ├── students/        # Student model, attendance, sync services, student auth
│   │   ├── lab_sessions/    # Session lifecycle and attendance bootstrap
│   │   ├── evaluation/      # Viva, exam, tasks, submissions, reports
│   │   └── monitor/         # Control commands and WebSocket consumers
│   ├── config/              # Django settings, URL routing, ASGI/WSGI
│   └── fixtures/            # Seed/demo data
├── lab/                     # Faculty PyQt6 desktop
│   ├── api/                 # REST client helpers
│   ├── ui/common/           # Shared widgets and faculty WebSocket client
│   └── ui/screens/          # Faculty screens
├── student/                 # Student PyQt6 desktop
│   ├── api_client.py        # Student REST client functions
│   ├── websocket_client.py  # Student WebSocket + WebRTC flow
│   └── student_dashboard.py # Main student UI
├── etlab_demo/              # Demo ETLab clone used as sync source
└── technical.md             # This document
```

## 5. Backend Design

### 5.1 Installed apps

The main backend loads:

- `apps.accounts`
- `apps.core`
- `apps.students`
- `apps.lab_sessions`
- `apps.monitor`
- `apps.evaluation`

Third-party integrations include `daphne`, `channels`, `rest_framework`, `rest_framework_simplejwt`, `corsheaders`, and Redis channel layers.

### 5.2 Core configuration

- Database: SQLite at `backend/db.sqlite3`
- Auth model: `accounts.User`
- Default auth for API: JWT bearer auth
- Default API permission: authenticated
- CORS: fully open in development
- Media uploads: `backend/media/`
- Channel layer host: `127.0.0.1:6379`
- Service sync token: `ETLAB_SERVICE_TOKEN = "etlab-smartlab-secret-123"`

### 5.3 URL layout

Main backend routes are mounted from `backend/config/urls.py`:

- `/admin/`
- `/api/auth/`
- `/api/` core resources
- `/api/` student and attendance resources
- `/api/` lab session resources
- `/api/` evaluation resources
- `/api/` control resources

### 5.4 Authentication model

The project uses one custom `User` table for login identities. Faculty accounts live directly in `accounts.User`. Student login also reuses the same table, with each `students.Student` record linked through `Student.user`.

Implication:

- faculty login authenticates `User`
- student login also authenticates `User`
- student-specific data is resolved through `user.student_profile`

## 6. Data Model

### 6.1 Accounts

`accounts.User`

- `faculty_id` is the username field
- `email`
- `name`
- `is_active`
- `is_staff`
- `is_superuser`
- `created_at`
- `last_login`

Despite the field name, this model currently stores both faculty identities and student-linked identities.

### 6.2 Academic core

`core.Semester`

- semester name and numeric order

`core.Batch`

- belongs to a semester
- stores academic year and total student count

`core.PCMapping`

- maps one PC ID to one student and a batch

`core.FacultyTimetableSlot`

- links faculty, semester, day, hour slot, and subject name
- populated via ETLab sync

### 6.3 Students and attendance

`students.Student`

- one-to-one with `accounts.User`
- `student_id`
- `name`
- optional `email`
- `batch`
- live state fields: `status`, `current_mode`, `last_seen`

`students.Attendance`

- links `Student` to `LabSession`
- stores `login_time`, `logout_time`, `duration_minutes`, `status`

### 6.4 Lab session domain

`lab_sessions.LabSession`

- `faculty`
- `batch`
- `subject_name`
- `scheduled_date`
- `scheduled_hour`
- `session_type`: regular / viva / exam
- `status`: active / ended / paused
- `start_time`, `end_time`

When a session is created, attendance rows are bulk-created for all students in the batch. Students currently online are marked present at creation time.

### 6.5 Evaluation domain

`evaluation.VivaSession`

- faculty-owned viva configuration
- supports `offline` and `online`
- supports platform metadata for online viva

`evaluation.VivaRecord`

- per-student viva result
- can be linked to `VivaSession` and optionally `LabSession`
- supports `is_published`

`evaluation.ExamSession`

- faculty-owned exam for a batch
- `title`, `duration_minutes`, `subject_name`, `status`

`evaluation.ExamQuestion`

- questions attached to an exam session

`evaluation.StudentExam`

- per-student assignment and evaluation record
- stores assigned questions, uploaded file, marks, feedback, publish state

`evaluation.Task`

- batch-level assignment with title, description, deadline, subject

`evaluation.TaskSubmission`

- per-student task submission
- stores uploaded file, marks, feedback, publish state

### 6.6 Monitoring and control

`monitor.ControlCommand`

- faculty-issued action for a batch
- examples: `lock_pc`, `block_internet`, `disable_usb`, `app_whitelist`

`monitor.ControlState`

- current effective state for a batch
- PC lock, internet block, USB disable, app whitelist

## 7. Backend API Surface

## 7.1 Authentication and faculty profile

- `POST /api/auth/login/`
- `POST /api/auth/register/`
- `POST /api/auth/refresh/`
- `GET /api/auth/profile/`
- `GET /api/auth/timetable/weekly/`

## 7.2 Academic data

- `GET /api/semesters/`
- `GET /api/batches/`
- `GET /api/pc-mappings/`

## 7.3 Students and attendance

- `GET /api/students/`
- `POST /api/students/<id>/mark_online/`
- `POST /api/students/<id>/mark_offline/`
- `POST /api/students/<id>/set_mode/`
- `GET /api/attendance/`
- `POST /api/api/student/login/` from `students.urls`
- `POST /api/student/login/` from `students.api.urls`
- `GET /api/student/me/`

The student login path is duplicated in the codebase through two URL modules. The desktop app uses `/api/student/login/`.

## 7.4 Sync endpoints

- `POST /api/sync/faculty/`
- `POST /api/sync/students/`
- `POST /api/sync/timetable/`

These accept the ETLab service token through `Authorization: Bearer <token>` or `X-Service-Token`.

## 7.5 Lab sessions

- `GET /api/sessions/`
- `POST /api/sessions/`
- `POST /api/sessions/<id>/end_session/`
- `GET /api/sessions/<id>/attendance/`

## 7.6 Viva

- `GET /api/viva-sessions/`
- `POST /api/viva-sessions/`
- `POST /api/viva-sessions/<id>/publish/`
- `POST /api/viva-sessions/<id>/complete/`
- `GET /api/viva/`
- `POST /api/viva/`
- `POST /api/viva-results/`
- `GET /api/live-viva/`

## 7.7 Exams

- `GET /api/exam-sessions/`
- `POST /api/exam-sessions/`
- `GET /api/exam-questions/`
- `POST /api/exam-questions/`
- `POST /api/exam-start/`
- `POST /api/exam-end/`
- `GET /api/exam-submissions/?session_id=<id>`
- `POST /api/exam-evaluate/`
- `GET /api/my-exam/`
- `POST /api/submit-exam/`

## 7.8 Tasks and submissions

- `GET /api/tasks/`
- `POST /api/tasks/`
- `GET /api/tasks/<id>/submissions/`
- `GET /api/submissions/`
- `POST /api/submissions/<id>/evaluate/`
- `GET /api/student/tasks/`

## 7.9 Reports

- `GET /api/reports/attendance/`
- `GET /api/reports/viva/`
- `GET /api/reports/submissions/`
- `GET /api/reports/submissions/student/<student_id>/pdf/`
- `GET /api/reports/submissions/batch/<batch_id>/pdf/`

## 7.10 Control

- `POST /api/control/command/`
- `GET /api/control/state/?batch=<id>`
- `POST /api/control/ack/`

## 8. WebSocket Design

### 8.1 WebSocket routes

- Faculty monitor: `/ws/monitor/<batch_id>/?token=<jwt>`
- Student channel: `/ws/student/?token=<jwt>`

### 8.2 Group strategy

- `monitor_batch_<batch_id>`: faculty-facing monitor events
- `batch_<batch_id>`: broadcast events for all students/faculty in a batch
- `student_<student_id>`: direct student-targeted events

### 8.3 Event categories

Implemented real-time events include:

- student online/offline status
- manual status updates and mode changes
- session started / paused / ended
- task evaluation publication
- online viva publication
- viva evaluation publication
- exam started / ended / evaluated
- control command delivery
- control acknowledgement
- WebRTC offer / answer / ICE exchange for live monitor

### 8.4 Authentication

Both consumers extract JWT access tokens from the query string and validate them with `AccessToken`.

## 9. Faculty Desktop Application (`lab/`)

### 9.1 Purpose

The faculty desktop is the operational UI for managing a selected semester/batch and performing all faculty workflows.

### 9.2 Main screens registered in `lab/main.py`

- Login
- Semester selection
- Attendance
- Batch dashboard
- Student list
- Student progress
- Evaluation
- Live monitor
- Single student
- Control panel
- Tasks
- Viva
- Exam
- Reports
- Settings

### 9.3 Client integration

`lab/api/client.py` wraps the backend REST API and stores:

- access token
- refresh token
- logged-in faculty profile

Key implemented faculty operations:

- login and token refresh
- fetch semesters, timetable, batches, students, attendance
- start and end sessions
- create tasks
- submit viva marks
- send control commands
- fetch reports
- download submission-report PDFs

### 9.4 Faculty WebSocket client

`lab/ui/common/websocket_client.py` connects to the batch monitor socket and emits Qt signals for:

- student status changes
- monitor answer / ICE events for screen viewing

## 10. Student Desktop Application (`student/`)

### 10.1 Purpose

The student desktop logs in a student from a lab PC, opens the student dashboard, maintains a live WebSocket connection, receives faculty commands, and handles submissions and exam/viva events.

### 10.2 Main modules

- `student/main.py`: app controller
- `student/login_modern_test.py`: login UI
- `student/student_dashboard.py`: dashboard UI
- `student/api_client.py`: REST functions
- `student/websocket_client.py`: event and WebRTC client
- `student/system_controller.py`: local machine control helpers
- `student/screen_track.py`: screen capture track for WebRTC

### 10.3 Implemented student operations

- login with `/api/student/login/`
- fetch tasks
- submit task file
- view published task results
- view viva results
- fetch active exams and assigned questions
- submit exam file
- fetch active online viva session
- acknowledge control commands

### 10.4 Live monitor implementation

The student client accepts WebRTC offers from faculty through WebSocket, creates an `RTCPeerConnection`, adds a screen-capture track, returns the SDP answer, and exchanges ICE candidates on the same socket channel.

## 11. ETLab Demo (`etlab_demo/`)

### 11.1 Purpose

`etlab_demo/` is a separate Django project that acts as an upstream academic source system.

### 11.2 Data exposed to backend sync

- student list
- faculty list
- timetable list

### 11.3 Access model

The ETLab APIs require the same service token used by the backend sync service.

### 11.4 Integration inside backend

`backend/apps/students/services/etlab_sync.py` fetches from:

- `http://127.0.0.1:8001/api/students/`
- `http://127.0.0.1:8001/api/faculty/`
- `http://127.0.0.1:8001/api/timetable/`

During sync:

- faculty are created or updated in `accounts.User`
- students are created or updated in `students.Student`
- semesters and batches are created if missing
- timetable slots are fully refreshed

## 12. Core Business Flows

### 12.1 Faculty login

1. Faculty logs in with `faculty_id` or email plus password.
2. Backend returns JWT access and refresh tokens.
3. Faculty desktop stores tokens and uses bearer auth on later requests.

### 12.2 Student login

1. Student logs in with `student_id` and password.
2. Backend authenticates against `accounts.User`.
3. Matching `students.Student` profile is returned.
4. Student desktop opens dashboard and can connect to student WebSocket.

### 12.3 Starting a lab session

1. Faculty creates `LabSession`.
2. Backend bulk-creates attendance rows for all batch students.
3. Signal broadcasts `session_started` over the batch WebSocket group.

### 12.4 Live attendance and status

1. Student WebSocket connects.
2. Backend marks student online and pushes `student_status` to faculty.
3. On disconnect, backend marks the student offline and broadcasts again.

### 12.5 Task lifecycle

1. Faculty creates a task for a batch.
2. Student fetches batch tasks through student endpoints.
3. Student uploads a file.
4. Faculty evaluates submission.
5. Backend sets `is_published=True` and notifies the student over WebSocket.

### 12.6 Viva lifecycle

1. Faculty creates offline or online viva session.
2. Offline viva auto-creates placeholder records for all students in the batch.
3. Online viva can be published live to batch WebSocket group.
4. Completed viva marks are published to students.

### 12.7 Exam lifecycle

1. Faculty creates exam session and question bank.
2. `exam-start/` assigns 1-2 questions per student.
3. Backend marks exam active and broadcasts event to students.
4. Students fetch assigned questions and submit files.
5. Faculty evaluates each `StudentExam`.
6. Backend publishes result to each student over WebSocket.

### 12.8 Control command flow

1. Faculty sends a batch-level command.
2. Backend stores `ControlCommand` and updates `ControlState`.
3. Command is pushed to `batch_<batch_id>`.
4. Student app executes locally and POSTs acknowledgement.
5. Backend forwards acknowledgement to faculty monitor group.

## 13. Setup and Run Guide

### 13.1 Backend

```powershell
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py create_faculty
python manage.py loaddata fixtures/initial_data.json
python manage.py runserver
```

For WebSocket-heavy validation, Daphne/ASGI is the safer runtime:

```powershell
cd backend
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### 13.2 Redis

Run Redis locally on `127.0.0.1:6379` before testing Channels features.

### 13.3 ETLab demo

```powershell
cd etlab_demo
python manage.py migrate
python manage.py runserver 8001
```

### 13.4 Faculty desktop

```powershell
cd lab
pip install -r requirements.txt
python main.py
```

### 13.5 Student desktop

```powershell
cd student
pip install -r requirements.txt
python main.py
```

## 14. Seed Data and Default Credentials

### 14.1 Faculty command-created users

From `backend/apps/accounts/management/commands/create_faculty.py`:

- `FAC001 / password123`
- `FAC002 / admin123`
- `FAC003 / faculty123`
- `admin / admin`
- `test / test`

### 14.2 ETLab faculty sync default password

When faculty are synced from ETLab, the backend sets:

- password = `<faculty_id in lowercase>@123`

### 14.3 ETLab student sync default password

When students are synced from ETLab, the backend sets:

- password = `<name_without_spaces>_<reg_number>` in lowercase

Example:

- `John Doe` + `CS2023001` -> `johndoe_cs2023001`

## 15. Reports

Implemented report outputs:

- aggregated attendance summary
- viva records report
- task submission report
- student-specific submission PDF
- batch-wide submission PDF

PDF generation is handled server-side with ReportLab and returned inline over HTTP.

## 16. Current Implementation Notes

- The backend is development-oriented: `DEBUG=True`, open CORS, SQLite, and a hardcoded service token.
- Redis is mandatory for WebSocket group messaging.
- Student login paths are duplicated in routing; the desktop client uses `/api/student/login/`.
- `accounts.User.faculty_id` is currently the shared credential field for both faculty and student-linked users.
- ETLab sync URLs are hardcoded to `127.0.0.1:8001`.
- Media uploads for task and exam submissions are stored under backend media paths.
- The root `requirements.txt` mixes backend and desktop dependencies; component-specific requirements also exist in `backend/`, `lab/`, and `student/`.

## 17. Recommended Production Hardening

- move secrets and tokens to environment variables
- replace SQLite with PostgreSQL
- restrict CORS and `ALLOWED_HOSTS`
- run Redis as a managed service
- separate faculty and student authentication concepts more explicitly
- add endpoint versioning
- centralize configuration for backend and both desktop clients
- add automated tests for session, control, viva, exam, and sync flows

## 18. Summary

The current Smart Lab Management System is a working multi-client academic lab platform with:

- Django REST + Channels backend
- faculty PyQt6 desktop
- student PyQt6 desktop
- ETLab demo sync source
- live WebSocket events
- WebRTC-based screen monitoring
- attendance, tasks, viva, exams, reports, and control-command support

This document reflects the code currently present in the repository on 2026-03-15.
