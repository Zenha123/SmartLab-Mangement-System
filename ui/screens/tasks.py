from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QTextEdit, QPushButton, QComboBox, QTableWidgetItem

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.theme import heading_font, Theme
from data.mock_data import task_rows, students


class TasksScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("Task & File Management")
        title.setFont(heading_font(18))
        root.addWidget(title)

        form_card = CardFrame()
        form = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Task title")
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Description")
        self.batch_combo = QComboBox()
        self.batch_combo.addItems(["Batch 1", "Batch 2"])
        upload_btn = QPushButton("Upload Task")
        upload_btn.setStyleSheet(f"background: {Theme.primary};")

        form.addWidget(self.task_input)
        form.addWidget(self.batch_combo)
        form.addWidget(upload_btn)
        form_card.layout.addLayout(form)
        form_card.layout.addWidget(self.desc_input)
        root.addWidget(form_card)

        table_card = CardFrame()
        table = StyledTableWidget(len(task_rows), 4)
        table.setHorizontalHeaderLabels(["Student", "File", "Time", "Auto-delete"])
        for r, item in enumerate(task_rows):
            table.setItem(r, 0, QTableWidgetItem(item["student"]))
            table.setItem(r, 1, QTableWidgetItem(item["file"]))
            table.setItem(r, 2, QTableWidgetItem(item["time"]))
            table.setItem(r, 3, QTableWidgetItem(item["auto"]))
        table_card.layout.addWidget(table)
        root.addWidget(table_card)
        root.addStretch(1)

