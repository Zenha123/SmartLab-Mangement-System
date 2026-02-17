from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame,
    QGridLayout, QStackedWidget, QTextEdit
)
from PyQt6.QtCore import Qt
import sys


from websocket_client import WebSocketClient
import api_client

class StudentDashboard(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.tasks = []
        self.init_ui()
        
        # Load initial data
        self.load_tasks()
        
        # Start WebSocket Client
        self.ws_client = WebSocketClient()
        self.ws_client.message_signal.connect(self.handle_websocket_message)
        self.ws_client.start()

    def handle_websocket_message(self, data):
        """Handle all WebSocket messages"""
        event_type = data.get('type')
        
        if event_type == 'session_status':
            self.update_session_ui(data)
        elif event_type == 'task_event':
            self.handle_task_event(data)

    def update_session_ui(self, data):
        """Handle session status updates"""
        status = data.get('status')
        if status == 'session_started':
            self.session_status_label.setText(f"🔴 LIVE SESSION: {data.get('session_type', 'Lab').upper()}")
            self.session_status_label.setStyleSheet("background-color: #22c55e; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
            self.session_status_label.show()
        elif status == 'session_ended':
            self.session_status_label.hide()

    def handle_task_event(self, data):
        """Handle task creation events"""
        if data.get('event_type') == 'task_created':
            task = data.get('task')
            self.add_task_to_ui(task)
            self.update_task_count()
            
            # Show notification (simulated with status label for now or alert)
            # We can use the notif btn or a temporary label
            self.session_status_label.setText(f"🔔 NEW TASK ASSIGNED: {task.get('title')}")
            self.session_status_label.setStyleSheet("background-color: #3b82f6; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
            self.session_status_label.show()
            # In a real app, use QTimer to hide it after few seconds

    def load_tasks(self):
        """Fetch tasks from API"""
        result = api_client.get_student_tasks()
        if result['success']:
            tasks_data = result['tasks']
            # Handle both list and dict responses (paginated)
            if isinstance(tasks_data, dict):
                self.tasks = tasks_data.get('results', [])
            elif isinstance(tasks_data, list):
                self.tasks = tasks_data
            else:
                self.tasks = []
            self.refresh_tasks_grid()
            self.update_task_count()
        else:
            print(f"Error loading tasks: {result.get('error')}")

    def update_task_count(self):
        """Update the total tasks card"""
        # Find the card linked to Total Tasks and update it
        # Since cards are created in init_ui, we need a reference.
        # Quick hack: recreate dashboard page or find child.
        # Better: Store reference in create_dashboard_page
        if hasattr(self, 'total_tasks_label'):
            self.total_tasks_label.setText(str(len(self.tasks)))

    def refresh_tasks_grid(self):
        """Clear and rebuild tasks grid"""
        if not hasattr(self, 'tasks_grid'):
            return
            
        # Clear existing items
        while self.tasks_grid.count():
            child = self.tasks_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add tasks
        for index, task in enumerate(self.tasks):
            row = index // 2
            col = index % 2
            card = self.create_experiment_card(task)
            self.tasks_grid.addWidget(card, row, col)

    def add_task_to_ui(self, task):
        """Add a single task to UI without full reload"""
        self.tasks.insert(0, task) # Add to top
        self.refresh_tasks_grid() # Rebuild grid to maintain order order


    def init_ui(self):
        self.setWindowTitle("Student Dashboard")
        self.showMaximized()

        # ================= GLOBAL STYLE =================
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f8;
                font-family: Segoe UI;
            }
            QFrame#sidebar {
                background-color: #111827;
            }

            QPushButton#menuBtn {
                background-color: transparent;
                color: white;
                height: 45px;
                text-align: left;
                padding-left: 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton#menuBtn:hover {
                background-color: #1f2937;
            }
            QPushButton#activeBtn {
                background-color: #2563eb;
                color: white;
                height: 45px;
                text-align: left;
                padding-left: 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }
            QFrame#card {
                background-color: white;
                border-radius: 12px;
            }
QFrame#topbar {
    background-color: white;
    border-bottom: 1px solid #e5e7eb;
}

QLabel#userLabel {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
}

