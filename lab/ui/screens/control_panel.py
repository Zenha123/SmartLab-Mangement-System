from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.theme import heading_font, Theme, body_font
from ui.common.cards import CardFrame
from api.global_client import api_client


class ControlPanelScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window = parent
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("🎛️ Control Panel")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        warning_label = QLabel("⚠️ These actions affect all students in the current batch. Use with caution.")
        warning_label.setFont(body_font(12))
        warning_label.setStyleSheet(
            f"""
            QLabel {{
                background: {Theme.warning_light};
                border: 1px solid {Theme.warning};
                border-radius: 8px;
                padding: 12px 16px;
                color: {Theme.warning};
            }}
            """
        )
        root.addWidget(warning_label)

        card = CardFrame(padding=24)
        heading = QLabel("Class-wide Controls")
        heading.setFont(body_font(16, QFont.Weight.Bold))
        heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        card.layout.addWidget(heading)
        
        grid = QGridLayout()
        grid.setSpacing(12)
        
        # Mapping UI text to backend command types
        self.command_map = {
            "🔒 Lock All PCs": "lock_pc",
            "🔓 Unlock All PCs": "unlock_pc",
            "🚫 Block Internet": "block_internet",
            "✅ Unblock Internet": "unblock_internet",
            "💾 Enable USB": "enable_usb",
            "🚫 Disable USB": "disable_usb",
            "📋 App Whitelist": "app_whitelist"
        }

        actions = [
            ("🔒 Lock All PCs", Theme.danger),
            ("🔓 Unlock All PCs", Theme.success),
            ("🚫 Block Internet", Theme.warning),
            ("✅ Unblock Internet", Theme.success),
            ("💾 Enable USB", Theme.primary),
            ("🚫 Disable USB", Theme.warning),
            ("📋 App Whitelist", Theme.primary),
        ]
        for i, (text, color) in enumerate(actions):
            btn = QPushButton(text)
            btn.setProperty("class", "primary" if color == Theme.primary else ("danger" if color == Theme.danger else "success"))
            btn.setStyleSheet(
                f"""
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
                QPushButton:hover {{
                    background: {color}dd;
                }}
                """
            )
            btn.clicked.connect(lambda checked, t=text: self.confirm_action(t))
            grid.addWidget(btn, i // 2, i % 2)
        card.layout.addLayout(grid)
        root.addWidget(card)
        root.addStretch(1)

    def confirm_action(self, action_text: str):
        batch_id = getattr(self.parent_window, 'current_batch_id', None)
        if not batch_id:
            QMessageBox.warning(self, "No Batch Selected", "Please select a batch first from the Dashboard.")
            return

        command_type = self.command_map.get(action_text)
        if not command_type:
            return

        reply = QMessageBox.question(
            self, 
            "Confirm Action", 
            f"Are you sure you want to execute '{action_text}'?\n\nThis will affect all students in the current batch.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Call API
            res = api_client.send_control_command(batch_id, command_type)
            
            if res.get("success"):
                QMessageBox.information(self, "Action Executed", f"'{action_text}' has been sent to all students.")
            else:
                QMessageBox.critical(self, "Execution Failed", f"Failed to execute action: {res.get('error')}")

