from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QComboBox,
    QGridLayout,
    QTableWidgetItem,
)
from PyQt6.QtGui import QFont, QColor
from datetime import datetime

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


class AttendanceScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_records = []

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("Attendance")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        header.addWidget(title)
        header.addStretch(1)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("class", "secondary")
        self.refresh_btn.clicked.connect(self.load_subjects)
        header.addWidget(self.refresh_btn)
        self.main_layout.addLayout(header)

        subtitle = QLabel("Select subject -> choose session date -> choose period/hour -> view present/absent list")
        subtitle.setFont(body_font(13))
        subtitle.setStyleSheet(f"color: {Theme.text_muted};")
        self.main_layout.addWidget(subtitle)

        filters_card = CardFrame(padding=18, hoverable=False)
        filters_grid = QGridLayout()
        filters_grid.setHorizontalSpacing(12)
        filters_grid.setVerticalSpacing(10)

        subject_label = QLabel("Subject")
        subject_label.setFont(body_font(12, QFont.Weight.DemiBold))
        filters_grid.addWidget(subject_label, 0, 0)

        self.subject_combo = QComboBox()
        self.subject_combo.addItem("Select subject...", "")
        self.subject_combo.currentIndexChanged.connect(self.on_subject_changed)
        filters_grid.addWidget(self.subject_combo, 1, 0)

        date_label = QLabel("Lab Session Date")
        date_label.setFont(body_font(12, QFont.Weight.DemiBold))
        filters_grid.addWidget(date_label, 0, 1)

        self.date_combo = QComboBox()
        self.date_combo.addItem("Select date...", "")
        self.date_combo.currentIndexChanged.connect(self.on_date_changed)
        filters_grid.addWidget(self.date_combo, 1, 1)

        hour_label = QLabel("Period / Hour")
        hour_label.setFont(body_font(12, QFont.Weight.DemiBold))
        filters_grid.addWidget(hour_label, 0, 2)

        self.hour_combo = QComboBox()
        self.hour_combo.addItem("All periods", "")
        filters_grid.addWidget(self.hour_combo, 1, 2)

        self.load_btn = QPushButton("Show Attendance")
        self.load_btn.clicked.connect(self.load_attendance_for_selection)
        filters_grid.addWidget(self.load_btn, 1, 3)

        filters_card.layout.addLayout(filters_grid)
        self.main_layout.addWidget(filters_card)

        self.summary_label = QLabel("Choose a subject to load available lab-session dates")
        self.summary_label.setFont(body_font(12))
        self.summary_label.setStyleSheet(
            f"color: {Theme.text_secondary}; padding: 8px 12px; background: {Theme.card_bg}; border: 1px solid {Theme.border}; border-radius: 8px;"
        )
        self.main_layout.addWidget(self.summary_label)

        table_card = CardFrame(padding=18, hoverable=False)
        self.table = StyledTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Student",
            "Student ID",
            "Batch",
            "Date",
            "Hour",
            "Status",
            "Login Time",
            "Session",
        ])
        table_card.layout.addWidget(self.table)
        self.main_layout.addWidget(table_card)

        footer = QHBoxLayout()
        footer.addStretch(1)

        self.sync_etlab_btn = QPushButton("Sync Attendance to ETLab")
        self.sync_etlab_btn.clicked.connect(self.sync_attendance_to_etlab)
        footer.addWidget(self.sync_etlab_btn)

        self.sync_subject_etlab_btn = QPushButton("Sync Whole Subject to ETLab")
        self.sync_subject_etlab_btn.clicked.connect(self.sync_subject_attendance_to_etlab)
        footer.addWidget(self.sync_subject_etlab_btn)

        self.main_layout.addLayout(footer)
        self.main_layout.addStretch(1)

    def _format_last_sync_text(self, records):
        sync_values = [
            (item.get("last_synced_to_etlab_at") or "").strip()
            for item in records
            if item.get("last_synced_to_etlab_at")
        ]

        if not sync_values:
            return "Last Sync to ETLab: Not synced yet"

        raw_value = max(sync_values)
        display_value = self._format_sync_timestamp(raw_value)
        return f"Last Sync to ETLab: {display_value}"

    def _format_sync_timestamp(self, raw_value):
        display_value = (raw_value or "").replace("T", " ").split("+")[0].replace("Z", "")
        try:
            dt_value = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
            display_value = dt_value.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
        return display_value or "Not synced yet"

    def _extract_subjects_from_timetable(self):
        subjects = set()
        timetable_result = api_client.get_faculty_weekly_timetable()
        if not timetable_result["success"]:
            return subjects

        payload = timetable_result.get("data") if isinstance(timetable_result.get("data"), dict) else {}
        for slot in payload.get("slots", []):
            subject = (slot.get("subject_name") or "").strip()
            if subject:
                subjects.add(subject)
        return subjects

    def load_subjects(self):
        self.subject_combo.clear()
        self.subject_combo.addItem("Select subject...", "")
        self.date_combo.clear()
        self.date_combo.addItem("Select date...", "")
        self.hour_combo.clear()
        self.hour_combo.addItem("All periods", "")
        self.table.setRowCount(0)
        self.current_records = []

        subjects = set()

        attendance_result = api_client.get_faculty_attendance()
        if attendance_result["success"]:
            for item in (attendance_result.get("data") or []):
                subject = (item.get("subject_name") or "").strip()
                if subject:
                    subjects.add(subject)

        if not subjects:
            subjects = self._extract_subjects_from_timetable()

        for subject in sorted(subjects):
            self.subject_combo.addItem(subject, subject)

        if subjects:
            self.summary_label.setText("Select a subject to view completed lab-session dates.")
        else:
            self.summary_label.setText("No subjects found for this faculty.")

    def on_subject_changed(self, _index: int):
        subject_name = self.subject_combo.currentData() or ""
        self.date_combo.clear()
        self.date_combo.addItem("Select date...", "")
        self.hour_combo.clear()
        self.hour_combo.addItem("All periods", "")
        self.table.setRowCount(0)
        self.current_records = []

        if not subject_name:
            self.summary_label.setText("Choose a subject to load session dates.")
            return

        result = api_client.get_faculty_attendance(subject_name=subject_name)
        if not result["success"]:
            QMessageBox.warning(self, "Error", f"Failed to load session dates:\n{result['error']}")
            return

        dates = set()
        for item in (result.get("data") or []):
            session_date = item.get("session_date") or item.get("scheduled_date")
            if session_date:
                dates.add(str(session_date))

        for date_str in sorted(dates, reverse=True):
            self.date_combo.addItem(date_str, date_str)

        if dates:
            self.summary_label.setText(f"Subject '{subject_name}' has {len(dates)} session date(s).")
        else:
            self.summary_label.setText(f"No completed lab-session dates found for '{subject_name}'.")

    def on_date_changed(self, _index: int):
        subject_name = self.subject_combo.currentData() or ""
        date_str = self.date_combo.currentData() or ""
        self.hour_combo.clear()
        self.hour_combo.addItem("All periods", "")

        if not subject_name or not date_str:
            return

        result = api_client.get_faculty_attendance(subject_name=subject_name, date=date_str)
        if not result["success"]:
            return

        hours = set()
        for item in (result.get("data") or []):
            hour = item.get("scheduled_hour")
            if hour:
                hours.add(int(hour))

        for hour in sorted(hours):
            self.hour_combo.addItem(f"P{hour}", hour)

    def load_attendance_for_selection(self):
        subject_name = self.subject_combo.currentData() or ""
        date_str = self.date_combo.currentData() or ""
        hour = self.hour_combo.currentData() or ""

        if not subject_name:
            QMessageBox.information(self, "Subject Required", "Please select a subject.")
            return
        if not date_str:
            QMessageBox.information(self, "Date Required", "Please select a lab-session date.")
            return

        result = api_client.get_faculty_attendance(subject_name=subject_name, date=date_str, hour=hour if hour else None)
        if not result["success"]:
            QMessageBox.warning(self, "Error", f"Failed to load attendance:\n{result['error']}")
            return

        records = result.get("data") or []
        self.current_records = records
        self.table.setRowCount(len(records))

        present_count = 0
        absent_count = 0

        for row, item in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(item.get("student_name", "Unknown")))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("student_id", "-")))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("batch_name", "-")))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.get("session_date") or item.get("scheduled_date") or "-")))

            hour = item.get("scheduled_hour")
            hour_text = f"P{hour}" if hour else "-"
            self.table.setItem(row, 4, QTableWidgetItem(hour_text))

            status = (item.get("status") or "").lower()
            if status == "present":
                present_count += 1
            elif status == "absent":
                absent_count += 1

            status_item = QTableWidgetItem(status.title() if status else "-")
            status_item.setFont(body_font(12, QFont.Weight.DemiBold))
            status_item.setForeground(QColor(Theme.success if status == "present" else Theme.danger))
            self.table.setItem(row, 5, status_item)

            login_time = item.get("login_time")
            if login_time:
                login_time = login_time.replace("T", " ").split("+")[0]
            self.table.setItem(row, 6, QTableWidgetItem(login_time or "-"))

            self.table.setItem(row, 7, QTableWidgetItem(item.get("session_info", "-")))

        self.table.resizeColumnsToContents()
        total = len(records)
        hour_label = self.hour_combo.currentText() if hour else "All periods"
        self.summary_label.setText(
            f"Subject: {subject_name} | Date: {date_str} | Hour: {hour_label} | Total: {total} | Present: {present_count} | Absent: {absent_count} | {self._format_last_sync_text(records)}"
        )

    def sync_attendance_to_etlab(self):
        subject_name = self.subject_combo.currentData() or ""
        date_str = self.date_combo.currentData() or ""
        hour = self.hour_combo.currentData() or ""

        if not subject_name:
            QMessageBox.information(self, "Subject Required", "Please select a subject.")
            return
        if not date_str:
            QMessageBox.information(self, "Date Required", "Please select a lab-session date.")
            return
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Load Attendance", "Please load the attendance list before syncing.")
            return

        self.sync_etlab_btn.setEnabled(False)
        try:
            result = api_client.sync_attendance_to_etlab(
                subject_name=subject_name,
                date=date_str,
                hour=hour if hour else None,
            )
        finally:
            self.sync_etlab_btn.setEnabled(True)

        if not result["success"]:
            QMessageBox.warning(self, "Sync Failed", f"Failed to sync attendance to ETLab:\n{result['error']}")
            return

        payload = result.get("data") or {}
        QMessageBox.information(
            self,
            "Sync Complete",
            (
                f"Attendance synced to ETLab.\n\n"
                f"Sessions: {payload.get('sessions_synced', payload.get('sessions_sent', 0))}\n"
                f"Records: {payload.get('records_synced', payload.get('records_sent', 0))}\n"
                f"Not Available: {payload.get('not_available_records', 0)}\n"
                f"Last Sync to ETLab: {self._format_sync_timestamp(payload.get('last_synced_to_etlab_at', ''))}"
            ),
        )
        self.load_attendance_for_selection()

    def sync_subject_attendance_to_etlab(self):
        subject_name = self.subject_combo.currentData() or ""
        if not subject_name:
            QMessageBox.information(self, "Subject Required", "Please select a subject.")
            return
        if not self.current_records:
            QMessageBox.information(self, "Load Attendance", "Please load one attendance session first.")
            return

        semester_ids = {
            item.get("semester_id")
            for item in self.current_records
            if item.get("semester_id") not in (None, "")
        }
        if not semester_ids:
            QMessageBox.warning(self, "Semester Missing", "Could not detect the semester from the loaded attendance.")
            return
        if len(semester_ids) > 1:
            QMessageBox.warning(self, "Multiple Semesters", "Loaded attendance contains multiple semesters. Please narrow the selection first.")
            return

        semester_id = next(iter(semester_ids))

        self.sync_subject_etlab_btn.setEnabled(False)
        try:
            result = api_client.sync_subject_attendance_to_etlab(
                subject_name=subject_name,
                semester_id=int(semester_id),
            )
        finally:
            self.sync_subject_etlab_btn.setEnabled(True)

        if not result["success"]:
            QMessageBox.warning(self, "Sync Failed", f"Failed to sync full subject attendance to ETLab:\n{result['error']}")
            return

        payload = result.get("data") or {}
        QMessageBox.information(
            self,
            "Bulk Sync Complete",
            (
                f"All recorded lab sessions for this subject and semester were synced to ETLab.\n\n"
                f"Sessions: {payload.get('sessions_synced', payload.get('sessions_sent', 0))}\n"
                f"Records: {payload.get('records_synced', payload.get('records_sent', 0))}\n"
                f"Not Available: {payload.get('not_available_records', 0)}\n"
                f"Last Sync to ETLab: {self._format_sync_timestamp(payload.get('last_synced_to_etlab_at', ''))}"
            ),
        )
        self.load_attendance_for_selection()

    def showEvent(self, event):
        super().showEvent(event)
        if self.subject_combo.count() <= 1:
            self.load_subjects()
