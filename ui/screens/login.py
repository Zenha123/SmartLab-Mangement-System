from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame
from PyQt6.QtCore import pyqtSignal, Qt

from ui.theme import heading_font, Theme
from ui.common.cards import CardFrame


class LoginScreen(QWidget):
    login_success = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        wrapper = QVBoxLayout(self)
        wrapper.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = CardFrame(padding=20)
        card.setFixedWidth(360)
        layout = QVBoxLayout(card)
        layout.setSpacing(14)

        title = QLabel("Faculty Login")
        title.setFont(heading_font(18))
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.error_lbl = QLabel("")
        self.error_lbl.setStyleSheet(f"color: {Theme.danger};")
        layout.addWidget(self.error_lbl)

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Faculty ID / Email")
        layout.addWidget(self.id_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pass_input)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        wrapper.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

    def handle_login(self):
        if not self.id_input.text().strip() or not self.pass_input.text():
            self.error_lbl.setText("Please enter Faculty ID and password.")
            return
        self.error_lbl.setText("")
        self.login_success.emit(self.id_input.text().strip())

