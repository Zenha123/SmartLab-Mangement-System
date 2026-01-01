from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.common.cards import CardFrame
from ui.common.badges import ModeBadge
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


class VivaScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window = parent
        self.students_data = []
        self.current_student = None
        self.current_session_id = None
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("🎤 Viva Mode")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        main = QHBoxLayout()
        main.setSpacing(20)

        # Student List
        list_card = CardFrame(padding=20)
        list_heading = QLabel("👥 Students")
        list_heading.setFont(body_font(16, QFont.Weight.Bold))
        list_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 12px;")
        list_card.layout.addWidget(list_heading)
        
        self.viva_list = QListWidget()
        self.viva_list.setStyleSheet(
            f"""
            QListWidget {{
                border: none;
                background: transparent;
            }}
            QListWidget::item {{
                padding: 12px;
                margin: 4px 0px;
                background: {Theme.background};
                border-radius: 8px;
            }}
            QListWidget::item:hover {{
                background: {Theme.primary}08;
            }}
            QListWidget::item:selected {{
                background: {Theme.primary}15;
                border-left: 3px solid {Theme.primary};
            }}
            """
        )
        self.viva_list.itemClicked.connect(self._on_student_selected)
        
        list_card.layout.addWidget(self.viva_list)
        main.addWidget(list_card, stretch=2)

        # Evaluation Panel
        eval_card = CardFrame(padding=24)
        eval_heading = QLabel("📝 Evaluation")
        eval_heading.setFont(body_font(16, QFont.Weight.Bold))
        eval_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        eval_card.layout.addWidget(eval_heading)
        
        self.student_lbl = QLabel("Select a student to evaluate")
        self.student_lbl.setFont(body_font(14, QFont.Weight.DemiBold))
        self.student_lbl.setStyleSheet(f"color: {Theme.primary}; padding: 12px; background: {Theme.primary}10; border-radius: 8px; margin-bottom: 16px;")
        eval_card.layout.addWidget(self.student_lbl)
        
        marks_label = QLabel("Marks (0-100):")
        marks_label.setFont(body_font(12, QFont.Weight.Medium))
        marks_label.setStyleSheet(f"color: {Theme.text_secondary}; margin-bottom: 6px;")
        eval_card.layout.addWidget(marks_label)
        
        self.marks_input = QLineEdit()
        self.marks_input.setPlaceholderText("Enter marks (e.g., 85)")
        self.marks_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {Theme.border};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                margin-bottom: 16px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Theme.primary};
            }}
            """
        )
        eval_card.layout.addWidget(self.marks_input)
        
        notes_label = QLabel("Notes:")
        notes_label.setFont(body_font(12, QFont.Weight.Medium))
        notes_label.setStyleSheet(f"color: {Theme.text_secondary}; margin-bottom: 6px;")
        eval_card.layout.addWidget(notes_label)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Add evaluation notes...")
        self.notes_input.setMaximumHeight(120)
        self.notes_input.setStyleSheet(
            f"""
            QTextEdit {{
                border: 2px solid {Theme.border};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                margin-bottom: 16px;
            }}
            QTextEdit:focus {{
                border: 2px solid {Theme.primary};
            }}
            """
        )
        eval_card.layout.addWidget(self.notes_input)
        
        self.save_btn = QPushButton("💾 Save & Next")
        self.save_btn.setProperty("class", "secondary")
        self.save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.secondary};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 700;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #16A085;
            }}
            """
        )
        self.save_btn.clicked.connect(self._save_viva_marks)
        self.save_btn.setEnabled(False)
        eval_card.layout.addWidget(self.save_btn)
        eval_card.layout.addStretch(1)
        main.addWidget(eval_card, stretch=1)

        root.addLayout(main)
        root.addStretch(1)
    
    def load_students(self):
        """Load students for viva evaluation"""
        if not hasattr(self.parent_window, 'current_batch_id') or self.parent_window.current_batch_id is None:
            return
        
        batch_id = self.parent_window.current_batch_id
        
        # Get students
        result = api_client.get_students(batch_id=batch_id)
        
        if result["success"]:
            self.students_data = result["data"]
            self._populate_student_list()
    
    def _populate_student_list(self):
        """Populate the student list widget"""
        self.viva_list.clear()
        
        for student in self.students_data:
            # Create custom widget for styling
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(8, 8, 8, 8)
            item_layout.setSpacing(12)
            
            # Use darker, more visible text color
            name_label = QLabel(f"👤 {student.get('name', 'Unknown')}")
            name_label.setFont(body_font(13, QFont.Weight.DemiBold))
            name_label.setStyleSheet(f"color: #2C3E50;")  # Dark gray for better visibility
            
            status_badge = ModeBadge(
                "Waiting", 
                Theme.warning,
                size="small"
            )
            
            item_layout.addWidget(name_label)
            item_layout.addStretch()
            item_layout.addWidget(status_badge)
            
            # Create list item
            item = QListWidgetItem()
            # CRITICAL FIX: Set text so item is visible even if widget fails to render
            item.setText(f"{student.get('name', 'Unknown')} ({student.get('student_id', 'N/A')})")
            item.setSizeHint(item_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, student)
            
            self.viva_list.addItem(item)
            self.viva_list.setItemWidget(item, item_widget)
    
    def _on_student_selected(self, item):
        """Handle student selection"""
        student = item.data(Qt.ItemDataRole.UserRole)
        self.current_student = student
        self.student_lbl.setText(f"Current Student: {student.get('name', 'Unknown')}")
        self.save_btn.setEnabled(True)
        self.marks_input.clear()
        self.notes_input.clear()
        self.marks_input.setFocus()
    
    def _save_viva_marks(self):
        """Save viva marks to backend"""
        if not self.current_student:
            return
        
        # Validate marks
        marks_text = self.marks_input.text().strip()
        if not marks_text:
            QMessageBox.warning(self, "Error", "Please enter marks")
            return
        
        try:
            marks = int(marks_text)
            if marks < 0 or marks > 100:
                QMessageBox.warning(self, "Error", "Marks must be between 0 and 100")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid number")
            return
        
        notes = self.notes_input.toPlainText().strip()
        
        # Get session ID from parent
        if hasattr(self.parent_window, 'dashboard_screen'):
            session_id = self.parent_window.dashboard_screen.current_session_id
            if not session_id:
                QMessageBox.warning(self, "Error", "No active session. Please start a lab session first.")
                return
        else:
            QMessageBox.warning(self, "Error", "Unable to determine session")
            return
        
        # Submit to backend
        result = api_client.submit_viva_marks(
            student_id=self.current_student['id'],
            session_id=session_id,
            marks=marks,
            notes=notes
        )
        
        if result["success"]:
            QMessageBox.information(self, "Success", f"Viva marks saved for {self.current_student.get('name')}")
            
            # Move to next student
            current_row = self.viva_list.currentRow()
            if current_row < self.viva_list.count() - 1:
                self.viva_list.setCurrentRow(current_row + 1)
                next_item = self.viva_list.item(current_row + 1)
                self._on_student_selected(next_item)
            else:
                self.student_lbl.setText("All students evaluated!")
                self.save_btn.setEnabled(False)
        else:
            QMessageBox.warning(self, "Error", f"Failed to save marks:\n{result['error']}")
    
    def showEvent(self, event):
        """Load students when screen is shown"""
        super().showEvent(event)
        self.load_students()

