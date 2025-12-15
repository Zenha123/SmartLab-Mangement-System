from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QHBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt

from ui.common.cards import CardFrame
from ui.theme import heading_font, Theme


class ExamScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("Exam Mode")
        title.setFont(heading_font(18))
        root.addWidget(title)

        banner = QFrame()
        banner.setStyleSheet(
            f"""
            QFrame {{
                background: {Theme.danger}22;
                border: 1px solid {Theme.danger};
                border-radius: 10px;
                padding: 10px;
            }}
            """
        )
        b_layout = QHBoxLayout(banner)
        b_layout.addWidget(QLabel("EXAM MODE ACTIVE (UI placeholder)"))
        root.addWidget(banner)

        allow_card = CardFrame()
        allow_card.layout.addWidget(QLabel("Allowed Apps"))
        for app in ["IDE", "Browser", "Terminal", "Docs"]:
            allow_card.layout.addWidget(QCheckBox(app))
        root.addWidget(allow_card)

        controls = QHBoxLayout()
        start = QPushButton("Start Exam")
        start.setStyleSheet(f"background: {Theme.danger};")
        end = QPushButton("End Exam")
        end.setStyleSheet(f"background: {Theme.secondary};")
        controls.addWidget(start)
        controls.addWidget(end)
        controls.addStretch(1)
        root.addLayout(controls)

        timer = QLabel("Timer: 00:00 (placeholder)")
        root.addWidget(timer)
        root.addStretch(1)

