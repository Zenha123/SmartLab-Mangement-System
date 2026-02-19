from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame,
    QGridLayout, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
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
        elif event_type == 'submission_event':
            self.handle_submission_event(data)

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

    def handle_submission_event(self, data):
        """Handle submission evaluation events"""
        if data.get('event_type') == 'evaluation_done':
            submission = data.get('submission', {})
            task_title = submission.get('task_title', 'Task')
            marks = submission.get('marks', 'N/A')
            
            # Show notification
            self.session_status_label.setText(f"✅ EVALUATED: {task_title} - Marks: {marks}")
            self.session_status_label.setStyleSheet("background-color: #22c55e; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
            self.session_status_label.show()
            
            # Optionally refresh tasks to show updated status
            # self.load_tasks()

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
        # Pass the full task object
        view_btn.clicked.connect(lambda: self.open_submission_page(task))

        layout.addWidget(title)
        layout.addWidget(subject)
        layout.addWidget(deadline)
        layout.addWidget(status)
        layout.addStretch()
        layout.addWidget(view_btn)

        return card

    # ================= SUBMISSION PAGE =================
    def open_submission_page(self, task):
        """Open submission page for a task with file upload"""
        if isinstance(task, str):
            task_name = task
            task_id = None
        else:
            task_name = task.get('title', 'Unknown Task')
            task_id = task.get('id')
        
        submission_page = QWidget()
        layout = QVBoxLayout(submission_page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Experiment Submission")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #1f2937;")

        subtitle = QLabel(f"Task: {task_name}")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #6b7280; margin-bottom: 20px;")
        
        # --- File Upload Section ---
        upload_container = QWidget()
        upload_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px dashed #e5e7eb;
                border-radius: 12px;
            }
        """)
        upload_layout = QVBoxLayout(upload_container)
        upload_layout.setContentsMargins(40, 40, 40, 40)
        upload_layout.setSpacing(15)
        upload_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon
        icon_lbl = QLabel("📁")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 48px; border: none; background: transparent;")
        
        # Instruction
        instruct_lbl = QLabel("Upload your solution file")
        instruct_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruct_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #374151; border: none; background: transparent;")
        
        # Allowed formats
        formats_lbl = QLabel("Accepted formats: .py, .txt, .java, .c, .cpp, .pdf")
        formats_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        formats_lbl.setStyleSheet("color: #9ca3af; border: none; background: transparent;")
        
        # File Display Label (Hidden initially)
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_path_label.setStyleSheet("color: #6b7280; font-weight: bold; margin-top: 10px; border: none; background: transparent;")
        self.selected_file_path = None
        
        # Choose File Button
        choose_btn = QPushButton("Choose File")
        choose_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        choose_btn.setFixedSize(150, 40)
        choose_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2563eb;
                border: 2px solid #2563eb;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #eff6ff;
            }
        """)
        choose_btn.clicked.connect(self.choose_file)
        
        upload_layout.addWidget(icon_lbl)
        upload_layout.addWidget(instruct_lbl)
        upload_layout.addWidget(formats_lbl)
        upload_layout.addWidget(self.file_path_label)
        upload_layout.addWidget(choose_btn)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(upload_container)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        back_btn = QPushButton("Back")
        back_btn.setFixedSize(120, 45)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #6b7280;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #f3f4f6;
                color: #374151;
            }
        """)
        back_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.dashboard_page))

        self.submit_btn = QPushButton("Submit Submission")
        self.submit_btn.setFixedSize(180, 45)
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                cursor: not-allowed;
            }
        """)
        self.submit_btn.clicked.connect(lambda: self.submit_code(task_id))

        btn_layout.addWidget(back_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.submit_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        self.stack.addWidget(submission_page)
        self.stack.setCurrentWidget(submission_page)
    
    def choose_file(self):
        """Open file dialog to select submission file"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Submission File", 
            "", 
            "Code Files (*.py *.txt *.java *.c *.cpp *.pdf);;All Files (*)"
        )
        
        if file_path:
            self.selected_file_path = file_path
            filename = file_path.split('/')[-1]
            self.file_path_label.setText(f"Selected: {filename}")
            self.file_path_label.setStyleSheet("color: #059669; font-weight: bold; margin-top: 10px; border: none; background: transparent;")

    def submit_code(self, task_id):
        """Submit the selected file"""
        from PyQt6.QtWidgets import QMessageBox
        
        if not task_id:
            QMessageBox.warning(self, "Error", "Invalid task ID")
            return
            
        if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
            QMessageBox.warning(self, "Validation Error", "Please select a file to upload first.")
            return

        self.submit_btn.setText("Submitting...")
        self.submit_btn.setEnabled(False)
        
        # Call API
        try:
            result = api_client.submit_task(task_id, self.selected_file_path)
            
            if result.get("success"):
                QMessageBox.information(self, "Success", "File submitted successfully! 🚀")
                # Go back to tasks page
                self.switch_page(1, self.menu_buttons[1])
            else:
                QMessageBox.critical(self, "Error", f"Failed: {result.get('error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
        finally:
            if hasattr(self, 'submit_btn'):
                self.submit_btn.setText("Submit Submission")
                self.submit_btn.setEnabled(True)

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
