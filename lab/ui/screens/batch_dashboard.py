from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton,
    QHBoxLayout, QMessageBox, QDialog, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.common.cards import StatCard, CardFrame
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


# ══════════════════════════════════════════════════════════════
#  StyledDialog  —  replaces ALL QMessageBox calls
#  Buttons are always clearly visible with solid colours
# ══════════════════════════════════════════════════════════════

class StyledDialog(QDialog):
    """
    Reusable styled dialog with always-visible buttons.

    Modes
    -----
    "info"     → blue  icon,  single blue  OK button
    "question" → blue  icon,  two buttons (cancel = white, ok = blue)
    "danger"   → orange icon, two buttons (cancel = white, ok = red)

    Parameters
    ----------
    ok_text     : label for the primary / confirm button  (default "OK")
    cancel_text : if given, a white Cancel button is added on the left
    sub_text    : smaller grey text shown below the main message
    """

    def __init__(self, parent=None, title="", message="", sub_text="",
                 mode="info", ok_text="OK", cancel_text=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedWidth(420)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setStyleSheet("QDialog { background: #f5f5f5; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Body ──────────────────────────────────────────────
        body_w = QWidget()
        body_w.setStyleSheet("background: #f5f5f5;")
        body = QHBoxLayout(body_w)
        body.setContentsMargins(24, 24, 24, 20)
        body.setSpacing(16)
        body.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Coloured circle icon
        icon_lbl = QLabel("?" if mode == "danger" else "i")
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_bg = "#FF9800" if mode == "danger" else "#2196F3"
        icon_lbl.setStyleSheet(f"""
            QLabel {{
                background: {icon_bg};
                color: white;
                border-radius: 22px;
                font-size: 20px;
                font-weight: 900;
                font-style: italic;
                font-family: Georgia, serif;
            }}
        """)

        # Text
        txt_col = QVBoxLayout()
        txt_col.setSpacing(6)

        main_lbl = QLabel(message)
        main_lbl.setWordWrap(True)
        main_lbl.setStyleSheet(
            "color: #111; font-size: 13px; font-weight: 600; background: transparent;"
        )
        txt_col.addWidget(main_lbl)

        if sub_text:
            sub_lbl = QLabel(sub_text)
            sub_lbl.setWordWrap(True)
            sub_lbl.setStyleSheet(
                "color: #555; font-size: 12px; background: transparent;"
            )
            txt_col.addWidget(sub_lbl)

        body.addWidget(icon_lbl, 0, Qt.AlignmentFlag.AlignTop)
        body.addLayout(txt_col, 1)
        root.addWidget(body_w)

        # ── Divider ───────────────────────────────────────────
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #d0d0d0;")
        root.addWidget(divider)

        # ── Footer ────────────────────────────────────────────
        footer_w = QWidget()
        footer_w.setStyleSheet("background: #ebebeb;")
        footer = QHBoxLayout(footer_w)
        footer.setContentsMargins(16, 12, 16, 14)
        footer.setSpacing(10)
        footer.addStretch(1)

        # Optional Cancel / secondary button (white)
        if cancel_text:
            cancel_btn = QPushButton(cancel_text)
            cancel_btn.setFixedHeight(34)
            cancel_btn.setMinimumWidth(100)
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: #ffffff;
                    color: #333333;
                    border: 1px solid #bbbbbb;
                    border-radius: 5px;
                    font-size: 13px;
                    font-weight: 500;
                    padding: 6px 18px;
                }
                QPushButton:hover   { background: #f0f0f0; border-color: #999; }
                QPushButton:pressed { background: #e0e0e0; }
            """)
            cancel_btn.clicked.connect(self.reject)
            footer.addWidget(cancel_btn)

        # Primary OK / confirm button
        ok_btn = QPushButton(ok_text)
        ok_btn.setFixedHeight(34)
        ok_btn.setMinimumWidth(100)
        ok_btn.setDefault(True)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        if mode == "danger":
            c, h, p = "#e53935", "#c62828", "#b71c1c"   # red
        else:
            c, h, p = "#2196F3", "#1976D2", "#1565C0"   # blue

        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c};
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: 600;
                padding: 6px 18px;
            }}
            QPushButton:hover   {{ background: {h}; }}
            QPushButton:pressed {{ background: {p}; }}
        """)
        ok_btn.clicked.connect(self.accept)
        footer.addWidget(ok_btn)

        root.addWidget(footer_w)


# ══════════════════════════════════════════════════════════════
#  BATCH DASHBOARD SCREEN
# ══════════════════════════════════════════════════════════════

class BatchDashboardScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window = parent
        self.current_session_id = None
        self.session_active = False
        self.ws_client = None
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)

        header = QHBoxLayout()
        title = QLabel("📊 Batch Dashboard")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        header.addWidget(title)
        header.addStretch(1)
        self.main_layout.addLayout(header)

        # Stats grid
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(16)
        
        self.total_pcs_card  = StatCard("💻 Total PCs",        "0",          Theme.info,       icon="💻")
        self.online_card     = StatCard("🟢 Students Online",  "0",          Theme.success,    icon="🟢")
        self.offline_card    = StatCard("🔴 Students Offline", "0",          Theme.text_muted, icon="🔴")
        self.attendance_card = StatCard("📋 Session Status",   "No Session", Theme.warning,    icon="📋")
        self.exam_mode_card  = StatCard("📝 Exam Mode",        "OFF",        Theme.danger,     icon="📝")
        
        self.stats_grid.addWidget(self.total_pcs_card,  0, 0)
        self.stats_grid.addWidget(self.online_card,     0, 1)
        self.stats_grid.addWidget(self.offline_card,    0, 2)
        self.stats_grid.addWidget(self.attendance_card, 1, 0)
        self.stats_grid.addWidget(self.exam_mode_card,  1, 1)
        self.main_layout.addLayout(self.stats_grid)

        # Quick Actions card
        actions_card = CardFrame(padding=24)
        actions_heading = QLabel("⚡ Quick Actions")
        actions_heading.setFont(body_font(16, QFont.Weight.Bold))
        actions_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        actions_card.layout.addWidget(actions_heading)
        
        actions_layout = QGridLayout()
        actions_layout.setSpacing(12)
        
        self.start_session_btn = QPushButton("🚀 Start Lab Session")
        self.start_session_btn.setStyleSheet(self._button_style(Theme.primary))
        self.start_session_btn.clicked.connect(self.start_lab_session)
        actions_layout.addWidget(self.start_session_btn, 0, 0)
        
        self.end_session_btn = QPushButton("⏹️ End Lab Session")
        self.end_session_btn.setStyleSheet(self._button_style(Theme.danger))
        self.end_session_btn.clicked.connect(self.end_lab_session)
        self.end_session_btn.setEnabled(False)
        actions_layout.addWidget(self.end_session_btn, 0, 1)
        
        other_actions = [
            ("📝 Start Exam Mode", Theme.danger,    self._show_placeholder),
            ("📤 Distribute Task", Theme.primary,   self._show_placeholder),
            ("🎤 Start Viva Mode", Theme.secondary, self.open_viva_screen),
            ("📊 View Reports",    Theme.info,       self._show_placeholder),
        ]
        
        for i, (text, color, handler) in enumerate(other_actions):
            btn = QPushButton(text)
            btn.setStyleSheet(self._button_style(color))
            btn.clicked.connect(handler)
            actions_layout.addWidget(btn, (i + 2) // 3, (i + 2) % 3)
        
        actions_card.layout.addLayout(actions_layout)
        self.main_layout.addWidget(actions_card)
        self.main_layout.addStretch(1)

    # ── Shared button style ───────────────────────────────────

    def _button_style(self, color):
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px 20px;
                font-weight: 600;
                font-size: 13px;
                text-align: left;
            }}
            QPushButton:hover   {{ background: {color}dd; }}
            QPushButton:pressed {{ background: {color}bb; }}
            QPushButton:disabled {{
                background: {Theme.border};
                color: {Theme.text_muted};
            }}
        """

    # ── Dialog helpers ────────────────────────────────────────

    def _info(self, title: str, message: str):
        """Single blue OK button."""
        StyledDialog(self, title=title, message=message, mode="info").exec()

    def _confirm(self, title: str, message: str, sub_text: str = "",
                 ok_text: str = "OK", cancel_text: str = "Cancel",
                 danger: bool = False) -> bool:
        """Returns True when user clicks the primary button."""
        dlg = StyledDialog(
            self,
            title=title,
            message=message,
            sub_text=sub_text,
            mode="danger" if danger else "question",
            ok_text=ok_text,
            cancel_text=cancel_text,
        )
        return dlg.exec() == QDialog.DialogCode.Accepted

    # ── Action handlers ───────────────────────────────────────

    def start_lab_session(self):
        if not hasattr(self.parent_window, 'current_batch_id') or \
                self.parent_window.current_batch_id is None:
            self._info("Error", "Please select a batch first.")
            return

        batch_id = self.parent_window.current_batch_id
        subject_name = getattr(self.parent_window, 'current_subject_name', "")
        selected_date = getattr(self.parent_window, 'current_selected_date', "")
        selected_hour = getattr(self.parent_window, 'current_selected_hour', None)
        
        # Call API to start session
        result = api_client.start_lab_session(
            batch_id,
            session_type="regular",
            subject_name=subject_name,
            scheduled_date=selected_date,
            scheduled_hour=selected_hour,
        )
        
        if result["success"]:
            self.current_session_id = result["data"].get("id")
            self.session_active     = True

            self.start_session_btn.setEnabled(False)
            self.end_session_btn.setEnabled(True)
            self.attendance_card.update_value("Active")
            
            msg = "Lab session started successfully!"
            if subject_name:
                msg = f"Lab session for '{subject_name}' started successfully!"
            if selected_date and selected_hour:
                msg += f"\nScheduled: {selected_date} P{selected_hour}"
                
            QMessageBox.information(self, "Success", msg)
            self.update_stats()

        else:
            self._info("Error", f"Failed to start session:\n{result['error']}")

    def end_lab_session(self):
        if not self.current_session_id:
            return

        # ✅ FIX 2 — Confirmation dialog: both "End Session" (red) and "Cancel"
        #            buttons are clearly visible
        if not self._confirm(
            title="End Lab Session",
            message="Are you sure you want to end this lab session?",
            sub_text="This will stop the timer and notify all students.",
            ok_text="End Session",
            cancel_text="Cancel",
            danger=True,
        ):
            return

        result = api_client.end_lab_session(self.current_session_id)

        if result["success"]:
            self.session_active     = False
            self.current_session_id = None

            self.start_session_btn.setEnabled(True)
            self.end_session_btn.setEnabled(False)
            self.attendance_card.update_value("Ended")

            duration = result["data"].get("duration_minutes", 0)
            self._info("Session Ended",
                       f"Lab session ended successfully.\nDuration: {duration} minutes")
        else:
            self._info("Error",
                       f"Failed to end session:\n{result.get('error', 'Unknown error')}")

    def _show_placeholder(self):
        # ✅ FIX 3 — Coming Soon dialog: blue OK button clearly visible
        self._info("Coming Soon", "This feature will be implemented next.")

    # ── WebSocket ─────────────────────────────────────────────

    def start_websocket(self):
        if not hasattr(self.parent_window, 'current_batch_id') or \
                self.parent_window.current_batch_id is None:
            return

        if self.ws_client:
            self.ws_client.stop()
            self.ws_client = None

        batch_id = self.parent_window.current_batch_id
        token    = api_client.access_token

        if not token:
            print("Cannot start WebSocket: No access token")
            return

        from ui.common.websocket_client import FacultyWebSocketClient
        self.ws_client = FacultyWebSocketClient(batch_id, token)
        self.ws_client.student_status_signal.connect(self.handle_student_status)
        self.ws_client.start()

    def handle_student_status(self, data):
        print(f"Live Update: {data}")
        status = data.get('status')
        try:
            online  = int(self.online_card.value_label.text())
            offline = int(self.offline_card.value_label.text())

            if status == 'online':
                online  += 1
                offline  = max(0, offline - 1)
            elif status == 'offline':
                online   = max(0, online - 1)
                offline += 1

            self.online_card.update_value(str(online))
            self.offline_card.update_value(str(offline))
        except ValueError:
            pass

    # ── Stats ─────────────────────────────────────────────────

    def update_stats(self):
        if not hasattr(self.parent_window, 'current_batch_id') or \
                self.parent_window.current_batch_id is None:
            return

        batch_id = self.parent_window.current_batch_id
        self.start_websocket()

        result = api_client.get_students(batch_id=batch_id)
        if result["success"]:
            students = result["data"]
            total    = len(students)
            online   = sum(1 for s in students if s.get('status') == 'online')
            offline  = total - online

            self.total_pcs_card.update_value(str(total))
            self.online_card.update_value(str(online))
            self.offline_card.update_value(str(offline))

    def showEvent(self, event):
        super().showEvent(event)
        self.update_stats()

    def open_viva_screen(self):
        self.parent_window.show_screen("viva")
