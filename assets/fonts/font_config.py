import os
from PyQt5.QtGui import QFontDatabase, QFont

# Font directory and file paths
FONT_DIR = os.path.dirname(os.path.abspath(__file__))
URDU_FONT_NAME = "Jameel Noori Nastaleeq"
URDU_FONT_PATH = os.path.join(FONT_DIR, "Jameel Noori Nastaleeq Regular.ttf")
FALLBACK_FONT_PATH = os.path.join(FONT_DIR, "Jameel Noori Nastaleeq Kasheeda.ttf")

def get_font_path():
    """Get the available Urdu font path."""
    if os.path.exists(URDU_FONT_PATH):
        return URDU_FONT_PATH
    elif os.path.exists(FALLBACK_FONT_PATH):
        return FALLBACK_FONT_PATH
    else:
        print("WARNING: No Urdu font found in assets/fonts/")
        return None

def register_font_with_qt(app):
    """Register Urdu font with Qt application and set as default."""
    font_path = get_font_path()
    if font_path:
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            # Set default application font
            font = QFont(URDU_FONT_NAME, 14)
            app.setFont(font)
            return True
        else:
            print("WARNING: Failed to register font with Qt")
            return False
    else:
        print("WARNING: No font file available to register")
        return False
