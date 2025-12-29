from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.common.badges import StatusDot, ModeBadge
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


class StudentListScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.students_data = []
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)

        # Header with title and stats
        self.header = QHBoxLayout()
        title = QLabel("👥 Students List")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        self.header.addWidget(title)
        self.header.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.secondary};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: #16A085;
            }}
            """
        )
        refresh_btn.clicked.connect(self.load_students)
        self.header.addWidget(refresh_btn)
        
        # Quick stats
        self.stats_label = QLabel("Loading...")
        self.stats_label.setFont(body_font(13))
        self.stats_label.setStyleSheet(f"color: {Theme.text_muted}; padding: 8px 16px; background: {Theme.background}; border-radius: 8px;")
        self.header.addWidget(self.stats_label)
        self.main_layout.addLayout(self.header)

        # Table card
        self.card = CardFrame(padding=20)
        self.table = None
        self.main_layout.addWidget(self.card)
        self.main_layout.addStretch(1)

    def load_students(self):
        """Load students from backend"""
        # Get batch_id from parent window
        if not hasattr(self.parent_window, 'current_batch_id') or self.parent_window.current_batch_id is None:
            self.stats_label.setText("No batch selected")
            return
        
        batch_id = self.parent_window.current_batch_id
        
        # Call API
        result = api_client.get_students(batch_id=batch_id)
        
        if not result["success"]:
            QMessageBox.warning(self, "Error", f"Failed to load students:\n{result['error']}")
            self.stats_label.setText("Error loading students")
            return
        
        self.students_data = result["data"]
        
        # Update stats
        online_count = sum(1 for s in self.students_data if s.get('status') == 'online')
        self.stats_label.setText(f"Total: {len(self.students_data)} | Online: {online_count}")
        
        # Rebuild table
        self._build_table()
    
    def _build_table(self):
        """Build/rebuild the student table"""
        # Remove old table if exists
        if self.table is not None:
            try:
                self.card.layout.removeWidget(self.table)
                self.table.setParent(None)
                self.table.deleteLater()
            except RuntimeError:
                pass  # Widget already deleted
            self.table = None
        
        if not self.students_data:
            no_data_label = QLabel("No students found")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet(f"color: {Theme.text_muted}; padding: 40px;")
            self.card.layout.addWidget(no_data_label)
            return
        
        self.table = StyledTableWidget(len(self.students_data), 5)
        self.table.setHorizontalHeaderLabels(["Student Name", "Student ID", "Status", "Mode", "Last Seen"])
        
        for row, s in enumerate(self.students_data):
            # Student name
            name_item = QTableWidgetItem(f"👤 {s.get('name', 'Unknown')}")
            name_item.setFont(body_font(13, QFont.Weight.Medium))
            self.table.setItem(row, 0, name_item)
            
            # Student ID
            id_item = QTableWidgetItem(s.get("student_id", "N/A"))
            id_item.setFont(body_font(12))
            id_item.setForeground(QColor(Theme.text_secondary))
            self.table.setItem(row, 1, id_item)

            # Status widget
            status = s.get("status", "offline")
            status_widget = self._status_widget(status)
            self.table.setCellWidget(row, 2, status_widget)

            # Mode widget
            mode = s.get("current_mode", "normal")
            mode_widget = self._mode_widget(mode)
            self.table.setCellWidget(row, 3, mode_widget)

            # Last seen
            last_seen = s.get("last_seen", "Never")
            if last_seen and last_seen != "Never":
                # Format timestamp
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                    last_seen = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            last_seen_item = QTableWidgetItem(last_seen if last_seen else "Never")
            last_seen_item.setFont(body_font(12))
            last_seen_item.setForeground(QColor(Theme.text_muted))
            self.table.setItem(row, 4, last_seen_item)

        self.table.resizeColumnsToContents()
        self.card.layout.addWidget(self.table)

    def _status_widget(self, status: str):
        wrap = QHBoxLayout()
        wrap.setContentsMargins(8, 6, 8, 6)
        wrap.setSpacing(8)
        color = Theme.success if status == "online" else Theme.danger
        wrap.addWidget(StatusDot(color, size=10, tooltip=status.title(), animated=(status == "online")))
        lbl = QLabel(status.title())
        lbl.setFont(body_font(12, QFont.Weight.DemiBold))
        lbl.setStyleSheet(f"color: {color};")
        wrap.addWidget(lbl)
        wrap.addStretch()
        container = QWidget()
        container.setLayout(wrap)
        return container

    def _mode_widget(self, mode: str):
        color_map = {
            "normal": Theme.text_muted,
            "locked": Theme.danger,
            "viva": Theme.secondary,
            "exam": Theme.warning,
        }
        badge = ModeBadge(mode.title(), color_map.get(mode.lower(), Theme.primary), size="small")
        wrap = QHBoxLayout()
        wrap.setContentsMargins(8, 6, 8, 6)
        wrap.addWidget(badge)
        wrap.addStretch()
        holder = QWidget()
        holder.setLayout(wrap)
        return holder
    
    def showEvent(self, event):
        """Load students when screen is shown"""
        super().showEvent(event)
        self.load_students()

