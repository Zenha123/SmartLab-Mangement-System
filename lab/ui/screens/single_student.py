from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.common.cards import CardFrame, KeyValueRow
from ui.common.badges import StatusDot
from ui.theme import heading_font, Theme, body_font
from PyQt6.QtGui import QImage, QPixmap


class SingleStudentScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("👤 Single Student View")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        main = QHBoxLayout()
        main.setSpacing(20)

        # Live view area
        viewer = CardFrame(padding=20)
        viewer.setMinimumHeight(400)
        self.viewer_label = QLabel("📺 Live Screen View\n(Placeholder)")
        self.viewer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viewer_label.setFont(body_font(16))
        self.viewer_label.setStyleSheet(
            f"""
            QLabel {{
                background: {Theme.background};
                border: 2px dashed {Theme.border};
                border-radius: 12px;
                padding: 40px;
                color: {Theme.text_muted};
            }}
            """
        )
        viewer.layout.addWidget(self.viewer_label)
        viewer.layout.addStretch(1)
        main.addWidget(viewer, stretch=3)

        # Side panel with details and actions
        side = CardFrame(padding=20)
        side_heading = QLabel("Student Details")
        side_heading.setFont(body_font(14, QFont.Weight.Bold))
        side_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        side.layout.addWidget(side_heading)
        
        side.layout.addWidget(KeyValueRow("👤 Student", "Andrea John"))
        side.layout.addWidget(KeyValueRow("💻 PC ID", "PC-01"))
        side.layout.addWidget(KeyValueRow("🟢 Status", "Online", Theme.success))
        side.layout.addWidget(KeyValueRow("📋 Mode", "Normal"))
        
        side.layout.addSpacing(20)
        actions_heading = QLabel("Actions")
        actions_heading.setFont(body_font(14, QFont.Weight.Bold))
        actions_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 12px;")
        side.layout.addWidget(actions_heading)

        actions = QVBoxLayout()
        actions.setSpacing(10)
        action_buttons = [
            ("🔒 Lock PC", Theme.danger),
            ("🚫 Block Internet", Theme.warning),
            ("❌ Kill App", Theme.danger),
            ("⚠️ Send Warning", Theme.warning),
            ("🎤 Start Viva", Theme.secondary),
        ]
        for text, color in action_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-weight: 600;
                    font-size: 12px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background: {color}dd;
                }}
                """
            )
            actions.addWidget(btn)
        actions.addStretch(1)
        side.layout.addLayout(actions)
        main.addWidget(side, stretch=1)
        root.addLayout(main)

        # Notes section
        notes = CardFrame(padding=20)
        notes_heading = QLabel("📝 Notes / Communication")
        notes_heading.setFont(body_font(14, QFont.Weight.Bold))
        notes_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 12px;")
        notes.layout.addWidget(notes_heading)
        
        notes_input = QTextEdit()
        notes_input.setPlaceholderText("Add notes or send communication to student...")
        notes_input.setMinimumHeight(100)
        notes_input.setStyleSheet(
            f"""
            QTextEdit {{
                border: 1px solid {Theme.border};
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border: 2px solid {Theme.primary};
            }}
            """
        )
        notes.layout.addWidget(notes_input)
        root.addWidget(notes)
        root.addStretch(1)

    

    def update_video_frame(self, student_id, frame):

        height, width, channel = frame.shape
        bytes_per_line = channel * width

        qt_img = QImage(
            frame.copy().data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_BGR888
        )

        pixmap = QPixmap.fromImage(qt_img)

        self.viewer_label.setPixmap(
            pixmap.scaled(
                self.viewer_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
