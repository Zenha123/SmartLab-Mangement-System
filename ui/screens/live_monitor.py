from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

from ui.theme import heading_font, Theme
from ui.common.cards import CardFrame


class LiveMonitorScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Live Monitoring (UI concept)")
        title.setFont(heading_font(18))
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        grid_card = CardFrame()
        grid = QGridLayout()
        grid.setSpacing(10)
        # Default 3x3 concept tiles
        for i in range(9):
            tile = self._tile(f"Student {i+1}", f"PC-{i+1:02d}", "Online" if i % 3 else "Offline")
            grid.addWidget(tile, i // 3, i % 3)
        grid_card.layout.addLayout(grid)
        root.addWidget(grid_card)
        root.addStretch(1)

    def _tile(self, name: str, pc: str, status: str):
        frame = QFrame()
        frame.setStyleSheet(
            f"""
            QFrame {{
                background: {Theme.card_bg};
                border: 1px solid {Theme.border};
                border-radius: 12px;
                min-height: 120px;
            }}
            """
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        layout.addWidget(QLabel(name))
        layout.addWidget(QLabel(pc))
        status_lbl = QLabel(status)
        status_lbl.setStyleSheet(f"color: {Theme.success if status == 'Online' else Theme.danger}; font-weight: 600;")
        layout.addWidget(status_lbl)
        layout.addStretch(1)
        btn = QPushButton("Open View")
        layout.addWidget(btn)
        return frame

