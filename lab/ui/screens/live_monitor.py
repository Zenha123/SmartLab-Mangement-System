from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QHBoxLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont,QImage, QPixmap

from ui.theme import heading_font, Theme, body_font
from ui.common.cards import CardFrame
from ui.common.badges import StatusDot, ModeBadge
from api.global_client import api_client
from monitor.webrtc_manager import FacultyWebRTCManager
class LiveMonitorScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        self.video_labels = {}
        self.webrtc_manager = None

        # Header with view selector
        header = QHBoxLayout()
        title = QLabel("🖥️ Live Monitoring")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        header.addWidget(title)
        header.addStretch()
        
        # Grid size selector
        view_label = QLabel("View:")
        view_label.setFont(body_font(12))
        view_label.setStyleSheet(f"color: {Theme.text_muted};")
        view_combo = QComboBox()
        view_combo.addItems(["2×2", "3×3", "4×4"])
        view_combo.setCurrentIndex(1)
        view_combo.setStyleSheet(
            f"""
            QComboBox {{
                border: 1px solid {Theme.border};
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 80px;
            }}
            """
        )
        header.addWidget(view_label)
        header.addWidget(view_combo)
        root.addLayout(header)

        grid_card = CardFrame(padding=20)
        grid = QGridLayout()
        grid.setSpacing(16)
        # Default 3x3 concept tiles
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)
        grid_card.layout.addLayout(self.grid_layout)

        self.students_data = []

        grid_card.layout.addLayout(grid)
        root.addWidget(grid_card)
        root.addStretch(1)

    def update_video_frame(self, student_id, frame):
        if student_id not in self.video_labels:
            return

        height, width, channel = frame.shape
        bytes_per_line = channel * width
        qt_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
        pixmap = QPixmap.fromImage(qt_img)

        self.video_labels[student_id].setPixmap(
            pixmap.scaled(
                self.video_labels[student_id].size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def _tile(self, student: dict):
        student_db_id = student.get("id")
        name = student.get("name", "Unknown")
        pc = student.get("student_id", "N/A")
        status = student.get("status", "offline").capitalize()

        frame = QFrame()
        frame.setObjectName("monitorTile")
        frame.setStyleSheet(
            f"""
            QFrame#monitorTile {{
                background: {Theme.card_bg};
                border: 2px solid {Theme.border};
                border-radius: 12px;
                min-height: 160px;
            }}
            QFrame#monitorTile:hover {{
                border: 2px solid {Theme.primary};
                background: {Theme.primary}05;
            }}
            """
        )
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        # Status badge at top
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_color = Theme.success if status == "Online" else Theme.danger
        status_dot = StatusDot(status_color, size=8, animated=True)
        status_label = QLabel(status)
        status_label.setFont(body_font(11, QFont.Weight.DemiBold))
        status_label.setStyleSheet(f"color: {status_color};")
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        layout.addWidget(status_widget)
        
        # Placeholder for screen view
        screen_placeholder = QLabel("📺")
        screen_placeholder.setMinimumHeight(150)
        screen_placeholder.setMinimumWidth(200)
        screen_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        screen_placeholder.setStyleSheet(
            f"""
            QLabel {{
                background: {Theme.background};
                border: 1px dashed {Theme.border};
                border-radius: 8px;
                min-height: 80px;
                font-size: 32px;
            }}
            """
        )

        self.video_labels[student_db_id] = screen_placeholder
        layout.addWidget(screen_placeholder)
        
        # Student info
        name_label = QLabel(name)
        name_label.setFont(body_font(13, QFont.Weight.DemiBold))
        name_label.setStyleSheet(f"color: {Theme.text_primary};")
        layout.addWidget(name_label)
        
        pc_label = QLabel(pc)
        pc_label.setFont(body_font(11))
        pc_label.setStyleSheet(f"color: {Theme.text_muted};")
        layout.addWidget(pc_label)
        
        layout.addStretch()
        
        # Open view button
        btn = QPushButton("👁️ View")
        btn.clicked.connect(lambda _, s=student: self.start_monitor(s))
        btn.setProperty("class", "primary")
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.primary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: {Theme.primary_hover};
            }}
            """
        )
        layout.addWidget(btn)
        return frame

    def set_websocket_client(self, ws_client):
        self.websocket_client = ws_client
    
    def start_monitor(self, student: dict):
        """Open single-student view. Accepts the full student dict."""
        student_id = student.get("id")

        main_window = self.window()

        ws_client = main_window.dashboard_screen.ws_client

        if not ws_client or not ws_client.connected:
            print("WebSocket client not available")
            return

        if not hasattr(main_window, "webrtc_manager"):
            main_window.webrtc_manager = FacultyWebRTCManager(
                ws_client,
                main_window.single_student_screen.update_video_frame
            )

        # Populate the single-student screen with real data BEFORE switching
        single_screen = main_window.single_student_screen
        single_screen.student_id = student_id
        single_screen.set_webrtc_manager(main_window.webrtc_manager)
        single_screen.load_student_data(student)   # fills side panel with real data

        main_window.stack.setCurrentWidget(single_screen)
        main_window.webrtc_manager.start_monitoring(student_id)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.load_students()


    def load_students(self):
    # Get batch_id from parent main window
        main_window = self.window()

        if not hasattr(main_window, "current_batch_id") or main_window.current_batch_id is None:
            return

        batch_id = main_window.current_batch_id

        result = api_client.get_students(batch_id=batch_id)

        if not result["success"]:
            print("Failed to load students")
            return

        self.students_data = result["data"]
        self._rebuild_grid()

        print("Batch ID:", main_window.current_batch_id)
    
    def _rebuild_grid(self):
    # Clear old tiles
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for index, student in enumerate(self.students_data):
            tile = self._tile(student)
            

            row = index // 3
            col = index % 3
            self.grid_layout.addWidget(tile, row, col)