from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from ui.common.cards import CardFrame
from ui.theme import heading_font, Theme, body_font
from data.mock_data import semesters


class SemesterSelectionScreen(QWidget):
    batch_selected = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        # Set background color
        self.setStyleSheet(f"background: {Theme.background};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("📚 Select Semester & Batch")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Choose a semester and batch to manage")
        subtitle.setFont(body_font(13))
        subtitle.setStyleSheet(f"color: {Theme.text_muted}; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        grid = QGridLayout()
        grid.setSpacing(16)
        row = col = 0
        for sem, batches in semesters.items():
            card = CardFrame(padding=20, hoverable=True)
            card.layout.setSpacing(12)
            
            # Semester label
            lbl = QLabel(sem)
            lbl.setFont(heading_font(16, bold=True))
            lbl.setStyleSheet(f"color: {Theme.primary}; margin-bottom: 8px;")
            card.layout.addWidget(lbl)
            
            # Batch buttons
            btn_row = QHBoxLayout()
            btn_row.setSpacing(10)
            for i, batch in enumerate(batches):
                btn = QPushButton(f"📦 {batch}")
                btn.setProperty("class", "secondary")
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background: {Theme.secondary};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 10px 18px;
                        font-weight: 600;
                        font-size: 13px;
                    }}
                    QPushButton:hover {{
                        background: #16A085;
                    }}
                    """
                )
                btn.clicked.connect(lambda checked, s=sem, b=batch: self.batch_selected.emit(s, b))
                btn_row.addWidget(btn)
            btn_row.addStretch()
            card.layout.addLayout(btn_row)
            
            grid.addWidget(card, row, col)
            col += 1
            if col == 4:  # 4 columns for better layout
                col = 0
                row += 1
        layout.addLayout(grid)
        layout.addStretch(1)

