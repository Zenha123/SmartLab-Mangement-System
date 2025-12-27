from PyQt6.QtGui import QFont, QColor


class Theme:
    # Professional Color Palette - Enterprise Grade
    primary = "#1E2A38"  # Deep Blue / Indigo
    primary_light = "#2C3E50"  # Lighter indigo
    primary_hover = "#34495E"  # Hover state
    secondary = "#1ABC9C"  # Teal / Emerald
    secondary_light = "#2ECC71"  # Light teal
    background = "#F4F6F8"  # Light grey / off-white
    card_bg = "#FFFFFF"  # Pure white
    text_primary = "#1F2937"  # Dark grey
    text_secondary = "#4B5563"  # Medium grey
    text_muted = "#6B7280"  # Light grey
    border = "#E5E7EB"  # Light border
    border_light = "#F3F4F6"  # Very light border
    
    # Status Colors
    success = "#10B981"  # Green
    success_light = "#D1FAE5"  # Light green background
    warning = "#F59E0B"  # Orange
    warning_light = "#FEF3C7"  # Light orange background
    danger = "#EF4444"  # Red
    danger_light = "#FEE2E2"  # Light red background
    info = "#3B82F6"  # Blue
    info_light = "#DBEAFE"  # Light blue background
    
    # Shadows
    shadow_sm = "0 1px 2px rgba(0, 0, 0, 0.05)"
    shadow = "0 2px 8px rgba(0, 0, 0, 0.08)"
    shadow_md = "0 4px 12px rgba(0, 0, 0, 0.1)"
    shadow_lg = "0 8px 24px rgba(0, 0, 0, 0.12)"
    
    # Spacing
    spacing_xs = 4
    spacing_sm = 8
    spacing_md = 12
    spacing_lg = 16
    spacing_xl = 24


