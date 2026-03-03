from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidgetItem,
    QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.theme import heading_font, body_font, Theme
from api.global_client import api_client


class ReportsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window = parent

        # ================= ROOT LAYOUT =================
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # ================= TITLE =================
        title = QLabel("📄 Reports")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary};")
        root.addWidget(title)

        # ================= CARD =================
        card = CardFrame(padding=20)
        root.addWidget(card)

        # ================= TABLE =================
        self.table = StyledTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([
            "STUDENT NAME",
            "STUDENT ID",
            "ACTION"
        ])

        # --- Formal look fixes ---
        self.table.setSelectionMode(self.table.SelectionMode.NoSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setAlternatingRowColors(False)

        # Row height (CRITICAL to avoid button clipping)
        self.table.verticalHeader().setDefaultSectionSize(56)

        # Header alignment & polish
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Remove hover / highlight noise
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                alternate-background-color: #FFFFFF;
            }
            QTableWidget::item:hover {
                background: transparent;
            }
            QHeaderView::section {
                background-color: #F9FAFB;
                color: #111827;
                font-weight: 700;
                font-size: 12px;
                padding: 12px;
                border-bottom: 1px solid #E5E7EB;
            }
        """)

        card.layout.addWidget(self.table)
        root.addStretch()

    # =================================================
    # Load students when page becomes visible
    # =================================================
    def showEvent(self, event):
        super().showEvent(event)
        self.load_students()

    # =================================================
    # Fetch students from backend
    # =================================================
    def load_students(self):
        if not hasattr(self.parent_window, "current_batch_id") or not self.parent_window.current_batch_id:
            QMessageBox.information(self, "Info", "Please select a batch first")
            return

        result = api_client.get_students(batch_id=self.parent_window.current_batch_id)

        if not result.get("success"):
            QMessageBox.warning(
                self,
                "Error",
                result.get("error", "Failed to load students")
            )
            return

        self.populate_table(result.get("data", []))

    # =================================================
    # Populate table
    # =================================================
    def populate_table(self, students):
        self.table.setRowCount(len(students))

        for row, student in enumerate(students):
            student_name = student.get("name", "")
            student_id = student.get("student_id", "")

            # ---- Name ----
            name_item = QTableWidgetItem(student_name)
            name_item.setFont(body_font(13, QFont.Weight.Medium))
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 0, name_item)
            
            # ---- ID ----
            id_item = QTableWidgetItem(student_id)
            id_item.setFont(body_font(12))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, id_item)
            
            # ---- Button ----
            btn = QPushButton("Generate Report")
            btn.setFixedSize(160, 36)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            btn.setStyleSheet("""
                QPushButton {
                    background-color: #111827;
                    color: #FFFFFF;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                }
                QPushButton:hover {
                    background-color: #1F2937;
                }
                QPushButton:pressed {
                    background-color: #030712;
                }
            """)

            btn.clicked.connect(self._make_report_handler(student_id, student_name))
            self.table.setCellWidget(row, 2, btn)

        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(2, 200)

    # =================================================
    # Safe signal binding
    # =================================================
    def _make_report_handler(self, student_id, student_name):
        def handler():
            self.on_report_clicked(student_id, student_name)
        return handler

    # =================================================
    # Button action
    # =================================================
    def on_report_clicked(self, student_id, student_name):
        # api_client.base_url already includes /api
        report_url = f"{api_client.base_url.rstrip('/')}/reports/student/{student_id}/"

        print(f"[REPORT] Opening PDF for {student_name} ({student_id})")
        print(f"[REPORT] URL: {report_url}")

        QDesktopServices.openUrl(QUrl(report_url))