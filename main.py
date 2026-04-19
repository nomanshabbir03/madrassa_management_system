import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt

from ui.main_window import MainWindow
from database import initialize_database
from assets.fonts.font_config import get_font_path, register_font_with_qt

def main():
    """Main entry point for the Madrassa Management System."""
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Set application layout direction to RTL globally
    app.setLayoutDirection(Qt.RightToLeft)
    
    # Set application name
    app.setApplicationName("مدارسہ مینجمنٹ سسٹم")
    
    # Register Urdu font
    register_font_with_qt(app)
    
    # Set default application font explicitly
    default_font = QFont("Noto Nastaliq Urdu", 14)
    app.setFont(default_font)
    
    # Initialize database
    initialize_database()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()