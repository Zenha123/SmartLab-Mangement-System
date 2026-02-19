from PyQt6.QtWidgets import QTableWidget, QHeaderView
from PyQt6.QtCore import Qt
from ui.theme import Theme


class StyledTableWidget(QTableWidget):
    def __init__(self, rows: int = 0, cols: int = 0, parent=None):
        super().__init__(rows, cols, parent)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setWordWrap(False)
        self.setShowGrid(False)  # Cleaner look without grid lines
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Enhanced styling
        self.setStyleSheet(
            f"""
            QTableWidget {{
                alternate-background-color: {Theme.background};
                background: {Theme.card_bg};
                gridline-color: {Theme.border_light};
                border: 1px solid {Theme.border};
                border-radius: 12px;
            }}
            QTableWidget::item {{
                padding: 12px 8px;
                border: none;
            }}
            QTableWidget::item:hover {{
                background: {Theme.primary}08;
            }}
            QTableWidget::item:selected {{
                background: {Theme.primary}15;
                color: {Theme.primary};
            }}
            QHeaderView::section {{
                background: {Theme.background};
                color: {Theme.text_primary};
                padding: 14px 8px;
                border: none;
                border-bottom: 2px solid {Theme.border};
                font-weight: 700;
                font-size: 12px;
            }}
            """
        )
        
        self.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerItem)
        self.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerItem)
        self.setSortingEnabled(False)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumHeight(260)
        
        # Set header styling
        header = self.horizontalHeader()
        header.setDefaultSectionSize(120)
        header.setStretchLastSection(True)