QFrame {
    background: transparent;
}



    """)

        # ================= SIDEBAR =================
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)


        btn_dashboard = QPushButton("📊 Dashboard")
        btn_tasks = QPushButton("📄 View Tasks")
        btn_exams = QPushButton("📝 Exams")
        btn_results = QPushButton("📈 Results")
        btn_logout = QPushButton("🚪 Logout")

        self.menu_buttons = [
            btn_dashboard, btn_tasks, btn_exams, btn_results
        ]

        for btn in self.menu_buttons:
            btn.setObjectName("menuBtn")

        btn_logout.setObjectName("menuBtn")
        btn_logout.clicked.connect(self.close)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 40, 20, 20)
        sidebar_layout.setSpacing(15)


        for btn in self.menu_buttons:
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        sidebar_layout.addWidget(btn_logout)

        # ================= STACK =================
        self.stack = QStackedWidget()

        self.dashboard_page = self.create_dashboard_page()
        self.tasks_page = self.create_tasks_page()
        self.exams_page = self.create_exams_page()
        self.results_page = self.create_results_page()


        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.tasks_page)
        self.stack.addWidget(self.exams_page)
        self.stack.addWidget(self.results_page)

        # Button Connections
        btn_dashboard.clicked.connect(lambda: self.switch_page(0, btn_dashboard))
        btn_tasks.clicked.connect(lambda: self.switch_page(1, btn_tasks))
        btn_exams.clicked.connect(lambda: self.switch_page(2, btn_exams))
        btn_results.clicked.connect(lambda: self.switch_page(3, btn_results))

        # ================= MAIN LAYOUT =================
        # ================= TOP BAR =================
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(70)

        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(30, 0, 30, 0)
        topbar_layout.setSpacing(20)

        topbar_layout.addStretch()

        # Session Status Label
        self.session_status_label = QLabel("No Active Session")
        self.session_status_label.hide()
        topbar_layout.addWidget(self.session_status_label)

        # 🔔 Notification Icon
        notif_btn = QLabel("🔔")
        notif_btn.setStyleSheet("font-size:18px;")
        notif_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        topbar_layout.addWidget(notif_btn)

        # Profile Container (Icon + Name Together)
        profile_container = QFrame()
        profile_layout = QHBoxLayout(profile_container)
        profile_layout.setContentsMargins(10, 5, 10, 5)
        profile_layout.setSpacing(8)

        # 👤 Circle Avatar
        avatar = QLabel("👤")
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background-color: #e5e7eb;
            border-radius: 18px;
            font-size:16px;
        """)

        # Username
        self.user_label = QLabel(self.username)
        self.user_label.setObjectName("userLabel")

        profile_layout.addWidget(avatar)
        profile_layout.addWidget(self.user_label)

        topbar_layout.addWidget(profile_container)


        # ================= CONTENT AREA =================
        content_layout = QVBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(topbar)
        content_layout.addWidget(self.stack)
        content_widget = QWidget()
        content_widget.setLayout(content_layout)



        # ================= MAIN LAYOUT =================
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_widget)

        self.switch_page(0, btn_dashboard)


    # ================= DASHBOARD =================
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        header = QLabel(f"Welcome back, {self.username} 👋")
        header.setStyleSheet("font-size:24px; font-weight:bold;")

        grid = QGridLayout()
        grid.setSpacing(20)

        total_tasks = 8
        upcoming_exams = 2
        submitted = 5
        overdue = 1

        t_card = self.create_card("Total Tasks", str(total_tasks))
        # Find the value label to update it later
        # We need to ensure create_card sets object name or we find by type order
        # Let's Modify create_card below to set objectName for valueLabel
        # Assuming create_card is modified:
        self.total_tasks_label = t_card.findChild(QLabel, "valueLabel")
        grid.addWidget(t_card, 0, 0)
        grid.addWidget(self.create_card("Upcoming Exams", str(upcoming_exams)), 0, 1)
        grid.addWidget(self.create_card("Submitted", str(submitted), "#16a34a"), 1, 0)

        # Overdue red
        overdue_color = "#dc2626" if overdue > 0 else "#16a34a"
        grid.addWidget(self.create_card("Overdue", str(overdue), overdue_color), 1, 1)

        layout.addWidget(header)
        layout.addLayout(grid)
        layout.addStretch()

        return page


    def create_card(self, title, value, color="#111827"):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(130)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size:14px; color:#6b7280;")

        value_label = QLabel(value)
        value_label.setObjectName("valueLabel")
        value_label.setStyleSheet(
            f"font-size:26px; font-weight:bold; color:{color};"
        )

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(value_label)

        return card


    # ================= VIEW TASKS PAGE =================
    def create_tasks_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        title = QLabel("My Experiments")
        title.setStyleSheet("font-size:26px; font-weight:bold;")
        layout.addWidget(title)

        self.tasks_grid = QGridLayout()
        self.tasks_grid.setSpacing(20)

        # Tasks are populated by load_tasks() via refresh_tasks_grid()

        layout.addLayout(self.tasks_grid)
        layout.addStretch()

        return page

    def create_experiment_card(self, task):
        # task is a dict or a string (for compatibility if needed, but we switched to dicts)
        if isinstance(task, str):
            name = task
            deadline_text = "Pending"
            status_text = "Pending"
            faculty_txt = "Faculty: Unknown"
        else:
            name = task.get('title', 'Unknown Task')
            deadline_text = f"Deadline: {task.get('deadline', 'No Deadline').split('T')[0]}" if task.get('deadline') else "No Deadline"
            status_text = f"Status: {task.get('status', 'Active').title()}"
            faculty_txt = f"Faculty: {task.get('faculty_name', 'Faculty')}"

        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(200)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"🧪 {name}")
        title.setStyleSheet("font-size:16px; font-weight:bold;")

        subject = QLabel(faculty_txt)
        deadline = QLabel(deadline_text)
        status = QLabel(status_text)

        view_btn = QPushButton("View Task")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1e40af;
            }
        """)

        # Store task details to open submission page
        # Passing 'name' for now, but should ideally pass full task ID
        view_btn.clicked.connect(lambda: self.open_submission_page(name))

        layout.addWidget(title)
        layout.addWidget(subject)
        layout.addWidget(deadline)
        layout.addWidget(status)
        layout.addStretch()
        layout.addWidget(view_btn)

        return card

    # ================= SUBMISSION PAGE =================
    def open_submission_page(self, experiment_name):
        submission_page = QWidget()
        layout = QVBoxLayout(submission_page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Experiment Submission")
        title.setStyleSheet("font-size:26px; font-weight:bold;")

        subtitle = QLabel(f"{experiment_name} - Write your code below and submit.")
        subtitle.setStyleSheet("color:gray;")

        code_editor = QTextEdit()
        code_editor.setPlaceholderText("Write your code here...")
        code_editor.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border-radius: 12px;
                padding: 15px;
                font-family: Consolas;
                font-size: 14px;
            }
        """)

        submit_btn = QPushButton("Submit Code")
        submit_btn.setFixedHeight(45)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #6366f1;
                color: white;
                border-radius: 10px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4f46e5;
            }
        """)

        back_btn = QPushButton("← Back to Experiments")
        back_btn.clicked.connect(lambda: self.switch_page(1, self.menu_buttons[1]))

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(code_editor)
        layout.addWidget(submit_btn)
        layout.addWidget(back_btn)

        self.stack.addWidget(submission_page)
        self.stack.setCurrentWidget(submission_page)

    def create_exams_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        title = QLabel("Exams")
        title.setStyleSheet("font-size:26px; font-weight:bold;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(20)

        # Viva Card
        grid.addWidget(self.create_exam_card(
            "🎤 Viva Exam",
            "Subject: Operating Systems",
            "Date: 25 Feb 2026",
            "Status: Scheduled"
        ), 0, 0)

        # Practical Card
        grid.addWidget(self.create_exam_card(
            "🧪 Practical Exam",
            "Subject: Python Lab",
            "Date: 28 Feb 2026",
            "Status: Upcoming"
        ), 0, 1)

        layout.addLayout(grid)
        layout.addStretch()

        return page
    
    def create_exam_card(self, title_text, subject, date, status_text):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(220)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setStyleSheet("font-size:16px; font-weight:bold;")

        subject_label = QLabel(subject)
        date_label = QLabel(date)

        status_label = QLabel(status_text)
        status_label.setStyleSheet("color:#eab308; font-weight:600;")

        # ✅ Start Button (hidden initially)
        start_btn = QPushButton("Start Exam")
        start_btn.setFixedHeight(40)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1e40af;
            }
        """)
        start_btn.hide()  # 👈 Hidden initially

        # 🔥 Show button when card is clicked
        def show_start():
            start_btn.show()

        card.mousePressEvent = lambda event: show_start()

        layout.addWidget(title)
        layout.addWidget(subject_label)
        layout.addWidget(date_label)
        layout.addWidget(status_label)
        layout.addStretch()
        layout.addWidget(start_btn)

        return card





    def create_results_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        title = QLabel("Results")
        title.setStyleSheet("font-size:26px; font-weight:bold;")
        layout.addWidget(title)

        subjects = {
            "Operating Systems": 85,
            "DBMS": 90,
            "Computer Networks": 78,
            "Python Lab": 95
        }

        grid = QGridLayout()
        grid.setSpacing(20)

        total_marks = 0
        total_subjects = len(subjects)

        row = 0
        col = 0

        for subject, mark in subjects.items():
            total_marks += mark

            # Color Logic
            if mark >= 85:
                color = "#16a34a"   # Green
            elif mark >= 60:
                color = "#eab308"   # Yellow
            else:
                color = "#dc2626"   # Red

            card = self.create_card(subject, f"{mark} / 100", color)
            grid.addWidget(card, row, col)

            col += 1
            if col > 1:
                col = 0
                row += 1

        # Calculate Percentage
        percentage = total_marks / total_subjects

        # GPA Calculation (simple 10 scale)
        gpa = round((percentage / 100) * 10, 2)

        layout.addLayout(grid)

        summary = QLabel(f"Overall Percentage: {percentage:.2f}%     |     GPA: {gpa}")
        summary.setStyleSheet("font-size:18px; font-weight:bold; color:#2563eb;")

        layout.addWidget(summary)
        layout.addStretch()

        return page



    # ================= SIMPLE PAGE =================
    def create_simple_page(self, text):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        label = QLabel(text)
        label.setStyleSheet("font-size:24px; font-weight:bold;")

        layout.addWidget(label)
        layout.addStretch()
        return page

    # ================= SWITCH PAGE =================
    def switch_page(self, index, button):
        self.stack.setCurrentIndex(index)

        for btn in self.menu_buttons:
            btn.setObjectName("menuBtn")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        button.setObjectName("activeBtn")
        button.style().unpolish(button)
        button.style().polish(button)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentDashboard("Jiya")
    window.show()
    sys.exit(app.exec())
