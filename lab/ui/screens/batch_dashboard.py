from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.common.cards import StatCard, CardFrame
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


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

        # Overview stats with icons
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(16)
        
        self.total_pcs_card = StatCard("💻 Total PCs", "0", Theme.info, icon="💻")
        self.online_card = StatCard("🟢 Students Online", "0", Theme.success, icon="🟢")
        self.offline_card = StatCard("🔴 Students Offline", "0", Theme.text_muted, icon="🔴")
        self.attendance_card = StatCard("📋 Session Status", "No Session", Theme.warning, icon="📋")
        self.exam_mode_card = StatCard("📝 Exam Mode", "OFF", Theme.danger, icon="📝")
        
        self.stats_grid.addWidget(self.total_pcs_card, 0, 0)
        self.stats_grid.addWidget(self.online_card, 0, 1)
        self.stats_grid.addWidget(self.offline_card, 0, 2)
        self.stats_grid.addWidget(self.attendance_card, 1, 0)
        self.stats_grid.addWidget(self.exam_mode_card, 1, 1)
        self.main_layout.addLayout(self.stats_grid)

        # Quick Actions
        actions_card = CardFrame(padding=24)
        actions_heading = QLabel("⚡ Quick Actions")
        actions_heading.setFont(body_font(16, QFont.Weight.Bold))
        actions_heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 16px;")
        actions_card.layout.addWidget(actions_heading)
        
        actions_layout = QGridLayout()
        actions_layout.setSpacing(12)
        
        # Start Lab Session button
        self.start_session_btn = QPushButton("🚀 Start Lab Session")
        self.start_session_btn.setStyleSheet(self._button_style(Theme.primary))
        self.start_session_btn.clicked.connect(self.start_lab_session)
        actions_layout.addWidget(self.start_session_btn, 0, 0)
        
        # End Lab Session button
        self.end_session_btn = QPushButton("⏹️ End Lab Session")
        self.end_session_btn.setStyleSheet(self._button_style(Theme.danger))
        self.end_session_btn.clicked.connect(self.end_lab_session)
        self.end_session_btn.setEnabled(False)
        actions_layout.addWidget(self.end_session_btn, 0, 1)
        
        # Other action buttons (placeholders for now)
        other_actions = [
            ("📝 Start Exam Mode", Theme.danger, self._show_placeholder),
            ("📤 Distribute Task", Theme.primary, self._show_placeholder),
            ("🎤 Start Viva Mode", Theme.secondary, self._show_placeholder),
            ("📊 View Reports", Theme.info, self._show_placeholder),
        ]
        
        for i, (text, color, handler) in enumerate(other_actions):
            btn = QPushButton(text)
            btn.setStyleSheet(self._button_style(color))
            btn.clicked.connect(handler)
            actions_layout.addWidget(btn, (i + 2) // 3, (i + 2) % 3)
        
        actions_card.layout.addLayout(actions_layout)
        self.main_layout.addWidget(actions_card)
        self.main_layout.addStretch(1)
    
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
            QPushButton:hover {{
                background: {color}dd;
            }}
            QPushButton:pressed {{
                background: {color}bb;
            }}
            QPushButton:disabled {{
                background: {Theme.border};
                color: {Theme.text_muted};
            }}
        """
    
    def start_lab_session(self):
        """Start a new lab session"""
        if not hasattr(self.parent_window, 'current_batch_id') or self.parent_window.current_batch_id is None:
            QMessageBox.warning(self, "Error", "Please select a batch first")
            return
        
        batch_id = self.parent_window.current_batch_id
        
        # Call API to start session
        result = api_client.start_lab_session(batch_id, session_type="regular")
        
        if result["success"]:
            session_data = result["data"]
            self.current_session_id = session_data.get("id")
            self.session_active = True
            
            # Update UI
            self.start_session_btn.setEnabled(False)
            self.end_session_btn.setEnabled(True)
            self.attendance_card.update_value("Active")
            
            QMessageBox.information(self, "Success", "Lab session started successfully!")
            self.update_stats()
        else:
            QMessageBox.warning(self, "Error", f"Failed to start session:\n{result['error']}")
    
    def end_lab_session(self):
        """End the current lab session"""
        if not self.current_session_id:
            return
        
        # Create a robust confirmation dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("End Lab Session")
        msg_box.setText("Are you sure you want to end this lab session?")
        msg_box.setInformativeText("This will stop the timer and notify all students.")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        # Add buttons explicitly to ensure they are active
        yes_btn = msg_box.addButton("End Session", QMessageBox.ButtonRole.YesRole)
        no_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.NoRole)
        
        # Set default
        msg_box.setDefaultButton(no_btn)
        
        # Show dialog
        msg_box.exec()
        
        # Check which button was clicked
        if msg_box.clickedButton() == yes_btn:
            # Call API to end session
            result = api_client.end_lab_session(self.current_session_id)
            
            if result["success"]:
                self.session_active = False
                self.current_session_id = None
                
                # Update UI
                self.start_session_btn.setEnabled(True)
                self.end_session_btn.setEnabled(False)
                self.attendance_card.update_value("Ended")
                
                # Show success message
                duration = result["data"].get("duration_minutes", 0)
                QMessageBox.information(self, "Session Ended", f"Lab session ended successfully.\nDuration: {duration} minutes")
                
                # Stop WebSocket if monitoring specific session stuff (optional)
                # We keep it running to see post-session updates or for generally online/offline
                
            else:
                QMessageBox.critical(self, "Error", f"Failed to end session:\n{result.get('error', 'Unknown error')}")
    
    
    def start_websocket(self):
        """Start WebSocket connection for live updates"""
        if not hasattr(self.parent_window, 'current_batch_id') or self.parent_window.current_batch_id is None:
            return

        # Stop existing client if running
        if self.ws_client:
            self.ws_client.stop()
            self.ws_client = None

        batch_id = self.parent_window.current_batch_id
        token = api_client.access_token
        
        if not token:
            print("Cannot start WebSocket: No access token")
            return

        from ui.common.websocket_client import FacultyWebSocketClient
        self.ws_client = FacultyWebSocketClient(batch_id, token)
        self.ws_client.student_status_signal.connect(self.handle_student_status)
        self.ws_client.start()

    def handle_student_status(self, data):
        """Handle live student status update"""
        # data = {'student_id': 1, 'status': 'online', 'name': '...'}
        print(f"Live Update: {data}")
        
        # Determine change
        status = data.get('status')
        
        # Optimistic update of counters
        # We need current values. The cards store strings.
        try:
            online_count = int(self.online_card.value_label.text())
            offline_count = int(self.offline_card.value_label.text())
            
            if status == 'online':
                online_count += 1
                offline_count = max(0, offline_count - 1)
            elif status == 'offline':
                online_count = max(0, online_count - 1)
                offline_count += 1
                
            self.online_card.update_value(str(online_count))
            self.offline_card.update_value(str(offline_count))
            
            # Ideally, we should also update the list if it was a table.
            # For now, just the counters are enough as per requirement.
            
        except ValueError:
            pass
            
            
    def update_stats(self):
        """Update dashboard statistics from backend"""
        if not hasattr(self.parent_window, 'current_batch_id') or self.parent_window.current_batch_id is None:
            return
        
        batch_id = self.parent_window.current_batch_id
        
        # Start WebSocket if not already running for this batch
        # (Or restart if batch changed - start_websocket handles logic)
        self.start_websocket()

        # Get students data
        result = api_client.get_students(batch_id=batch_id)
        
        if result["success"]:
            students = result["data"]
            total = len(students)
            online = sum(1 for s in students if s.get('status') == 'online')
            offline = total - online
            
            self.total_pcs_card.update_value(str(total))
            self.online_card.update_value(str(online))
            self.offline_card.update_value(str(offline))
    
    def showEvent(self, event):
        """Update stats when screen is shown"""
        super().showEvent(event)
        self.update_stats()

    def _show_placeholder(self):
        QMessageBox.information(self, "Coming Soon", "This feature will be implemented next.")

