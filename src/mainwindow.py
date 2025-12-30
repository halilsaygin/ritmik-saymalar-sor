import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QGuiApplication
from .ui_generated.ui_form_main import Ui_MainWindow
from .new_game_window import NewGameWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Load style
        self.load_stylesheet()
        
        # Center the main window on screen
        self.center_on_screen()
        
        # Connect Menu Action
        self.ui.actionYeniOyun.triggered.connect(self.open_new_game_window)
        
        self.new_game_window = None

    def load_stylesheet(self):
        # Path: resources/styles/main.qss
        base_dir = os.path.dirname(os.path.dirname(__file__))
        style_path = os.path.join(base_dir, "resources", "styles", "main.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def center_on_screen(self):
        screen = QGuiApplication.primaryScreen().geometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def open_new_game_window(self):
        # Create the window if it doesn't exist
        if self.new_game_window is None:
            self.new_game_window = NewGameWindow(self)
        
        self.new_game_window.show()
        # Center relative to main window after showing (to ensure geometry is calculated)
        self.new_game_window.center_relative_to_parent()


