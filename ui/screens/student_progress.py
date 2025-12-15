from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QProgressBar, QTableWidgetItem, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt

from ui.common.cards import CardFrame, StatCard
from ui.common.tables import StyledTableWidget
from ui.theme import heading_font, Theme, body_font
from data.mock_data import progress_rows


class StudentProgressScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("Students Progress")
        title.setFont(heading_font(18))
        root.addWidget(title)

        content = QHBoxLayout()
        content.setSpacing(12)
        root.addLayout(content)

        table_card = CardFrame()
        table = StyledTableWidget(len(progress_rows), 6)
        table.setHorizontalHeaderLabels(["Student", "Student ID", "Content Progress", "Grades", "Goal", "Performance"])
        for row, item in enumerate(progress_rows):
            table.setItem(row, 0, QTableWidgetItem(item["name"]))
            table.setItem(row, 1, QTableWidgetItem(item["id"]))

            progress_widget = self._progress_cell(item["visited"], item["progress"])
            table.setCellWidget(row, 2, progress_widget)

            table.setItem(row, 3, QTableWidgetItem(item["grade"]))
            table.setItem(row, 4, QTableWidgetItem(item["goal"]))
            perf_lbl = QLabel(item["performance"])
            perf_lbl.setStyleSheet(
                f"color: {Theme.success if item['performance'].lower() == 'great' else Theme.warning}; font-weight: 600;"
            )
            perf_holder = QWidget()
            ph_layout = QHBoxLayout(perf_holder)
            ph_layout.setContentsMargins(6, 4, 6, 4)
            ph_layout.addWidget(perf_lbl)
            ph_layout.addStretch()
            table.setCellWidget(row, 5, perf_holder)
        table_card.layout.addWidget(table)
        content.addWidget(table_card, stretch=3)

        side = QVBoxLayout()
        side.setSpacing(10)

        stats_card = CardFrame()
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setSpacing(10)
        stats_layout.addWidget(StatCard("Performance Statistics", "Semester Trend", accent=Theme.primary, subtitle="UI-only demo"))
        stats_layout.addWidget(self._bar_placeholder("Great", 70, Theme.success))
        stats_layout.addWidget(self._bar_placeholder("Good", 20, Theme.warning))
        stats_layout.addWidget(self._bar_placeholder("At risk", 10, Theme.danger))
        side.addWidget(stats_card)

        risk_card = CardFrame()
        risk_layout = QVBoxLayout(risk_card)
        risk_layout.setSpacing(6)
        heading = QLabel("Students at Risk")
        heading.setFont(body_font(12, weight=600))
        risk_layout.addWidget(heading)

        risk_list = QListWidget()
        for name in ["Decca Thomas", "John Doe", "Mike Harry"]:
            item = QListWidgetItem(f"{name} - Underperformed")
            risk_list.addItem(item)
        risk_card.layout.addWidget(risk_list)
        side.addWidget(risk_card)

        content.addLayout(side, stretch=1)
        root.addStretch(1)

    def _progress_cell(self, visited: int, pct: int):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        bar = QProgressBar()
        bar.setValue(pct)
        bar.setFormat(f"{pct}%  |  Visited {visited}/100")
        bar.setStyleSheet(
            f"""
            QProgressBar {{
                background: #e5e7eb;
                border: none;
                border-radius: 6px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: {Theme.primary};
                border-radius: 6px;
            }}
            """
        )
        layout.addWidget(bar)
        return widget

    def _bar_placeholder(self, label: str, value: int, color: str):
        wrap = QWidget()
        l = QVBoxLayout(wrap)
        l.setContentsMargins(0, 0, 0, 0)
        text = QLabel(label)
        text.setStyleSheet("font-weight: 600;")
        bar = QProgressBar()
        bar.setMaximum(100)
        bar.setValue(value)
        bar.setTextVisible(False)
        bar.setStyleSheet(
            f"""
            QProgressBar {{
                background: #e5e7eb;
                border: none;
                border-radius: 8px;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 8px;
            }}
            """
        )
        l.addWidget(text)
        l.addWidget(bar)
        return wrap

