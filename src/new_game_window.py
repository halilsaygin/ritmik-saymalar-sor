import os
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal
from .ui_generated.ui_new_game import Ui_NewGameDialog

class NewGameWindow(QWidget):
    game_started = Signal(int, int, int)  # step, time_limit, max_errors

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
        
        # Hide radio buttons
        self.ui.radioTimed.hide()
        self.ui.radioErrors.hide()
        
        # Add labels to the layouts instead of radio buttons
        from PySide6.QtWidgets import QLabel
        
        time_label = QLabel("Süre Sınırı:")
        time_label.setObjectName("timeLabel")
        self.ui.horizontalLayout_timed.insertWidget(0, time_label)
        
        error_label = QLabel("Hata Sınırı:")
        error_label.setObjectName("errorLabel")
        self.ui.horizontalLayout_errors.insertWidget(0, error_label)
        
        # Enable both settings
        self.ui.spinTime.setEnabled(True)
        self.ui.spinErrors.setEnabled(True)
        self.ui.modeGroupBox.setTitle("Oyun Ayarları")

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
        # Extract settings
        step_text = self.ui.countingCombo.currentText()
        try:
            import re
            step = int(re.search(r'\d+', step_text).group())
        except:
            step = 2

        time_limit = self.ui.spinTime.value()
        max_errors = self.ui.spinErrors.value()
        
        self.game_started.emit(step, time_limit, max_errors)
        self.close()
