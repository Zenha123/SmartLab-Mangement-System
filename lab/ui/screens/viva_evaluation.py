from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QFrame, 
    QLineEdit, QTextEdit, QPushButton, 
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from ui.theme import Theme, heading_font, body_font
from api.global_client import api_client


class VivaEvaluationScreen(QWidget):
    """
    Split-panel UI for Viva Evaluation.
    Left: Student List (Register No - Name | Status)
    Right: Evaluation Form (Marks, Feedback, Save)
    """

    def __init__(self, session_id, subject_name, parent=None):
        super().__init__()
        self.session_id = session_id
        self.subject_name = subject_name
        self.parent_window = parent
        self.viva_records = []
        self.current_record = None

        self.init_ui()
        self.load_records()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # --- Header ---
        header = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setFixedWidth(80)
        back_btn.setStyleSheet(f"background: {Theme.border}; color: {Theme.text_primary}; padding: 8px;")
        back_btn.clicked.connect(self.go_back)
        
        title = QLabel(f"🎤 Viva Evaluation: {self.subject_name}")
        title.setFont(heading_font(22, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary};")
        
        header.addWidget(back_btn)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # --- Splitter ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # --- Left Panel: Student List ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        
        list_label = QLabel("STUDENTS")
        list_label.setStyleSheet(f"color: {Theme.text_secondary}; font-weight: bold; letter-spacing: 1px;")
        
        self.student_list = QListWidget()
        self.student_list.setObjectName("studentList")
        self.student_list.itemSelectionChanged.connect(self.on_student_selected)
        
        left_layout.addWidget(list_label)
        left_layout.addWidget(self.student_list)
        
        # --- Right Panel: Evaluation Form ---
        self.right_panel = QFrame()
        self.right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.right_panel.setStyleSheet(f"""
            QFrame {{
                background: {Theme.card_bg};
                border: 1px solid {Theme.border};
                border-radius: 12px;
            }}
        """)
        self.form_layout = QVBoxLayout(self.right_panel)
        self.form_layout.setContentsMargins(30, 30, 30, 30)
        self.form_layout.setSpacing(15)

        self.empty_label = QLabel("Select a student to begin evaluation")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"color: {Theme.text_muted}; font-size: 16px;")
        self.form_layout.addWidget(self.empty_label)

        # Form content (hidden initially)
        self.form_widget = QWidget()
        form_content = QVBoxLayout(self.form_widget)
        form_content.setContentsMargins(0, 0, 0, 0)
        form_content.setSpacing(20)

        self.student_title = QLabel("Student Name")
        self.student_title.setFont(heading_font(18, bold=True))
        
        self.marks_input = QLineEdit()
        self.marks_input.setPlaceholderText("Enter Marks (0-100)")
        self.marks_input.setFixedHeight(45)
        
        self.feedback_input = QTextEdit()
        self.feedback_input.setPlaceholderText("Enter Feedback...")
        self.feedback_input.setMinimumHeight(150)
        
        self.save_btn = QPushButton("💾 Save & Next Student")
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {Theme.success};
                color: white;
                font-size: 15px;
                padding: 15px;
            }}
            QPushButton:hover {{ background: #059669; }}
        """)
        self.save_btn.clicked.connect(self.save_evaluation)

        form_content.addWidget(self.student_title)
        form_content.addWidget(QLabel("Marks (0-100)"))
        form_content.addWidget(self.marks_input)
        form_content.addWidget(QLabel("Feedback"))
        form_content.addWidget(self.feedback_input)
        form_content.addStretch()
        form_content.addWidget(self.save_btn)

        self.form_layout.addWidget(self.form_widget)
        self.form_widget.hide()

        # Add to splitter
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 2)
        
        layout.addWidget(self.splitter)

    def load_records(self):
        """Fetch viva records for this session from API"""
        try:
            # Note: We use the evaluation API with viva_session filter
            response = api_client.get(f"viva/?viva_session={self.session_id}")
            if response.status_code == 200:
                self.viva_records = response.json()
                self.populate_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load students: {str(e)}")

    def populate_list(self):
        self.student_list.clear()
        for record in self.viva_records:
            name = record.get('student_name', 'N/A')
            roll = record.get('student_roll', 'N/A')
            status = record.get('status', 'waiting')
            
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, record)
            
            status_indicator = "✓" if status == 'completed' else "○"
            status_color = "#10B981" if status == 'completed' else "#9CA3AF"
            
            item.setText(f"{status_indicator}  {roll} - {name}")
            item.setForeground(Qt.GlobalColor.black if status == 'waiting' else Qt.GlobalColor.darkGray)
            
            self.student_list.addItem(item)

    def on_student_selected(self):
        items = self.student_list.selectedItems()
        if not items:
            return
            
        record = items[0].data(Qt.ItemDataRole.UserRole)
        self.current_record = record
        
        self.empty_label.hide()
        self.form_widget.show()
        
        self.student_title.setText(f"{record['student_roll']} - {record['student_name']}")
        self.marks_input.setText(str(record.get('marks') or ""))
        self.feedback_input.setText(record.get('notes') or "")
        self.marks_input.setFocus()

    def save_evaluation(self):
        if not self.current_record:
            return
            
        marks_text = self.marks_input.text().strip()
        if not marks_text:
            QMessageBox.warning(self, "Error", "Please enter marks")
            return
            
        try:
            marks = int(marks_text)
            if not (0 <= marks <= 100):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Marks must be between 0 and 100")
            return

        feedback = self.feedback_input.toPlainText().strip()
        
        # Call API to save (PATCH)
        try:
            response = api_client.patch(f"viva/{self.current_record['id']}/", {
                "marks": marks,
                "notes": feedback,
                "status": "completed",
                "conducted_at": QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate)
            })
            
            if response.status_code == 200:
                # Refresh locally
                self.current_record['status'] = 'completed'
                self.current_record['marks'] = marks
                self.current_record['notes'] = feedback
                
                # Update item in list
                current_row = self.student_list.currentRow()
                self.populate_list()
                
                # Auto-select next student
                next_row = current_row + 1
                if next_row < self.student_list.count():
                    self.student_list.setCurrentRow(next_row)
                else:
                    QMessageBox.information(self, "Success", "All evaluations for this session are complete!")
                    self.go_back()
            else:
                QMessageBox.critical(self, "Error", "Failed to save evaluation")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"API Error: {str(e)}")

    def go_back(self):
        if self.parent_window:
            self.parent_window.show_screen("batch_dashboard")
