from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidgetItem
from PyQt6.QtCore import Qt

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.common.badges import StatusDot, ModeBadge
from ui.theme import heading_font, Theme
from data.mock_data import students


class StudentListScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Students List")
        title.setFont(heading_font(18))
        layout.addWidget(title)

        card = CardFrame()
        table = StyledTableWidget(len(students), 5)
        table.setHorizontalHeaderLabels(["Student Name", "PC ID", "Status", "Mode", "Action"])
        for row, s in enumerate(students):
            name_item = QTableWidgetItem(s["name"])
            pc_item = QTableWidgetItem(s["pc"])
            table.setItem(row, 0, name_item)
            table.setItem(row, 1, pc_item)

            status_widget = self._status_widget(s["status"])
            table.setCellWidget(row, 2, status_widget)

            mode_widget = self._mode_widget(s["mode"])
            table.setCellWidget(row, 3, mode_widget)

            btn = QPushButton("View")
            btn.setStyleSheet(f"background: {Theme.primary}; padding: 6px 10px;")
            btn.clicked.connect(self._placeholder)
            btn_wrap = QHBoxLayout()
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
        wrap.setContentsMargins(6, 4, 6, 4)
        wrap.setSpacing(6)
        color = Theme.success if status == "Online" else Theme.danger
        wrap.addWidget(StatusDot(color, tooltip=status))
        lbl = QLabel(status)
        lbl.setStyleSheet("font-weight: 600;")
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
        badge = ModeBadge(mode, color_map.get(mode, Theme.primary))
        wrap = QHBoxLayout()
        wrap.setContentsMargins(6, 4, 6, 4)
        wrap.addWidget(badge)
        wrap.addStretch()
        holder = QWidget()
        holder.setLayout(wrap)
        return holder

    def _placeholder(self):
        # UI-only placeholder
        pass

