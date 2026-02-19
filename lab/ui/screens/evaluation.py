from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QTableWidgetItem, 
    QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QMessageBox, 
    QTableWidget, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QCursor

from ui.common.cards import StatCard, CardFrame
from ui.theme import heading_font, Theme, body_font
from api.global_client import api_client
import requests
import os


class EvaluationScreen(QWidget):
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window
        self.submissions = []
        self.submission_widgets = {}  # Map row -> (submission_id, grade_input, feedback_input)
        
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("✅ Evaluation")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # Summary cards
        stats = QGridLayout()
        stats.setSpacing(16)
        self.received_card = StatCard("📄 Assignment Received", "0", Theme.info, icon="📄")
        self.pending_card = StatCard("⏳ Yet to Receive", "0", Theme.warning, icon="⏳")
        self.evaluated_card = StatCard("✅ Evaluated", "0", Theme.success, icon="✅")
        self.to_evaluate_card = StatCard("📝 Yet to Evaluate", "0", Theme.primary, icon="📝")
        stats.addWidget(self.received_card, 0, 0)
        stats.addWidget(self.pending_card, 0, 1)
        stats.addWidget(self.evaluated_card, 0, 2)
        stats.addWidget(self.to_evaluate_card, 0, 3)
        root.addLayout(stats)

        card = CardFrame(padding=20)
        
        # Table with explicit columns
        # Added "Action" column for the Publish button
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Student", "Student ID", "Date", "Submission File", "Grade", "Feedback", "Action"
        ])
        
        # Modern Table Styling
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                gridline-color: #f3f4f6;
                selection-background-color: transparent;
                selection-color: black;
            }}
            QHeaderView::section {{
                background-color: #f9fafb;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e5e7eb;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 700;
                color: #374151;
                font-size: 13px;
                text-transform: uppercase;
            }}
            QTableWidget::item {{
                padding: 0px;
                border-bottom: 1px solid #f3f4f6;
            }}
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Adjust specific column widths
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # ID
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed) # Grade
        self.table.setColumnWidth(4, 100)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        card.layout.addWidget(self.table)
        root.addWidget(card)
        root.addStretch(1)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.load_submissions()
    
    def load_submissions(self):
        print("\n" + "="*60)
        print("DEBUG: load_submissions() called")
        
        if not self.parent_window or not hasattr(self.parent_window, 'current_batch_id'):
            return
        
        batch_id = self.parent_window.current_batch_id
        
        try:
            url = f"http://localhost:8000/api/submissions/?task__batch={batch_id}"
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {api_client.access_token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    self.submissions = data['results']
                else:
                    self.submissions = data
                
                print(f"DEBUG: Loaded {len(self.submissions)} submissions")
                self.populate_table()
                self.update_stats()
            else:
                print(f"DEBUG: ❌ API Error: {response.status_code}")
        except Exception as e:
            print(f"DEBUG: ❌ Exception: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print("="*60 + "\n")
    
    def populate_table(self):
        self.table.setRowCount(len(self.submissions))
        self.submission_widgets.clear()
        
        for r, item in enumerate(self.submissions):
            # IMPORTANT: Set fixed row height to ensure widgets are visible
            self.table.setRowHeight(r, 60)
            
            # 1. Student Name
            name_lbl = QLabel(f"👤 {item.get('student_name', 'Unknown')}")
            name_lbl.setStyleSheet("font-weight: 600; color: #1f2937; padding-left: 10px;")
            self.table.setCellWidget(r, 0, name_lbl)
            
            # 2. Student ID
            id_lbl = QLabel(str(item.get('student', '')))
            id_lbl.setStyleSheet("color: #6b7280; padding-left: 10px;")
            self.table.setCellWidget(r, 1, id_lbl)
            
            # 3. Date
            date_str = item.get('submitted_at', '-').split('T')[0] if item.get('submitted_at') else '-'
            date_lbl = QLabel(date_str)
            date_lbl.setStyleSheet("color: #6b7280; padding-left: 10px;")
            self.table.setCellWidget(r, 2, date_lbl)
            
            # 4. File Link
            file_path = item.get('file_path', '')
            # Handle different path separators and ensure we get a clean filename
            if file_path:
                clean_path = file_path.replace('\\', '/')
                file_name = clean_path.split('/')[-1]
            else:
                file_name = "No File"
                
            file_btn = QPushButton(f"📎 {file_name}")
            file_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            file_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    color: #2563eb;
                    text-align: left;
                    font-weight: 500;
                    padding: 5px;
                }
                QPushButton:hover {
                    text-decoration: underline;
                    color: #1d4ed8;
                }
            """)
            if file_path:
                file_btn.clicked.connect(lambda checked, path=file_path: self.view_code(path))
            else:
                file_btn.setEnabled(False)
                file_btn.setStyleSheet("color: #9ca3af; border: none; background: transparent; padding: 5px;")
            
            # Wrap in widget for alignment
            file_container = QWidget()
            file_layout = QHBoxLayout(file_container)
            file_layout.setContentsMargins(10, 0, 0, 0)
            file_layout.addWidget(file_btn)
            self.table.setCellWidget(r, 3, file_container)

            # 5. Grade Input
            grade_input = QLineEdit()
            grade_input.setPlaceholderText("0-100")
            grade_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grade_input.setFixedWidth(60)
            grade_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    padding: 6px;
                    font-weight: 600;
                }
                QLineEdit:focus {
                    border: 2px solid #2563eb;
                }
            """)
            if item.get("marks") is not None:
                grade_input.setText(str(item["marks"]))
            
            # Center the grade input
            grade_container = QWidget()
            grade_layout = QHBoxLayout(grade_container)
            grade_layout.setContentsMargins(0, 0, 0, 0)
            grade_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grade_layout.addWidget(grade_input)
            self.table.setCellWidget(r, 4, grade_container)
            
            # 6. Feedback Input
            feedback_input = QLineEdit()
            feedback_input.setPlaceholderText("Enter feedback...")
            feedback_input.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    padding: 6px 12px;
                }
                QLineEdit:focus {
                    border: 2px solid #2563eb;
                }
            """)
            if item.get("feedback"):
                feedback_input.setText(item["feedback"])
            
            feedback_container = QWidget()
            feedback_layout = QHBoxLayout(feedback_container)
            feedback_layout.setContentsMargins(5, 0, 5, 0)
            feedback_layout.addWidget(feedback_input)
            self.table.setCellWidget(r, 5, feedback_container)

            # 7. Publish Button
            publish_btn = QPushButton("Publish")
            publish_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            publish_btn.setFixedSize(80, 32)
            publish_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
                QPushButton:pressed {
                    background-color: #1e40af;
                }
            """)
            publish_btn.clicked.connect(lambda checked, row=r: self._on_publish(row))
            
            action_container = QWidget()
            action_layout = QHBoxLayout(action_container)
            action_layout.setContentsMargins(0, 0, 10, 0)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            action_layout.addWidget(publish_btn)
            self.table.setCellWidget(r, 6, action_container)
            
            # Store references
            self.submission_widgets[r] = (item['id'], grade_input, feedback_input)

    def update_stats(self):
        submitted = sum(1 for s in self.submissions if s.get('status') == 'submitted')
        evaluated = sum(1 for s in self.submissions if s.get('status') == 'evaluated')
        
        self.received_card.update_value(str(submitted))
        self.evaluated_card.update_value(str(evaluated))
        self.to_evaluate_card.update_value(str(max(0, submitted - evaluated)))
    
    def view_code(self, file_path):
        import os
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        
        # Normalize path separators (Django FileField uses forward slashes)
        normalized = file_path.replace('\\', os.sep).replace('/', os.sep)
        
        full_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            'backend', 'media', normalized
        )
        
        # For PDF files, open with system default viewer
        if full_path.lower().endswith('.pdf'):
            import subprocess
            try:
                os.startfile(full_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open PDF:\n{str(e)}")
            return
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                code = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}\nPath: {full_path}")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"View Code - {os.path.basename(file_path)}")
        dialog.resize(900, 700)
        
        layout = QVBoxLayout(dialog)
        
        code_viewer = QTextEdit()
        code_viewer.setReadOnly(True)
        code_viewer.setPlainText(code)
        code_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14px;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        close_btn.clicked.connect(dialog.accept)
        
        layout.addWidget(code_viewer)
        layout.addWidget(close_btn)
        dialog.exec()
    
    def _on_publish(self, row: int):
        if row not in self.submission_widgets:
            return
        
        submission_id, grade_input, feedback_input = self.submission_widgets[row]
        
        grade_text = grade_input.text().strip()
        feedback_text = feedback_input.text().strip()
        
        if not grade_text:
            QMessageBox.warning(self, "Validation Error", "Please enter a grade before publishing.")
            return
        
        try:
            marks = int(grade_text)
            if marks < 0 or marks > 100:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Grade must be a number between 0 and 100.")
            return
        
        try:
            response = requests.patch(
                f"http://localhost:8000/api/submissions/{submission_id}/",
                json={
                    "marks": marks,
                    "feedback": feedback_text,
                    "status": "evaluated"
                },
                headers={"Authorization": f"Bearer {api_client.access_token}"},
                timeout=5
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Result published to student successfully! 🎉")
                self.load_submissions()
            else:
                QMessageBox.critical(self, "Error", f"Failed to publish result. Status: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection Error: {str(e)}")
