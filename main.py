import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.mainwindow import MainWindow

if __name__ == "__main__":
    QApplication.setApplicationName("ritmik_saymalar")
    QApplication.setApplicationDisplayName("Ritmik Saymalar Sor")
    QApplication.setDesktopFileName("ritmik-saymalar")
    
    app = QApplication(sys.argv)
    
    # Set application icon
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "resources", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
