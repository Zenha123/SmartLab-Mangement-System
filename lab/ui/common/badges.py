from PyQt6.QtWidgets import QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPainter, QPixmap, QFont

from ui.theme import Theme


class StatusDot(QLabel):
    def __init__(self, color: str, size: int = 12, tooltip: str | None = None, animated: bool = True):
        super().__init__()
        self.size_val = size
        self.color = QColor(color)
        self.animated = animated
        self.setFixedSize(QSize(size + 4, size + 4))  # Extra space for glow
        if tooltip:
            self.setToolTip(tooltip)
        self._paint()

    def _paint(self):
        pix = QPixmap(self.size_val + 4, self.size_val + 4)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Outer glow for animated effect
        if self.animated:
            glow_color = QColor(self.color)
            glow_color.setAlpha(80)
            painter.setBrush(glow_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(2, 2, self.size_val, self.size_val)
        
        # Main dot
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, self.size_val - 4, self.size_val - 4)
        
        painter.end()
        self.setPixmap(pix)


class ModeBadge(QFrame):
    def __init__(self, text: str, color: str, size: str = "medium"):
        super().__init__()
        self.setObjectName("modeBadge")
        
        # Size variants
        size_map = {
            "small": {"padding": "4px 8px", "font": 10},
            "medium": {"padding": "6px 12px", "font": 11},
            "large": {"padding": "8px 16px", "font": 12}
        }
        size_config = size_map.get(size, size_map["medium"])
        
        self.setStyleSheet(
            f"""
            QFrame#modeBadge {{
                background: {color}15;
                border: 1.5px solid {color};
                border-radius: 12px;
                padding: {size_config['padding']};
            }}
            QLabel {{
                color: {color};
                font-weight: 700;
                font-size: {size_config['font']}px;
                letter-spacing: 0.5px;
            }}
            """
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        lbl = QLabel(text.upper())
        lbl.setFont(QFont("Segoe UI", size_config['font'], QFont.Weight.Bold))
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

