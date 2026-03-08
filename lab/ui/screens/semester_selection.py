from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout, QMessageBox, QLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from ui.common.cards import CardFrame
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


class SemesterSelectionScreen(QWidget):
    batch_selected = pyqtSignal(str, str, int, str)  # semester_name, batch_name, batch_id, subject_name

    def __init__(self):

        super().__init__()
        # Set background color
        self.setStyleSheet(f"background: {Theme.background};")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)

        title = QLabel("📚 Weekly Timetable")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        self.main_layout.addWidget(title)
        
        subtitle = QLabel("Pick a timetable slot, then choose a batch under that semester")
        subtitle.setFont(body_font(13))
        subtitle.setStyleSheet(f"color: {Theme.text_muted}; margin-bottom: 20px;")
        self.main_layout.addWidget(subtitle)

        # Loading label
        self.loading_label = QLabel("🔄 Loading faculty timetable...")
        self.loading_label.setFont(body_font(14))
        self.loading_label.setStyleSheet(f"color: {Theme.text_muted};")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.loading_label)

        self.slot_grid = QGridLayout()
        self.slot_grid.setSpacing(16)
        self.main_layout.addLayout(self.slot_grid)

        self.batch_header = QLabel("")
        self.batch_header.setFont(heading_font(16, bold=True))
        self.batch_header.setStyleSheet(f"color: {Theme.primary}; margin-top: 8px;")
        self.batch_header.hide()
        self.main_layout.addWidget(self.batch_header)

        self.batch_layout = QGridLayout()
        self.batch_layout.setSpacing(12)
        self.main_layout.addLayout(self.batch_layout)

        self.timetable_payload = {}
        self.semester_batches = {}

        self.main_layout.addStretch(1)

    def _clear_layout(self, layout: QLayout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_layout(child_layout)

    def _set_error(self, text: str):
        self.loading_label.setText(f"❌ {text}")
        self.loading_label.show()
        QMessageBox.warning(self, "Error", text)

    def load_semesters(self):
        """Load faculty weekly timetable and map semesters to batches."""
        self._clear_layout(self.slot_grid)
        self._clear_layout(self.batch_layout)
        self.batch_header.hide()

        result = api_client.get_faculty_weekly_timetable()
        if not result["success"]:
            self._set_error(f"Failed to load faculty timetable:\n{result['error']}")
            return

        payload = result["data"] if isinstance(result.get("data"), dict) else {}
        slots = payload.get("slots", [])
        semesters = payload.get("semesters", [])

        if not slots:
            self.loading_label.setText("No timetable slots assigned to this faculty")
            return

        self.loading_label.hide()
        self.timetable_payload = payload
        self.semester_batches = {
            sem.get("id"): {
                "name": sem.get("name", f"Sem {sem.get('number', '')}").strip(),
                "batches": sem.get("batches", []),
            }
            for sem in semesters
            if sem.get("id")
        }

        grouped_by_day = {}
        for slot in slots:
            day = slot.get("day_of_week", "Unknown")
            grouped_by_day.setdefault(day, []).append(slot)

        weekday_order = {d: i for i, d in enumerate(payload.get("weekdays", []), start=1)}
        sorted_days = sorted(grouped_by_day.keys(), key=lambda d: weekday_order.get(d, 99))

        row = 0
        for day in sorted_days:
            day_slots = sorted(grouped_by_day[day], key=lambda s: int(s.get("hour_slot", 0)))
            card = CardFrame(padding=20, hoverable=True)
            card.layout.setSpacing(10)

            day_lbl = QLabel(day)
            day_lbl.setFont(heading_font(16, bold=True))
            day_lbl.setStyleSheet(f"color: {Theme.primary}; margin-bottom: 6px;")
            card.layout.addWidget(day_lbl)

            buttons_row = QHBoxLayout()
            buttons_row.setSpacing(10)
            for slot in day_slots:
                semester = slot.get("semester", {})
                sem_id = semester.get("id")
                sem_name = semester.get("name", "Unknown Semester")
                subject = slot.get("subject_name", "Unknown Subject")
                hour = slot.get("hour_slot", "")
                button_text = f"H{hour}: {subject} ({sem_name})"

                btn = QPushButton(button_text)
                btn.setProperty("class", "secondary")
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background: {Theme.secondary};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 10px 16px;
                        font-weight: 600;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background: #16A085;
                    }}
                    """
                )
                btn.clicked.connect(
                    lambda checked, sid=sem_id, sname=sem_name, subj=subject:
                    self.show_batches_for_semester(sid, sname, subj)
                )
                buttons_row.addWidget(btn)

            buttons_row.addStretch()
            card.layout.addLayout(buttons_row)
            self.slot_grid.addWidget(card, row, 0)
            row += 1

    def show_batches_for_semester(self, semester_id: int, semester_name: str, subject_name: str):
        self._clear_layout(self.batch_layout)

        sem_data = self.semester_batches.get(semester_id)
        if not sem_data:
            QMessageBox.information(self, "No Batches", f"No batches found for {semester_name}.")
            self.batch_header.hide()
            return

        batches = sem_data.get("batches", [])
        if not batches:
            QMessageBox.information(self, "No Batches", f"No batches found for {semester_name}.")
            self.batch_header.hide()
            return

        self.batch_header.setText(f"Select Batch: {semester_name} - {subject_name}")
        self.batch_header.show()

        row = col = 0
        for batch in sorted(batches, key=lambda b: b.get("name", "")):
            batch_name = batch.get("name", "Batch")
            batch_id = batch.get("id")
            if not batch_id:
                continue

            btn = QPushButton(f"📦 {batch_name}")
            btn.setProperty("class", "secondary")
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background: {Theme.secondary};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 18px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: #16A085;
                }}
                """
            )
            btn.clicked.connect(
                lambda checked, s=semester_name, b=batch_name, bid=batch_id, subj=subject_name:
                self.batch_selected.emit(s, b, bid, subj)
            )
            self.batch_layout.addWidget(btn, row, col)

            col += 1
            if col == 4:
                col = 0
                row += 1

    def showEvent(self, event):
        """Load timetable each time this screen is shown."""
        super().showEvent(event)
        self.load_semesters()

