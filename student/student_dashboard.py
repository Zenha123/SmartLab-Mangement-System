from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFrame, QStackedWidget
)
from PyQt5.QtCore import Qt


class StudentDashboard(QWidget): 
    def __init__(self, student_name="Student"): 
        super().__init__() 
        self.student_name = student_name 
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle("Student Dashboard")
        self.showFullScreen()

        # ---------------- STYLE ----------------
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f8;
                font-family: Segoe UI;
            }
            QFrame#sidebar {
                background-color: #000000;
            }
            QLabel {
                color: white;
            }
            QPushButton#menu {
                height: 42px;
                border-radius: 6px;
                font-size: 14px;
                text-align: left;
                padding-left: 15px;
                color: white;
                background-color: transparent;
            }
            QPushButton#menu:hover {
                background-color: #40444b;
            }
            QPushButton#logout {
                background-color: #c0392b;
                color: white;
                height: 42px;
                border-radius: 6px;
            }
            QPushButton#logout:hover {
                background-color: #a93226;
            }
        """)

        # ---------------- SIDEBAR ----------------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)

        welcome = QLabel(f"Welcome,\n{self.student_name}")
        welcome.setStyleSheet("font-size:18px; font-weight:600;")

        btn_dashboard = QPushButton("🏠  Dashboard")
        btn_tasks = QPushButton("📄  View Tasks")
        btn_exams = QPushButton("📝  Exams")
        btn_results = QPushButton("📊  Results")
        btn_logout = QPushButton("Logout")
        self.menu_buttons = [btn_dashboard, btn_tasks, btn_exams, btn_results]


        for btn in [btn_dashboard, btn_tasks, btn_exams, btn_results]:
            btn.setObjectName("menu")

        btn_logout.setObjectName("logout")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 40, 20, 20)
        sidebar_layout.setSpacing(15)
        sidebar_layout.addWidget(welcome)
        sidebar_layout.addSpacing(30)
        sidebar_layout.addWidget(btn_dashboard)
        sidebar_layout.addWidget(btn_tasks)
        sidebar_layout.addWidget(btn_exams)
        sidebar_layout.addWidget(btn_results)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(btn_logout)

        # ---------------- MAIN CONTENT (STACK) ----------------
        self.stack = QStackedWidget()

        self.page_dashboard = self.create_page("Dashboard", "Assigned Tasks | Submitted Tasks | Available Exams")
        self.page_tasks = self.create_page("View Tasks", "List of assigned tasks will appear here")
        self.page_exams = self.create_page("Exams", "Upcoming and ongoing exams")
        self.page_results = self.create_page("Results", "Exam results will be displayed here")

        self.stack.addWidget(self.page_dashboard)  # index 0
        self.stack.addWidget(self.page_tasks)      # index 1
        self.stack.addWidget(self.page_exams)      # index 2
        self.stack.addWidget(self.page_results)    # index 3

        # ---------------- BUTTON CONNECTIONS ----------------
        btn_dashboard.clicked.connect(
            lambda: (self.stack.setCurrentIndex(0), self.set_active(btn_dashboard))
        )
        btn_tasks.clicked.connect(
            lambda: (self.stack.setCurrentIndex(1), self.set_active(btn_tasks))
        )
        btn_exams.clicked.connect(
            lambda: (self.stack.setCurrentIndex(2), self.set_active(btn_exams))
        )
        btn_results.clicked.connect(
            lambda: (self.stack.setCurrentIndex(3), self.set_active(btn_results))
        )
        


        # ---------------- ROOT LAYOUT ----------------
        root = QHBoxLayout(self)
        root.setSpacing(0)
        root.addWidget(sidebar)
        root.addWidget(self.stack)
        self.set_active(btn_dashboard)

    def set_active(self, button):
        for btn in self.menu_buttons:
            btn.setStyleSheet("")
        button.setStyleSheet("background-color:#5865f2;")

    # ---------------- PAGE TEMPLATE ----------------
    def create_page(self, title_text, body_text):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel(title_text)
        title.setStyleSheet("font-size:26px; font-weight:700; color:#2c3e50;")

        body = QLabel(body_text)
        body.setStyleSheet("font-size:16px; color:#555;")
        body.setAlignment(Qt.AlignTop)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(body)
        layout.addStretch()

        return page
