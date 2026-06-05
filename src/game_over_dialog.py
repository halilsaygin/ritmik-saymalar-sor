import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

class GameOverDialog(QDialog):
    play_again_requested = Signal()

    def __init__(self, message, score, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.resize(340, 400)
        
        # Frameless window configuration to remove GNOME app title bar and achieve custom round corners
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # UI Setup
        self.setup_ui(message, score)
        self.apply_styles()

    def setup_ui(self, message, score):
        # Main dialog layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Margins for shadow area

        # Main styled container frame
        self.container = QFrame(self)
        self.container.setObjectName("containerFrame")
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(25, 30, 25, 25)
        container_layout.setSpacing(15)
        container_layout.setAlignment(Qt.AlignCenter)

        # Drop Shadow Effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        # Icon
        # Icon label removed as per requirement to eliminate emoji from the game over dialog.
        # Previously an emoji was displayed based on the message content.
        # The label is now omitted to keep the dialog text‑only.

        # Title
        self.title_label = QLabel("OYUN BİTTİ")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.title_label)

        # Message
        self.msg_label = QLabel(message)
        self.msg_label.setObjectName("msgLabel")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setWordWrap(True)
        container_layout.addWidget(self.msg_label)

        # Score Box (Frame)
        self.score_frame = QFrame()
        self.score_frame.setObjectName("scoreFrame")
        score_layout = QVBoxLayout(self.score_frame)
        score_layout.setContentsMargins(15, 12, 15, 12)
        score_layout.setSpacing(2)
        score_layout.setAlignment(Qt.AlignCenter)

        score_title = QLabel("TOPLAM SKOR")
        score_title.setObjectName("scoreTitle")
        score_title.setAlignment(Qt.AlignCenter)
        
        self.score_val = QLabel(str(score))
        self.score_val.setObjectName("scoreVal")
        self.score_val.setAlignment(Qt.AlignCenter)

        score_layout.addWidget(score_title)
        score_layout.addWidget(self.score_val)
        container_layout.addWidget(self.score_frame)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_close = QPushButton("Kapat")
        self.btn_close.setObjectName("btnClose")
        self.btn_close.clicked.connect(self.reject)
        
        self.btn_again = QPushButton("Tekrar Oyna")
        self.btn_again.setObjectName("btnAgain")
        self.btn_again.clicked.connect(self.on_again_clicked)

        btn_layout.addWidget(self.btn_close)
        btn_layout.addWidget(self.btn_again)
        container_layout.addLayout(btn_layout)
        
        main_layout.addWidget(self.container)

    def on_again_clicked(self):
        self.accept()
        self.play_again_requested.emit()

    def apply_styles(self):
        self.setStyleSheet("""
            #containerFrame {
                background-color: #eff1f5;
                border: 2px solid #ccd0da;
                border-radius: 16px;
            }
            #titleLabel {
                color: #d20f39;
                font-size: 22px;
                font-weight: bold;
                font-family: 'Segoe UI', Roboto, sans-serif;
            }
            #msgLabel {
                color: #5c5f77;
                font-size: 14px;
                font-family: 'Segoe UI', Roboto, sans-serif;
            }
            #scoreFrame {
                background-color: #ffffff;
                border: 2px solid #e6e9ef;
                border-radius: 12px;
            }
            #scoreTitle {
                color: #7c7f93;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            #scoreVal {
                color: #1e66f5;
                font-size: 32px;
                font-weight: bold;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 8px;
                min-width: 105px;
            }
            #btnClose {
                background-color: #ffffff;
                color: #4c4f69;
                border: 1px solid #dce0e8;
            }
            #btnClose:hover {
                background-color: #e6e9ef;
            }
            #btnAgain {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1e66f5, stop:1 #7287fd);
                color: #ffffff;
                border: none;
            }
            #btnAgain:hover {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #04a5e5, stop:1 #1e66f5);
            }
            #btnAgain:pressed {
                background-color: #1750c7;
            }
        """)
