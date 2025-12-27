from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.theme import heading_font, Theme, body_font
from ui.common.cards import CardFrame
from ui.common.badges import StatusDot, ModeBadge


class LiveMonitorScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # Header with view selector
        header = QHBoxLayout()
        title = QLabel("🖥️ Live Monitoring")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        header.addWidget(title)
        header.addStretch()
        
        # Grid size selector
        view_label = QLabel("View:")
        view_label.setFont(body_font(12))
        view_label.setStyleSheet(f"color: {Theme.text_muted};")
        view_combo = QComboBox()
        view_combo.addItems(["2×2", "3×3", "4×4"])
        view_combo.setCurrentIndex(1)
        view_combo.setStyleSheet(
            f"""
            QComboBox {{
                border: 1px solid {Theme.border};
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 80px;
            }}
            """
        )
        header.addWidget(view_label)
        header.addWidget(view_combo)
        root.addLayout(header)

        grid_card = CardFrame(padding=20)
        grid = QGridLayout()
        grid.setSpacing(16)
        # Default 3x3 concept tiles
        for i in range(9):
            tile = self._tile(f"Student {i+1}", f"PC-{i+1:02d}", "Online" if i % 3 else "Offline")
            grid.addWidget(tile, i // 3, i % 3)
        grid_card.layout.addLayout(grid)
        root.addWidget(grid_card)
        root.addStretch(1)

    def _tile(self, name: str, pc: str, status: str):
        frame = QFrame()
        frame.setObjectName("monitorTile")
        frame.setStyleSheet(
            f"""
            QFrame#monitorTile {{
                background: {Theme.card_bg};
                border: 2px solid {Theme.border};
                border-radius: 12px;
                min-height: 160px;
            }}
            QFrame#monitorTile:hover {{
                border: 2px solid {Theme.primary};
                background: {Theme.primary}05;
            }}
            """
        )
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        # Status badge at top
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_color = Theme.success if status == "Online" else Theme.danger
        status_dot = StatusDot(status_color, size=8, animated=True)
        status_label = QLabel(status)
        status_label.setFont(body_font(11, QFont.Weight.DemiBold))
        status_label.setStyleSheet(f"color: {status_color};")
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        layout.addWidget(status_widget)
        
        # Placeholder for screen view
        screen_placeholder = QLabel("📺")
        screen_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        screen_placeholder.setStyleSheet(
            f"""
            QLabel {{
                background: {Theme.background};
                border: 1px dashed {Theme.border};
                border-radius: 8px;
                min-height: 80px;
                font-size: 32px;
            }}
            """
        )
        layout.addWidget(screen_placeholder)
        
        # Student info
        name_label = QLabel(name)
        name_label.setFont(body_font(13, QFont.Weight.DemiBold))
        name_label.setStyleSheet(f"color: {Theme.text_primary};")
        layout.addWidget(name_label)
        
        pc_label = QLabel(pc)
        pc_label.setFont(body_font(11))
        pc_label.setStyleSheet(f"color: {Theme.text_muted};")
        layout.addWidget(pc_label)
        
        layout.addStretch()
        
        # Open view button
        btn = QPushButton("👁️ View")
        btn.setProperty("class", "primary")
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.primary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {Theme.primary_hover};
            }}
            """
        )
        layout.addWidget(btn)
        return frame

