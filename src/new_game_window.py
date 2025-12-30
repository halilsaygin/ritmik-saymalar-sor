import os
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from .ui_generated.ui_new_game import Ui_NewGameDialog

class NewGameWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_NewGameDialog()
        self.ui.setupUi(self)
        
        # Set window as a standard window that stays on top of parent
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        self.setWindowModality(Qt.WindowModal)
        
        # Load dedicated stylesheet
        self.load_stylesheet()
        
        # UI Interactions
        self.ui.btnStart.clicked.connect(self.on_start_clicked)
        
        # Toggle spinboxes based on radio buttons
        self.ui.radioTimed.toggled.connect(self.ui.spinTime.setEnabled)
        self.ui.radioErrors.toggled.connect(self.ui.spinErrors.setEnabled)
        
        # Initial state
        self.ui.spinErrors.setEnabled(False)

    def load_stylesheet(self):
        # Path: resources/styles/new_game.qss
        base_dir = os.path.dirname(os.path.dirname(__file__))
        style_path = os.path.join(base_dir, "resources", "styles", "new_game.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def center_relative_to_parent(self):
        if self.parentWidget():
            parent_geo = self.parentWidget().geometry()
            child_geo = self.geometry()
            x = parent_geo.x() + (parent_geo.width() - child_geo.width()) // 2
            y = parent_geo.y() + (parent_geo.height() - child_geo.height()) // 2
            self.move(x, y)

    def on_start_clicked(self):
        # This is where the game initialization logic would go
        print("Starting new game with settings:")
        print(f"Counting: {self.ui.countingCombo.currentText()}")
        if self.ui.radioTimed.isChecked():
            print(f"Mode: Timed ({self.ui.spinTime.value()} seconds)")
        else:
            print(f"Mode: Error Limited ({self.ui.spinErrors.value()} errors)")
        
        self.close()
