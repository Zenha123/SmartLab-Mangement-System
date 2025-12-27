from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QProgressBar, QTableWidgetItem, QListWidget, QListWidgetItem, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.common.cards import CardFrame, StatCard
from ui.common.tables import StyledTableWidget
from ui.theme import heading_font, Theme, body_font
from data.mock_data import progress_rows


class StudentProgressScreen(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("📈 Students Progress")
        title.setFont(heading_font(24, bold=True))
        title.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 4px;")
        root.addWidget(title)

        content = QHBoxLayout()
        content.setSpacing(20)
        root.addLayout(content)

        table_card = CardFrame(padding=20)
        table = StyledTableWidget(len(progress_rows), 6)
        table.setHorizontalHeaderLabels(["Student", "Student ID", "Content Progress", "Grades", "Goal", "Performance"])
        for row, item in enumerate(progress_rows):
            # Student name with avatar
            name_item = QTableWidgetItem(f"👤 {item['name']}")
            name_item.setFont(body_font(13, QFont.Weight.Medium))
            table.setItem(row, 0, name_item)
            
            # Student ID
            id_item = QTableWidgetItem(item["id"])
            id_item.setFont(body_font(12))
            id_item.setForeground(QColor(Theme.text_secondary))
            table.setItem(row, 1, id_item)

            progress_widget = self._progress_cell(item["visited"], item["progress"])
            table.setCellWidget(row, 2, progress_widget)

            # Grades
            grade_item = QTableWidgetItem(item["grade"])
            grade_item.setFont(body_font(13, QFont.Weight.DemiBold))
            grade_item.setForeground(QColor(Theme.primary))
            table.setItem(row, 3, grade_item)
            
            # Goal
            goal_item = QTableWidgetItem(item["goal"])
            goal_item.setFont(body_font(13, QFont.Weight.Medium))
            goal_item.setForeground(QColor(Theme.secondary))
            table.setItem(row, 4, goal_item)
            
            # Performance badge
            perf_color = Theme.success if item['performance'].lower() == 'great' else (Theme.warning if 'good' in item['performance'].lower() else Theme.danger)
            perf_lbl = QLabel(item["performance"])
            perf_lbl.setFont(body_font(12, QFont.Weight.Bold))
            perf_lbl.setStyleSheet(
                f"color: {perf_color}; padding: 4px 12px; background: {perf_color}15; border-radius: 12px;"
            )
            perf_holder = QWidget()
            ph_layout = QHBoxLayout(perf_holder)
            ph_layout.setContentsMargins(8, 6, 8, 6)
            ph_layout.addWidget(perf_lbl)
            ph_layout.addStretch()
            table.setCellWidget(row, 5, perf_holder)
        table_card.layout.addWidget(table)
        content.addWidget(table_card, stretch=3)

        side = QVBoxLayout()
        side.setSpacing(16)

        # Performance Statistics Card
        stats_card = CardFrame(padding=20)
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setSpacing(16)
        
        heading = QLabel("📊 Performance Statistics")
        heading.setFont(body_font(14, QFont.Weight.Bold))
        heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 8px;")
        stats_layout.addWidget(heading)
        
        # Legend
        legend = QHBoxLayout()
        legend.setSpacing(12)
        for label, color in [("Great", Theme.success), ("Good", Theme.warning), ("At risk", Theme.danger)]:
            legend_item = QHBoxLayout()
            legend_item.setSpacing(6)
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 12px;")
            legend_lbl = QLabel(label)
            legend_lbl.setFont(body_font(11))
            legend_lbl.setStyleSheet(f"color: {Theme.text_muted};")
            legend_item.addWidget(dot)
            legend_item.addWidget(legend_lbl)
            legend_widget = QWidget()
            legend_widget.setLayout(legend_item)
            legend.addWidget(legend_widget)
        legend.addStretch()
        stats_layout.addLayout(legend)
        
        # Bars
        stats_layout.addWidget(self._bar_placeholder("Great", 70, Theme.success))
        stats_layout.addWidget(self._bar_placeholder("Good", 20, Theme.warning))
        stats_layout.addWidget(self._bar_placeholder("At risk", 10, Theme.danger))
        stats_layout.addStretch()
        side.addWidget(stats_card)

        # Students at Risk Card
        risk_card = CardFrame(padding=20)
        risk_layout = QVBoxLayout(risk_card)
        risk_layout.setSpacing(12)
        
        heading = QLabel("⚠️ Students at Risk")
        heading.setFont(body_font(14, QFont.Weight.Bold))
        heading.setStyleSheet(f"color: {Theme.text_primary}; margin-bottom: 8px;")
        risk_layout.addWidget(heading)

        risk_list = QListWidget()
        risk_list.setStyleSheet(
            f"""
            QListWidget {{
                border: none;
                background: transparent;
            }}
            QListWidget::item {{
                padding: 12px;
                margin: 4px 0px;
                background: {Theme.danger_light};
                border-left: 3px solid {Theme.danger};
                border-radius: 6px;
            }}
            QListWidget::item:hover {{
                background: {Theme.danger_light};
            }}
            """
        )
        risk_data = [
            ("Decca Thomas", "32%", "Under performed in Projects"),
            ("John Doe", "12%", "Under performed in Exams"),
            ("Mike Harry", "30%", "Low attendance"),
        ]
        for name, pct, reason in risk_data:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)
            
            name_lbl = QLabel(f"👤 {name}")
            name_lbl.setFont(body_font(12, QFont.Weight.DemiBold))
            name_lbl.setStyleSheet(f"color: {Theme.text_primary};")
            
            reason_lbl = QLabel(reason)
            reason_lbl.setFont(body_font(11))
            reason_lbl.setStyleSheet(f"color: {Theme.text_muted};")
            
            pct_lbl = QLabel(pct)
            pct_lbl.setFont(body_font(13, QFont.Weight.Bold))
            pct_lbl.setStyleSheet(f"color: {Theme.danger};")
            pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            
            item_layout.addWidget(name_lbl)
            item_layout.addWidget(reason_lbl)
            
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            risk_list.addItem(item)
            risk_list.setItemWidget(item, item_widget)
        
        risk_card.layout.addWidget(risk_list)
        
        # View all link
        view_all = QLabel("View all →")
        view_all.setFont(body_font(11))
        view_all.setStyleSheet(f"color: {Theme.primary}; text-decoration: underline; cursor: pointer;")
        view_all.setAlignment(Qt.AlignmentFlag.AlignRight)
        risk_layout.addWidget(view_all)
        
        side.addWidget(risk_card)

        content.addLayout(side, stretch=1)
        root.addStretch(1)

    def _progress_cell(self, visited: int, pct: int):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        bar = QProgressBar()
        bar.setValue(pct)
        bar.setFormat(f"{pct}%")
        bar.setStyleSheet(
            f"""
            QProgressBar {{
                background: {Theme.border_light};
                border: none;
                border-radius: 8px;
                height: 24px;
                text-align: center;
                color: {Theme.text_primary};
                font-weight: 600;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Theme.success}, stop:1 {Theme.secondary});
                border-radius: 8px;
            }}
            """
        )
        
        info_label = QLabel(f"Visited {visited}/100")
        info_label.setFont(body_font(11))
        info_label.setStyleSheet(f"color: {Theme.text_muted};")
        
        layout.addWidget(bar)
        layout.addWidget(info_label)
        return widget

    def _bar_placeholder(self, label: str, value: int, color: str):
        wrap = QWidget()
        l = QVBoxLayout(wrap)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(8)
        
        header = QHBoxLayout()
        text = QLabel(label)
        text.setFont(body_font(12, QFont.Weight.DemiBold))
        text.setStyleSheet(f"color: {Theme.text_primary};")
        pct_label = QLabel(f"{value}%")
        pct_label.setFont(body_font(12, QFont.Weight.Bold))
        pct_label.setStyleSheet(f"color: {color};")
        header.addWidget(text)
        header.addStretch()
        header.addWidget(pct_label)
        header_widget = QWidget()
        header_widget.setLayout(header)
        
        bar = QProgressBar()
        bar.setMaximum(100)
        bar.setValue(value)
        bar.setTextVisible(False)
        bar.setFixedHeight(12)
        bar.setStyleSheet(
            f"""
            QProgressBar {{
                background: {Theme.border_light};
                border: none;
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 6px;
            }}
            """
        )
        l.addWidget(header_widget)
        l.addWidget(bar)
        return wrap

