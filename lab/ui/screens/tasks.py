from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QComboBox, QTableWidgetItem, QVBoxLayout as VLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.theme import heading_font, Theme, body_font
from data.mock_data import task_rows, students


class TasksScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("📝 Task & File Management")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # Upload form
        form_card = CardFrame(padding=20)
        form_heading = QLabel("📤 Upload New Task")
        form_heading.setFont(body_font(16, QFont.Weight.Bold))
        form_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        form_card.layout.addWidget(form_heading)
        
        # Task title and batch
        top_row = QHBoxLayout()
        top_row.setSpacing(12)
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
        self.batch_combo = QComboBox()
        self.batch_combo.addItems(["Batch 1", "Batch 2"])
        self.batch_combo.setStyleSheet(
            f"""
            QComboBox {{
                border: 1px solid {Theme.border};
                border-radius: 8px;
                padding: 10px 14px;
                min-width: 120px;
            }}
            QComboBox:focus {{
                border: 2px solid {Theme.primary};
            }}
            """
        )
        top_row.addWidget(self.task_input, stretch=2)
        top_row.addWidget(self.batch_combo, stretch=1)
        form_card.layout.addLayout(top_row)
        
        # Description
        desc_label = QLabel("Description:")
        desc_label.setFont(body_font(12, QFont.Weight.Medium))
        desc_label.setStyleSheet(f"color: {Theme.text_secondary}; margin-top: 12px; margin-bottom: 6px;")
        form_card.layout.addWidget(desc_label)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter task description...")
        self.desc_input.setMaximumHeight(100)
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
        
        # Upload button
        upload_btn = QPushButton("📤 Upload Task")
        upload_btn.setProperty("class", "primary")
        upload_btn.setStyleSheet(
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
        form_card.layout.addWidget(upload_btn)
        root.addWidget(form_card)

        # Submissions table
        table_card = CardFrame(padding=20)
        table_heading = QLabel("📋 Student Submissions")
        table_heading.setFont(body_font(16, QFont.Weight.Bold))
        table_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        table_card.layout.addWidget(table_heading)
        
        table = StyledTableWidget(len(task_rows), 4)
        table.setHorizontalHeaderLabels(["Student", "File", "Time", "Auto-delete"])
        for r, item in enumerate(task_rows):
            student_item = QTableWidgetItem(f"👤 {item['student']}")
            student_item.setFont(body_font(13, QFont.Weight.Medium))
            table.setItem(r, 0, student_item)
            
            file_item = QTableWidgetItem(f"📎 {item['file']}")
            file_item.setFont(body_font(12))
            file_item.setForeground(QColor(Theme.primary))
            table.setItem(r, 1, file_item)
            
            time_item = QTableWidgetItem(item["time"])
            time_item.setFont(body_font(12))
            time_item.setForeground(QColor(Theme.text_muted))
            table.setItem(r, 2, time_item)
            
            auto_item = QTableWidgetItem(item["auto"])
            auto_item.setFont(body_font(12))
            auto_item.setForeground(QColor(Theme.success if item["auto"] == "Yes" else Theme.text_muted))
            table.setItem(r, 3, auto_item)
        table_card.layout.addWidget(table)
        root.addWidget(table_card)
        root.addStretch(1)

