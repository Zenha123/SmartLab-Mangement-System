from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from ui.common.cards import CardFrame
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client


class SemesterSelectionScreen(QWidget):
    batch_selected = pyqtSignal(str, str, int)  # semester_name, batch_name, batch_id

    def __init__(self):
        super().__init__()
        # Set background color
        self.setStyleSheet(f"background: {Theme.background};")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(20)

        title = QLabel("📚 Select Semester & Batch")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        self.main_layout.addWidget(title)
        
        subtitle = QLabel("Choose a semester and batch to manage")
        subtitle.setFont(body_font(13))
        subtitle.setStyleSheet(f"color: {Theme.text_muted}; margin-bottom: 20px;")
        self.main_layout.addWidget(subtitle)

        # Loading label
        self.loading_label = QLabel("🔄 Loading semesters...")
        self.loading_label.setFont(body_font(14))
        self.loading_label.setStyleSheet(f"color: {Theme.text_muted};")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.loading_label)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)
        self.main_layout.addLayout(self.grid_layout)
        self.main_layout.addStretch(1)

    def load_semesters(self):
        """Load semesters and batches from backend"""
        # Get semesters
        result = api_client.get_semesters()
        
        if not result["success"]:
            self.loading_label.setText(f"❌ Error: {result['error']}")
            QMessageBox.warning(self, "Error", f"Failed to load semesters:\n{result['error']}")
            return
        
        semesters_data = result["data"]
        
        # Handle paginated response
        if isinstance(semesters_data, dict) and 'results' in semesters_data:
            semesters_data = semesters_data['results']
        
        # Ensure it's a list
        if not isinstance(semesters_data, list):
            self.loading_label.setText("❌ Invalid data format")
            QMessageBox.warning(self, "Error", f"Unexpected data format: {type(semesters_data)}")
            return
        
        if not semesters_data:
            self.loading_label.setText("No semesters available")
            return
        
        # Hide loading label
        self.loading_label.hide()
        
        # Group batches by semester
        semester_batches = {}
        for semester in semesters_data:
            try:
                sem_id = semester.get("id")
                sem_name = semester.get("name")
                
                if not sem_id or not sem_name:
                    continue
                
                # Get batches for this semester
                batch_result = api_client.get_batches(semester_id=sem_id)
                
                if batch_result["success"]:
                    batches = batch_result["data"]
                    
                    # Handle paginated batch response
                    if isinstance(batches, dict) and 'results' in batches:
                        batches = batches['results']
                    
                    if batches and isinstance(batches, list):
                        semester_batches[sem_name] = {
                            "semester_id": sem_id,
                            "batches": batches
                        }
            except Exception as e:
                print(f"Error processing semester: {e}")
                continue
        
        # Display semesters and batches
        row = col = 0
        for sem_name, data in semester_batches.items():
            card = CardFrame(padding=20, hoverable=True)
            card.layout.setSpacing(12)
            
            # Semester label
            lbl = QLabel(sem_name)
            lbl.setFont(heading_font(16, bold=True))
            lbl.setStyleSheet(f"color: {Theme.primary}; margin-bottom: 8px;")
            card.layout.addWidget(lbl)
            
            # Batch buttons
            btn_row = QHBoxLayout()
            btn_row.setSpacing(10)
            for batch in data["batches"]:
                batch_name = batch["name"]
                batch_id = batch["id"]
                
                btn = QPushButton(f"📦 {batch_name}")
                btn.setProperty("class", "secondary")
                btn.setStyleSheet(
                    f"""
                    QPushButton {{
                        background: {Theme.secondary};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 10px 18px;
                        font-weight: 600;
                        font-size: 13px;
                    }}
                    QPushButton:hover {{
                        background: #16A085;
                    }}
                    """
                )
                btn.clicked.connect(lambda checked, s=sem_name, b=batch_name, bid=batch_id: 
                                  self.batch_selected.emit(s, b, bid))
                btn_row.addWidget(btn)
            btn_row.addStretch()
            card.layout.addLayout(btn_row)
            
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col == 4:  # 4 columns for better layout
                col = 0
                row += 1
    
    def showEvent(self, event):
        """Load semesters when screen is shown (after login)"""
        super().showEvent(event)
        # Only load if we haven't loaded yet (grid is empty)
        if self.grid_layout.count() == 0:
            self.load_semesters()

