from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QImage, QPixmap

from ui.common.cards import CardFrame
from ui.common.badges import StatusDot
from ui.theme import heading_font, Theme, body_font


class SingleStudentScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.student_id = None
        self.webrtc_manager = None

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # ── Header with Back button ──────────────────────────────────────────
        header = QHBoxLayout()

        back_btn = QPushButton("← Back")
        back_btn.setFixedWidth(90)
        back_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                color: {Theme.primary};
                border: 1px solid {Theme.primary};
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {Theme.primary}18;
            }}
            """
        )
        back_btn.clicked.connect(self._go_back)
        header.addWidget(back_btn)

        title = QLabel("👤 Single Student View")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-left: 12px;")
        header.addWidget(title)
        header.addStretch(1)
        root.addLayout(header)

        # ── Main area ────────────────────────────────────────────────────────
        main = QHBoxLayout()
        main.setSpacing(20)

        # Live viewer card
        viewer = CardFrame(padding=20)
        viewer.setMinimumHeight(400)

        self.viewer_label = QLabel("📺 Live Screen View\n(Connecting…)")
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

        self.stop_btn = QPushButton("⏹ Stop Streaming")
        self.stop_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.danger};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 700;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {Theme.danger}cc;
            }}
            """
        )
        self.stop_btn.clicked.connect(self._stop_streaming)
        viewer.layout.addWidget(self.stop_btn)

        main.addWidget(viewer, stretch=3)

        # ── Side panel ───────────────────────────────────────────────────────
        side = CardFrame(padding=20)

        side_heading = QLabel("Student Details")
        side_heading.setFont(body_font(14, QFont.Weight.Bold))
        side_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        side.layout.addWidget(side_heading)

        # Dynamic info rows — built with _info_row() so we hold direct
        # references to the value QLabel and can update them freely.
        self.val_name,   row_name   = self._info_row("👤 Student", "—")
        self.val_pc,     row_pc     = self._info_row("💻 PC ID",   "—")
        self.val_status, row_status = self._info_row("🟢 Status",  "—")
        self.val_mode,   row_mode   = self._info_row("📋 Mode",    "—")

        side.layout.addWidget(row_name)
        side.layout.addWidget(row_pc)
        side.layout.addWidget(row_status)
        side.layout.addWidget(row_mode)

        side.layout.addSpacing(20)

        actions_heading = QLabel("Actions")
        actions_heading.setFont(body_font(14, QFont.Weight.Bold))
        actions_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 12px;")
        side.layout.addWidget(actions_heading)

        actions = QVBoxLayout()
        actions.setSpacing(10)
        action_buttons = [
            ("🔒 Lock PC",        Theme.danger),
            ("🚫 Block Internet", Theme.warning),
            ("❌ Kill App",        Theme.danger),
            ("⚠️ Send Warning",   Theme.warning),
            ("🎤 Start Viva",     Theme.secondary),
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

        # ── Notes section ────────────────────────────────────────────────────
        notes = CardFrame(padding=20)
        notes_heading = QLabel("📝 Notes / Communication")
        notes_heading.setFont(body_font(14, QFont.Weight.Bold))
        notes_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 12px;")
        notes.layout.addWidget(notes_heading)

        notes_input = QTextEdit()
        notes_input.setPlaceholderText("Add notes or send communication to student…")
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

    # ── Public API ───────────────────────────────────────────────────────────

    @staticmethod
    def _info_row(label_text: str, value_text: str):
        """
        Build a horizontal key/value row.
        Returns (value_QLabel, row_QWidget) so the caller can update the value freely.
        """
        from PyQt6.QtWidgets import QWidget, QHBoxLayout
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 4, 0, 4)

        lbl = QLabel(label_text)
        lbl.setFont(body_font(12))
        lbl.setStyleSheet(f"color: {Theme.text_muted};")
        lbl.setFixedWidth(100)

        val = QLabel(value_text)
        val.setFont(body_font(12))
        val.setStyleSheet(f"color: {Theme.text_primary}; font-weight: 500;")
        val.setWordWrap(True)

        h.addWidget(lbl)
        h.addWidget(val)
        h.addStretch()
        return val, row

    def set_webrtc_manager(self, manager):
        self.webrtc_manager = manager

    def load_student_data(self, student: dict):
        """
        Populate the side panel with real student data.
        Call this from live_monitor before switching to this screen.

        Expected keys: name, student_id (pc label), status, current_mode
        """
        name   = student.get("name", "—")
        pc     = student.get("student_id", student.get("pc_id", "—"))
        status = student.get("status", "offline").capitalize()
        mode   = student.get("current_mode", student.get("mode", "Normal"))

        self.val_name.setText(name)
        self.val_pc.setText(str(pc))

        status_color = Theme.success if status.lower() == "online" else Theme.danger
        self.val_status.setText(status)
        self.val_status.setStyleSheet(f"color: {status_color}; font-weight: 600;")

        self.val_mode.setText(str(mode))

    def update_video_frame(self, student_id, frame):
        """Receive a BGR numpy frame and paint it into the viewer label."""
        height, width, channel = frame.shape
        bytes_per_line = channel * width

        qt_img = QImage(
            frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_BGR888
        ).copy()

        pixmap = QPixmap.fromImage(qt_img)
        self.viewer_label.setPixmap(
            pixmap.scaled(
                self.viewer_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    # ── Private helpers ──────────────────────────────────────────────────────

    def _stop_streaming(self):
        if self.webrtc_manager and self.student_id is not None:
            self.webrtc_manager.stop_monitoring(self.student_id)

        # Reset viewer back to placeholder
        self.viewer_label.setPixmap(QPixmap())
        self.viewer_label.setText("📺 Live Screen View\n(Stopped)")

    def _go_back(self):
        """Navigate back to Live Monitor without stopping the stream."""
        main_window = self.window()
        if hasattr(main_window, "live_monitor_screen"):
            main_window.stack.setCurrentWidget(main_window.live_monitor_screen)

    '''def _stop_and_go_back(self):
        """Stop streaming AND navigate back to Live Monitor."""
        self._stop_streaming()
        self._go_back()'''