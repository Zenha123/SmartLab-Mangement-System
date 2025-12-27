from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout, QPushButton, QFrame, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.common.cards import CardFrame
from ui.theme import heading_font, Theme, body_font


class ExamScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("📝 Exam Mode")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # Exam Mode Banner
        banner = QFrame()
        banner.setStyleSheet(
            f"""
            QFrame {{
                background: {Theme.danger_light};
                border: 2px solid {Theme.danger};
                border-radius: 12px;
                padding: 16px 20px;
            }}
            QLabel {{
                color: {Theme.danger};
                font-weight: 700;
                font-size: 16px;
                letter-spacing: 1px;
            }}
            """
        )
        b_layout = QHBoxLayout(banner)
        b_layout.setContentsMargins(0, 0, 0, 0)
        b_layout.setSpacing(12)
        icon_label = QLabel("🚨")
        icon_label.setStyleSheet("font-size: 24px;")
        text_label = QLabel("EXAM MODE ACTIVE")
        text_label.setFont(body_font(16, QFont.Weight.Bold))
        b_layout.addWidget(icon_label)
        b_layout.addWidget(text_label)
        b_layout.addStretch()
        root.addWidget(banner)

        # Timer display
        timer_card = CardFrame(padding=20)
        timer_layout = QHBoxLayout()
        timer_layout.setSpacing(12)
        timer_label = QLabel("⏱️ Exam Timer:")
        timer_label.setFont(body_font(14, QFont.Weight.Bold))
        timer_label.setStyleSheet(f"color: {Theme.text_primary};")
        timer_value = QLabel("02:30:00")
        timer_value.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        timer_value.setStyleSheet(f"color: {Theme.danger};")
        timer_layout.addWidget(timer_label)
        timer_layout.addWidget(timer_value)
        timer_layout.addStretch()
        timer_card.layout.addLayout(timer_layout)
        root.addWidget(timer_card)

        # Allowed Apps
        allow_card = CardFrame(padding=20)
        allow_heading = QLabel("✅ Allowed Applications")
        allow_heading.setFont(body_font(14, QFont.Weight.Bold))
        allow_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 12px;")
        allow_card.layout.addWidget(allow_heading)
        
        apps_grid = QGridLayout()
        apps_grid.setSpacing(12)
        apps = [
            ("💻 IDE", True),
            ("🌐 Browser", False),
            ("💻 Terminal", True),
            ("📄 Docs", False),
        ]
        for i, (app_name, checked) in enumerate(apps):
            cb = QCheckBox(app_name)
            cb.setChecked(checked)
            cb.setFont(body_font(13))
            cb.setStyleSheet(
                f"""
                QCheckBox {{
                    color: {Theme.text_primary};
                    spacing: 8px;
                }}
                QCheckBox::indicator:checked {{
                    background: {Theme.success};
                }}
                """
            )
            apps_grid.addWidget(cb, i // 2, i % 2)
        allow_card.layout.addLayout(apps_grid)
        root.addWidget(allow_card)

        # Control buttons
        controls = QHBoxLayout()
        controls.setSpacing(12)
        start = QPushButton("🚨 Start Exam")
        start.setProperty("class", "danger")
        start.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.danger};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px 24px;
                font-weight: 700;
                font-size: 14px;
                min-width: 180px;
            }}
            QPushButton:hover {{
                background: #DC2626;
            }}
            """
        )
        end = QPushButton("✅ End Exam")
        end.setProperty("class", "success")
        end.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.success};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px 24px;
                font-weight: 700;
                font-size: 14px;
                min-width: 180px;
            }}
            QPushButton:hover {{
                background: #059669;
            }}
            """
        )
        controls.addWidget(start)
        controls.addWidget(end)
        controls.addStretch(1)
        root.addLayout(controls)
        root.addStretch(1)

