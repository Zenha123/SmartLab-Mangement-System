import sys
from PyQt6.QtWidgets import QApplication
from login_modern_test import LoginPage
from student_dashboard import StudentDashboard
import asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class AppController:
    def __init__(self):
        self.login = LoginPage(self.open_dashboard)
        self.login.show()

    def open_dashboard(self, username):
        self.dashboard = StudentDashboard(username)
        self.dashboard.show()
        self.login.close()   # move close here


if __name__ == "__main__":
    app = QApplication(sys.argv)

    controller = AppController()   # keep reference

    sys.exit(app.exec())
