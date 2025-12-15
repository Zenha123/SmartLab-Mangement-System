from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QTableWidgetItem, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

from ui.common.cards import StatCard, CardFrame
from ui.common.tables import StyledTableWidget
from ui.theme import heading_font, Theme
from data.mock_data import evaluation_rows


class EvaluationScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("Evaluation")
        title.setFont(heading_font(18))
        root.addWidget(title)

        stats = QGridLayout()
        stats.setSpacing(10)
        stats.addWidget(StatCard("Assignment Received", "43"), 0, 0)
        stats.addWidget(StatCard("Yet to Receive", "13", Theme.warning), 0, 1)
        stats.addWidget(StatCard("Evaluated", "20", Theme.secondary), 0, 2)
        stats.addWidget(StatCard("Yet to Evaluate", "13", Theme.primary), 0, 3)
        root.addLayout(stats)

        card = CardFrame()
        table = StyledTableWidget(len(evaluation_rows), 6)
        table.setHorizontalHeaderLabels(["Student", "Student ID", "Submission Time", "File", "Grades", "Feedback"])
        for r, item in enumerate(evaluation_rows):
            table.setItem(r, 0, QTableWidgetItem(item["name"]))
            table.setItem(r, 1, QTableWidgetItem(item["id"]))
            table.setItem(r, 2, QTableWidgetItem(item["submitted"]))
            table.setItem(r, 3, QTableWidgetItem(item["file"]))

            grade_input = QLineEdit()
            grade_input.setPlaceholderText("/100")
            if item["grade"]:
                grade_input.setText(item["grade"])
            table.setCellWidget(r, 4, grade_input)

            feedback_input = QLineEdit()
            feedback_input.setPlaceholderText("Feedback")
            if item["feedback"]:
                feedback_input.setText(item["feedback"])
            btn = QPushButton("Publish")
            btn.setStyleSheet(f"background: {Theme.primary};")

            hb = QHBoxLayout()
            hb.setContentsMargins(0, 0, 0, 0)
            hb.addWidget(feedback_input)
            hb.addWidget(btn)
            cell = QWidget()
            cell.setLayout(hb)
            table.setCellWidget(r, 5, cell)
        card.layout.addWidget(table)
        root.addWidget(card)
        root.addStretch(1)

