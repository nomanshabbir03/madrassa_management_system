# Color Constants
COLOR_SIDEBAR = "#1B4332"
COLOR_SIDEBAR_HOVER = "#2D6A4F"
COLOR_SIDEBAR_ACTIVE = "#D4A017"
COLOR_ACCENT = "#D4A017"
COLOR_ACCENT_HOVER = "#B8860B"
COLOR_BACKGROUND = "#FFFFFF"
COLOR_SURFACE = "#F8F9FA"
COLOR_TEXT_PRIMARY = "#1A1A1A"
COLOR_TEXT_LIGHT = "#FFFFFF"
COLOR_BORDER = "#E0E0E0"
COLOR_ERROR = "#DC3545"
COLOR_SUCCESS = "#28A745"
COLOR_WARNING = "#FFC107"
FONT_FAMILY = "Noto Nastaliq Urdu"
FONT_SIZE_NORMAL = 14
FONT_SIZE_LARGE = 16
FONT_SIZE_SMALL = 12

def get_main_stylesheet():
    """Return the main QSS stylesheet for the application."""
    return f"""
    QMainWindow, QWidget {{
        background-color: {COLOR_BACKGROUND};
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE_NORMAL}px;
    }}
    
    #sidebar {{
        background-color: {COLOR_SIDEBAR};
        border: none;
    }}
    
    #sidebar QPushButton {{
        color: {COLOR_TEXT_LIGHT};
        background-color: transparent;
        font-size: {FONT_SIZE_NORMAL}px;
        padding: 15px 20px;
        text-align: right;
        border: none;
        min-height: 45px;
        width: 100%;
    }}
    
    #sidebar QPushButton:hover {{
        background-color: {COLOR_SIDEBAR_HOVER};
    }}
    
    #sidebar QPushButton[active="true"] {{
        background-color: {COLOR_SIDEBAR_ACTIVE};
        color: {COLOR_TEXT_LIGHT};
        font-weight: bold;
    }}
    
    #logo_label {{
        color: {COLOR_TEXT_LIGHT};
        font-size: {FONT_SIZE_LARGE}px;
        font-weight: bold;
        padding: 20px;
        background-color: {COLOR_SIDEBAR};
    }}
    
    QPushButton {{
        background-color: {COLOR_ACCENT};
        color: {COLOR_TEXT_LIGHT};
        border-radius: 6px;
        padding: 8px 20px;
        font-size: {FONT_SIZE_NORMAL}px;
        font-family: {FONT_FAMILY};
        min-height: 35px;
    }}
    
    QPushButton:hover {{
        background-color: {COLOR_ACCENT_HOVER};
    }}
    
    QPushButton:pressed {{
        background-color: #9A7209;
    }}
    
    QPushButton#danger_btn {{
        background-color: {COLOR_ERROR};
    }}
    
    QPushButton#danger_btn:hover {{
        background-color: #C82333;
    }}
    
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {{
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        padding: 8px;
        font-size: {FONT_SIZE_NORMAL}px;
        font-family: {FONT_FAMILY};
        background-color: {COLOR_BACKGROUND};
        min-height: 35px;
    }}
    
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border: 2px solid {COLOR_ACCENT};
    }}
    
    QTableWidget {{
        border: 1px solid {COLOR_BORDER};
        gridline-color: {COLOR_BORDER};
        font-size: 13px;
        font-family: {FONT_FAMILY};
        background-color: {COLOR_BACKGROUND};
    }}
    
    QTableWidget::item {{
        padding: 8px;
        text-align: right;
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLOR_ACCENT};
        color: {COLOR_TEXT_LIGHT};
    }}
    
    QHeaderView::section {{
        background-color: {COLOR_SIDEBAR};
        color: {COLOR_TEXT_LIGHT};
        padding: 10px;
        font-size: 13px;
        font-family: {FONT_FAMILY};
        border: none;
    }}
    
    QLabel {{
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE_NORMAL}px;
        color: {COLOR_TEXT_PRIMARY};
    }}
    
    QLabel#heading_label {{
        font-size: 18px;
        font-weight: bold;
        color: {COLOR_SIDEBAR};
    }}
    
    QLabel#error_label {{
        color: {COLOR_ERROR};
        font-size: {FONT_SIZE_SMALL}px;
    }}
    
    QFrame#card_frame {{
        background-color: {COLOR_SURFACE};
        border-radius: 8px;
        border: 1px solid {COLOR_BORDER};
    }}
    
    QScrollBar:vertical {{
        width: 8px;
        background-color: {COLOR_SURFACE};
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLOR_SIDEBAR};
        border-radius: 4px;
    }}
    
    QMessageBox {{
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE_NORMAL}px;
    }}
    
    QTabWidget::pane {{
        border: 1px solid {COLOR_BORDER};
    }}
    
    QTabBar::tab {{
        background-color: {COLOR_SURFACE};
        padding: 10px 20px;
        font-family: {FONT_FAMILY};
        font-size: 13px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLOR_SIDEBAR};
        color: {COLOR_TEXT_LIGHT};
    }}
    """

def get_card_style(color="#F8F9FA"):
    """Return QSS style for a summary card widget."""
    return f"""
    QFrame {{
        background-color: {color};
        border-radius: 10px;
        border: 1px solid {COLOR_BORDER};
        padding: 15px;
    }}
    """

def apply_table_style(table_widget):
    """Apply styling to a QTableWidget."""
    # Set alternating row colors
    table_widget.setAlternatingRowColors(True)
    table_widget.setStyleSheet(f"""
        QTableWidget {{
            alternate-background-color: {COLOR_SURFACE};
            background-color: {COLOR_BACKGROUND};
        }}
    """)
    
    # Set row height
    table_widget.verticalHeader().setDefaultSectionSize(40)
    
    # Hide vertical header
    table_widget.verticalHeader().setVisible(False)
    
    # Set horizontal header to stretch last section
    table_widget.horizontalHeader().setStretchLastSection(True)
    
    # Enable RTL layout
    table_widget.setLayoutDirection(1)  # Qt.RightToLeft