def app_stylesheet() -> str:
    return f"""
    /* Global Styles */
    QWidget {{
        background: {Theme.background};
        color: {Theme.text_primary};
        font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
        font-size: 14px;
    }}
    
    /* Input Fields */
    QLineEdit, QComboBox, QTextEdit, QSpinBox, QDoubleSpinBox {{
        background: {Theme.card_bg};
        border: 1px solid {Theme.border};
        border-radius: 8px;
        padding: 8px 12px;
        selection-background-color: {Theme.primary};
        selection-color: white;
    }}
    QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
        border: 2px solid {Theme.primary};
        background: {Theme.card_bg};
    }}
    QLineEdit:hover, QComboBox:hover {{
        border: 1px solid {Theme.primary_light};
    }}
    
    /* Buttons */
    QPushButton {{
        background: {Theme.primary};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: {Theme.primary_hover};
    }}
    QPushButton:pressed {{
        background: {Theme.primary_light};
    }}
    QPushButton:disabled {{
        background: {Theme.border};
        color: {Theme.text_muted};
    }}
    
    /* Primary Action Button */
    QPushButton[class="primary"] {{
        background: {Theme.primary};
    }}
    QPushButton[class="primary"]:hover {{
        background: {Theme.primary_hover};
    }}
    
    /* Success Button */
    QPushButton[class="success"] {{
        background: {Theme.success};
    }}
    QPushButton[class="success"]:hover {{
        background: #059669;
    }}
    
    /* Danger Button */
    QPushButton[class="danger"] {{
        background: {Theme.danger};
    }}
    QPushButton[class="danger"]:hover {{
        background: #DC2626;
    }}
    
    /* Warning Button */
    QPushButton[class="warning"] {{
        background: {Theme.warning};
    }}
    QPushButton[class="warning"]:hover {{
        background: #D97706;
    }}
    
    /* Secondary Button */
    QPushButton[class="secondary"] {{
        background: {Theme.secondary};
    }}
    QPushButton[class="secondary"]:hover {{
        background: #16A085;
    }}
    
    /* Toolbar */
    QToolBar {{
        background: {Theme.card_bg};
        border: none;
        border-bottom: 1px solid {Theme.border};
        padding: 8px;
        spacing: 8px;
    }}
    QToolBar::separator {{
        background: {Theme.border};
        width: 1px;
        margin: 4px 8px;
    }}
    
    /* Tables */
    QTableWidget {{
        background: {Theme.card_bg};
        gridline-color: {Theme.border_light};
        border: 1px solid {Theme.border};
        border-radius: 12px;
        alternate-background-color: {Theme.background};
        selection-background-color: {Theme.primary}20;
        selection-color: {Theme.primary};
    }}
    QTableWidget::item {{
        padding: 10px 8px;
        border: none;
    }}
    QTableWidget::item:hover {{
        background: {Theme.primary}10;
    }}
    QTableWidget::item:selected {{
        background: {Theme.primary}25;
        color: {Theme.primary};
    }}
    
    /* Table Headers */
    QHeaderView::section {{
        background: {Theme.background};
        color: {Theme.text_primary};
        padding: 12px 8px;
        border: none;
        border-bottom: 2px solid {Theme.border};
        font-weight: 700;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    QHeaderView::section:first {{
        border-top-left-radius: 12px;
    }}
    QHeaderView::section:last {{
        border-top-right-radius: 12px;
    }}
    
    /* Scrollbars */
    QScrollBar:vertical {{
        background: {Theme.background};
        width: 12px;
        border: none;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical {{
        background: {Theme.border};
        border-radius: 6px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {Theme.text_muted};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background: {Theme.background};
        height: 12px;
        border: none;
        border-radius: 6px;
    }}
    QScrollBar::handle:horizontal {{
        background: {Theme.border};
        border-radius: 6px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {Theme.text_muted};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* Tabs */
    QTabWidget::pane {{
        background: {Theme.card_bg};
        border: 1px solid {Theme.border};
        border-radius: 10px;
        padding: 8px;
    }}
    QTabBar::tab {{
        background: {Theme.background};
        color: {Theme.text_secondary};
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
        margin-right: 4px;
        font-weight: 600;
    }}
    QTabBar::tab:hover {{
        background: {Theme.border_light};
        color: {Theme.text_primary};
    }}
    QTabBar::tab:selected {{
        background: {Theme.card_bg};
        color: {Theme.primary};
        border-bottom: 3px solid {Theme.primary};
    }}
    
    /* Progress Bars */
    QProgressBar {{
        background: {Theme.border_light};
        border: none;
        border-radius: 8px;
        text-align: center;
        color: {Theme.text_primary};
        font-weight: 600;
        height: 24px;
    }}
    QProgressBar::chunk {{
        background: {Theme.primary};
        border-radius: 8px;
    }}
    
    /* Checkboxes */
    QCheckBox {{
        spacing: 8px;
        color: {Theme.text_primary};
    }}
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid {Theme.border};
        border-radius: 4px;
        background: {Theme.card_bg};
    }}
    QCheckBox::indicator:hover {{
        border-color: {Theme.primary};
    }}
    QCheckBox::indicator:checked {{
        background: {Theme.primary};
        border-color: {Theme.primary};
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNEw2IDEyTDIuNjY2NjcgOC42NjY2NyIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
    }}
    
    /* List Widget */
    QListWidget {{
        background: {Theme.card_bg};
        border: 1px solid {Theme.border};
        border-radius: 12px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 10px 12px;
        border-radius: 8px;
        margin: 2px;
    }}
    QListWidget::item:hover {{
        background: {Theme.primary}10;
    }}
    QListWidget::item:selected {{
        background: {Theme.primary}25;
        color: {Theme.primary};
    }}
    
    /* Status Bar */
    QStatusBar {{
        background: {Theme.card_bg};
        border-top: 1px solid {Theme.border};
        color: {Theme.text_secondary};
    }}
    """


def heading_font(size: int, bold: bool = True) -> QFont:
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    if size >= 20:
        font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 102)
    return font


def body_font(size: int, weight: int = QFont.Weight.Normal) -> QFont:
    font = QFont("Segoe UI", size)
    font.setWeight(weight)
    return font


def get_color(color_name: str) -> QColor:
    """Get QColor from theme color name"""
    color_map = {
        "primary": Theme.primary,
        "secondary": Theme.secondary,
        "success": Theme.success,
        "warning": Theme.warning,
        "danger": Theme.danger,
        "info": Theme.info,
    }
    return QColor(color_map.get(color_name, Theme.primary))

