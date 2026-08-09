import sys
from PyQt6.QtWidgets import QApplication
from ui import FormatterWindow

def main():
    app = QApplication(sys.argv)
    
    # Set a clean style if available
    app.setStyle("Fusion")
    
    window = FormatterWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
