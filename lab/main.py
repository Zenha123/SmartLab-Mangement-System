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
    QPushButton,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QColor

from ui.theme import app_stylesheet, Theme
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
        # Set reasonable window size that fits most screens
        self.resize(1400, 900)
        # Set minimum size to prevent layout issues
        self.setMinimumSize(1000, 700)
        
        # Track login state
        self.is_logged_in = False
        self.current_faculty_id = ""

        self.toolbar = self._build_toolbar()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # Container for main app (with sidebar)
        self.main_container = QWidget()
        self.main_layout = QHBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet(
            f"""
            QListWidget {{
                background: {Theme.card_bg};
                border-right: 1px solid {Theme.border};
                padding: 8px 0px;
            }}
            QListWidget::item {{
                padding: 14px 20px;
                margin: 2px 8px;
                border-radius: 8px;
                color: {Theme.text_secondary};
                font-weight: 500;
                font-size: 14px;
            }}
            QListWidget::item:hover {{
                background: {Theme.primary}08;
                color: {Theme.text_primary};
            }}
            QListWidget::item:selected {{
                background: {Theme.primary};
                color: white;
                font-weight: 600;
            }}
            """
        )

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {Theme.background};")

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stack, stretch=1)
        
        # Always use main_container as central widget
        self.setCentralWidget(self.main_container)

        self._init_screens()
        self.sidebar.currentRowChanged.connect(self._on_nav_change)
        
        # Show login screen initially
        self._show_login()

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
        self.profile_label = QLabel("Guest \u2022 Faculty")
        tb.addWidget(self.profile_label)
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

        # Add login screen to stack (but not to navigation)
        self.stack.addWidget(self.login_screen)

        # Navigation items with icons (excluding login - it's shown separately)
        self.screens = [
            ("📚 Semester Select", self.sem_screen),
            ("📊 Dashboard", self.dashboard_screen),
            ("👥 Student List", self.student_list_screen),
            ("📈 Student Progress", self.student_progress_screen),
            ("✅ Evaluation", self.evaluation_screen),
            ("🖥️ Live Monitor", self.live_monitor_screen),
            ("👤 Single Student", self.single_student_screen),
            ("🎛️ Control Panel", self.control_panel_screen),
            ("📝 Tasks", self.tasks_screen),
            ("🎤 Viva", self.viva_screen),
            ("📋 Exam", self.exam_screen),
            ("📄 Reports", self.reports_screen),
            ("⚙️ Settings", self.settings_screen),
        ]

        for name, widget in self.screens:
            self.stack.addWidget(widget)
        
        # Add logout button as a special item (we'll handle it separately)
        self.logout_item_index = len(self.screens)

    def _show_login(self):
        """Show login screen and hide navigation elements"""
        self.is_logged_in = False
        # Hide sidebar and toolbar
        self.sidebar.hide()
        self.toolbar.hide()
        # Show login screen in stack
        self.stack.setCurrentWidget(self.login_screen)
    
    def _show_main_app(self):
        """Show main application with navigation"""
        self.is_logged_in = True
        # Show sidebar and toolbar
        self.sidebar.show()
        self.toolbar.show()
        # Build navigation menu
        self._build_navigation()
        # Show semester selection screen
        self.stack.setCurrentWidget(self.sem_screen)
        self.sidebar.setCurrentRow(0)
    
    def _build_navigation(self):
        """Build navigation sidebar with logout button"""
        self.sidebar.clear()
        
        # Add regular navigation items
        for name, widget in self.screens:
            item = QListWidgetItem(name)
            item.setFont(QFont("Segoe UI", 13))
            self.sidebar.addItem(item)
        
        # Add separator (spacer item)
        separator = QListWidgetItem()
        separator.setFlags(Qt.ItemFlag.NoItemFlags)
        separator.setSizeHint(QSize(0, 20))
        self.sidebar.addItem(separator)
        
        # Add logout button
        logout_item = QListWidgetItem("🚪 Logout")
        logout_item.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        logout_item.setForeground(QColor(Theme.danger))
        self.sidebar.addItem(logout_item)
        self.logout_item_index = self.sidebar.count() - 1

    def _on_login(self, faculty_id: str):
        self.current_faculty_id = faculty_id
        self._show_main_app()
        self.statusBar().showMessage(f"Logged in as {faculty_id}", 3000)
        
        # Update profile label in toolbar
        if hasattr(self, 'profile_label'):
            self.profile_label.setText(f"{faculty_id} \u2022 Faculty")
    
    def _on_logout(self):
        """Handle logout"""
        self.current_faculty_id = ""
        if hasattr(self, 'profile_label'):
            self.profile_label.setText("Guest \u2022 Faculty")
        self._show_login()
        self.statusBar().showMessage("Logged out successfully", 3000)

    def _on_batch_selected(self, semester: str, batch: str):
        self.stack.setCurrentWidget(self.dashboard_screen)
        # Dashboard is at index 1 in screens list (after Semester Select at 0)
        self.sidebar.setCurrentRow(1)
        self.statusBar().showMessage(f"Selected {semester} - {batch}", 3000)

    def _on_nav_change(self, index: int):
        if index < 0:
            return
        
        # Check if logout was clicked
        if index == self.logout_item_index:
            self._on_logout()
            return
        
        # Check if valid navigation index
        if index >= len(self.screens):
            return
        
        widget = self.screens[index][1]
        
        self.stack.setCurrentWidget(widget)
        self.statusBar().showMessage(f"Navigated to {self.screens[index][0].split(' ', 1)[1] if ' ' in self.screens[index][0] else self.screens[index][0]}", 2000)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(app_stylesheet())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

