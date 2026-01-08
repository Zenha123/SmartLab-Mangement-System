import sys
from PyQt5.QtWidgets import QApplication
from login_modern_test import LoginPage
from student_dashboard import StudentDashboard



class AppController:
    def __init__(self):
        self.login = LoginPage(self.open_dashboard)
        self.login.show()

    def open_dashboard(self, student_name):
        self.dashboard = StudentDashboard(student_name)
        self.dashboard.logout_requested.connect(self.show_login)
        self.dashboard.show()

    def handle_logout(self):
        self.dashboard=None
        self.show_login()

    def show_login(self):
        self.login = LoginPage(self.open_dashboard)
        self.login.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = AppController()
    sys.exit(app.exec_())
