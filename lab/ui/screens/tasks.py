from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.common.cards import CardFrame
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


class TasksScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window = parent
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("📝 Task & File Management")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # Upload form
        form_card = CardFrame(padding=20)
        form_heading = QLabel("📤 Create New Task")
        form_heading.setFont(body_font(16, QFont.Weight.Bold))
        form_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        form_card.layout.addWidget(form_heading)
        
        # Task title
        title_label = QLabel("Task Title:")
        title_label.setFont(body_font(12, QFont.Weight.Medium))
        title_label.setStyleSheet(f"color: {Theme.text_secondary}; margin-bottom: 6px;")
        form_card.layout.addWidget(title_label)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter task title...")
        self.task_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {Theme.border};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Theme.primary};
            }}
            """
        )
        form_card.layout.addWidget(self.task_input)
        
        # Description
        desc_label = QLabel("Description:")
        desc_label.setFont(body_font(12, QFont.Weight.Medium))
        desc_label.setStyleSheet(f"color: {Theme.text_secondary}; margin-top: 12px; margin-bottom: 6px;")
        form_card.layout.addWidget(desc_label)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter task description and instructions...")
        self.desc_input.setMaximumHeight(120)
        self.desc_input.setStyleSheet(
            f"""
            QTextEdit {{
                border: 1px solid {Theme.border};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border: 2px solid {Theme.primary};
            }}
            """
        )
        form_card.layout.addWidget(self.desc_input)
        
        # Create button
        create_btn = QPushButton("📤 Create Task")
        create_btn.setProperty("class", "primary")
        create_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.primary};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 700;
                font-size: 14px;
                margin-top: 12px;
            }}
            QPushButton:hover {{
                background: {Theme.primary_hover};
            }}
            """
        )
        create_btn.clicked.connect(self._create_task)
        form_card.layout.addWidget(create_btn)
        root.addWidget(form_card)

        # Info card
        info_card = CardFrame(padding=20)
        info_label = QLabel("ℹ️ Tasks will be distributed to all students in the selected batch")
        info_label.setFont(body_font(13))
        info_label.setStyleSheet(f"color: {Theme.text_muted};")
        info_label.setWordWrap(True)
        info_card.layout.addWidget(info_label)
        root.addWidget(info_card)
        
        root.addStretch(1)
    
    def _create_task(self):
        """Create a new task via backend API"""
        title = self.task_input.text().strip()
        description = self.desc_input.toPlainText().strip()
        
        if not title:
            QMessageBox.warning(self, "Error", "Please enter a task title")
            return
        
        if not description:
            QMessageBox.warning(self, "Error", "Please enter a task description")
            return
        
        # Get batch_id from parent
        if not hasattr(self.parent_window, 'current_batch_id') or self.parent_window.current_batch_id is None:
            QMessageBox.warning(self, "Error", "Please select a batch first")
            return
        
        batch_id = self.parent_window.current_batch_id
        
        # Call API to create task
        result = api_client.create_task(
            batch_id=batch_id,
            title=title,
            description=description
        )
        
        if result["success"]:
            QMessageBox.information(
                self, 
                "Success", 
                f"Task '{title}' created successfully!\nIt has been distributed to all students in the batch."
            )
            # Clear form
            self.task_input.clear()
            self.desc_input.clear()
        else:
            QMessageBox.warning(self, "Error", f"Failed to create task:\n{result['error']}")

