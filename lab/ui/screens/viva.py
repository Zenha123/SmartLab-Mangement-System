from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout, QLineEdit, QPushButton, QTextEdit

from ui.common.cards import CardFrame
from ui.common.badges import ModeBadge
from ui.theme import heading_font, Theme, body_font
from data.mock_data import viva_rows
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class VivaScreen(QWidget):
    def __init__(self):
        super().__init__()
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
        
        viva_list = QListWidget()
        viva_list.setStyleSheet(
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
        for row in viva_rows:
            status = row["status"]
            marks = f" - {row['marks']}/100" if row["marks"] is not None else ""
            
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(8, 8, 8, 8)
            item_layout.setSpacing(12)
            
            name_label = QLabel(f"👤 {row['name']}")
            name_label.setFont(body_font(13, QFont.Weight.DemiBold))
            name_label.setStyleSheet(f"color: {Theme.text_primary};")
            
            status_badge = ModeBadge(
                status, 
                Theme.success if status == "Completed" else Theme.warning,
                size="small"
            )
            
            marks_label = QLabel(marks)
            marks_label.setFont(body_font(12, QFont.Weight.Bold))
            marks_label.setStyleSheet(f"color: {Theme.secondary};")
            
            item_layout.addWidget(name_label)
            item_layout.addStretch()
            item_layout.addWidget(status_badge)
            if marks:
                item_layout.addWidget(marks_label)
            
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            viva_list.addItem(item)
            viva_list.setItemWidget(item, item_widget)
        
        list_card.layout.addWidget(viva_list)
        main.addWidget(list_card, stretch=2)

        # Evaluation Panel
        eval_card = CardFrame(padding=24)
        eval_heading = QLabel("📝 Evaluation")
        eval_heading.setFont(body_font(16, QFont.Weight.Bold))
        eval_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        eval_card.layout.addWidget(eval_heading)
        
        self.student_lbl = QLabel("Current Student: Andrea John")
        self.student_lbl.setFont(body_font(14, QFont.Weight.DemiBold))
        self.student_lbl.setStyleSheet(f"color: {Theme.primary}; padding: 12px; background: {Theme.primary}10; border-radius: 8px; margin-bottom: 16px;")
        eval_card.layout.addWidget(self.student_lbl)
        
        marks_label = QLabel("Marks:")
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
        eval_card.layout.addWidget(self.save_btn)
        eval_card.layout.addStretch(1)
        main.addWidget(eval_card, stretch=1)

        root.addLayout(main)
        root.addStretch(1)

