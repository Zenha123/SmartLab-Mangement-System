# lab/ui/screens/reports.py
#
# New feature: Viva Marks tab now accepts a Quizizz-exported Excel file.
# Faculty clicks "Upload Quizizz Report", picks the .xlsx/.xls file,
# and SmartLab reads it and displays Rank / First Name / Accuracy / Score
# in a clean styled table — no backend call needed.
#
# Requires:  pip install openpyxl  (already in most PyQt6 setups)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.common.styled_dialogs import info, warning, error
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

        # ── Page title ────────────────────────────────────────
        title = QLabel("📄 Reports")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # ── Global action bar ─────────────────────────────────
        actions_card = CardFrame(padding=16)
        actions = QHBoxLayout()
        actions.setSpacing(12)

        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setStyleSheet(self._btn(Theme.secondary, "#16A085"))
        refresh_btn.clicked.connect(self.load_reports)

        actions.addWidget(refresh_btn)
        actions.addStretch()
        actions_card.layout.addLayout(actions)
        root.addWidget(actions_card)

        # ── Tabs ──────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {Theme.border};
                border-radius: 8px;
                background: white;
            }}
            QTabBar::tab {{
                padding: 10px 20px;
                font-size: 13px; font-weight: 600;
                color: {Theme.text_muted};
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {Theme.primary};
                border-bottom: 2px solid {Theme.primary};
            }}
        """)

        self.tabs.addTab(self._create_attendance_tab(),        "📊 Attendance")
        self.tabs.addTab(self._create_viva_tab(),              "🎤 Viva Marks")
        self.tabs.addTab(self._generic_tab("Task Submissions"),"📝 Submissions")

        root.addWidget(self.tabs)
        root.addStretch(1)

    # ── Shared button style ───────────────────────────────────

    def _btn(self, bg, hover):
        return f"""
            QPushButton {{
                background: {bg}; color: white; border: none;
                border-radius: 6px; padding: 10px 20px;
                font-weight: 600; font-size: 13px;
            }}
            QPushButton:hover   {{ background: {hover}; }}
            QPushButton:pressed {{ background: {hover}cc; }}
        """

    # ══════════════════════════════════════════════════════════
    # TAB 1 — Attendance
    # ══════════════════════════════════════════════════════════

    def _create_attendance_tab(self):
        widget = CardFrame(padding=20)
        self.attendance_table = StyledTableWidget(0, 4)
        self.attendance_table.setHorizontalHeaderLabels(
            ["Student", "Student ID", "Status", "Duration (min)"]
        )
        widget.layout.addWidget(self.attendance_table)
        return widget

    # ══════════════════════════════════════════════════════════
    # TAB 2 — Viva Marks  (Quizizz Excel upload)
    # ══════════════════════════════════════════════════════════

    def _create_viva_tab(self):
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(20, 20, 20, 20)
        v.setSpacing(14)

        # ── Top bar: description + upload button ──────────────
        top_row = QHBoxLayout()

        desc = QLabel(
            "Upload the Excel report exported from Quizizz.\n"
            "SmartLab will automatically read and display the results below."
        )
        desc.setStyleSheet(f"color: {Theme.text_muted}; font-size: 13px;")
        desc.setWordWrap(True)
        top_row.addWidget(desc, 1)

        upload_btn = QPushButton("📂  Upload Quizizz Report (.xlsx)")
        upload_btn.setStyleSheet(self._btn(Theme.primary, "#1565C0"))
        upload_btn.setFixedHeight(40)
        upload_btn.clicked.connect(self._upload_quizizz_excel)
        top_row.addWidget(upload_btn)

        v.addLayout(top_row)

        # ── Divider ───────────────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #e0e0e0;")
        v.addWidget(line)

        # ── Loaded file name indicator ────────────────────────
        self.viva_file_label = QLabel("No file loaded yet.")
        self.viva_file_label.setStyleSheet(
            f"color: {Theme.text_muted}; font-size: 12px; font-style: italic;"
        )
        v.addWidget(self.viva_file_label)

        # ── Results table ─────────────────────────────────────
        self.viva_table = StyledTableWidget(0, 4)
        self.viva_table.setHorizontalHeaderLabels(
            ["Rank", "Student Name", "Accuracy", "Score"]
        )
        self.viva_table.setStyleSheet(f"""
            QTableWidget {{
                background: white;
                border: 1px solid {Theme.border};
                border-radius: 8px;
                gridline-color: #f3f4f6;
                font-size: 13px;
                selection-background-color: transparent;
            }}
            QHeaderView::section {{
                background: #f9fafb;
                font-weight: 700; font-size: 12px;
                color: #374151; padding: 10px 8px;
                border: none;
                border-bottom: 2px solid {Theme.border};
                text-transform: uppercase;
            }}
            QTableWidget::item         {{ padding: 10px; }}
            QTableWidget::item:alternate {{ background: #fafafa; }}
        """)
        self.viva_table.verticalHeader().setVisible(False)
        self.viva_table.setShowGrid(False)
        self.viva_table.setAlternatingRowColors(True)
        v.addWidget(self.viva_table)

        # ── Summary line ──────────────────────────────────────
        self.viva_summary_label = QLabel("")
        self.viva_summary_label.setStyleSheet(
            f"color: {Theme.text_muted}; font-size: 12px;"
        )
        v.addWidget(self.viva_summary_label)

        return container

    # ── Upload handler ────────────────────────────────────────

    def _upload_quizizz_excel(self):
        """Open file picker → read Quizizz Excel → fill viva table."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Quizizz Excel Report",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)",
        )
        if not file_path:
            return                          # user cancelled

        try:
            import openpyxl
        except ImportError:
            error(self, "Missing Library",
                  "openpyxl is not installed.\n\nRun:  pip install openpyxl")
            return

        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            ws = wb.active

            # Collect non-empty rows
            all_rows = [
                row for row in ws.iter_rows(values_only=True)
                if any(c is not None for c in row)
            ]

            if len(all_rows) < 2:
                warning(self, "Empty File",
                        "The selected file appears to be empty.")
                return

            # Find header row — look for rank/name keywords
            header_idx = 0
            for i, row in enumerate(all_rows):
                cells_lower = [
                    str(c).strip().lower() for c in row if c is not None
                ]
                if any(k in cells_lower
                       for k in ("rank", "first name", "firstname", "name")):
                    header_idx = i
                    break

            headers   = [
                str(c).strip().lower() if c is not None else ""
                for c in all_rows[header_idx]
            ]
            data_rows = all_rows[header_idx + 1:]

            # Map roles to column indices
            col_map = self._detect_columns(headers)
            if not col_map:
                error(self, "Unrecognised Format",
                      "Could not find expected columns "
                      "(Rank, Name, Accuracy, Score).\n\n"
                      "Please upload a standard Quizizz Excel export.")
                return

            self._populate_viva_table(data_rows, col_map)

            import os
            self.viva_file_label.setText(
                f"📄  Loaded: {os.path.basename(file_path)}"
            )
            self.viva_file_label.setStyleSheet(
                f"color: {Theme.success}; font-size: 12px; font-weight: 600;"
            )

        except Exception as e:
            error(self, "Read Error",
                  f"Could not read the Excel file:\n{str(e)}")

    # ── Column auto-detection ─────────────────────────────────

    def _detect_columns(self, headers: list) -> dict:
        """
        Match column roles to indices regardless of exact Quizizz header wording.
        Returns {} if fewer than 2 roles matched (probably wrong file).
        """
        keywords = {
            "rank":     ["rank"],
            "name":     ["first name", "firstname", "name", "student", "player"],
            "accuracy": ["accuracy", "acc", "%", "correct"],
            "score":    ["score", "marks", "points", "total"],
        }
        col_map = {}
        for role, kws in keywords.items():
            for idx, h in enumerate(headers):
                if any(kw in h for kw in kws):
                    col_map[role] = idx
                    break
        return col_map if len(col_map) >= 2 else {}

    # ── Populate viva table ───────────────────────────────────

    def _populate_viva_table(self, data_rows: list, col_map: dict):
        valid = [r for r in data_rows if any(c is not None for c in r)]
        self.viva_table.setRowCount(len(valid))

        for ri, row in enumerate(valid):

            def _cell(key):
                idx = col_map.get(key)
                if idx is None or idx >= len(row):
                    return ""
                v = row[idx]
                return str(v).strip() if v is not None else ""

            rank     = _cell("rank")
            name     = _cell("name")
            accuracy = _cell("accuracy")
            score    = _cell("score")

            # ── Rank ──────────────────────────────────────────
            r_item = QTableWidgetItem(rank)
            r_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            r_item.setFont(body_font(13, QFont.Weight.Bold))
            self.viva_table.setItem(ri, 0, r_item)

            # ── Name ──────────────────────────────────────────
            n_item = QTableWidgetItem(f"👤  {name}" if name else "—")
            n_item.setFont(body_font(13, QFont.Weight.Medium))
            self.viva_table.setItem(ri, 1, n_item)

            # ── Accuracy — colour-coded ───────────────────────
            a_item = QTableWidgetItem(accuracy)
            a_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            a_item.setFont(body_font(13, QFont.Weight.DemiBold))
            try:
                val = float(accuracy.replace("%", "").strip())
                if val >= 75:
                    a_item.setForeground(QColor("#43A047"))   # green  ≥75 %
                elif val >= 50:
                    a_item.setForeground(QColor("#FF9800"))   # orange ≥50 %
                else:
                    a_item.setForeground(QColor("#e53935"))   # red    <50 %
            except ValueError:
                pass
            self.viva_table.setItem(ri, 2, a_item)

            # ── Score ─────────────────────────────────────────
            s_item = QTableWidgetItem(score)
            s_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            s_item.setFont(body_font(13))
            self.viva_table.setItem(ri, 3, s_item)

        self.viva_table.resizeColumnsToContents()

        self.viva_summary_label.setText(
            f"✅  {len(valid)} student(s) loaded from Quizizz report."
        )
        self.viva_summary_label.setStyleSheet(
            f"color: {Theme.success}; font-size: 12px; font-weight: 600;"
        )

    # ══════════════════════════════════════════════════════════
    # TAB 3 — Generic placeholder
    # ══════════════════════════════════════════════════════════

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

    # ══════════════════════════════════════════════════════════
    # Attendance (unchanged)
    # ══════════════════════════════════════════════════════════

    def load_reports(self):
        if not hasattr(self.parent_window, 'current_batch_id') or \
                self.parent_window.current_batch_id is None:
            info(self, "No Batch Selected", "Please select a batch first.")
            return

        result = api_client.get_students(
            batch_id=self.parent_window.current_batch_id)
        if result["success"]:
            self._populate_attendance_table(result["data"])
        else:
            warning(self, "Load Failed",
                    f"Failed to load reports:\n{result['error']}")

    def _populate_attendance_table(self, students):
        self.attendance_table.setRowCount(len(students))
        for row, student in enumerate(students):
            name_item = QTableWidgetItem(
                f"👤 {student.get('name', 'Unknown')}")
            name_item.setFont(body_font(13, QFont.Weight.Medium))
            self.attendance_table.setItem(row, 0, name_item)

            id_item = QTableWidgetItem(student.get("student_id", "N/A"))
            id_item.setFont(body_font(12))
            self.attendance_table.setItem(row, 1, id_item)

            status      = student.get("status", "offline")
            status_item = QTableWidgetItem(status.title())
            status_item.setFont(body_font(13, QFont.Weight.DemiBold))
            status_item.setForeground(
                QColor(Theme.success if status == "online" else Theme.text_muted))
            self.attendance_table.setItem(row, 2, status_item)

            dur_item = QTableWidgetItem("N/A")
            dur_item.setFont(body_font(12))
            dur_item.setForeground(QColor(Theme.text_muted))
            self.attendance_table.setItem(row, 3, dur_item)

        self.attendance_table.resizeColumnsToContents()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_reports()
