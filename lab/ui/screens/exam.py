# lab/ui/screens/exam.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QTextEdit, QComboBox, QSpinBox, QFrame,
    QSplitter, QScrollArea, QDialog, QDialogButtonBox,
    QFormLayout, QStackedWidget, QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QBrush, QDesktopServices
from PyQt6.QtCore import QUrl

from ui.common.styled_dialogs import info, success, warning, error, confirm  # ← replaces QMessageBox
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


# ── Helpers ───────────────────────────────────────────────────

def _btn(text, color, hover=None):
    hover = hover or color
    b = QPushButton(text)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(f"""
        QPushButton {{
            background: {color}; color: white; border: none;
            border-radius: 8px; padding: 10px 20px;
            font-weight: bold; font-size: 13px;
        }}
        QPushButton:hover {{ background: {hover}; }}
    """)
    return b

def _section_title(text):
    lbl = QLabel(text)
    lbl.setFont(heading_font(15, bold=True))
    lbl.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 6px;")
    return lbl

def _card():
    f = QFrame()
    f.setStyleSheet(f"""
        QFrame {{
            background: {Theme.card_bg}; border: 1px solid {Theme.border};
            border-radius: 12px; padding: 0px;
        }}
    """)
    return f

_TABLE_STYLE = f"""
    QTableWidget {{
        border: 1px solid {Theme.border};
        border-radius: 8px; background: white;
        gridline-color: #f3f4f6; font-size: 13px;
    }}
    QTableWidget::item {{ padding: 8px; }}
    QHeaderView::section {{
        background: #f9fafb; font-weight: bold;
        padding: 10px 8px; border: none;
        border-bottom: 1px solid {Theme.border};
    }}
"""


# ── Create Exam Dialog ─────────────────────────────────────────

class CreateExamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Exam Session")
        self.setMinimumWidth(400)
        self.setStyleSheet("QDialog { background: #f5f5f5; }")
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g. Mid-Semester Lab Exam")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(10, 480)
        self.duration_spin.setValue(120)
        self.duration_spin.setSuffix(" min")
        form.addRow("Title:", self.title_input)
        form.addRow("Duration:", self.duration_spin)
        layout.addLayout(form)

        # ✅ Styled footer buttons
        footer_w = QWidget()
        footer_w.setStyleSheet("background: #ebebeb; border-top: 1px solid #d0d0d0; margin-top: 8px;")
        footer = QHBoxLayout(footer_w)
        footer.setContentsMargins(12, 10, 12, 12)
        footer.addStretch(1)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(34); cancel_btn.setMinimumWidth(90)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #fff; color: #333; border: 1px solid #bbb;
                border-radius: 5px; font-size: 13px; font-weight: 500; padding: 6px 16px;
            }
            QPushButton:hover { background: #f0f0f0; }
        """)
        cancel_btn.clicked.connect(self.reject)

        ok_btn = QPushButton("Create")
        ok_btn.setFixedHeight(34); ok_btn.setMinimumWidth(90)
        ok_btn.setDefault(True)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3; color: white; border: none;
                border-radius: 5px; font-size: 13px; font-weight: 600; padding: 6px 16px;
            }
            QPushButton:hover   { background: #1976D2; }
            QPushButton:pressed { background: #1565C0; }
        """)
        ok_btn.clicked.connect(self.accept)

        footer.addWidget(cancel_btn)
        footer.addWidget(ok_btn)
        layout.addWidget(footer_w)

    def get_data(self):
        return {
            "title": self.title_input.text().strip(),
            "duration_minutes": self.duration_spin.value(),
        }


# ── Question Dialog ────────────────────────────────────────────

class QuestionDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Question" if not data else "Edit Question")
        self.setMinimumWidth(480)
        self.setStyleSheet("QDialog { background: #f5f5f5; }")
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.title_input = QLineEdit()
        self.desc_input  = QTextEdit()
        self.desc_input.setMinimumHeight(100)
        self.marks_spin  = QSpinBox()
        self.marks_spin.setRange(1, 100)
        self.marks_spin.setValue(10)
        self.diff_combo  = QComboBox()
        self.diff_combo.addItems(["easy", "medium", "hard"])
        form.addRow("Title:", self.title_input)
        form.addRow("Description:", self.desc_input)
        form.addRow("Marks:", self.marks_spin)
        form.addRow("Difficulty:", self.diff_combo)
        layout.addLayout(form)

        if data:
            self.title_input.setText(data.get("title", ""))
            self.desc_input.setPlainText(data.get("description", ""))
            self.marks_spin.setValue(data.get("marks", 10))
            idx = {"easy": 0, "medium": 1, "hard": 2}.get(data.get("difficulty", "medium"), 1)
            self.diff_combo.setCurrentIndex(idx)

        # ✅ Styled footer buttons
        footer_w = QWidget()
        footer_w.setStyleSheet("background: #ebebeb; border-top: 1px solid #d0d0d0; margin-top: 8px;")
        footer = QHBoxLayout(footer_w)
        footer.setContentsMargins(12, 10, 12, 12)
        footer.addStretch(1)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(34); cancel_btn.setMinimumWidth(90)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #fff; color: #333; border: 1px solid #bbb;
                border-radius: 5px; font-size: 13px; font-weight: 500; padding: 6px 16px;
            }
            QPushButton:hover { background: #f0f0f0; }
        """)
        cancel_btn.clicked.connect(self.reject)

        ok_btn = QPushButton("Save")
        ok_btn.setFixedHeight(34); ok_btn.setMinimumWidth(90)
        ok_btn.setDefault(True)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3; color: white; border: none;
                border-radius: 5px; font-size: 13px; font-weight: 600; padding: 6px 16px;
            }
            QPushButton:hover   { background: #1976D2; }
            QPushButton:pressed { background: #1565C0; }
        """)
        ok_btn.clicked.connect(self.accept)

        footer.addWidget(cancel_btn)
        footer.addWidget(ok_btn)
        layout.addWidget(footer_w)

    def get_data(self):
        return {
            "title":       self.title_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "marks":       self.marks_spin.value(),
            "difficulty":  self.diff_combo.currentText(),
        }


# ── Main Exam Screen ───────────────────────────────────────────

class ExamScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window   = parent
        self.selected_session = None
        self.sessions        = []
        self.questions       = []
        self.submissions     = []

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        page = QWidget()
        self.page_layout = QVBoxLayout(page)
        self.page_layout.setContentsMargins(28, 24, 28, 24)
        self.page_layout.setSpacing(20)

        title_row = QHBoxLayout()
        page_title = QLabel("📋 Exam Module")
        page_title.setFont(heading_font(24, bold=True))
        page_title.setStyleSheet(f"color: {Theme.text_primary};")
        title_row.addWidget(page_title)
        title_row.addStretch()
        self.page_layout.addLayout(title_row)

        tab_row = QHBoxLayout()
        self.tab_sessions_btn  = _btn("📁 Exam Sessions", Theme.primary)
        self.tab_questions_btn = _btn("❓ Questions",      "#6B7280")
        self.tab_controls_btn  = _btn("🚨 Exam Control",  "#6B7280")
        self.tab_evaluate_btn  = _btn("📊 Evaluate",      "#6B7280")
        for b in [self.tab_sessions_btn, self.tab_questions_btn,
                  self.tab_controls_btn, self.tab_evaluate_btn]:
            tab_row.addWidget(b)
        tab_row.addStretch()
        self.page_layout.addLayout(tab_row)

        self.stack = QStackedWidget()
        self.page_layout.addWidget(self.stack)

        self._build_sessions_tab()
        self._build_questions_tab()
        self._build_controls_tab()
        self._build_evaluate_tab()

        self.tab_sessions_btn.clicked.connect( lambda: self._switch_tab(0))
        self.tab_questions_btn.clicked.connect(lambda: self._switch_tab(1))
        self.tab_controls_btn.clicked.connect( lambda: self._switch_tab(2))
        self.tab_evaluate_btn.clicked.connect( lambda: self._switch_tab(3))

        self.page_layout.addStretch()
        scroll.setWidget(page)
        root_layout.addWidget(scroll)

    def _switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        colors_active = ["#1d4ed8", "#059669", "#DC2626", "#7C3AED"]
        for i, b in enumerate([self.tab_sessions_btn, self.tab_questions_btn,
                                self.tab_controls_btn, self.tab_evaluate_btn]):
            col = colors_active[i] if i == index else "#6B7280"
            b.setStyleSheet(f"""
                QPushButton {{
                    background: {col}; color: white; border: none;
                    border-radius: 8px; padding: 10px 20px;
                    font-weight: bold; font-size: 13px;
                }}
            """)

    # ── Tab 1: Sessions ───────────────────────────────────────

    def _build_sessions_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0); v.setSpacing(12)

        bar = QHBoxLayout()
        bar.addWidget(_section_title("Exam Sessions"))
        bar.addStretch()
        refresh_btn = _btn("↻ Refresh", "#6B7280")
        new_btn     = _btn("+ New Exam", Theme.success)
        refresh_btn.clicked.connect(self.load_sessions)
        new_btn.clicked.connect(self.create_exam)
        bar.addWidget(refresh_btn); bar.addWidget(new_btn)
        v.addLayout(bar)

        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels(
            ["ID", "Title", "Duration", "Status", "Questions", "Actions"])
        self.sessions_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch)
        self.sessions_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.sessions_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.sessions_table.setAlternatingRowColors(True)
        self.sessions_table.verticalHeader().setVisible(False)
        self.sessions_table.setStyleSheet(_TABLE_STYLE)
        v.addWidget(self.sessions_table)
        self.stack.addWidget(w)

    # ── Tab 2: Questions ──────────────────────────────────────

    def _build_questions_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0); v.setSpacing(12)

        bar = QHBoxLayout()
        self.q_session_label = QLabel("Select a session first")
        self.q_session_label.setStyleSheet(
            f"color: {Theme.text_muted}; font-weight: bold;")
        bar.addWidget(self.q_session_label); bar.addStretch()
        add_q_btn = _btn("+ Add Question", Theme.success)
        add_q_btn.clicked.connect(self.add_question)
        bar.addWidget(add_q_btn)
        v.addLayout(bar)

        self.q_table = QTableWidget()
        self.q_table.setColumnCount(5)
        self.q_table.setHorizontalHeaderLabels(
            ["#", "Title", "Marks", "Difficulty", "Actions"])
        self.q_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch)
        self.q_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.q_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.q_table.setAlternatingRowColors(True)
        self.q_table.verticalHeader().setVisible(False)
        self.q_table.setStyleSheet(_TABLE_STYLE)
        v.addWidget(self.q_table)
        self.stack.addWidget(w)

    # ── Tab 3: Controls ───────────────────────────────────────

    def _build_controls_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0); v.setSpacing(16)

        self.ctrl_session_label = QLabel("No session selected")
        self.ctrl_session_label.setFont(heading_font(16, bold=True))
        self.ctrl_session_label.setStyleSheet(f"color: {Theme.text_primary};")
        v.addWidget(self.ctrl_session_label)

        self.ctrl_status_label = QLabel("Status: —")
        self.ctrl_status_label.setStyleSheet(
            f"color: {Theme.text_muted}; font-size: 14px;")
        v.addWidget(self.ctrl_status_label)

        btns = QHBoxLayout()
        self.start_btn = _btn("🚨 Start Exam", "#DC2626", "#B91C1C")
        self.start_btn.setFixedHeight(55)
        self.start_btn.clicked.connect(self.start_exam)
        self.end_btn = _btn("✅ End Exam", Theme.success, "#059669")
        self.end_btn.setFixedHeight(55)
        self.end_btn.clicked.connect(self.end_exam)
        btns.addWidget(self.start_btn); btns.addWidget(self.end_btn); btns.addStretch()
        v.addLayout(btns)

        hint = QLabel(
            "• Start Exam: randomly assigns questions to every student, notifies via WebSocket.\n"
            "• End Exam: marks session completed, blocks further submissions, notifies students."
        )
        hint.setStyleSheet(f"color: {Theme.text_muted}; font-size: 12px; margin-top: 10px;")
        hint.setWordWrap(True)
        v.addWidget(hint); v.addStretch()
        self.stack.addWidget(w)

    # ── Tab 4: Evaluate ───────────────────────────────────────

    def _build_evaluate_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0); v.setSpacing(12)

        bar = QHBoxLayout()
        self.eval_session_label = QLabel("No session selected")
        self.eval_session_label.setStyleSheet(
            f"color: {Theme.text_muted}; font-weight: bold;")
        bar.addWidget(self.eval_session_label); bar.addStretch()
        load_btn = _btn("↻ Load Submissions", "#6B7280")
        load_btn.clicked.connect(self.load_submissions)
        bar.addWidget(load_btn)
        v.addLayout(bar)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.eval_table = QTableWidget()
        self.eval_table.setColumnCount(5)
        self.eval_table.setHorizontalHeaderLabels(
            ["Student", "Roll No", "Submitted", "File", "Status"])
        self.eval_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self.eval_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.eval_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.eval_table.setAlternatingRowColors(True)
        self.eval_table.verticalHeader().setVisible(False)
        self.eval_table.setStyleSheet(_TABLE_STYLE)
        self.eval_table.itemSelectionChanged.connect(self.on_eval_row_selected)
        splitter.addWidget(self.eval_table)

        right = QWidget(); right.setMinimumWidth(280)
        right_v = QVBoxLayout(right)
        right_v.setContentsMargins(16, 0, 0, 0); right_v.setSpacing(12)

        self.eval_student_name = QLabel("Select a student →")
        self.eval_student_name.setFont(body_font(14, QFont.Weight.Bold))
        right_v.addWidget(self.eval_student_name)

        right_v.addWidget(QLabel("Marks (0–100):"))
        self.eval_marks = QLineEdit()
        self.eval_marks.setPlaceholderText("Enter marks")
        self.eval_marks.setFixedHeight(40)
        self.eval_marks.setStyleSheet(
            f"border: 1px solid {Theme.border}; border-radius: 8px; padding: 8px;")
        right_v.addWidget(self.eval_marks)

        right_v.addWidget(QLabel("Feedback:"))
        self.eval_feedback = QTextEdit()
        self.eval_feedback.setPlaceholderText("Optional feedback...")
        self.eval_feedback.setMaximumHeight(120)
        self.eval_feedback.setStyleSheet(
            f"border: 1px solid {Theme.border}; border-radius: 8px; padding: 8px;")
        right_v.addWidget(self.eval_feedback)

        self.eval_save_btn = _btn("💾 Save Evaluation", Theme.primary)
        self.eval_save_btn.clicked.connect(self.save_evaluation)
        right_v.addWidget(self.eval_save_btn)
        right_v.addStretch()

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3); splitter.setStretchFactor(1, 2)
        v.addWidget(splitter)
        self.stack.addWidget(w)
        self._current_eval_id = None

    # ── Lifecycle ─────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self.load_sessions()

    # ── Sessions ──────────────────────────────────────────────

    def load_sessions(self):
        if not hasattr(self.parent_window, 'current_batch_id') or \
                not self.parent_window.current_batch_id:
            return
        try:
            res = api_client.get(
                f"exam-sessions/?batch={self.parent_window.current_batch_id}")
            if res.status_code == 200:
                data = res.json()
                self.sessions = (data.get('results', data)
                                 if isinstance(data, dict) else data)
                self._populate_sessions_table()
        except Exception as e:
            print(f"Error loading sessions: {e}")

    def _populate_sessions_table(self):
        self.sessions_table.setRowCount(0)
        for s in self.sessions:
            row = self.sessions_table.rowCount()
            self.sessions_table.insertRow(row)
            self.sessions_table.setItem(row, 0, QTableWidgetItem(str(s['id'])))
            self.sessions_table.setItem(row, 1, QTableWidgetItem(s['title']))
            self.sessions_table.setItem(row, 2,
                QTableWidgetItem(f"{s['duration_minutes']} min"))

            status_item = QTableWidgetItem(s['status'].upper())
            colors = {"scheduled": "#EAB308", "active": "#DC2626", "completed": "#10B981"}
            status_item.setForeground(QBrush(QColor(colors.get(s['status'], '#6B7280'))))
            status_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            self.sessions_table.setItem(row, 3, status_item)
            self.sessions_table.setItem(row, 4,
                QTableWidgetItem(str(s.get('question_count', 0))))

            sel_btn = _btn("Select", Theme.primary)
            sel_btn.clicked.connect(lambda _, sid=s['id']: self.select_session(sid))
            self.sessions_table.setCellWidget(row, 5, sel_btn)

    def create_exam(self):
        if not hasattr(self.parent_window, 'current_batch_id') or \
                not self.parent_window.current_batch_id:
            warning(self, "No Batch", "Please select a batch first.")
            return
        dlg = CreateExamDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            if not d['title']:
                warning(self, "Missing Title", "Please enter an exam title.")
                return
            d['batch'] = self.parent_window.current_batch_id
            d['subject_name'] = getattr(self.parent_window, 'current_subject_name', "")
            try:
                res = api_client.post("exam-sessions/", d)
                if res.status_code == 201:
                    # ✅ Green success
                    success(self, "Exam Created", "Exam session created successfully!")
                    self.load_sessions()
                else:
                    error(self, "Create Failed", res.text)
            except Exception as e:
                error(self, "Connection Error", str(e))

    def select_session(self, session_id):
        self.selected_session = next(
            (s for s in self.sessions if s['id'] == session_id), None)
        if not self.selected_session:
            return
        title  = self.selected_session['title']
        status = self.selected_session['status']

        self.q_session_label.setText(f"Session: {title}")
        self.ctrl_session_label.setText(f"📋 {title}")
        self.ctrl_status_label.setText(f"Status: {status.upper()}")
        self.eval_session_label.setText(f"Session: {title}")

        self.load_questions()
        self.load_submissions()
        # ✅ Blue info dialog
        info(self, "Session Selected",
             f"'{title}' is now active.",
             sub_text="Switch tabs to manage questions, start/end, or evaluate.")

    # ── Questions ─────────────────────────────────────────────

    def load_questions(self):
        if not self.selected_session:
            return
        try:
            res = api_client.get(
                f"exam-questions/?session={self.selected_session['id']}")
            if res.status_code == 200:
                data = res.json()
                self.questions = (data.get('results', data)
                                  if isinstance(data, dict) else data)
                self._populate_q_table()
        except Exception as e:
            print(f"Error loading questions: {e}")

    def _populate_q_table(self):
        self.q_table.setRowCount(0)
        for i, q in enumerate(self.questions, 1):
            row = self.q_table.rowCount()
            self.q_table.insertRow(row)
            self.q_table.setItem(row, 0, QTableWidgetItem(str(i)))
            self.q_table.setItem(row, 1, QTableWidgetItem(q['title']))
            self.q_table.setItem(row, 2, QTableWidgetItem(str(q['marks'])))
            diff      = q.get('difficulty', 'medium')
            diff_item = QTableWidgetItem(diff.capitalize())
            diff_item.setForeground(QBrush(QColor(
                {"easy": "#10B981", "medium": "#F59E0B", "hard": "#EF4444"}.get(diff, "#6B7280"))))
            self.q_table.setItem(row, 3, diff_item)

            actions = QWidget()
            ah = QHBoxLayout(actions); ah.setContentsMargins(4, 2, 4, 2)
            edit_btn = _btn("Edit", "#6B7280"); edit_btn.setFixedHeight(28)
            edit_btn.clicked.connect(lambda _, qd=q: self.edit_question(qd))
            del_btn  = _btn("Del", "#EF4444");  del_btn.setFixedHeight(28)
            del_btn.clicked.connect(lambda _, qid=q['id']: self.delete_question(qid))
            ah.addWidget(edit_btn); ah.addWidget(del_btn)
            self.q_table.setCellWidget(row, 4, actions)

    def add_question(self):
        if not self.selected_session:
            warning(self, "No Session", "Please select an exam session first.")
            return
        dlg = QuestionDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            if not d['title'] or not d['description']:
                warning(self, "Missing Fields", "Title and description are required.")
                return
            d['session'] = self.selected_session['id']
            try:
                res = api_client.post("exam-questions/", d)
                if res.status_code == 201:
                    self.load_questions()
                else:
                    error(self, "Error", res.text)
            except Exception as e:
                error(self, "Connection Error", str(e))

    def edit_question(self, q_data):
        dlg = QuestionDialog(self, data=q_data)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            try:
                res = api_client.patch(f"exam-questions/{q_data['id']}/", d)
                if res.status_code == 200:
                    self.load_questions()
                else:
                    error(self, "Error", res.text)
            except Exception as e:
                error(self, "Connection Error", str(e))

    def delete_question(self, qid):
        # ✅ Red confirm dialog — clearly visible "Delete" and "Cancel"
        if not confirm(self, "Delete Question",
                       "Are you sure you want to delete this question?",
                       ok_text="Delete", cancel_text="Cancel", danger=True):
            return
        try:
            res = api_client.delete(f"exam-questions/{qid}/")
            if res.status_code == 204:
                self.load_questions()
            else:
                error(self, "Delete Failed", res.text)
        except Exception as e:
            error(self, "Connection Error", str(e))

    # ── Exam Controls ─────────────────────────────────────────

    def start_exam(self):
        if not self.selected_session:
            warning(self, "No Session", "Select a session first.")
            return
        # ✅ Confirmation — clearly visible buttons
        if not confirm(
            self, "Start Exam",
            f"Start '{self.selected_session['title']}'?",
            sub_text="Questions will be randomly assigned to all students.",
            ok_text="Start Exam", cancel_text="Cancel", danger=True,
        ):
            return
        try:
            res = api_client.post("exam-start/",
                                  {"session_id": self.selected_session['id']})
            if res.status_code == 200:
                # ✅ Green success
                success(self, "Exam Started",
                        "Exam started! Students can see their questions now.")
                self.selected_session['status'] = 'active'
                self.ctrl_status_label.setText("Status: ACTIVE")
                self.load_sessions()
            else:
                error(self, "Start Failed", res.text)
        except Exception as e:
            error(self, "Connection Error", str(e))

    def end_exam(self):
        if not self.selected_session:
            warning(self, "No Session", "Select a session first.")
            return
        # ✅ Red confirmation
        if not confirm(
            self, "End Exam",
            f"End '{self.selected_session['title']}'?",
            sub_text="Students will be notified and submissions will be locked.",
            ok_text="End Exam", cancel_text="Cancel", danger=True,
        ):
            return
        try:
            res = api_client.post("exam-end/",
                                  {"session_id": self.selected_session['id']})
            if res.status_code == 200:
                success(self, "Exam Ended",
                        "Exam ended. Students have been notified.")
                self.selected_session['status'] = 'completed'
                self.ctrl_status_label.setText("Status: COMPLETED")
                self.load_sessions()
            else:
                error(self, "End Failed", res.text)
        except Exception as e:
            error(self, "Connection Error", str(e))

    # ── Evaluation ────────────────────────────────────────────

    def load_submissions(self):
        if not self.selected_session:
            return
        try:
            res = api_client.get(
                f"exam-submissions/?session_id={self.selected_session['id']}")
            if res.status_code == 200:
                self.submissions = res.json()
                self._populate_eval_table()
        except Exception as e:
            print(f"Error loading submissions: {e}")

    def _populate_eval_table(self):
        self.eval_table.setRowCount(0)
        for sub in self.submissions:
            row = self.eval_table.rowCount()
            self.eval_table.insertRow(row)
            self.eval_table.setItem(row, 0, QTableWidgetItem(sub.get('student_name', 'N/A')))
            self.eval_table.setItem(row, 1, QTableWidgetItem(sub.get('student_roll', 'N/A')))
            submitted_at = sub.get('submitted_at', '')
            self.eval_table.setItem(row, 2, QTableWidgetItem(
                submitted_at[:19].replace('T', ' ') if submitted_at else 'Not submitted'))

            file_url = sub.get('file_url', '')
            if file_url:
                dl_btn = _btn("📥 Download", "#6B7280")
                dl_btn.clicked.connect(
                    lambda _, u=file_url: QDesktopServices.openUrl(QUrl(u)))
                self.eval_table.setCellWidget(row, 3, dl_btn)
            else:
                self.eval_table.setItem(row, 3, QTableWidgetItem("No file"))

            status      = sub.get('status', 'pending')
            status_item = QTableWidgetItem(status.capitalize())
            status_item.setForeground(QBrush(QColor(
                {"pending": "#EAB308", "submitted": "#3B82F6",
                 "evaluated": "#10B981"}.get(status, "#6B7280"))))
            status_item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            self.eval_table.setItem(row, 4, status_item)
            self.eval_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, sub)

    def on_eval_row_selected(self):
        row  = self.eval_table.currentRow()
        item = self.eval_table.item(row, 0)
        if not item:
            return
        sub = item.data(Qt.ItemDataRole.UserRole)
        if not sub:
            return
        self._current_eval_id = sub['id']
        self.eval_student_name.setText(sub.get('student_name', 'Unknown'))
        self.eval_marks.setText(str(sub.get('marks', '') or ''))
        self.eval_feedback.setPlainText(sub.get('feedback', ''))

    def save_evaluation(self):
        if not self._current_eval_id:
            warning(self, "No Student", "Select a student from the table.")
            return
        marks_text = self.eval_marks.text().strip()
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
        try:
            res = api_client.post("exam-evaluate/", {
                "student_exam_id": self._current_eval_id,
                "marks":    m,
                "feedback": self.eval_feedback.toPlainText().strip(),
            })
            if res.status_code == 200:
                # ✅ Green success
                success(self, "Evaluation Saved",
                        "Evaluation saved and published to student!")
                self.load_submissions()
            else:
                error(self, "Save Failed", res.text)
        except Exception as e:
            error(self, "Connection Error", str(e))
