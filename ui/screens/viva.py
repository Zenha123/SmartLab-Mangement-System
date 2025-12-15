from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QHBoxLayout, QLineEdit, QPushButton

from ui.common.cards import CardFrame
from ui.theme import heading_font, Theme
from data.mock_data import viva_rows


class VivaScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("Viva Mode")
        title.setFont(heading_font(18))
        root.addWidget(title)

        main = QHBoxLayout()
        main.setSpacing(12)

        list_card = CardFrame()
        viva_list = QListWidget()
        for row in viva_rows:
            status = row["status"]
            marks = f" - Marks: {row['marks']}" if row["marks"] is not None else ""
            item = QListWidgetItem(f"{row['name']} - {status}{marks}")
            viva_list.addItem(item)
        list_card.layout.addWidget(QLabel("Students"))
        list_card.layout.addWidget(viva_list)
        main.addWidget(list_card, stretch=2)

        eval_card = CardFrame()
        eval_card.layout.addWidget(QLabel("Evaluation"))
        self.student_lbl = QLabel("Current: Andrea John")
        self.marks_input = QLineEdit()
        self.marks_input.setPlaceholderText("Marks")
        self.save_btn = QPushButton("Save & Next")
        self.save_btn.setStyleSheet(f"background: {Theme.secondary};")
        eval_card.layout.addWidget(self.student_lbl)
        eval_card.layout.addWidget(self.marks_input)
        eval_card.layout.addWidget(self.save_btn)
        eval_card.layout.addStretch(1)
        main.addWidget(eval_card, stretch=1)

        root.addLayout(main)
        root.addStretch(1)

