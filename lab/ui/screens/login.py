from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from ui.theme import heading_font, Theme, body_font
from ui.common.cards import CardFrame
from api.global_client import api_client


class LoginScreen(QWidget):
    login_success = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Set background for the login screen widget
        self.setStyleSheet(f"background: {Theme.background};")
        wrapper = QVBoxLayout(self)
        wrapper.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wrapper.setContentsMargins(40, 40, 40, 40)

        card = CardFrame(padding=32, hoverable=False)
        card.setFixedWidth(420)
        # Use CardFrame's existing layout
        layout = card.layout
        layout.setSpacing(20)
        # Ensure card has a minimum height so content is visible
        card.setMinimumHeight(400)

        # App logo/title
        title = QLabel("🔐 Faculty Login")
        title.setFont(heading_font(28, bold=True))
        title.setStyleSheet(f"color: {Theme.primary}; margin-bottom: 8px;")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Smart Lab Management System")
        subtitle.setFont(body_font(13))
        subtitle.setStyleSheet(f"color: {Theme.text_muted}; margin-bottom: 24px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(subtitle)

        self.error_lbl = QLabel("")
        self.error_lbl.setFont(body_font(12))
        self.error_lbl.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.danger};
                background: {Theme.danger_light};
                border: 1px solid {Theme.danger};
                border-radius: 8px;
                padding: 10px 12px;
            }}
            """
        )
        self.error_lbl.setWordWrap(True)
        self.error_lbl.hide()
        layout.addWidget(self.error_lbl)

        # Faculty ID input
        id_label = QLabel("Faculty ID / Email:")
        id_label.setFont(body_font(12, QFont.Weight.Medium))
        id_label.setStyleSheet(f"color: {Theme.text_secondary}; margin-bottom: 6px;")
        layout.addWidget(id_label)
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter your faculty ID or email")
        self.id_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {Theme.border};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Theme.primary};
            }}
            """
        )
        layout.addWidget(self.id_input)

        # Password input
        pass_label = QLabel("Password:")
        pass_label.setFont(body_font(12, QFont.Weight.Medium))
        pass_label.setStyleSheet(f"color: {Theme.text_secondary}; margin-top: 12px; margin-bottom: 6px;")
        layout.addWidget(pass_label)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Enter your password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {Theme.border};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Theme.primary};
            }}
            """
        )
        layout.addWidget(self.pass_input)

        # Login button
        self.login_btn = QPushButton("🚀 Login")
        self.login_btn.setProperty("class", "primary")
        self.login_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.primary};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px 24px;
                font-weight: 700;
                font-size: 15px;
                margin-top: 8px;
            }}
            QPushButton:hover {{
                background: {Theme.primary_hover};
            }}
            """
        )
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        layout.addStretch()

        wrapper.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def handle_login(self):
        faculty_id = self.id_input.text().strip()
        password = self.pass_input.text()
        
        # Validate input fields
        if not faculty_id or not password:
            self.error_lbl.setText("⚠️ Please enter Faculty ID and password.")
            self.error_lbl.show()
            return
        
        # Disable login button during request
        self.login_btn.setEnabled(False)
        self.login_btn.setText("🔄 Logging in...")
        
        # Call backend API using global client
        result = api_client.login(faculty_id, password)
        
        # Re-enable button
        self.login_btn.setEnabled(True)
        self.login_btn.setText("🚀 Login")
        
        if result["success"]:
            # Login successful
            self.error_lbl.hide()
            self.error_lbl.setText("")
            faculty_name = result["data"]["faculty"]["name"]
            self.login_success.emit(faculty_name)
        else:
            # Login failed
            error_msg = result.get("error", "Login failed")
            self.error_lbl.setText(f"❌ {error_msg}")
            self.error_lbl.show()

