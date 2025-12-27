from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QTableWidgetItem, QHBoxLayout, QLineEdit, QPushButton, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.common.cards import StatCard, CardFrame
from ui.common.tables import StyledTableWidget
from ui.theme import heading_font, Theme, body_font
from data.mock_data import evaluation_rows


class EvaluationScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("✅ Evaluation")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # Summary cards with icons
        stats = QGridLayout()
        stats.setSpacing(16)
        stats.addWidget(StatCard("📄 Assignment Received", "43", Theme.info, icon="📄"), 0, 0)
        stats.addWidget(StatCard("⏳ Yet to Receive", "13", Theme.warning, icon="⏳"), 0, 1)
        stats.addWidget(StatCard("✅ Evaluated", "20", Theme.success, icon="✅"), 0, 2)
        stats.addWidget(StatCard("📝 Yet to Evaluate", "13", Theme.primary, icon="📝"), 0, 3)
        root.addLayout(stats)

        card = CardFrame(padding=20)
        table = StyledTableWidget(len(evaluation_rows), 6)
        table.setHorizontalHeaderLabels(["Student", "Student ID", "Date of submission", "Submission file", "Grades", "Feedback"])
        
        for r, item in enumerate(evaluation_rows):
            # Student name with avatar
            name_item = QTableWidgetItem(f"👤 {item['name']}")
            name_item.setFont(body_font(13, QFont.Weight.Medium))
            table.setItem(r, 0, name_item)
            
            # Student ID
            id_item = QTableWidgetItem(item["id"])
            id_item.setFont(body_font(12))
            id_item.setForeground(QColor(Theme.text_secondary))
            table.setItem(r, 1, id_item)
            
            # Submission time
            time_item = QTableWidgetItem(item["submitted"])
            time_item.setFont(body_font(12))
            time_item.setForeground(QColor(Theme.text_muted))
            table.setItem(r, 2, time_item)
            
            # File name with icon
            file_item = QTableWidgetItem(f"📎 {item['file']}")
            file_item.setFont(body_font(12))
            file_item.setForeground(QColor(Theme.primary))
            table.setItem(r, 3, file_item)

            # Grades input
            grade_widget = QWidget()
            grade_layout = QHBoxLayout(grade_widget)
            grade_layout.setContentsMargins(8, 4, 8, 4)
            grade_input = QLineEdit()
            grade_input.setPlaceholderText("/100")
            grade_input.setStyleSheet(
                f"""
                QLineEdit {{
                    border: 1px solid {Theme.border};
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-size: 13px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {Theme.primary};
                }}
                """
            )
            if item["grade"]:
                grade_input.setText(item["grade"])
            grade_layout.addWidget(grade_input)
            table.setCellWidget(r, 4, grade_widget)

            # Feedback input with publish button
            feedback_widget = QWidget()
            feedback_layout = QHBoxLayout(feedback_widget)
            feedback_layout.setContentsMargins(8, 4, 8, 4)
            feedback_layout.setSpacing(8)
            
            feedback_input = QLineEdit()
            feedback_input.setPlaceholderText("Enter feedback...")
            feedback_input.setStyleSheet(
                f"""
                QLineEdit {{
                    border: 1px solid {Theme.border};
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-size: 13px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {Theme.primary};
                }}
                """
            )
            if item["feedback"]:
                feedback_input.setText(item["feedback"])
            
            btn = QPushButton("📤 Publish")
            btn.setProperty("class", "primary")
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background: {Theme.primary};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 12px;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background: {Theme.primary_hover};
                }}
                QPushButton:pressed {{
                    background: {Theme.primary_light};
                }}
                """
            )
            btn.clicked.connect(lambda checked, row=r: self._on_publish(row))
            
            feedback_layout.addWidget(feedback_input, stretch=1)
            feedback_layout.addWidget(btn)
            table.setCellWidget(r, 5, feedback_widget)
            
        card.layout.addWidget(table)
        root.addWidget(card)
        root.addStretch(1)
    
    def _on_publish(self, row: int):
        # Placeholder for publish action
        pass

