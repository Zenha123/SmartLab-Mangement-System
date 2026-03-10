from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTabWidget,
    QTableWidgetItem,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QComboBox,
    QGridLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


class ReportsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window = parent
        self.attendance_data = []
        self.semester_map = {}
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("📄 Reports")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # Action buttons
        actions_card = CardFrame(padding=16)
        actions = QHBoxLayout()
        actions.setSpacing(12)
        
        refresh_btn = QPushButton("🔄 Refresh Data")
        refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.secondary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: #16A085;
            }}
            """
        )
        refresh_btn.clicked.connect(self.load_reports)
        
        actions.addWidget(refresh_btn)
        actions.addStretch()
        actions_card.layout.addLayout(actions)
        root.addWidget(actions_card)

        # Tabs
        self.tabs = QTabWidget()
        self.attendance_tab_widget = self._create_attendance_tab()
        self.tabs.addTab(self.attendance_tab_widget, "📊 Attendance")
        self.tabs.addTab(self._generic_tab("Viva Marks"), "🎤 Viva Marks")
        self.tabs.addTab(self._generic_tab("Task Submissions"), "📝 Submissions")
        root.addWidget(self.tabs)
        root.addStretch(1)
    
    def _create_attendance_tab(self):
        """Create attendance report tab"""
        widget = CardFrame(padding=20)

        filters_layout = QGridLayout()
        filters_layout.setHorizontalSpacing(12)
        filters_layout.setVerticalSpacing(8)

        sem_lbl = QLabel("Semester")
        sem_lbl.setFont(body_font(12, QFont.Weight.DemiBold))
        filters_layout.addWidget(sem_lbl, 0, 0)
        self.semester_combo = QComboBox()
        self.semester_combo.addItem("Select semester...", None)
        self.semester_combo.currentIndexChanged.connect(self.on_semester_changed)
        filters_layout.addWidget(self.semester_combo, 1, 0)

        subject_lbl = QLabel("Subject")
        subject_lbl.setFont(body_font(12, QFont.Weight.DemiBold))
        filters_layout.addWidget(subject_lbl, 0, 1)
        self.subject_combo = QComboBox()
        self.subject_combo.addItem("Select subject...", "")
        filters_layout.addWidget(self.subject_combo, 1, 1)

        self.attendance_load_btn = QPushButton("Show Attendance Report")
        self.attendance_load_btn.clicked.connect(self.load_attendance_report)
        filters_layout.addWidget(self.attendance_load_btn, 1, 2)

        widget.layout.addLayout(filters_layout)

        self.attendance_summary_label = QLabel("Select semester and subject to view attendance percentage.")
        self.attendance_summary_label.setFont(body_font(12))
        self.attendance_summary_label.setStyleSheet(
            f"color: {Theme.text_secondary}; padding: 8px 12px; background: {Theme.background}; border-radius: 8px;"
        )
        widget.layout.addWidget(self.attendance_summary_label)

        self.attendance_table = StyledTableWidget(0, 5)
        self.attendance_table.setHorizontalHeaderLabels([
            "Student Name",
            "Student ID",
            "Present / Total",
            "Attendance %",
            "Batch",
        ])
        widget.layout.addWidget(self.attendance_table)
        return widget
    
    def load_reports(self):
        """Load attendance filter data and refresh report if filters are selected."""
        timetable_result = api_client.get_faculty_weekly_timetable()
        if not timetable_result["success"]:
            QMessageBox.warning(self, "Error", f"Failed to load timetable filters:\n{timetable_result['error']}")
            return

        payload = timetable_result.get("data") if isinstance(timetable_result.get("data"), dict) else {}
        semesters = payload.get("semesters", [])
        slots = payload.get("slots", [])

        self.semester_map = {}
        for sem in semesters:
            sem_id = sem.get("id")
            if not sem_id:
                continue
            self.semester_map[sem_id] = {
                "id": sem_id,
                "name": sem.get("name", "Semester"),
                "number": sem.get("number", 0),
                "batches": sem.get("batches", []),
                "subjects": set(),
            }

        for slot in slots:
            sem = slot.get("semester", {})
            sem_id = sem.get("id")
            subject = (slot.get("subject_name") or "").strip()
            if sem_id in self.semester_map and subject:
                self.semester_map[sem_id]["subjects"].add(subject)

        previous_sem_id = self.semester_combo.currentData() if hasattr(self, "semester_combo") else None
        self.semester_combo.blockSignals(True)
        self.semester_combo.clear()
        self.semester_combo.addItem("Select semester...", None)
        for sem in sorted(self.semester_map.values(), key=lambda s: (s["number"], s["name"])):
            self.semester_combo.addItem(sem["name"], sem["id"])
        self.semester_combo.blockSignals(False)

        if previous_sem_id in self.semester_map:
            idx = self.semester_combo.findData(previous_sem_id)
            if idx >= 0:
                self.semester_combo.setCurrentIndex(idx)
                self.on_semester_changed(idx)
                if self.subject_combo.currentData():
                    self.load_attendance_report()
            return

        self.on_semester_changed(self.semester_combo.currentIndex())

    def on_semester_changed(self, _index: int):
        sem_id = self.semester_combo.currentData()
        self.subject_combo.clear()
        self.subject_combo.addItem("Select subject...", "")
        self.attendance_table.setRowCount(0)

        if not sem_id or sem_id not in self.semester_map:
            self.attendance_summary_label.setText("Select semester and subject to view attendance percentage.")
            return

        subjects = sorted(self.semester_map[sem_id]["subjects"])
        for subject in subjects:
            self.subject_combo.addItem(subject, subject)

        if subjects:
            self.attendance_summary_label.setText("Select a subject and click 'Show Attendance Report'.")
        else:
            self.attendance_summary_label.setText("No subjects found for selected semester.")

    def load_attendance_report(self):
        sem_id = self.semester_combo.currentData()
        subject_name = (self.subject_combo.currentData() or "").strip()

        if not sem_id:
            QMessageBox.information(self, "Semester Required", "Please select a semester.")
            return
        if not subject_name:
            QMessageBox.information(self, "Subject Required", "Please select a subject.")
            return

        sem_data = self.semester_map.get(sem_id)
        if not sem_data:
            QMessageBox.warning(self, "Error", "Semester metadata not available.")
            return

        attendance_result = api_client.get_semester_attendance(semester_id=int(sem_id), subject_name=subject_name)
        if not attendance_result["success"]:
            QMessageBox.warning(self, "Error", f"Failed to load attendance report:\n{attendance_result['error']}")
            return

        records = attendance_result.get("data") or []
        session_ids = {r.get("session") for r in records if r.get("session")}
        total_sessions = len(session_ids)

        students_by_id = {}
        for batch in sem_data.get("batches", []):
            batch_id = batch.get("id")
            if not batch_id:
                continue
            students_result = api_client.get_students(batch_id=batch_id)
            if not students_result["success"]:
                continue
            for st in students_result.get("data") or []:
                sid = st.get("id")
                if not sid:
                    continue
                students_by_id[sid] = {
                    "id": sid,
                    "name": st.get("name", "Unknown"),
                    "student_id": st.get("student_id", "N/A"),
                    "batch_name": st.get("batch_name", "-"),
                }

        present_counts = {}
        for rec in records:
            sid = rec.get("student")
            if not sid:
                continue
            if rec.get("status") == "present":
                present_counts[sid] = present_counts.get(sid, 0) + 1

        sorted_students = sorted(students_by_id.values(), key=lambda s: s["name"].lower())
        self.attendance_table.setRowCount(len(sorted_students))

        total_present_marks = 0
        for row, student in enumerate(sorted_students):
            sid = student["id"]
            present = present_counts.get(sid, 0)
            total_present_marks += present
            percentage = (present / total_sessions * 100.0) if total_sessions > 0 else 0.0

            name_item = QTableWidgetItem(student["name"])
            name_item.setFont(body_font(12, QFont.Weight.Medium))
            self.attendance_table.setItem(row, 0, name_item)
            self.attendance_table.setItem(row, 1, QTableWidgetItem(student["student_id"]))
            self.attendance_table.setItem(row, 2, QTableWidgetItem(f"{present}/{total_sessions}"))

            pct_item = QTableWidgetItem(f"{percentage:.1f}%")
            pct_item.setFont(body_font(12, QFont.Weight.DemiBold))
            pct_item.setForeground(QColor(Theme.success if percentage >= 75 else Theme.warning if percentage >= 50 else Theme.danger))
            self.attendance_table.setItem(row, 3, pct_item)
            self.attendance_table.setItem(row, 4, QTableWidgetItem(student["batch_name"]))

        self.attendance_table.resizeColumnsToContents()

        student_count = len(sorted_students)
        denominator = student_count * total_sessions
        overall_percentage = (total_present_marks / denominator * 100.0) if denominator > 0 else 0.0
        self.attendance_summary_label.setText(
            f"Semester: {sem_data['name']} | Subject: {subject_name} | Students: {student_count} | Sessions: {total_sessions} | Overall Present: {overall_percentage:.1f}%"
        )

    def _generic_tab(self, title: str):
        """Create generic placeholder tab"""
        widget = CardFrame(padding=40)
        placeholder = QLabel(f"📋 {title} Report\n\nThis section will display {title.lower()} data.\nData will be loaded from backend when available.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(body_font(14))
        placeholder.setStyleSheet(f"color: {Theme.text_muted};")
        placeholder.setWordWrap(True)
        widget.layout.addWidget(placeholder)
        return widget
    
    def showEvent(self, event):
        """Load reports when screen is shown"""
        super().showEvent(event)
        self.load_reports()

