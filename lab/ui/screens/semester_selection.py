from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QLayout,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDateEdit,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt, QDate
from PyQt6.QtGui import QFont

from ui.common.cards import CardFrame
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


class SemesterSelectionScreen(QWidget):
    batch_selected = pyqtSignal(str, str, int, str, str, int)  # semester_name, batch_name, batch_id, subject_name, selected_date, selected_hour

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {Theme.background};")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(16)

        self.timetable_payload = {}
        self.weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.hours = [1, 2, 3, 4, 5, 6]
        self.slot_index = {}  # (day, hour) -> slot dict
        self.semester_lookup = {}  # sem_id -> {"name","number","batches","subjects"}
        self.selected_semester_id = None
        self.selected_semester_name = ""
        self.selected_subject_name = ""
        self.selected_date = None
        self.selected_hour = None
        self.subject_buttons = []
        self.showing_timetable = False

        header = QHBoxLayout()
        title = QLabel("Semester Selection")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        header.addWidget(title)
        header.addStretch()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("class", "secondary")
        self.refresh_btn.clicked.connect(self.load_semesters)
        header.addWidget(self.refresh_btn)
        self.main_layout.addLayout(header)

        subtitle = QLabel("Structured workflow: class -> subject -> date/hour -> batch")
        subtitle.setFont(body_font(13))
        subtitle.setStyleSheet(f"color: {Theme.text_muted};")
        self.main_layout.addWidget(subtitle)

        summary_card = CardFrame(padding=14, hoverable=False)
        summary_title = QLabel("Current Selection")
        summary_title.setFont(body_font(13, QFont.Weight.Bold))
        summary_title.setStyleSheet(f"color: {Theme.text_primary};")
        summary_card.layout.addWidget(summary_title)

        self.selection_summary = QLabel("Selection: -")
        self.selection_summary.setFont(body_font(12))
        self.selection_summary.setStyleSheet(
            f"color: {Theme.text_secondary}; padding: 8px 10px; background: {Theme.background}; border: 1px solid {Theme.border}; border-radius: 8px;"
        )
        summary_card.layout.addWidget(self.selection_summary)
        self.main_layout.addWidget(summary_card)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.main_layout.addWidget(self.scroll_area)

        self.content = QWidget()
        self.scroll_area.setWidget(self.content)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)

        timetable_block = CardFrame(padding=16, hoverable=False)
        timetable_title = QLabel("Weekly Timetable")
        timetable_title.setFont(body_font(14, QFont.Weight.Bold))
        timetable_title.setStyleSheet(f"color: {Theme.text_primary};")
        timetable_block.layout.addWidget(timetable_title)

        self.loading_label = QLabel("Loading faculty timetable...")
        self.loading_label.setFont(body_font(14))
        self.loading_label.setStyleSheet(f"color: {Theme.text_muted};")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timetable_block.layout.addWidget(self.loading_label)

        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(10)
        self.timetable_toggle_btn = QPushButton(">")
        self.timetable_toggle_btn.setFixedWidth(36)
        self.timetable_toggle_btn.setProperty("class", "secondary")
        self.timetable_toggle_btn.clicked.connect(self.toggle_timetable_visibility)
        toggle_row.addWidget(self.timetable_toggle_btn, 0)
        self.timetable_toggle_text = QLabel("Full Weekly Timetable")
        self.timetable_toggle_text.setFont(body_font(13, QFont.Weight.DemiBold))
        self.timetable_toggle_text.setStyleSheet(f"color: {Theme.text_primary};")
        toggle_row.addWidget(self.timetable_toggle_text)
        toggle_row.addStretch(1)
        timetable_block.layout.addLayout(toggle_row)

        self.timetable_card = CardFrame(padding=14, hoverable=False)
        self.timetable_table = QTableWidget(0, 0)
        self.timetable_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.timetable_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.timetable_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.timetable_table.setAlternatingRowColors(True)
        self.timetable_table.verticalHeader().setVisible(False)
        self.timetable_table.verticalHeader().setDefaultSectionSize(56)
        self.timetable_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.timetable_table.setMinimumHeight(360)
        self.timetable_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.timetable_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.timetable_card.layout.addWidget(self.timetable_table)
        self.timetable_card.hide()
        timetable_block.layout.addWidget(self.timetable_card)
        self.content_layout.addWidget(timetable_block)

        class_card = CardFrame(padding=20, hoverable=False)
        class_label = QLabel("Step 1 - Select Class (Semester)")
        class_label.setFont(body_font(14, QFont.Weight.Bold))
        class_label.setStyleSheet(f"color: {Theme.text_primary};")
        class_card.layout.addWidget(class_label)

        self.semester_combo = QComboBox()
        self.semester_combo.addItem("Select a semester...", None)
        self.semester_combo.currentIndexChanged.connect(self.on_semester_changed)
        class_card.layout.addWidget(self.semester_combo)
        self.content_layout.addWidget(class_card)

        subject_card = CardFrame(padding=20, hoverable=False)
        subject_label = QLabel("Step 2 - Select Subject")
        subject_label.setFont(body_font(14, QFont.Weight.Bold))
        subject_label.setStyleSheet(f"color: {Theme.text_primary};")
        subject_card.layout.addWidget(subject_label)

        self.subject_empty_label = QLabel("Choose a semester to view subjects.")
        self.subject_empty_label.setFont(body_font(12))
        self.subject_empty_label.setStyleSheet(f"color: {Theme.text_muted};")
        subject_card.layout.addWidget(self.subject_empty_label)

        self.subject_grid = QGridLayout()
        self.subject_grid.setSpacing(10)
        subject_card.layout.addLayout(self.subject_grid)
        self.content_layout.addWidget(subject_card)

        schedule_card = CardFrame(padding=20, hoverable=False)
        schedule_label = QLabel("Step 3 - Select Date and Hour")
        schedule_label.setFont(body_font(14, QFont.Weight.Bold))
        schedule_label.setStyleSheet(f"color: {Theme.text_primary};")
        schedule_card.layout.addWidget(schedule_label)

        self.schedule_hint = QLabel("Pick a date first. Available timetable hours for the selected subject will be shown.")
        self.schedule_hint.setFont(body_font(12))
        self.schedule_hint.setStyleSheet(f"color: {Theme.text_muted};")
        schedule_card.layout.addWidget(self.schedule_hint)

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.dateChanged.connect(self.on_date_changed)
        schedule_card.layout.addWidget(self.date_picker)

        self.date_hour_table = QTableWidget(0, 0)
        self.date_hour_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.date_hour_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.date_hour_table.setAlternatingRowColors(True)
        self.date_hour_table.verticalHeader().setVisible(False)
        self.date_hour_table.verticalHeader().setDefaultSectionSize(52)
        self.date_hour_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.date_hour_table.setMinimumHeight(420)
        self.date_hour_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.date_hour_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        schedule_card.layout.addWidget(self.date_hour_table)

        self.selected_slot_label = QLabel("No date/hour selected.")
        self.selected_slot_label.setFont(body_font(12, QFont.Weight.DemiBold))
        self.selected_slot_label.setStyleSheet(f"color: {Theme.info};")
        schedule_card.layout.addWidget(self.selected_slot_label)
        self.content_layout.addWidget(schedule_card)

        batch_card = CardFrame(padding=20, hoverable=False)
        batch_label = QLabel("Step 4 - Select Batch and Proceed")
        batch_label.setFont(body_font(14, QFont.Weight.Bold))
        batch_label.setStyleSheet(f"color: {Theme.text_primary};")
        batch_card.layout.addWidget(batch_label)

        self.batch_combo = QComboBox()
        self.batch_combo.addItem("Select a batch...", None)
        self.batch_combo.currentIndexChanged.connect(self._update_proceed_button_state)
        batch_card.layout.addWidget(self.batch_combo)

        proceed_row = QHBoxLayout()
        proceed_row.addStretch(1)
        self.proceed_btn = QPushButton("Proceed to Dashboard")
        self.proceed_btn.setProperty("class", "primary")
        self.proceed_btn.setEnabled(False)
        self.proceed_btn.clicked.connect(self.proceed_to_dashboard)
        proceed_row.addWidget(self.proceed_btn)
        batch_card.layout.addLayout(proceed_row)
        self.content_layout.addWidget(batch_card)

        self.content_layout.addStretch(1)
        self._apply_local_table_styles()

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

    def _apply_local_table_styles(self):
        table_style = f"""
            QTableWidget {{
                background: {Theme.card_bg};
                border: 1px solid {Theme.border};
                border-radius: 10px;
                gridline-color: {Theme.border_light};
                alternate-background-color: {Theme.background};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background: {Theme.background};
                color: {Theme.text_primary};
                border: none;
                border-bottom: 1px solid {Theme.border};
                font-weight: 700;
                padding: 10px 8px;
            }}
        """
        self.timetable_table.setStyleSheet(table_style)
        self.date_hour_table.setStyleSheet(table_style)

    def _update_summary(self):
        semester_txt = self.selected_semester_name or "-"
        subject_txt = self.selected_subject_name or "-"
        date_txt = self.selected_date.toString("yyyy-MM-dd") if self.selected_date else "-"
        hour_txt = f"P{self.selected_hour}" if self.selected_hour else "-"
        batch_txt = self.batch_combo.currentText() if self.batch_combo.currentData() else "-"
        self.selection_summary.setText(
            f"Selection: Semester {semester_txt} | Subject {subject_txt} | Date {date_txt} | Hour {hour_txt} | Batch {batch_txt}"
        )

    def load_semesters(self):
        self._clear_layout(self.subject_grid)
        self.subject_buttons.clear()
        self.selected_semester_id = None
        self.selected_semester_name = ""
        self.selected_subject_name = ""
        self.selected_date = None
        self.selected_hour = None
        self.selected_slot_label.setText("No date/hour selected.")
        self.schedule_hint.setText("Pick a date first. Available timetable hours for the selected subject will be shown.")
        self.proceed_btn.setEnabled(False)
        self.subject_empty_label.setText("Choose a semester to view subjects.")
        self.subject_empty_label.show()
        self.date_hour_table.clear()
        self.date_hour_table.setRowCount(0)
        self.date_hour_table.setColumnCount(0)
        self.batch_combo.clear()
        self.batch_combo.addItem("Select a batch...", None)
        self.semester_combo.clear()
        self.semester_combo.addItem("Select a semester...", None)
        self.timetable_table.clear()
        self.timetable_table.setRowCount(0)
        self.timetable_table.setColumnCount(0)
        self._update_summary()

        result = api_client.get_faculty_weekly_timetable()
        if not result["success"]:
            self._set_error(f"Failed to load faculty timetable:\n{result['error']}")
            return

        payload = result["data"] if isinstance(result.get("data"), dict) else {}
        slots = payload.get("slots", [])
        semesters = payload.get("semesters", [])

        if not slots or not semesters:
            self.loading_label.setText("No timetable slots assigned to this faculty")
            return

        self.loading_label.hide()
        self.timetable_payload = payload
        self.weekdays = payload.get("weekdays", self.weekdays)
        self.hours = payload.get("hours", self.hours)
        self.slot_index = {}
        self.semester_lookup = {}

        for sem in semesters:
            sem_id = sem.get("id")
            if not sem_id:
                continue
            self.semester_lookup[sem_id] = {
                "id": sem_id,
                "name": sem.get("name", f"Sem {sem.get('number', '')}").strip(),
                "number": sem.get("number", 0),
                "batches": sem.get("batches", []),
                "subjects": {},
            }

        for slot in slots:
            day = slot.get("day_of_week")
            hour = int(slot.get("hour_slot", 0) or 0)
            if day and hour:
                self.slot_index[(day, hour)] = slot

            semester = slot.get("semester", {})
            sem_id = semester.get("id")
            subject = slot.get("subject_name", "Unknown Subject")
            sem_data = self.semester_lookup.get(sem_id)
            if sem_data is None:
                continue
            sem_data["subjects"].setdefault(subject, []).append(slot)

        sorted_semesters = sorted(
            self.semester_lookup.values(),
            key=lambda sem: (sem.get("number", 999), sem.get("name", "")),
        )
        for sem in sorted_semesters:
            self.semester_combo.addItem(sem["name"], sem["id"])

        self.populate_timetable_table()

    def populate_timetable_table(self):
        column_headers = ["Day / Hour"] + [f"H{h}" for h in self.hours]
        self.timetable_table.setColumnCount(len(column_headers))
        self.timetable_table.setHorizontalHeaderLabels(column_headers)
        self.timetable_table.setRowCount(len(self.weekdays))

        for row, day in enumerate(self.weekdays):
            day_item = QTableWidgetItem(day)
            day_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            day_item.setFont(body_font(12, QFont.Weight.Bold))
            self.timetable_table.setItem(row, 0, day_item)

            for col, hour in enumerate(self.hours, start=1):
                slot = self.slot_index.get((day, int(hour)))
                if slot:
                    sem = slot.get("semester", {})
                    sem_name = sem.get("name", "")
                    text = f"{slot.get('subject_name', 'Unknown')}\n{sem_name}"
                else:
                    text = "Free"
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.timetable_table.setItem(row, col, item)

        self.timetable_table.resizeRowsToContents()

    def toggle_timetable_visibility(self):
        self.showing_timetable = not self.showing_timetable
        self.timetable_card.setVisible(self.showing_timetable)
        if self.showing_timetable:
            self.timetable_toggle_btn.setText("^")
        else:
            self.timetable_toggle_btn.setText(">")

    def on_semester_changed(self, _index: int):
        sem_id = self.semester_combo.currentData()
        self.selected_semester_id = sem_id
        self.selected_semester_name = ""
        self.selected_subject_name = ""
        self.selected_date = None
        self.selected_hour = None
        self.selected_slot_label.setText("No date/hour selected.")
        self.batch_combo.clear()
        self.batch_combo.addItem("Select a batch...", None)
        self._clear_layout(self.subject_grid)
        self.subject_buttons.clear()
        self.subject_empty_label.show()
        self._update_summary()

        if not sem_id:
            self.subject_empty_label.setText("Choose a semester to view subjects.")
            self.schedule_hint.setText("Pick a date first. Available timetable hours for the selected subject will be shown.")
            self.date_hour_table.clear()
            self.date_hour_table.setRowCount(0)
            self.date_hour_table.setColumnCount(0)
            self._update_proceed_button_state()
            return

        sem_data = self.semester_lookup.get(sem_id)
        if sem_data is None:
            self.subject_empty_label.setText("Semester data unavailable.")
            self._update_proceed_button_state()
            return

        self.selected_semester_name = sem_data.get("name", "")
        subjects = sorted(sem_data.get("subjects", {}).keys())
        if not subjects:
            self.subject_empty_label.setText("No subjects mapped for this semester.")
        else:
            self.subject_empty_label.hide()

        row = col = 0
        for subject_name in subjects:
            btn = QPushButton(subject_name)
            btn.setStyleSheet(self._subject_btn_style(selected=False))
            btn.clicked.connect(lambda checked, s=subject_name: self.on_subject_selected(s))
            self.subject_grid.addWidget(btn, row, col)
            self.subject_buttons.append((subject_name, btn))
            col += 1
            if col == 3:
                col = 0
                row += 1

        for batch in sorted(sem_data.get("batches", []), key=lambda b: b.get("name", "")):
            batch_name = batch.get("name", "Batch")
            batch_id = batch.get("id")
            if batch_id:
                self.batch_combo.addItem(batch_name, batch_id)

        self.on_date_changed(self.date_picker.date())
        self._update_proceed_button_state()
        self._update_summary()

    def _subject_btn_style(self, selected: bool):
        if selected:
            return f"""
                QPushButton {{
                    background: {Theme.primary};
                    color: white;
                    border: 1px solid {Theme.primary};
                    border-radius: 8px;
                    padding: 10px 14px;
                    font-weight: 700;
                    font-size: 13px;
                }}
            """
        return f"""
            QPushButton {{
                background: {Theme.card_bg};
                color: {Theme.text_primary};
                border: 1px solid {Theme.border};
                border-radius: 8px;
                padding: 10px 14px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {Theme.primary};
                background: {Theme.background};
            }}
        """

    def on_subject_selected(self, subject_name: str):
        self.selected_subject_name = subject_name
        self.selected_date = None
        self.selected_hour = None
        self.selected_slot_label.setText("No date/hour selected.")

        for name, btn in self.subject_buttons:
            btn.setStyleSheet(self._subject_btn_style(selected=(name == subject_name)))

        self.schedule_hint.setText(f"Selected subject: {subject_name}. Choose date and click Select under available hour.")
        self.refresh_date_hour_table()
        self._update_proceed_button_state()
        self._update_summary()

    def on_date_changed(self, _date: QDate):
        if self.selected_date and self.selected_date != self.date_picker.date():
            self.selected_date = None
            self.selected_hour = None
            self.selected_slot_label.setText("No date/hour selected.")
        self.refresh_date_hour_table()
        self._update_proceed_button_state()
        self._update_summary()

    def refresh_date_hour_table(self):
        headers = ["Date", "Day"] + [f"P{h}" for h in self.hours]
        self.date_hour_table.clear()
        self.date_hour_table.setColumnCount(len(headers))
        self.date_hour_table.setHorizontalHeaderLabels(headers)
        self.date_hour_table.setRowCount(7)

        base_date = self.date_picker.date()
        week_start = base_date.addDays(1 - base_date.dayOfWeek())  # Monday

        for row in range(7):
            date = week_start.addDays(row)
            day_name = date.toString("dddd")

            date_item = QTableWidgetItem(date.toString("MMMM d, yyyy"))
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.date_hour_table.setItem(row, 0, date_item)

            day_item = QTableWidgetItem(day_name)
            day_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.date_hour_table.setItem(row, 1, day_item)

            for col, hour in enumerate(self.hours, start=2):
                cell_slot = self._get_subject_slot_for(self.selected_semester_id, self.selected_subject_name, day_name, int(hour))
                if cell_slot is None:
                    dash_item = QTableWidgetItem("—")
                    dash_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.date_hour_table.setItem(row, col, dash_item)
                    continue

                btn = QPushButton("Select")
                btn.setStyleSheet(self._slot_button_style(
                    selected=(
                        self.selected_date is not None
                        and self.selected_hour is not None
                        and self.selected_date == date
                        and self.selected_hour == int(hour)
                    )
                ))
                btn.clicked.connect(lambda checked, d=date, h=int(hour): self.select_date_hour(d, h))
                self.date_hour_table.setCellWidget(row, col, btn)

        self.date_hour_table.resizeRowsToContents()

    def _slot_button_style(self, selected: bool):
        color = Theme.success if selected else Theme.primary
        hover = "#059669" if selected else Theme.primary_hover
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
        """

    def _get_subject_slot_for(self, semester_id: int, subject_name: str, day_name: str, hour: int):
        if not semester_id or not subject_name:
            return None

        sem_data = self.semester_lookup.get(semester_id)
        if sem_data is None:
            return None

        subject_slots = sem_data.get("subjects", {}).get(subject_name, [])
        for slot in subject_slots:
            if slot.get("day_of_week") == day_name and int(slot.get("hour_slot", 0) or 0) == hour:
                return slot
        return None

    def select_date_hour(self, date: QDate, hour: int):
        self.selected_date = date
        self.selected_hour = hour
        self.selected_slot_label.setText(
            f"Selected: {date.toString('MMMM d, yyyy')} ({date.toString('dddd')}) - Hour P{hour}"
        )
        self.refresh_date_hour_table()
        self._update_proceed_button_state()
        self._update_summary()

    def _update_proceed_button_state(self):
        has_batch = self.batch_combo.currentData() is not None
        ready = (
            bool(self.selected_semester_id)
            and bool(self.selected_subject_name)
            and self.selected_date is not None
            and self.selected_hour is not None
            and has_batch
        )
        self.proceed_btn.setEnabled(ready)
        self._update_summary()

    def proceed_to_dashboard(self):
        batch_id = self.batch_combo.currentData()
        if not batch_id:
            QMessageBox.information(self, "Batch Required", "Please select a batch.")
            return
        if self.selected_date is None or self.selected_hour is None:
            QMessageBox.information(self, "Date/Hour Required", "Please select date and hour.")
            return

        batch_name = self.batch_combo.currentText()
        self.batch_selected.emit(
            self.selected_semester_name,
            batch_name,
            int(batch_id),
            self.selected_subject_name,
            self.selected_date.toString("yyyy-MM-dd"),
            int(self.selected_hour),
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.load_semesters()

