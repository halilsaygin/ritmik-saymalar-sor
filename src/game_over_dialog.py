import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject


class GameOverDialog(Gtk.Window):
    __gsignals__ = {
        "play-again-requested": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, message, score, parent=None):
        super().__init__(
            title="Oyun Bitti",
            transient_for=parent,
            modal=True,
            default_width=360,
            default_height=340,
            resizable=False,
        )
        self.add_css_class("dialog-window")

        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)
        title_lbl = Gtk.Label(label="Oyun Bitti")
        title_lbl.add_css_class("title")
        header_bar.set_title_widget(title_lbl)
        self.set_titlebar(header_bar)

        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        container.add_css_class("gameover-container")
        container.set_margin_top(16)
        container.set_margin_bottom(16)
        container.set_margin_start(16)
        container.set_margin_end(16)
        container.set_valign(Gtk.Align.CENTER)
        self.set_child(container)

        # Title
        title_label = Gtk.Label(label="OYUN BİTTİ")
        title_label.add_css_class("gameover-title")
        title_label.set_halign(Gtk.Align.CENTER)
        container.append(title_label)

        # Message
        msg_label = Gtk.Label(label=message)
        msg_label.add_css_class("gameover-msg")
        msg_label.set_halign(Gtk.Align.CENTER)
        msg_label.set_wrap(True)
        container.append(msg_label)

        # Score Box
        score_frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        score_frame.add_css_class("score-card")
        score_frame.set_halign(Gtk.Align.FILL)

        score_title = Gtk.Label(label="TOPLAM SKOR")
        score_title.add_css_class("score-card-title")
        score_title.set_halign(Gtk.Align.CENTER)

        score_val = Gtk.Label(label=str(score))
        score_val.add_css_class("score-card-value")
        score_val.set_halign(Gtk.Align.CENTER)

        score_frame.append(score_title)
        score_frame.append(score_val)
        container.append(score_frame)

        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_homogeneous(True)

        self.btn_close = Gtk.Button(label="Kapat")
        self.btn_close.add_css_class("close-btn")
        self.btn_close.connect("clicked", lambda _btn: self.close())

        self.btn_again = Gtk.Button(label="Tekrar Oyna")
        self.btn_again.add_css_class("again-btn")
        self.btn_again.connect("clicked", self.on_again_clicked)

        btn_box.append(self.btn_close)
        btn_box.append(self.btn_again)
        container.append(btn_box)

    def on_again_clicked(self, _button):
        self.close()
        self.emit("play-again-requested")
