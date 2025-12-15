from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTextEdit
from PyQt6.QtCore import Qt

from ui.common.cards import CardFrame, KeyValueRow
from ui.theme import heading_font, Theme


class SingleStudentScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Single Student View")
        title.setFont(heading_font(18))
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        main = QHBoxLayout()
        main.setSpacing(12)

        viewer = CardFrame()
        viewer.setMinimumHeight(260)
        viewer.layout.addWidget(QLabel("Live view placeholder"))
        viewer.layout.addStretch(1)
        main.addWidget(viewer, stretch=3)

        side = CardFrame()
        side.layout.addWidget(KeyValueRow("Student", "Andrea John"))
        side.layout.addWidget(KeyValueRow("PC ID", "PC-01"))
        side.layout.addWidget(KeyValueRow("Status", "Online", Theme.success))
        side.layout.addWidget(KeyValueRow("Mode", "Normal"))

        actions = QVBoxLayout()
        for text, color in [
            ("Lock PC", Theme.danger),
            ("Block Internet", Theme.warning),
            ("Kill App", Theme.danger),
            ("Send Warning", Theme.warning),
            ("Start Viva", Theme.secondary),
        ]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"background: {color};")
            actions.addWidget(btn)
        actions.addStretch(1)
        side.layout.addLayout(actions)
        main.addWidget(side, stretch=1)
        root.addLayout(main)

        notes = CardFrame()
        notes.layout.addWidget(QLabel("Notes / Communication"))
        notes.layout.addWidget(QTextEdit("UI-only notes area..."))
        root.addWidget(notes)
        root.addStretch(1)

