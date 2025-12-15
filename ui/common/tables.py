from PyQt6.QtWidgets import QTableWidget, QHeaderView
from PyQt6.QtCore import Qt


class StyledTableWidget(QTableWidget):
    def __init__(self, rows: int = 0, cols: int = 0, parent=None):
        super().__init__(rows, cols, parent)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setWordWrap(False)
        self.setShowGrid(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setStyleSheet(
            """
            QTableWidget {
                alternate-background-color: #f8fafc;
            }
            QTableWidget::item:selected {
                background: #e0e7ff;
            }
            """
        )
        self.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.setSortingEnabled(False)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumHeight(260)

