import sys
from PyQt5.QtWidgets import QApplication
from login_modern_test import LoginPage
from student_dashboard import StudentDashboard


class AppController:
    def __init__(self):
        self.login = LoginPage(self.open_dashboard)
        self.login.show()

    def open_dashboard(self, username):
        self.dashboard = StudentDashboard(username)
        self.dashboard.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = AppController()
    sys.exit(app.exec_()) 