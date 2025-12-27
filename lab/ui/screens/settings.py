from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.common.cards import CardFrame, KeyValueRow
from ui.common.badges import StatusDot
from ui.theme import heading_font, Theme, body_font


class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("⚙️ Settings & Profile")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # Profile Card
        profile_card = CardFrame(padding=24)
        profile_heading = QLabel("👤 Faculty Profile")
        profile_heading.setFont(body_font(16, QFont.Weight.Bold))
        profile_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 20px;")
        profile_card.layout.addWidget(profile_heading)
        
        # Avatar and info
        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(16)
        
        avatar = QLabel("👤")
        avatar.setStyleSheet(
            f"""
            QLabel {{
                background: {Theme.primary};
                color: white;
                border-radius: 40px;
                padding: 20px;
                font-size: 48px;
                min-width: 80px;
                max-width: 80px;
                min-height: 80px;
                max-height: 80px;
            }}
            """
        )
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        profile_info = QVBoxLayout()
        profile_info.setSpacing(8)
        name_label = QLabel("Shireen")
        name_label.setFont(body_font(18, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {Theme.text_primary};")
        role_label = QLabel("Faculty Member")
        role_label.setFont(body_font(13))
        role_label.setStyleSheet(f"color: {Theme.text_muted};")
        profile_info.addWidget(name_label)
        profile_info.addWidget(role_label)
        profile_info.addStretch()
        
        profile_layout.addWidget(avatar)
        profile_widget = QWidget()
        profile_widget.setLayout(profile_info)
        profile_layout.addWidget(profile_widget)
        profile_layout.addStretch()
        profile_card.layout.addLayout(profile_layout)
        root.addWidget(profile_card)

        # Server Configuration
        server_card = CardFrame(padding=20)
        server_heading = QLabel("🔧 Server Configuration")
        server_heading.setFont(body_font(16, QFont.Weight.Bold))
        server_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        server_card.layout.addWidget(server_heading)
        
        server_label = QLabel("Backend Server URL:")
        server_label.setFont(body_font(12, QFont.Weight.Medium))
        server_label.setStyleSheet(f"color: {Theme.text_secondary}; margin-bottom: 8px;")
        server_card.layout.addWidget(server_label)
        
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("https://backend.example.com/api")
        self.server_input.setText("http://localhost:8000/api")
        self.server_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {Theme.border};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Theme.primary};
            }}
            """
        )
        server_card.layout.addWidget(self.server_input)
        
        # Network status
        status_layout = QHBoxLayout()
        status_layout.setSpacing(8)
        status_dot = StatusDot(Theme.success, size=10, animated=True)
        self.network_status = QLabel("Network: Connected")
        self.network_status.setFont(body_font(13, QFont.Weight.DemiBold))
        self.network_status.setStyleSheet(f"color: {Theme.success}; margin-top: 12px;")
        status_layout.addWidget(status_dot)
        status_layout.addWidget(self.network_status)
        status_layout.addStretch()
        server_card.layout.addLayout(status_layout)
        root.addWidget(server_card)

        # Logout
        logout_card = CardFrame(padding=20)
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setProperty("class", "danger")
        logout_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.danger};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 700;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #DC2626;
            }}
            """
        )
        logout_card.layout.addWidget(logout_btn)
        root.addWidget(logout_card)
        root.addStretch(1)

