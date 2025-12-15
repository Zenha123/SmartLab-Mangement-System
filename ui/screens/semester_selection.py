from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt

from ui.common.cards import CardFrame
from ui.theme import heading_font, Theme
from data.mock_data import semesters


class SemesterSelectionScreen(QWidget):
    batch_selected = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Select Semester & Batch")
        title.setFont(heading_font(18))
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)
        row = col = 0
        for sem, batches in semesters.items():
            card = CardFrame()
            card.layout.setSpacing(6)
            lbl = QLabel(sem)
            lbl.setFont(heading_font(14, bold=False))
            card.layout.addWidget(lbl)
            btn_row = QGridLayout()
            for i, batch in enumerate(batches):
                btn = QPushButton(batch)
                btn.setStyleSheet(
                    f"QPushButton {{ background: {Theme.secondary}; padding: 6px 10px; }}"
                    f"QPushButton:hover {{ background: #00796b; }}"
                )
                btn.clicked.connect(lambda _, s=sem, b=batch: self.batch_selected.emit(s, b))
                btn_row.addWidget(btn, 0, i)
            card.layout.addLayout(btn_row)
            grid.addWidget(card, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1
        layout.addLayout(grid)
        layout.addStretch(1)

