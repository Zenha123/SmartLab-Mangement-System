from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox, QPushButton

from ui.common.cards import CardFrame
from ui.theme import heading_font
from data.mock_data import reports_attendance


class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("Reports")
        title.setFont(heading_font(18))
        root.addWidget(title)

        filters = QHBoxLayout()
        self.date_filter = QComboBox()
        self.date_filter.addItems(["All Dates", *[r["date"] for r in reports_attendance]])
        self.sem_filter = QComboBox()
        self.sem_filter.addItems([f"Sem {i}" for i in range(1, 9)])
        self.batch_filter = QComboBox()
        self.batch_filter.addItems(["Batch 1", "Batch 2"])
        export_btn = QPushButton("Export")
        filters.addWidget(self.date_filter)
        filters.addWidget(self.sem_filter)
        filters.addWidget(self.batch_filter)
        filters.addWidget(export_btn)
        filters.addStretch(1)
        root.addLayout(filters)

        tabs = QTabWidget()
        tabs.addTab(self._attendance_tab(), "Attendance")
        tabs.addTab(self._generic_tab("Viva Marks"), "Viva Marks")
        tabs.addTab(self._generic_tab("Submissions"), "Submissions")
        root.addWidget(tabs)
        root.addStretch(1)

    def _attendance_tab(self):
        widget = CardFrame()
        table = QTableWidget(len(reports_attendance), 3)
        table.setHorizontalHeaderLabels(["Date", "Present", "Absent"])
        for r, row in enumerate(reports_attendance):
            table.setItem(r, 0, QTableWidgetItem(row["date"]))
            table.setItem(r, 1, QTableWidgetItem(str(row["present"])))
            table.setItem(r, 2, QTableWidgetItem(str(row["absent"])))
        widget.layout.addWidget(table)
        return widget

    def _generic_tab(self, title: str):
        widget = CardFrame()
        widget.layout.addWidget(QLabel(f"{title} table placeholder"))
        return widget

