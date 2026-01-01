from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont

from ui.theme import Theme, heading_font, body_font


class CardFrame(QFrame):
    def __init__(self, parent=None, padding: int = 16, hoverable: bool = True):
        super().__init__(parent)
        self.setObjectName("card")
        self.hoverable = hoverable
        self._shadow_offset = 0
        
        # Animation for hover effect
        if hoverable:
            self.shadow_anim = QPropertyAnimation(self, b"shadowOffset")
            self.shadow_anim.setDuration(200)
            self.shadow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.setStyleSheet(
            f"""
            QFrame#card {{
                background: {Theme.card_bg};
                border: 1px solid {Theme.border};
                border-radius: 12px;
            }}
            """
        )
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(padding, padding, padding, padding)
        self.layout.setSpacing(10)
        
        if hoverable:
            self.setMouseTracking(True)
    
    def enterEvent(self, event):
        if self.hoverable:
            self.shadow_anim.setStartValue(0)
            self.shadow_anim.setEndValue(4)
            self.shadow_anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        if self.hoverable:
            self.shadow_anim.setStartValue(self._shadow_offset)
            self.shadow_anim.setEndValue(0)
            self.shadow_anim.start()
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.hoverable and self._shadow_offset > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Draw shadow
            shadow_color = QColor(0, 0, 0, 20)
            painter.setBrush(shadow_color)
            painter.drawRoundedRect(
                self.rect().adjusted(self._shadow_offset, self._shadow_offset, 
                                   -self._shadow_offset, -self._shadow_offset),
                12, 12
            )
            painter.end()
    
    def getShadowOffset(self):
        return self._shadow_offset
    
    def setShadowOffset(self, value):
        self._shadow_offset = value
        self.update()
    
    shadowOffset = pyqtProperty(int, getShadowOffset, setShadowOffset)


class StatCard(CardFrame):
    def __init__(self, title: str, value: str, accent: str = Theme.primary, 
                 subtitle: str | None = None, icon: str | None = None):
        super().__init__(padding=20, hoverable=True)
        
        # Icon + Title row
        if icon:
            header_layout = QHBoxLayout()
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet(f"font-size: 24px; color: {accent};")
            header_layout.addWidget(icon_lbl)
            header_layout.addStretch()
            self.layout.addLayout(header_layout)
        
        title_lbl = QLabel(title)
        title_lbl.setFont(body_font(12, QFont.Weight.Medium))
        title_lbl.setStyleSheet(f"color: {Theme.text_muted}; text-transform: uppercase; letter-spacing: 0.5px;")

        value_lbl = QLabel(value)
        value_lbl.setFont(heading_font(28, bold=True))
        value_lbl.setStyleSheet(f"color: {accent}; font-weight: 700;")
        self.value_label = value_lbl  # Store reference for updates

        self.layout.addWidget(title_lbl)
        self.layout.addWidget(value_lbl)
        
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setFont(body_font(11))
            sub_lbl.setStyleSheet(f"color: {Theme.text_muted};")
            self.layout.addWidget(sub_lbl)
        
        self.layout.addStretch(1)
        
        # Add subtle accent line at bottom
        accent_line = QFrame()
        accent_line.setFixedHeight(3)
        accent_line.setStyleSheet(f"background: {accent}; border-radius: 2px;")
        self.layout.addWidget(accent_line)
    
    def update_value(self, new_value: str):
        """Update the value displayed on the card"""
        self.value_label.setText(new_value)


class KeyValueRow(QFrame):
    def __init__(self, label: str, value: str, accent: str = Theme.text_primary):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(12)
        k_lbl = QLabel(label)
        k_lbl.setFont(body_font(13))
        k_lbl.setStyleSheet(f"color: {Theme.text_muted};")
        v_lbl = QLabel(value)
        v_lbl.setFont(body_font(13, QFont.Weight.DemiBold))
        v_lbl.setStyleSheet(f"color: {accent};")
        layout.addWidget(k_lbl)
        layout.addStretch()
        layout.addWidget(v_lbl, alignment=Qt.AlignmentFlag.AlignRight)

