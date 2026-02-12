from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame,
    QGridLayout, QStackedWidget, QTextEdit
)
from PyQt6.QtCore import Qt
import sys


class StudentDashboard(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.init_ui()

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
        self.exams_page = self.create_simple_page("Exams")
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
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

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

        grid.addWidget(self.create_card("Total Tasks", str(total_tasks)), 0, 0)
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

        grid = QGridLayout()
        grid.setSpacing(20)

        grid.addWidget(self.create_experiment_card("Experiment 1"), 0, 0)
        grid.addWidget(self.create_experiment_card("Experiment 2"), 0, 1)
        grid.addWidget(self.create_experiment_card("Experiment 3"), 1, 0)
        grid.addWidget(self.create_experiment_card("Experiment 4"), 1, 1)

        layout.addLayout(grid)
        layout.addStretch()

        return page

    def create_experiment_card(self, name):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedHeight(150)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"🧪 {name}")
        title.setStyleSheet("font-size:16px; font-weight:bold;")

        subject = QLabel("Subject: OS Lab")
        deadline = QLabel("Deadline: 20 Feb 2026")
        status = QLabel("Status: Pending")

        view_btn = QPushButton("View Task")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #1e40af;
            }
        """)

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
