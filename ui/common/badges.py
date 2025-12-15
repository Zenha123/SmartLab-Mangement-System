from PyQt6.QtWidgets import QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPainter, QPixmap

from ui.theme import Theme


class StatusDot(QLabel):
    def __init__(self, color: str, size: int = 10, tooltip: str | None = None):
        super().__init__()
        self.size_val = size
        self.color = QColor(color)
        self.setFixedSize(QSize(size, size))
        if tooltip:
            self.setToolTip(tooltip)
        self._paint()

    def _paint(self):
        pix = QPixmap(self.size_val, self.size_val)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.size_val, self.size_val)
        painter.end()
        self.setPixmap(pix)


class ModeBadge(QFrame):
    def __init__(self, text: str, color: str):
        super().__init__()
        self.setObjectName("modeBadge")
        self.setStyleSheet(
            f"""
            QFrame#modeBadge {{
                background: {color}22;
                border: 1px solid {color};
                border-radius: 10px;
                padding: 2px 8px;
            }}
            QLabel {{
                color: {color};
                font-weight: 600;
            }}
            """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        lbl = QLabel(text.upper())
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

