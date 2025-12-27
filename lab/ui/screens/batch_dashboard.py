from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.common.cards import StatCard, CardFrame
from ui.theme import heading_font, Theme, body_font


class BatchDashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("📊 Batch Dashboard")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        header.addWidget(title)
        header.addStretch(1)
        layout.addLayout(header)

        # Overview stats with icons
        stats = QGridLayout()
        stats.setSpacing(16)
        stats.addWidget(StatCard("💻 Total PCs", "40", Theme.info, icon="💻"), 0, 0)
        stats.addWidget(StatCard("🟢 Students Online", "28", Theme.success, icon="🟢"), 0, 1)
        stats.addWidget(StatCard("🔴 Students Offline", "12", Theme.text_muted, icon="🔴"), 0, 2)
        stats.addWidget(StatCard("📋 Attendance Status", "In Progress", Theme.warning, icon="📋"), 1, 0)
        stats.addWidget(StatCard("📝 Exam Mode", "OFF", Theme.danger, icon="📝"), 1, 1)
        layout.addLayout(stats)

        # Quick Actions
        actions_card = CardFrame(padding=24)
        actions_heading = QLabel("⚡ Quick Actions")
        actions_heading.setFont(body_font(16, QFont.Weight.Bold))
        actions_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        actions_card.layout.addWidget(actions_heading)
        
        actions_layout = QGridLayout()
        actions_layout.setSpacing(12)
        actions = [
            ("🚀 Start Lab Session", Theme.primary),
            ("🖥️ View Live Screens", Theme.secondary),
            ("📝 Start Exam Mode", Theme.danger),
            ("📤 Distribute Task", Theme.primary),
            ("🎤 Start Viva Mode", Theme.secondary),
            ("📊 View Attendance", Theme.info),
        ]
        for i, (text, color) in enumerate(actions):
            btn = QPushButton(text)
            btn.setProperty("class", "primary" if color == Theme.primary else ("danger" if color == Theme.danger else "secondary"))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 14px 20px;
                    font-weight: 600;
                    font-size: 13px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background: {color}dd;
                    transform: translateY(-2px);
                }}
                QPushButton:pressed {{
                    background: {color}bb;
                }}
                """
            )
            btn.clicked.connect(self._show_placeholder)
            actions_layout.addWidget(btn, i // 3, i % 3)
        actions_card.layout.addLayout(actions_layout)
        layout.addWidget(actions_card)
        layout.addStretch(1)

    def _show_placeholder(self):
        QMessageBox.information(self, "Action", "This is a UI-only action placeholder.")

