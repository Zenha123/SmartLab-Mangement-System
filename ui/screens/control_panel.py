from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

from ui.theme import heading_font, Theme
from ui.common.cards import CardFrame


class ControlPanelScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("Control Panel")
        title.setFont(heading_font(18))
        root.addWidget(title)

        card = CardFrame()
        grid = QGridLayout()
        grid.setSpacing(10)
        actions = [
            ("Lock All PCs", Theme.danger),
            ("Unlock All PCs", Theme.secondary),
            ("Block Internet", Theme.warning),
            ("Unblock Internet", Theme.secondary),
            ("Enable USB", Theme.primary),
            ("Disable USB", Theme.warning),
            ("App Whitelist", Theme.primary),
        ]
        for i, (text, color) in enumerate(actions):
            btn = QPushButton(text)
            btn.setStyleSheet(f"background: {color};")
            btn.clicked.connect(lambda _, t=text: self.confirm_action(t))
            grid.addWidget(btn, i // 2, i % 2)
        card.layout.addLayout(grid)
        root.addWidget(card)
        root.addStretch(1)

    def confirm_action(self, action: str):
        QMessageBox.information(self, "Action", f"'{action}' executed (UI-only demo).")

