# lab/ui/screens/reports.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget,
    QTableWidgetItem, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.common.styled_dialogs import info, warning          # ← replaces QMessageBox
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


class ReportsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window   = parent
        self.attendance_data = []

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("📄 Reports")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # ── Action buttons ────────────────────────────────────
        actions_card = CardFrame(padding=16)
        actions = QHBoxLayout()
        actions.setSpacing(12)

        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.secondary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover   {{ background: #16A085; }}
            QPushButton:pressed {{ background: #0e8c74; }}
        """)
        refresh_btn.clicked.connect(self.load_reports)

        actions.addWidget(refresh_btn)
        actions.addStretch()
        actions_card.layout.addLayout(actions)
        root.addWidget(actions_card)

        # ── Tabs ──────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.attendance_tab_widget = self._create_attendance_tab()
        self.tabs.addTab(self.attendance_tab_widget,           "📊 Attendance")
        self.tabs.addTab(self._generic_tab("Viva Marks"),      "🎤 Viva Marks")
        self.tabs.addTab(self._generic_tab("Task Submissions"),"📝 Submissions")
        root.addWidget(self.tabs)
        root.addStretch(1)

    # ── Tab builders ──────────────────────────────────────────

    def _create_attendance_tab(self):
        widget = CardFrame(padding=20)
        self.attendance_table = StyledTableWidget(0, 4)
        self.attendance_table.setHorizontalHeaderLabels(
            ["Student", "Student ID", "Status", "Duration (min)"]
        )
        widget.layout.addWidget(self.attendance_table)
        return widget

    def _generic_tab(self, title: str):
        widget = CardFrame(padding=40)
        placeholder = QLabel(
            f"📋 {title} Report\n\n"
            f"This section will display {title.lower()} data.\n"
            f"Data will be loaded from backend when available."
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(body_font(14))
        placeholder.setStyleSheet(f"color: {Theme.text_muted};")
        placeholder.setWordWrap(True)
        widget.layout.addWidget(placeholder)
        return widget

    # ── Data ──────────────────────────────────────────────────

    def load_reports(self):
        if not hasattr(self.parent_window, 'current_batch_id') or \
                self.parent_window.current_batch_id is None:
            # ✅ Blue info dialog — clearly visible OK button
            info(self, "No Batch Selected", "Please select a batch first.")
            return

        batch_id = self.parent_window.current_batch_id
        result   = api_client.get_students(batch_id=batch_id)

        if result["success"]:
            self._populate_attendance_table(result["data"])
        else:
            # ✅ Orange warning dialog — clearly visible OK button
            warning(self, "Load Failed",
                    f"Failed to load reports:\n{result['error']}")

    def _populate_attendance_table(self, students):
        self.attendance_table.setRowCount(len(students))

        for row, student in enumerate(students):
            name_item = QTableWidgetItem(f"👤 {student.get('name', 'Unknown')}")
            name_item.setFont(body_font(13, QFont.Weight.Medium))
            self.attendance_table.setItem(row, 0, name_item)

            id_item = QTableWidgetItem(student.get("student_id", "N/A"))
            id_item.setFont(body_font(12))
            self.attendance_table.setItem(row, 1, id_item)

            status      = student.get("status", "offline")
            status_item = QTableWidgetItem(status.title())
            status_item.setFont(body_font(13, QFont.Weight.DemiBold))
            status_item.setForeground(
                QColor(Theme.success if status == "online" else Theme.text_muted)
            )
            self.attendance_table.setItem(row, 2, status_item)

            duration_item = QTableWidgetItem("N/A")
            duration_item.setFont(body_font(12))
            duration_item.setForeground(QColor(Theme.text_muted))
            self.attendance_table.setItem(row, 3, duration_item)

        self.attendance_table.resizeColumnsToContents()

    # ── Lifecycle ─────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self.load_reports()
