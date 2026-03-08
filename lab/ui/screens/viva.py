# lab/ui/screens/viva.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QHBoxLayout, QLineEdit, QPushButton, QTextEdit,
    QFrame, QSplitter, QComboBox, QDateTimeEdit, QScrollArea,
    QGridLayout
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont, QColor

from ui.common.cards import CardFrame
from ui.common.styled_dialogs import info, success, warning, error, confirm  # ← replaces QMessageBox
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client
from ui.common.websocket_client import FacultyWebSocketClient


class VivaScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window          = parent
        self.students               = []
        self.viva_records           = []
        self.current_record         = None
        self.current_viva_session_id= None
        self.ws_client              = None
        self.student_items          = {}   # student_id → QListWidgetItem

        # ── Scrollable root ───────────────────────────────────
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(24, 24, 24, 24)
        self.scroll_layout.setSpacing(30)

        title = QLabel("🎤 Viva Module")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary};")
        self.scroll_layout.addWidget(title)

        # ═══════════════════════════════════════════════════════
        # SECTION 1 — Offline Viva
        # ═══════════════════════════════════════════════════════
        self.offline_card = CardFrame(padding=0)
        offline_v = self.offline_card.layout

        off_title_lbl = QLabel("Offline Viva Session")
        off_title_lbl.setFont(heading_font(18, bold=True))
        off_title_lbl.setStyleSheet(
            f"padding: 20px; color: {Theme.text_primary}; "
            f"border-bottom: 1px solid {Theme.border};"
        )
        offline_v.addWidget(off_title_lbl)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet(
            "QSplitter::handle { background-color: #e5e7eb; width: 1px; }"
        )

        # Left: Student list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(15, 15, 15, 15)

        self.student_list = QListWidget()
        self.student_list.setStyleSheet(f"""
            QListWidget {{ border: none; background: white; }}
            QListWidget::item {{
                padding: 10px; border-bottom: 1px solid #f3f4f6;
            }}
            QListWidget::item:selected {{
                background: {Theme.primary}10; color: black;
                border-left: 5px solid {Theme.primary};
            }}
        """)
        self.student_list.itemSelectionChanged.connect(self.on_student_selected)
        left_layout.addWidget(self.student_list)

        # Right: Evaluation form
        self.right_panel = QWidget()
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        self.form_instruct = QLabel("Select a student to begin evaluation")
        self.form_instruct.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.form_instruct.setStyleSheet(
            f"color: {Theme.text_muted}; margin-top: 50px;"
        )

        self.evaluation_form = QWidget()
        form_v = QVBoxLayout(self.evaluation_form)
        form_v.setContentsMargins(0, 0, 0, 0)

        self.active_student_lbl = QLabel("Student Name")
        self.active_student_lbl.setFont(body_font(16, QFont.Weight.Bold))

        self.marks_input = QLineEdit()
        self.marks_input.setPlaceholderText("Marks (0-100)")
        self.marks_input.setFixedHeight(45)
        self.marks_input.setStyleSheet(
            f"border: 1px solid {Theme.border}; border-radius: 8px; padding: 10px;"
        )

        self.feedback_input = QTextEdit()
        self.feedback_input.setPlaceholderText("Feedback textarea")
        self.feedback_input.setMinimumHeight(150)
        self.feedback_input.setStyleSheet(
            f"border: 1px solid {Theme.border}; border-radius: 8px; padding: 10px;"
        )

        self.save_btn = QPushButton("Save & Next Student")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.success}; color: white;
                border-radius: 8px; padding: 12px;
                font-weight: bold; font-size: 14px;
            }}
            QPushButton:hover {{ background: #059669; }}
        """)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_evaluation)

        self.publish_offline_btn = QPushButton("Publish Offline Results")
        self.publish_offline_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.primary}; color: white;
                border-radius: 8px; padding: 12px;
                font-weight: bold; font-size: 14px;
            }}
            QPushButton:hover {{ background: #1d4ed8; }}
        """)
        self.publish_offline_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.publish_offline_btn.clicked.connect(self.publish_offline_results)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.publish_offline_btn)

        form_v.addWidget(self.active_student_lbl)
        form_v.addWidget(QLabel("Marks (0-100):"))
        form_v.addWidget(self.marks_input)
        form_v.addWidget(QLabel("Feedback:"))
        form_v.addWidget(self.feedback_input)
        form_v.addStretch()
        form_v.addLayout(buttons_layout)

        right_layout.addWidget(self.form_instruct)
        right_layout.addWidget(self.evaluation_form)
        self.evaluation_form.hide()

        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        offline_v.addWidget(self.splitter)
        self.scroll_layout.addWidget(self.offline_card)

        # ═══════════════════════════════════════════════════════
        # SECTION 2 — Online Viva
        # ═══════════════════════════════════════════════════════
        self.online_card = CardFrame(padding=24)
        online_v = self.online_card.layout

        on_title_lbl = QLabel("Online Viva Session")
        on_title_lbl.setFont(heading_font(18, bold=True))
        on_title_lbl.setStyleSheet(
            f"color: {Theme.text_primary}; margin-bottom: 20px;"
        )
        online_v.addWidget(on_title_lbl)

        on_grid = QGridLayout()
        on_grid.setSpacing(15)

        on_grid.addWidget(QLabel("Platform Name:"), 0, 0)
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Quizizz", "Kahoot", "Google Meet", "Custom"])
        on_grid.addWidget(self.platform_combo, 0, 1)

        on_grid.addWidget(QLabel("Join Code:"), 1, 0)
        self.join_code_input = QLineEdit()
        self.join_code_input.setPlaceholderText("Text input")
        on_grid.addWidget(self.join_code_input, 1, 1)

        on_grid.addWidget(QLabel("Join Link:"), 2, 0)
        self.join_link_input = QLineEdit()
        self.join_link_input.setPlaceholderText("URL input")
        on_grid.addWidget(self.join_link_input, 2, 1)

        on_grid.addWidget(QLabel("Start Time:"), 3, 0)
        self.start_time_input = QDateTimeEdit(QDateTime.currentDateTime())
        on_grid.addWidget(self.start_time_input, 3, 1)

        on_grid.addWidget(QLabel("Instructions:"), 4, 0)
        self.on_instructions = QTextEdit()
        self.on_instructions.setPlaceholderText("Textarea optional")
        self.on_instructions.setMaximumHeight(80)
        on_grid.addWidget(self.on_instructions, 4, 1)

        online_v.addLayout(on_grid)

        self.publish_btn = QPushButton("Publish Viva")
        self.publish_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.primary}; color: white;
                border-radius: 8px; padding: 15px;
                font-weight: bold; font-size: 15px; margin-top: 10px;
            }}
            QPushButton:hover {{ background: #1d4ed8; }}
        """)
        self.publish_btn.clicked.connect(self.publish_online_viva)
        online_v.addWidget(self.publish_btn)

        self.scroll_layout.addWidget(self.online_card)
        self.scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    # ── Lifecycle ─────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self.sync_offline_session()

    def hideEvent(self, event):
        if self.ws_client:
            self.ws_client.stop()
            self.ws_client = None
        super().hideEvent(event)

    # ── Session sync ──────────────────────────────────────────

    def sync_offline_session(self):
        if not hasattr(self.parent_window, 'current_batch_id') or \
                self.parent_window.current_batch_id is None:
            return

        batch_id = self.parent_window.current_batch_id
        self.load_records()

        if not self.ws_client:
            token = api_client.access_token
            if token:
                self.ws_client = FacultyWebSocketClient(batch_id, token)
                self.ws_client.student_status_signal.connect(self.handle_status_update)
                self.ws_client.start()

        try:
            res = api_client.get(
                f"viva-sessions/?batch={batch_id}&viva_type=offline")
            if res.status_code == 200:
                sessions = res.json()
                if sessions:
                    self.current_viva_session_id = sessions[0]['id']
                else:
                    create_res = api_client.post("viva-sessions/", {
                        "batch":      batch_id,
                        "subject":    "General Viva",
                        "viva_type":  "offline",
                    })
                    if create_res.status_code == 201:
                        self.current_viva_session_id = create_res.json()['id']
                self.load_records()
        except Exception as e:
            print(f"Error syncing offline session: {e}")

    def handle_status_update(self, data):
        student_id = data.get('student_id')
        status     = data.get('status')
        if student_id in self.student_items:
            item   = self.student_items[student_id]
            widget = self.student_list.itemWidget(item)
            dot    = widget.findChild(QLabel, "presenceDot")
            if dot:
                color = "#10B981" if status == 'online' else "#D1D5DB"
                dot.setStyleSheet(f"background: {color}; border-radius: 5px;")

    # ── Data loading ──────────────────────────────────────────

    def load_records(self):
        batch_id = self.parent_window.current_batch_id
        if not batch_id:
            return

        try:
            res_stud = api_client.get(f"students/?batch={batch_id}")
            if res_stud.status_code == 200:
                data = res_stud.json()
                self.students = (data.get('results', data)
                                 if isinstance(data, dict) else data)
        except Exception as e:
            print(f"Error fetching students: {e}")
            self.students = []

        if self.current_viva_session_id:
            try:
                res = api_client.get(
                    f"viva/?viva_session={self.current_viva_session_id}")
                if res.status_code == 200:
                    data = res.json()
                    self.viva_records = (data.get('results', data)
                                         if isinstance(data, dict) else data)
            except Exception as e:
                print(f"Error fetching viva records: {e}")
                self.viva_records = []

        self.populate_student_list()

    def populate_student_list(self):
        self.student_list.clear()
        self.student_items = {}
        record_map = {rec['student']: rec for rec in self.viva_records}
        for student in self.students:
            rec = record_map.get(student['id'])
            self.add_student_item(student, rec)

    def add_student_item(self, student, rec):
        name       = student.get('name', 'Unknown')
        roll       = student.get('register_number', 'N/A')
        student_id = student.get('id')

        status = marks = notes = ''
        if rec:
            status = rec.get('status', 'waiting')
            marks  = rec.get('marks', '')
            notes  = rec.get('notes', '')

        item_data = {
            'student_id':   student_id,
            'student_name': name,
            'student_roll': roll,
            'status':       status or 'waiting',
            'marks':        marks,
            'notes':        notes,
        }

        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, item_data)

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)

        text_container = QWidget()
        text_v = QVBoxLayout(text_container)
        text_v.setContentsMargins(0, 0, 0, 0)
        text_v.setSpacing(2)

        top_row = QWidget()
        top_h   = QHBoxLayout(top_row)
        top_h.setContentsMargins(0, 0, 0, 0)
        top_h.setSpacing(8)

        presence_dot = QLabel()
        presence_dot.setFixedSize(10, 10)
        presence_dot.setObjectName("presenceDot")
        presence_dot.setStyleSheet("background: #D1D5DB; border-radius: 5px;")

        roll_lbl = QLabel(roll)
        roll_lbl.setFont(body_font(10, QFont.Weight.Bold))
        roll_lbl.setStyleSheet(f"color: {Theme.text_muted};")

        top_h.addWidget(presence_dot)
        top_h.addWidget(roll_lbl)
        top_h.addStretch()

        name_lbl = QLabel(name)
        name_lbl.setFont(body_font(13, QFont.Weight.Medium))
        name_lbl.setStyleSheet("color: #111827;")
        name_lbl.setWordWrap(True)

        text_v.addWidget(top_row)
        text_v.addWidget(name_lbl)

        layout.addWidget(text_container)
        layout.addStretch()

        self.student_items[student_id] = item

        is_waiting  = (status or 'waiting') == 'waiting'
        badge_color = "#EAB308" if is_waiting else "#10B981"
        badge_text  = "Not Evaluated" if is_waiting else "Evaluated ✓"
        badge = QLabel(badge_text)
        badge.setStyleSheet(f"""
            background: {badge_color}; color: white;
            border-radius: 4px; padding: 4px 10px;
            font-size: 11px; font-weight: bold;
        """)
        badge.setObjectName("statusBadge")
        layout.addWidget(badge)

        item.setSizeHint(widget.sizeHint())
        self.student_list.addItem(item)
        self.student_list.setItemWidget(item, widget)

    # ── Student selection ─────────────────────────────────────

    def on_student_selected(self):
        items = self.student_list.selectedItems()
        if not items:
            return
        rec = items[0].data(Qt.ItemDataRole.UserRole)
        self.current_record = rec

        self.form_instruct.hide()
        self.evaluation_form.show()

        self.active_student_lbl.setText(rec.get('student_name', ''))
        self.marks_input.setText(str(rec.get('marks') or ""))
        self.feedback_input.setText(rec.get('notes') or "")
        self.marks_input.setFocus()

    # ── Offline session guard ─────────────────────────────────

    def _ensure_offline_session(self) -> bool:
        if self.current_viva_session_id:
            return True
        if not hasattr(self.parent_window, 'current_batch_id') or \
                not self.parent_window.current_batch_id:
            warning(self, "No Batch", "Please select a batch first.")
            return False
        batch_id = self.parent_window.current_batch_id
        try:
            res = api_client.get(
                f"viva-sessions/?batch={batch_id}&viva_type=offline")
            if res.status_code == 200:
                data     = res.json()
                sessions = (data.get('results', data)
                            if isinstance(data, dict) else data)
                if sessions:
                    self.current_viva_session_id = sessions[0]['id']
                    return True
            create_res = api_client.post("viva-sessions/", {
                "batch":     batch_id,
                "subject":   "General Viva",
                "viva_type": "offline",
            })
            if create_res.status_code == 201:
                self.current_viva_session_id = create_res.json()['id']
                return True
            error(self, "Session Error",
                  f"Could not create offline session:\n{create_res.text}")
        except Exception as e:
            error(self, "Connection Error", f"Connection error:\n{e}")
        return False

    # ── Save evaluation ───────────────────────────────────────

    def save_evaluation(self):
        if not self.current_record:
            return
        if not self._ensure_offline_session():
            return

        marks_text = self.marks_input.text().strip()
        if not marks_text:
            warning(self, "Missing Marks", "Please enter marks before saving.")
            return

        try:
            m = int(marks_text)
            if not (0 <= m <= 100):
                raise ValueError
        except ValueError:
            warning(self, "Invalid Marks", "Marks must be a number between 0 and 100.")
            return

        feedback = self.feedback_input.toPlainText().strip()
        res = api_client.post("viva-results/", {
            "viva_session": self.current_viva_session_id,
            "student":      self.current_record['student_id'],
            "marks":        m,
            "notes":        feedback,
        })

        if res.status_code in (200, 201):
            self.current_record['status'] = 'completed'
            self.current_record['marks']  = m
            self.current_record['notes']  = feedback

            # Update badge instantly
            current_item = self.student_list.currentItem()
            if current_item:
                current_item.setData(Qt.ItemDataRole.UserRole, self.current_record)
                widget = self.student_list.itemWidget(current_item)
                badge  = widget.findChild(QLabel, "statusBadge")
                if badge:
                    badge.setText("Evaluated ✓")
                    badge.setStyleSheet("""
                        background: #10B981; color: white;
                        border-radius: 4px; padding: 4px 10px;
                        font-size: 11px; font-weight: bold;
                    """)

            # Auto-move to next student
            current_idx = self.student_list.currentRow()
            if current_idx < self.student_list.count() - 1:
                self.student_list.setCurrentRow(current_idx + 1)
            else:
                # ✅ Green success — all done
                success(self, "All Done!",
                        "All students evaluated.",
                        sub_text="Remember to publish results!")
        else:
            error(self, "Save Failed",
                  f"Failed to save evaluation:\n{res.text}")

    # ── Publish offline results ───────────────────────────────

    def publish_offline_results(self):
        if not self.current_viva_session_id:
            return

        # ✅ Confirmation before publishing
        if not confirm(
            self,
            title="Publish Offline Results",
            message="Publish offline viva results to all students?",
            sub_text="Students will be able to see their marks and feedback.",
            ok_text="Publish",
            cancel_text="Cancel",
        ):
            return

        res = api_client.post(
            f"viva-sessions/{self.current_viva_session_id}/complete/")
        if res.status_code == 200:
            success(self, "Published",
                    "Offline Viva results published to all students.")
        else:
            error(self, "Publish Failed",
                  "Failed to publish Offline Viva results.")

    # ── Publish online viva ───────────────────────────────────

    def publish_online_viva(self):
        if not hasattr(self.parent_window, 'current_batch_id') or \
                self.parent_window.current_batch_id is None:
            warning(self, "No Batch", "Please select a batch first.")
            return

        batch_id = self.parent_window.current_batch_id
        data = {
            "batch":         batch_id,
            "subject":       "Online Viva",
            "viva_type":     "online",
            "status":        "live",
            "platform_name": self.platform_combo.currentText(),
            "join_code":     self.join_code_input.text(),
            "join_link":     self.join_link_input.text(),
            "start_time":    self.start_time_input.dateTime()
                                  .toPyDateTime().isoformat(),
            "instructions":  self.on_instructions.toPlainText(),
        }

        res = api_client.post("viva-sessions/", data)
        if res.status_code == 201:
            success(self, "Viva Published",
                    "Online Viva published & visible to students!")
        else:
            error(self, "Publish Failed", f"Failed:\n{res.text}")
