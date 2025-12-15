import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QToolBar,
    QLabel,
    QLineEdit,
    QSizePolicy,
)
from PyQt6.QtCore import Qt

from ui.theme import app_stylesheet
from ui.screens import (
    LoginScreen,
    SemesterSelectionScreen,
    BatchDashboardScreen,
    StudentListScreen,
    StudentProgressScreen,
    EvaluationScreen,
    LiveMonitorScreen,
    SingleStudentScreen,
    ControlPanelScreen,
    TasksScreen,
    VivaScreen,
    ExamScreen,
    ReportsScreen,
    SettingsScreen,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Lab Management & Evaluation System – Faculty")
        self.resize(1200, 800)

        self.toolbar = self._build_toolbar()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet(
            """
            QListWidget {
                background: #eef2ff;
                border-right: 1px solid #e5e7eb;
            }
            QListWidget::item {
                padding: 12px 10px;
            }
            QListWidget::item:selected {
                background: #c7d2fe;
                border-left: 4px solid #3f51b5;
            }
            """
        )

        self.stack = QStackedWidget()

        layout.addWidget(self.sidebar)
        layout.addWidget(self.stack, stretch=1)
        self.setCentralWidget(container)

        self._init_screens()
        self.sidebar.currentRowChanged.connect(self._on_nav_change)

    def _build_toolbar(self) -> QToolBar:
        tb = QToolBar("Top Bar")
        tb.setMovable(False)
        search = QLineEdit()
        search.setPlaceholderText("Search...")
        search.setMaximumWidth(240)
        tb.addWidget(search)
        tb.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)
        profile = QLabel("Shireen \u2022 Faculty")
        tb.addWidget(profile)
        return tb

    def _init_screens(self):
        self.login_screen = LoginScreen()
        self.login_screen.login_success.connect(self._on_login)

        self.sem_screen = SemesterSelectionScreen()
        self.sem_screen.batch_selected.connect(self._on_batch_selected)

        self.dashboard_screen = BatchDashboardScreen()
        self.student_list_screen = StudentListScreen()
        self.student_progress_screen = StudentProgressScreen()
        self.evaluation_screen = EvaluationScreen()
        self.live_monitor_screen = LiveMonitorScreen()
        self.single_student_screen = SingleStudentScreen()
        self.control_panel_screen = ControlPanelScreen()
        self.tasks_screen = TasksScreen()
        self.viva_screen = VivaScreen()
        self.exam_screen = ExamScreen()
        self.reports_screen = ReportsScreen()
        self.settings_screen = SettingsScreen()

        self.screens = [
            ("Login", self.login_screen),
            ("Semester Select", self.sem_screen),
            ("Dashboard", self.dashboard_screen),
            ("Student List", self.student_list_screen),
            ("Student Progress", self.student_progress_screen),
            ("Evaluation", self.evaluation_screen),
            ("Live Monitor", self.live_monitor_screen),
            ("Single Student", self.single_student_screen),
            ("Control Panel", self.control_panel_screen),
            ("Tasks", self.tasks_screen),
            ("Viva", self.viva_screen),
            ("Exam", self.exam_screen),
            ("Reports", self.reports_screen),
            ("Settings", self.settings_screen),
        ]

        for name, widget in self.screens:
            self.stack.addWidget(widget)
            item = QListWidgetItem(name)
            self.sidebar.addItem(item)

        self.sidebar.setCurrentRow(0)
        self.stack.setCurrentWidget(self.login_screen)

    def _on_login(self, faculty_id: str):
        self.stack.setCurrentWidget(self.sem_screen)
        self.sidebar.setCurrentRow(1)
        self.statusBar().showMessage(f"Logged in as {faculty_id}", 3000)

    def _on_batch_selected(self, semester: str, batch: str):
        self.stack.setCurrentWidget(self.dashboard_screen)
        self.sidebar.setCurrentRow(2)
        self.statusBar().showMessage(f"Selected {semester} - {batch}", 3000)

    def _on_nav_change(self, index: int):
        if index < 0 or index >= len(self.screens):
            return
        widget = self.screens[index][1]
        self.stack.setCurrentWidget(widget)
        self.statusBar().showMessage(f"Navigated to {self.screens[index][0]}", 1500)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(app_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

