# lab/ui/screens/evaluation.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QTableWidgetItem,
    QHBoxLayout, QLineEdit, QPushButton, QTextEdit,
    QTableWidget, QHeaderView, QFrame, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QCursor

from ui.common.cards import StatCard, CardFrame
from ui.common.styled_dialogs import success, warning, error, confirm  # ← replaces QMessageBox
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client
import requests
import os


class EvaluationScreen(QWidget):
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window
        self.submissions = []
        self.submission_widgets = {}   # row → (submission_id, grade_input, feedback_input)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("✅ Evaluation")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # ── Summary stat cards ────────────────────────────────
        stats = QGridLayout()
        stats.setSpacing(16)
        self.received_card   = StatCard("📄 Assignment Received", "0", Theme.info,    icon="📄")
        self.pending_card    = StatCard("⏳ Yet to Receive",       "0", Theme.warning, icon="⏳")
        self.evaluated_card  = StatCard("✅ Evaluated",            "0", Theme.success, icon="✅")
        self.to_evaluate_card= StatCard("📝 Yet to Evaluate",      "0", Theme.primary, icon="📝")
        stats.addWidget(self.received_card,    0, 0)
        stats.addWidget(self.pending_card,     0, 1)
        stats.addWidget(self.evaluated_card,   0, 2)
        stats.addWidget(self.to_evaluate_card, 0, 3)
        root.addLayout(stats)

        # ── Table card ────────────────────────────────────────
        card = CardFrame(padding=20)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Student", "Student ID", "Date", "Submission File",
            "Grade", "Feedback", "Action"
        ])
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                gridline-color: #f3f4f6;
                selection-background-color: transparent;
                selection-color: black;
            }}
            QHeaderView::section {{
                background-color: #f9fafb;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 700;
                color: #374151;
                font-size: 13px;
                text-transform: uppercase;
            }}
            QTableWidget::item {{
                padding: 0px;
                border-bottom: 1px solid #f3f4f6;
            }}
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 100)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        card.layout.addWidget(self.table)
        root.addWidget(card)
        root.addStretch(1)

    # ── Lifecycle ─────────────────────────────────────────────

    def showEvent(self, event):
        super().showEvent(event)
        self.load_submissions()

    # ── Data ──────────────────────────────────────────────────

    def load_submissions(self):
        if not self.parent_window or not hasattr(self.parent_window, 'current_batch_id'):
            return

        batch_id = self.parent_window.current_batch_id
        try:
            url      = f"http://localhost:8000/api/submissions/?task__batch={batch_id}"
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {api_client.access_token}"},
                timeout=5,
            )
            if response.status_code == 200:
                data = response.json()
                self.submissions = data.get('results', data) if isinstance(data, dict) else data
                self.populate_table()
                self.update_stats()
            else:
                print(f"API Error: {response.status_code}")
        except Exception as e:
            print(f"Exception: {e}")

    def populate_table(self):
        self.table.setRowCount(len(self.submissions))
        self.submission_widgets.clear()

        for r, item in enumerate(self.submissions):
            self.table.setRowHeight(r, 60)

            # Student name
            name_lbl = QLabel(f"👤 {item.get('student_name', 'Unknown')}")
            name_lbl.setStyleSheet("font-weight: 600; color: #1f2937; padding-left: 10px;")
            self.table.setCellWidget(r, 0, name_lbl)

            # Student ID
            id_lbl = QLabel(str(item.get('student', '')))
            id_lbl.setStyleSheet("color: #6b7280; padding-left: 10px;")
            self.table.setCellWidget(r, 1, id_lbl)

            # Date
            date_str = (item.get('submitted_at', '-') or '-').split('T')[0]
            date_lbl = QLabel(date_str)
            date_lbl.setStyleSheet("color: #6b7280; padding-left: 10px;")
            self.table.setCellWidget(r, 2, date_lbl)

            # File button
            file_path = item.get('file_path', '')
            file_name = file_path.replace('\\', '/').split('/')[-1] if file_path else "No File"
            file_btn  = QPushButton(f"📎 {file_name}")
            file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            file_btn.setStyleSheet("""
                QPushButton {
                    border: none; background: transparent;
                    color: #2563eb; text-align: left;
                    font-weight: 500; padding: 5px;
                }
                QPushButton:hover { text-decoration: underline; color: #1d4ed8; }
            """)
            if file_path:
                file_btn.clicked.connect(lambda _, p=file_path: self.view_code(p))
            else:
                file_btn.setEnabled(False)
                file_btn.setStyleSheet(
                    "color: #9ca3af; border: none; background: transparent; padding: 5px;"
                )
            file_container = QWidget()
            fl = QHBoxLayout(file_container)
            fl.setContentsMargins(10, 0, 0, 0)
            fl.addWidget(file_btn)
            self.table.setCellWidget(r, 3, file_container)

            # Grade input
            grade_input = QLineEdit()
            grade_input.setPlaceholderText("0-100")
            grade_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grade_input.setFixedWidth(60)
            grade_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d1d5db; border-radius: 6px;
                    padding: 6px; font-weight: 600;
                }
                QLineEdit:focus { border: 2px solid #2563eb; }
            """)
            if item.get("marks") is not None:
                grade_input.setText(str(item["marks"]))
            grade_container = QWidget()
            gl = QHBoxLayout(grade_container)
            gl.setContentsMargins(0, 0, 0, 0)
            gl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            gl.addWidget(grade_input)
            self.table.setCellWidget(r, 4, grade_container)

            # Feedback input
            feedback_input = QLineEdit()
            feedback_input.setPlaceholderText("Enter feedback...")
            feedback_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d1d5db; border-radius: 6px; padding: 6px 12px;
                }
                QLineEdit:focus { border: 2px solid #2563eb; }
            """)
            if item.get("feedback"):
                feedback_input.setText(item["feedback"])
            feedback_container = QWidget()
            fbl = QHBoxLayout(feedback_container)
            fbl.setContentsMargins(5, 0, 5, 0)
            fbl.addWidget(feedback_input)
            self.table.setCellWidget(r, 5, feedback_container)

            # Publish button
            publish_btn = QPushButton("Publish")
            publish_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            publish_btn.setFixedSize(80, 32)
            publish_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb; color: white;
                    border: none; border-radius: 6px;
                    font-weight: 600; font-size: 12px;
                }
                QPushButton:hover   { background-color: #1d4ed8; }
                QPushButton:pressed { background-color: #1e40af; }
            """)
            publish_btn.clicked.connect(lambda _, row=r: self._on_publish(row))
            action_container = QWidget()
            al = QHBoxLayout(action_container)
            al.setContentsMargins(0, 0, 10, 0)
            al.setAlignment(Qt.AlignmentFlag.AlignCenter)
            al.addWidget(publish_btn)
            self.table.setCellWidget(r, 6, action_container)

            self.submission_widgets[r] = (item['id'], grade_input, feedback_input)

    def update_stats(self):
        submitted = sum(1 for s in self.submissions if s.get('status') == 'submitted')
        evaluated = sum(1 for s in self.submissions if s.get('status') == 'evaluated')
        self.received_card.update_value(str(submitted))
        self.evaluated_card.update_value(str(evaluated))
        self.to_evaluate_card.update_value(str(max(0, submitted - evaluated)))

    # ── File viewer ───────────────────────────────────────────

    def view_code(self, file_path: str):
        normalized = file_path.replace('\\', os.sep).replace('/', os.sep)
        full_path  = os.path.normpath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'backend', 'media', normalized
        ))

        if full_path.lower().endswith('.pdf'):
            try:
                os.startfile(full_path)
            except Exception as e:
                # ✅ Red error dialog
                error(self, "Cannot Open PDF", f"Could not open PDF:\n{str(e)}")
            return

        try:
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                code = f.read()
        except Exception as e:
            # ✅ Red error dialog
            error(self, "Cannot Open File",
                  f"Could not open file:\n{str(e)}\n\nPath: {full_path}")
            return

        # Code viewer dialog — close button styled blue
        dialog = QDialog(self)
        dialog.setWindowTitle(f"View Code — {os.path.basename(file_path)}")
        dialog.resize(900, 700)
        dialog.setStyleSheet("QDialog { background: #1e1e1e; }")

        v = QVBoxLayout(dialog)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        code_viewer = QTextEdit()
        code_viewer.setReadOnly(True)
        code_viewer.setPlainText(code)
        code_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                border: none; padding: 16px;
            }
        """)
        v.addWidget(code_viewer)

        # ✅ Styled footer with blue Close button
        footer_w = QWidget()
        footer_w.setStyleSheet("background: #ebebeb; border-top: 1px solid #d0d0d0;")
        footer = QHBoxLayout(footer_w)
        footer.setContentsMargins(16, 10, 16, 12)
        footer.addStretch(1)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(34)
        close_btn.setMinimumWidth(100)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3; color: white; border: none;
                border-radius: 5px; font-size: 13px;
                font-weight: 600; padding: 6px 18px;
            }
            QPushButton:hover   { background: #1976D2; }
            QPushButton:pressed { background: #1565C0; }
        """)
        close_btn.clicked.connect(dialog.accept)
        footer.addWidget(close_btn)
        v.addWidget(footer_w)

        dialog.exec()

    # ── Publish grade ─────────────────────────────────────────

    def _on_publish(self, row: int):
        if row not in self.submission_widgets:
            return

        submission_id, grade_input, feedback_input = self.submission_widgets[row]
        grade_text    = grade_input.text().strip()
        feedback_text = feedback_input.text().strip()

        # ✅ Validation — orange warning, always visible
        if not grade_text:
            warning(self, "Missing Grade", "Please enter a grade before publishing.")
            return

        try:
            marks = int(grade_text)
            if not (0 <= marks <= 100):
                raise ValueError
        except ValueError:
            warning(self, "Invalid Grade", "Grade must be a number between 0 and 100.")
            return

        try:
            response = requests.post(
                f"http://localhost:8000/api/submissions/{submission_id}/evaluate/",
                json={"marks": marks, "feedback": feedback_text},
                headers={"Authorization": f"Bearer {api_client.access_token}"},
                timeout=5,
            )

            if response.status_code == 200:
                # ✅ Green success dialog
                success(self, "Published",
                        "Result published to student successfully! 🎉")
                self.load_submissions()
            else:
                # ✅ Red error dialog
                error(self, "Publish Failed",
                      f"Failed to publish result.\nStatus: {response.status_code}")
        except Exception as e:
            error(self, "Connection Error", str(e))
