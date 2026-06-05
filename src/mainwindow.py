import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QTimer, QUrl
# Attempt to import QSoundEffect; if unavailable, try pygame as fallback
try:
    from PySide6.QtMultimedia import QSoundEffect
    _sound_backend = "qt"
except Exception:  # pragma: no cover
    QSoundEffect = None
    _sound_backend = None
    try:
        import pygame
        pygame.mixer.init()
        _sound_backend = "pygame"
    except Exception:
        _sound_backend = None
from .ui_generated.ui_form_main import Ui_MainWindow
from .new_game_window import NewGameWindow
from .game_engine import GameEngine

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Ritmik Saymalar Sor")
        
        # Load style
        self.load_stylesheet()
        
        # Center the main window on screen
        self.center_on_screen()
        
        # Set Window Icon
        base_dir = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(base_dir, "resources", "icons", "app_icon.png")
        if os.path.exists(icon_path):
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
            
        # Set all fields to "?" at the beginning and make progress bar full green
        self.ui.stepLabel.setText("?")
        self.ui.numberLabel.setText("?")
        self.ui.btn_option1.setText("?")
        self.ui.btn_option2.setText("?")
        self.ui.btn_option3.setText("?")
        self.ui.timeProgress.setValue(self.ui.timeProgress.maximum())
        self.ui.timeProgress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #dce0e8;
                height: 8px;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #40a02b;
                border-radius: 4px;
            }
        """)
        
        # Create Error Count Label dynamically at the top left
        from PySide6.QtWidgets import QLabel, QSpacerItem, QSizePolicy
        from PySide6.QtCore import Qt
        self.errorLabel = QLabel(self)
        self.errorLabel.setObjectName("errorLabel")
        self.errorLabel.setAlignment(Qt.AlignCenter)
        self.errorLabel.setText("? / ?")
        self.errorLabel.setStyleSheet("""
            QLabel#errorLabel {
                background-color: #fcebeb;
                color: #d20f39;
                border: 1px solid #f9d6d6;
                border-radius: 10px;
                padding: 4px 12px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.ui.horizontalLayout_top.insertWidget(0, self.errorLabel)
        
        # Create Score Label dynamically at the top center
        self.scoreLabel = QLabel(self)
        self.scoreLabel.setObjectName("scoreLabel")
        self.scoreLabel.setAlignment(Qt.AlignCenter)
        self.scoreLabel.setText("Skor: ?")
        self.scoreLabel.setStyleSheet("""
            QLabel#scoreLabel {
                background-color: #e8f5e9;
                color: #40a02b;
                border: 1px solid #c8e6c9;
                border-radius: 10px;
                padding: 4px 12px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        # Layout: [errorLabel] [spacer] [scoreLabel] [spacer] [stepLabel]
        # spacer at index 1 already exists, insert scoreLabel at index 2 (before stepLabel)
        self.ui.horizontalLayout_top.insertWidget(2, self.scoreLabel)
        # Add another spacer after scoreLabel to keep it centered
        self.ui.horizontalLayout_top.insertItem(3, QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        # Connect Menu Action
        self.ui.actionYeniOyun.triggered.connect(self.open_new_game_window)
        
        # Game Engine
        self.engine = GameEngine()
        self.new_game_window = None
        
        # Timers
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_time_limit)
        self.remaining_time = 0
        
        # Connect Buttons
        self.ui.btn_option1.clicked.connect(lambda: self.handle_answer(self.ui.btn_option1))
        self.ui.btn_option2.clicked.connect(lambda: self.handle_answer(self.ui.btn_option2))
        self.ui.btn_option3.clicked.connect(lambda: self.handle_answer(self.ui.btn_option3))

        # Load sound effects using the available backend
        if _sound_backend == "qt":
            self.sound_correct = QSoundEffect(self)
            self.sound_wrong = QSoundEffect(self)
            base_dir = os.path.dirname(os.path.dirname(__file__))
            correct_path = os.path.join(base_dir, "resources", "sound", "correct.mp3")
            wrong_path = os.path.join(base_dir, "resources", "sound", "wrong.mp3")
            self.sound_correct.setSource(QUrl.fromLocalFile(correct_path))
            self.sound_wrong.setSource(QUrl.fromLocalFile(wrong_path))
        elif _sound_backend == "pygame":
            base_dir = os.path.dirname(os.path.dirname(__file__))
            correct_path = os.path.join(base_dir, "resources", "sound", "correct.mp3")
            wrong_path = os.path.join(base_dir, "resources", "sound", "wrong.mp3")
            self.sound_correct = pygame.mixer.Sound(correct_path)
            self.sound_wrong = pygame.mixer.Sound(wrong_path)
        else:
            self.sound_correct = None
            self.sound_wrong = None

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
        if self.new_game_window is None:
            self.new_game_window = NewGameWindow(self)
            self.new_game_window.game_started.connect(self.start_new_game)
        
        self.new_game_window.show()
        self.new_game_window.center_relative_to_parent()

    def start_new_game(self, step, time_limit, max_errors):
        self.engine.start_game(step, time_limit, max_errors)
        self.update_ui()
        self.errorLabel.setText(f"0 / {max_errors}")
        self.scoreLabel.setText("Skor: 0")
        self.ui.timeProgress.show()
        self.reset_timer()

    def update_ui(self):
        curr_num, options = self.engine.current_number, self.engine.options
        self.ui.numberLabel.setText(str(curr_num))
        self.ui.stepLabel.setText(f"{self.engine.current_step}'er")
        
        self.ui.btn_option1.setText(str(options[0]))
        self.ui.btn_option2.setText(str(options[1]))
        self.ui.btn_option3.setText(str(options[2]))

    def handle_answer(self, button):
        if not self.engine.is_active:
            return
            
        selected = int(button.text())
        correct = self.engine.check_answer(selected)
        
        if correct:
            if self.sound_correct is not None:
                self.sound_correct.play()
            self.scoreLabel.setText(f"Skor: {self.engine.score}")
            self.update_ui()
            if self.engine.time_limit > 0:
                self.reset_timer()
        else:
            if self.sound_wrong is not None:
                self.sound_wrong.play()
            self.errorLabel.setText(f"{self.engine.errors} / {self.engine.max_errors}")
            # Check if game over by errors
            if self.engine.errors >= self.engine.max_errors and self.engine.max_errors > 0:
                self.game_over("Hata sınırına ulaştın!")
            else:
                button.setStyleSheet("background-color: #f38ba8; color: white;")
                QTimer.singleShot(500, lambda: self.reset_button_style(button))

    def reset_button_style(self, button):
        button.setStyleSheet("")

    def update_progress_bar_color(self):
        max_val = self.ui.timeProgress.maximum()
        if max_val <= 0:
            return
        percentage = (self.remaining_time / max_val) * 100
        if percentage > 50:
            color = "#40a02b"  # green
        elif percentage > 25:
            color = "#df8e1d"  # yellow/orange
        else:
            color = "#d20f39"  # red
            
        self.ui.timeProgress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: #dce0e8;
                height: 8px;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)

    def reset_timer(self):
        self.remaining_time = self.engine.time_limit * 10
        self.ui.timeProgress.setMaximum(self.remaining_time)
        self.ui.timeProgress.setValue(self.remaining_time)
        self.update_progress_bar_color()
        self.game_timer.start(100) # Update every 100ms

    def update_time_limit(self):
        self.remaining_time -= 1
        self.ui.timeProgress.setValue(self.remaining_time)
        self.update_progress_bar_color()
        if self.remaining_time <= 0:
            self.game_timer.stop()
            self.game_over("Süre doldu!")

    def game_over(self, message):
        self.engine.is_active = False
        self.game_timer.stop()
        
        from .game_over_dialog import GameOverDialog
        dialog = GameOverDialog(message, self.engine.score, self)
        dialog.play_again_requested.connect(self.open_new_game_window)
        dialog.exec()
        
        self.ui.stepLabel.setText("?")
        self.ui.numberLabel.setText("?")
        self.ui.btn_option1.setText("?")
        self.ui.btn_option2.setText("?")
        self.ui.btn_option3.setText("?")
        self.errorLabel.setText("? / ?")
        self.scoreLabel.setText("Skor: ?")
        self.ui.timeProgress.setValue(self.ui.timeProgress.maximum())
        self.ui.timeProgress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #dce0e8;
                height: 8px;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #40a02b;
                border-radius: 4px;
            }
        """)


