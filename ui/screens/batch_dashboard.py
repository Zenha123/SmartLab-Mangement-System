from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt

from ui.common.cards import StatCard, CardFrame
from ui.theme import heading_font, Theme


class BatchDashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Batch Dashboard")
        title.setFont(heading_font(18))
        header.addWidget(title)
        header.addStretch(1)
        layout.addLayout(header)

        stats = QGridLayout()
        stats.setSpacing(10)
        stats.addWidget(StatCard("Total PCs", "40"), 0, 0)
        stats.addWidget(StatCard("Students Online", "28", Theme.secondary), 0, 1)
        stats.addWidget(StatCard("Students Offline", "12", Theme.text_muted), 0, 2)
        stats.addWidget(StatCard("Attendance Status", "In Progress", Theme.warning), 1, 0)
        stats.addWidget(StatCard("Exam Mode", "OFF", Theme.danger), 1, 1)
        layout.addLayout(stats)

        actions_card = CardFrame()
        actions_layout = QGridLayout()
        actions_layout.setSpacing(10)
        actions = [
            ("Start Lab Session", Theme.primary),
            ("View Live Screens", Theme.secondary),
            ("Start Exam Mode", Theme.danger),
            ("Distribute Task", Theme.primary),
            ("Start Viva Mode", Theme.secondary),
            ("View Attendance", Theme.primary),
        ]
        for i, (text, color) in enumerate(actions):
            btn = QPushButton(text)
            btn.setStyleSheet(f"QPushButton {{ background: {color}; }}")
            btn.clicked.connect(self._show_placeholder)
            actions_layout.addWidget(btn, i // 3, i % 3)
        actions_card.layout.addLayout(actions_layout)
        layout.addWidget(actions_card)
        layout.addStretch(1)

    def _show_placeholder(self):
        QMessageBox.information(self, "Action", "This is a UI-only action placeholder.")

