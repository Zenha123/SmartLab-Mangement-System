# ui/common/styled_dialogs.py
#
# Place this file at:  lab/ui/common/styled_dialogs.py
#
# Import in every screen like this:
#   from ui.common.styled_dialogs import info, success, warning, error, confirm
#
# ─────────────────────────────────────────────────────────────
# REPLACES every QMessageBox call across the entire faculty app.
# All buttons always have solid colours — never invisible.
# ─────────────────────────────────────────────────────────────
#
# Quick-reference
# ───────────────
#   info(self, "Title", "Message")
#   success(self, "Title", "Message")
#   warning(self, "Title", "Message")
#   error(self, "Title", "Message")
#
#   if confirm(self, "Title", "Message",
#              sub_text="Extra detail",
#              ok_text="Delete", cancel_text="Cancel",
#              danger=True):          # danger=True → red primary button
#       ...

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt


# ══════════════════════════════════════════════════════════════
#  Core dialog class
# ══════════════════════════════════════════════════════════════

class StyledDialog(QDialog):
    """
    Reusable modal dialog.  Buttons always have a solid background.

    mode        icon colour   primary-btn colour
    ──────────  ───────────   ──────────────────
    info        blue          blue
    success     green         green
    warning     orange        orange
    error       red           red
    question    blue          blue
    danger      orange        red   ← use for destructive confirmations
    """

    _ICON_BG = {
        "info":     "#2196F3",
        "success":  "#43A047",
        "warning":  "#FF9800",
        "error":    "#e53935",
        "question": "#2196F3",
        "danger":   "#FF9800",
    }
    _ICON_TXT = {
        "info":     "i",
        "success":  "✓",
        "warning":  "!",
        "error":    "✕",
        "question": "?",
        "danger":   "?",
    }
    _BTN_COLORS = {
        "info":     ("#2196F3", "#1976D2", "#1565C0"),
        "success":  ("#43A047", "#388E3C", "#2E7D32"),
        "warning":  ("#FF9800", "#F57C00", "#E65100"),
        "error":    ("#e53935", "#c62828", "#b71c1c"),
        "question": ("#2196F3", "#1976D2", "#1565C0"),
        "danger":   ("#e53935", "#c62828", "#b71c1c"),   # red btn even though icon is orange
    }

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

        # Coloured circle
        icon_lbl = QLabel(self._ICON_TXT.get(mode, "i"))
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            QLabel {{
                background: {self._ICON_BG.get(mode, '#2196F3')};
                color: white;
                border-radius: 22px;
                font-size: 20px;
                font-weight: 900;
                font-style: italic;
                font-family: Georgia, serif;
            }}
        """)

        # Text column
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

        # White cancel button (optional)
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

        # Coloured primary button
        ok_btn = QPushButton(ok_text)
        ok_btn.setFixedHeight(34)
        ok_btn.setMinimumWidth(100)
        ok_btn.setDefault(True)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        c, h, p = self._BTN_COLORS.get(mode, self._BTN_COLORS["info"])
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
#  Public helper functions  ← use these in every screen
# ══════════════════════════════════════════════════════════════

def info(parent, title: str, message: str, sub_text: str = "") -> None:
    StyledDialog(parent, title=title, message=message,
                 sub_text=sub_text, mode="info").exec()

def success(parent, title: str, message: str, sub_text: str = "") -> None:
    StyledDialog(parent, title=title, message=message,
                 sub_text=sub_text, mode="success").exec()

def warning(parent, title: str, message: str, sub_text: str = "") -> None:
    StyledDialog(parent, title=title, message=message,
                 sub_text=sub_text, mode="warning").exec()

def error(parent, title: str, message: str, sub_text: str = "") -> None:
    StyledDialog(parent, title=title, message=message,
                 sub_text=sub_text, mode="error").exec()

def confirm(parent, title: str, message: str,
            sub_text: str = "", ok_text: str = "OK",
            cancel_text: str = "Cancel", danger: bool = False) -> bool:
    """Returns True when the user clicks the primary button."""
    dlg = StyledDialog(
        parent,
        title=title,
        message=message,
        sub_text=sub_text,
        mode="danger" if danger else "question",
        ok_text=ok_text,
        cancel_text=cancel_text,
    )
    return dlg.exec() == QDialog.DialogCode.Accepted
