from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.common.cards import CardFrame
from ui.common.tables import StyledTableWidget
from ui.theme import heading_font, Theme, body_font
from data.mock_data import reports_attendance


class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("📄 Reports")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        # Filters
        filters_card = CardFrame(padding=16)
        filters_label = QLabel("🔍 Filters:")
        filters_label.setFont(body_font(13, QFont.Weight.DemiBold))
        filters_label.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 12px;")
        filters_card.layout.addWidget(filters_label)
        
        filters = QHBoxLayout()
        filters.setSpacing(12)
        
        date_label = QLabel("Date:")
        date_label.setFont(body_font(12))
        date_label.setStyleSheet(f"color: {Theme.text_secondary};")
        self.date_filter = QComboBox()
        self.date_filter.addItems(["All Dates", *[r["date"] for r in reports_attendance]])
        self.date_filter.setStyleSheet(
            f"""
            QComboBox {{
                border: 1px solid {Theme.border};
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 150px;
            }}
            """
        )
        
        sem_label = QLabel("Semester:")
        sem_label.setFont(body_font(12))
        sem_label.setStyleSheet(f"color: {Theme.text_secondary};")
        self.sem_filter = QComboBox()
        self.sem_filter.addItems([f"Sem {i}" for i in range(1, 9)])
        self.sem_filter.setStyleSheet(
            f"""
            QComboBox {{
                border: 1px solid {Theme.border};
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 120px;
            }}
            """
        )
        
        batch_label = QLabel("Batch:")
        batch_label.setFont(body_font(12))
        batch_label.setStyleSheet(f"color: {Theme.text_secondary};")
        self.batch_filter = QComboBox()
        self.batch_filter.addItems(["Batch 1", "Batch 2"])
        self.batch_filter.setStyleSheet(
            f"""
            QComboBox {{
                border: 1px solid {Theme.border};
                border-radius: 6px;
                padding: 8px 12px;
                min-width: 120px;
            }}
            """
        )
        
        export_btn = QPushButton("📥 Export Report")
        export_btn.setProperty("class", "primary")
        export_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {Theme.primary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: {Theme.primary_hover};
            }}
            """
        )
        
        filters.addWidget(date_label)
        filters.addWidget(self.date_filter)
        filters.addWidget(sem_label)
        filters.addWidget(self.sem_filter)
        filters.addWidget(batch_label)
        filters.addWidget(self.batch_filter)
        filters.addStretch()
        filters.addWidget(export_btn)
        filters_card.layout.addLayout(filters)
        root.addWidget(filters_card)

        tabs = QTabWidget()
        tabs.addTab(self._attendance_tab(), "📊 Attendance")
        tabs.addTab(self._generic_tab("Viva Marks"), "🎤 Viva Marks")
        tabs.addTab(self._generic_tab("Submissions"), "📝 Submissions")
        root.addWidget(tabs)
        root.addStretch(1)

    def _attendance_tab(self):
        widget = CardFrame(padding=20)
        table = StyledTableWidget(len(reports_attendance), 3)
        table.setHorizontalHeaderLabels(["Date", "Present", "Absent"])
        for r, row in enumerate(reports_attendance):
            date_item = QTableWidgetItem(row["date"])
            date_item.setFont(body_font(13))
            table.setItem(r, 0, date_item)
            
            present_item = QTableWidgetItem(str(row["present"]))
            present_item.setFont(body_font(13, QFont.Weight.DemiBold))
            present_item.setForeground(QColor(Theme.success))
            table.setItem(r, 1, present_item)
            
            absent_item = QTableWidgetItem(str(row["absent"]))
            absent_item.setFont(body_font(13, QFont.Weight.DemiBold))
            absent_item.setForeground(QColor(Theme.danger))
            table.setItem(r, 2, absent_item)
        widget.layout.addWidget(table)
        return widget

    def _generic_tab(self, title: str):
        widget = CardFrame(padding=40)
        placeholder = QLabel(f"📋 {title} Report\n\nThis section will display {title.lower()} data based on selected filters.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(body_font(14))
        placeholder.setStyleSheet(f"color: {Theme.text_muted};")
        widget.layout.addWidget(placeholder)
        return widget

