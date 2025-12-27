from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.common.badges import StatusDot, ModeBadge
from ui.theme import heading_font, Theme, body_font
from data.mock_data import students


class StudentListScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header with title and stats
        header = QHBoxLayout()
        title = QLabel("👥 Students List")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        header.addWidget(title)
        header.addStretch()
        
        # Quick stats
        stats_label = QLabel(f"Total: {len(students)} students")
        stats_label.setFont(body_font(13))
        stats_label.setStyleSheet(f"color: {Theme.text_muted}; padding: 8px 16px; background: {Theme.background}; border-radius: 8px;")
        header.addWidget(stats_label)
        layout.addLayout(header)

        card = CardFrame(padding=20)
        table = StyledTableWidget(len(students), 5)
        table.setHorizontalHeaderLabels(["Student Name", "PC ID", "Status", "Mode", "Action"])
        
        for row, s in enumerate(students):
            # Student name with avatar placeholder
            name_item = QTableWidgetItem(f"👤 {s['name']}")
            name_item.setFont(body_font(13, QFont.Weight.Medium))
            table.setItem(row, 0, name_item)
            
            # PC ID
            pc_item = QTableWidgetItem(s["pc"])
            pc_item.setFont(body_font(12))
            pc_item.setForeground(QColor(Theme.text_secondary))
            table.setItem(row, 1, pc_item)

            # Status widget
            status_widget = self._status_widget(s["status"])
            table.setCellWidget(row, 2, status_widget)

            # Mode widget
            mode_widget = self._mode_widget(s["mode"])
            table.setCellWidget(row, 3, mode_widget)

            # Action button
            btn = QPushButton("👁️ View")
            btn.setProperty("class", "primary")
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background: {Theme.primary};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background: {Theme.primary_hover};
                }}
                """
            )
            btn.clicked.connect(self._placeholder)
            btn_wrap = QHBoxLayout()
            btn_wrap.setContentsMargins(8, 4, 8, 4)
            btn_wrap.addWidget(btn)
            btn_wrap.addStretch()
            holder = QWidget()
            holder.setLayout(btn_wrap)
            table.setCellWidget(row, 4, holder)

        table.resizeColumnsToContents()
        card.layout.addWidget(table)
        layout.addWidget(card)
        layout.addStretch(1)

    def _status_widget(self, status: str):
        wrap = QHBoxLayout()
        wrap.setContentsMargins(8, 6, 8, 6)
        wrap.setSpacing(8)
        color = Theme.success if status == "Online" else Theme.danger
        wrap.addWidget(StatusDot(color, size=10, tooltip=status, animated=True))
        lbl = QLabel(status)
        lbl.setFont(body_font(12, QFont.Weight.DemiBold))
        lbl.setStyleSheet(f"color: {color};")
        wrap.addWidget(lbl)
        wrap.addStretch()
        container = QWidget()
        container.setLayout(wrap)
        return container

    def _mode_widget(self, mode: str):
        color_map = {
            "Normal": Theme.text_muted,
            "Locked": Theme.danger,
            "Viva": Theme.secondary,
            "Exam": Theme.warning,
        }
        badge = ModeBadge(mode, color_map.get(mode, Theme.primary), size="small")
        wrap = QHBoxLayout()
        wrap.setContentsMargins(8, 6, 8, 6)
        wrap.addWidget(badge)
        wrap.addStretch()
        holder = QWidget()
        holder.setLayout(wrap)
        return holder

    def _placeholder(self):
        # UI-only placeholder
        pass

