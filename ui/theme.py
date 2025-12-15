from PyQt6.QtGui import QFont


class Theme:
    primary = "#3f51b5"  # Indigo
    secondary = "#009688"  # Teal
    background = "#f5f7fb"
    card_bg = "#ffffff"
    text_primary = "#1f2937"
    text_muted = "#6b7280"
    border = "#e5e7eb"
    success = "#22c55e"
    warning = "#f59e0b"
    danger = "#ef4444"
    shadow = "0 2px 8px rgba(15, 23, 42, 0.08)"


def app_stylesheet() -> str:
    return f"""
    QWidget {{
        background: {Theme.background};
        color: {Theme.text_primary};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 14px;
    }}
    QLineEdit, QComboBox, QTextEdit {{
        background: #fff;
        border: 1px solid {Theme.border};
        border-radius: 8px;
        padding: 6px 10px;
    }}
    QPushButton {{
        background: {Theme.primary};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 8px 14px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background: #334299; }}
    QPushButton:disabled {{ background: #cbd5e1; color: #94a3b8; }}
    QToolBar {{
        background: {Theme.card_bg};
        border-bottom: 1px solid {Theme.border};
    }}
    QTableWidget {{
        background: {Theme.card_bg};
        gridline-color: {Theme.border};
        border: 1px solid {Theme.border};
        border-radius: 12px;
    }}
    QHeaderView::section {{
        background: #f3f4f6;
        padding: 8px;
        border: 1px solid {Theme.border};
        font-weight: 600;
    }}
    QTabWidget::pane {{
        border: 1px solid {Theme.border};
        border-radius: 10px;
        padding: 6px;
    }}
    QTabBar::tab {{
        padding: 8px 14px;
        background: #e5e7eb;
        border-radius: 8px;
        margin: 4px;
    }}
    QTabBar::tab:selected {{
        background: {Theme.primary};
        color: white;
    }}
    """


def heading_font(size: int, bold: bool = True) -> QFont:
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    return font


def body_font(size: int, weight: int = QFont.Weight.Normal) -> QFont:
    font = QFont("Segoe UI", size)
    font.setWeight(weight)
    return font

