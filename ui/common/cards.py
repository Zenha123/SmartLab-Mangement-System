from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

from ui.theme import Theme, heading_font, body_font


class CardFrame(QFrame):
    def __init__(self, parent=None, padding: int = 12):
        super().__init__(parent)
        self.setObjectName("card")
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
        self.layout.setSpacing(8)


class StatCard(CardFrame):
    def __init__(self, title: str, value: str, accent: str = Theme.primary, subtitle: str | None = None):
        super().__init__()
        title_lbl = QLabel(title)
        title_lbl.setFont(body_font(11))
        title_lbl.setStyleSheet(f"color: {Theme.text_muted};")

        value_lbl = QLabel(value)
        value_lbl.setFont(heading_font(20))
        value_lbl.setStyleSheet(f"color: {accent};")

        self.layout.addWidget(title_lbl)
        self.layout.addWidget(value_lbl)
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet(f"color: {Theme.text_muted};")
            self.layout.addWidget(sub_lbl)
        self.layout.addStretch(1)


class KeyValueRow(QFrame):
    def __init__(self, label: str, value: str, accent: str = Theme.text_primary):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        k_lbl = QLabel(label)
        k_lbl.setStyleSheet(f"color: {Theme.text_muted};")
        v_lbl = QLabel(value)
        v_lbl.setStyleSheet(f"color: {accent}; font-weight: 600;")
        layout.addWidget(k_lbl)
        layout.addStretch()
        layout.addWidget(v_lbl, alignment=Qt.AlignmentFlag.AlignRight)

