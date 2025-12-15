from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout

from ui.common.cards import CardFrame
from ui.theme import heading_font, Theme


class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("Settings & Profile")
        title.setFont(heading_font(18))
        root.addWidget(title)

        card = CardFrame()
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("Backend server URL")
        self.network_status = QLabel("Network: Connected (mock)")
        self.profile = QLabel("Faculty: Shireen (avatar placeholder)")
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet(f"background: {Theme.danger};")

        card.layout.addWidget(self.server_input)
        card.layout.addWidget(self.network_status)
        card.layout.addWidget(self.profile)
        card.layout.addWidget(logout_btn)
        root.addWidget(card)
        root.addStretch(1)

