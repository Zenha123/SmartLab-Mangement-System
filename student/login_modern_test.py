from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt


class LoginPage(QWidget):
    def __init__(self, on_login_success=None):
        super().__init__()
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        self.showMaximized()

        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f8;
                font-family: Segoe UI;
            }
            QLabel {
                font-size: 28px;
                font-weight: 700;
                color: #222;
            }
            QLineEdit {
                height: 42px;
                border-radius: 8px;
                padding-left: 12px;
                font-size: 15px;
                border: 1px solid #ccc;
            }
            QPushButton {
                height: 44px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                background-color: #6a5acd;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a4acb;
            }
        """)

        title = QLabel("Student Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedWidth(360)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(360)

        login_btn = QPushButton("Login")
        login_btn.setFixedWidth(360)
        login_btn.clicked.connect(self.handle_login)

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.username_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
             QMessageBox.warning(self, "Validation Error", "Please enter username and password")
             return

        # Use API Client to login
        import api_client
        result = api_client.login_student(username, password)
        
        if result["success"]:
            if self.on_login_success:
                self.on_login_success(username)  # Pass username for dashboard title
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", result.get("error", "Unknown error"))
