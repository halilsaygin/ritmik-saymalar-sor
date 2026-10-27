import os
import subprocess
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gio, Gdk

# Try GStreamer for sound playback, with Gtk.MediaFile and subprocess fallbacks
_gst_available = False
try:
    gi.require_version("Gst", "1.0")
    from gi.repository import Gst

    Gst.init(None)
    _gst_available = True
except Exception:
    Gst = None

from .game_engine import GameEngine
from .new_game_window import NewGameWindow
from .game_over_dialog import GameOverDialog


def get_Step_Suffix(step: int) -> str:
    suffixes = {
        2: "2'şer",
        3: "3'er",
        4: "4'er",
        5: "5'er",
        6: "6'şar",
        7: "7'şer",
        8: "8'er",
        9: "9'ar",
        10: "10'ar",
    }
    return suffixes.get(step, f"{step}'er")


class SoundPlayer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.player = None
        self.media_file = None

        if not os.path.exists(self.file_path):
            return

        if _gst_available and Gst is not None:
            try:
                self.player = Gst.ElementFactory.make("playbin", None)
                if self.player is not None:
                    uri = Gio.File.new_for_path(self.file_path).get_uri()
                    self.player.set_property("uri", uri)
            except Exception:
                self.player = None

    def play(self):
        if not os.path.exists(self.file_path):
            return

        if self.player is not None:
            try:
                self.player.set_state(Gst.State.NULL)
                self.player.set_state(Gst.State.PLAYING)
                return
            except Exception:
                pass

        try:
            self.media_file = Gtk.MediaFile.new_for_filename(self.file_path)
            self.media_file.play()
            return
        except Exception:
            pass

        for cmd in (["paplay", self.file_path], ["mpv", "--no-video", self.file_path], ["ffplay", "-nodisp", "-autoexit", self.file_path]):
            try:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                break
            except Exception:
                continue


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(
            application=application,
            title="Ritmik Saymalar Sor",
            default_width=640,
            default_height=520,
        )
        self.add_css_class("main-window")

        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.load_stylesheet()
        self.setup_icon()

        # Engine & Timer state
        self.engine = GameEngine()
        self.timer_source_id = None
        self.remaining_time = 0
        self.max_time_ticks = 50
        self.new_game_window = None

        # HeaderBar with "Yeni Oyun" button and Menu
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)
        title_lbl = Gtk.Label(label="Ritmik Saymalar Sor")
        title_lbl.add_css_class("title")
        header_bar.set_title_widget(title_lbl)

        self.btn_new_game = Gtk.Button(label="Yeni Oyun")
        self.btn_new_game.add_css_class("new-game-header-btn")
        self.btn_new_game.connect("clicked", lambda _btn: self.open_new_game_window())
        header_bar.pack_start(self.btn_new_game)

        # Menu model for standard desktop compatibility
        menu = Gio.Menu()
        menu.append("Yeni Oyun", "win.new_game")
        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu_btn.set_menu_model(menu)
        header_bar.pack_end(menu_btn)

        new_game_action = Gio.SimpleAction.new("new_game", None)
        new_game_action.connect("activate", lambda _action, _param: self.open_new_game_window())
        self.add_action(new_game_action)

        self.set_titlebar(header_bar)

        # Main vertical layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(28)
        main_box.set_margin_start(30)
        main_box.set_margin_end(30)
        self.set_child(main_box)

        # Top status bar: [Error Label] --- [Score Label] --- [Step Label]
        top_box = Gtk.CenterBox()
        top_box.set_hexpand(True)

        self.error_label = Gtk.Label(label="? / ?")
        self.error_label.add_css_class("error-badge")
        top_box.set_start_widget(self.error_label)

        self.score_label = Gtk.Label(label="Skor: ?")
        self.score_label.add_css_class("score-badge")
        top_box.set_center_widget(self.score_label)

        self.step_label = Gtk.Label(label="?")
        self.step_label.add_css_class("step-badge")
        top_box.set_end_widget(self.step_label)

        main_box.append(top_box)

        # Center question number card
        self.number_label = Gtk.Label(label="?")
        self.number_label.add_css_class("number-card")
        self.number_label.set_vexpand(True)
        self.number_label.set_hexpand(True)
        self.number_label.set_halign(Gtk.Align.FILL)
        self.number_label.set_valign(Gtk.Align.FILL)
        main_box.append(self.number_label)

        # Option buttons row
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        buttons_box.set_homogeneous(True)
        buttons_box.set_hexpand(True)

        self.btn_option1 = Gtk.Button(label="?")
        self.btn_option2 = Gtk.Button(label="?")
        self.btn_option3 = Gtk.Button(label="?")

        for btn in (self.btn_option1, self.btn_option2, self.btn_option3):
            btn.add_css_class("option-btn")
            btn.connect("clicked", self.handle_answer)
            buttons_box.append(btn)

        main_box.append(buttons_box)

        # Progress bar for time limit
        self.time_progress = Gtk.ProgressBar()
        self.time_progress.set_fraction(1.0)
        self.time_progress.add_css_class("progress-green")
        self.time_progress.set_margin_top(10)
        main_box.append(self.time_progress)

        # Load sound effects
        correct_path = os.path.join(self.base_dir, "resources", "sound", "correct.mp3")
        wrong_path = os.path.join(self.base_dir, "resources", "sound", "wrong.mp3")
        self.sound_correct = SoundPlayer(correct_path)
        self.sound_wrong = SoundPlayer(wrong_path)

        # Center window when realized/mapped (supported on X11 / Pardus ETAP XFCE)
        self.connect("map", self.on_window_map)

    def on_window_map(self, _widget):
        GLib.idle_add(self.center_on_screen)

    def center_on_screen(self):
        try:
            display = self.get_display()
            surface = self.get_surface()
            if display is None or surface is None:
                return GLib.SOURCE_REMOVE

            monitor = display.get_monitor_at_surface(surface)
            if monitor is None:
                monitors = display.get_monitors()
                if monitors.get_n_items() > 0:
                    monitor = monitors.get_item(0)
            if monitor is None:
                return GLib.SOURCE_REMOVE

            geo = monitor.get_geometry()
            width = self.get_width() or 640
            height = self.get_height() or 520
            x = geo.x + max(0, (geo.width - width) // 2)
            y = geo.y + max(0, (geo.height - height) // 2)

            if hasattr(surface, "get_xid"):
                xid = surface.get_xid()
                for cmd in (
                    ["xdotool", "windowmove", str(xid), str(x), str(y)],
                    ["wmctrl", "-i", "-r", hex(xid), "-e", f"0,{x},{y},-1,-1"],
                ):
                    try:
                        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        if res.returncode == 0:
                            break
                    except Exception:
                        continue
        except Exception:
            pass
        return GLib.SOURCE_REMOVE

    def load_stylesheet(self):
        style_path = os.path.join(self.base_dir, "resources", "styles", "style.css")
        if os.path.exists(style_path):
            css_provider = Gtk.CssProvider()
            css_provider.load_from_path(style_path)
            display = Gdk.Display.get_default()
            if display is not None:
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
                )

    def setup_icon(self):
        icon_dir = os.path.join(self.base_dir, "resources", "icons")
        display = Gdk.Display.get_default()
        if display is not None and os.path.isdir(icon_dir):
            icon_theme = Gtk.IconTheme.get_for_display(display)
            icon_theme.add_search_path(icon_dir)
        self.set_icon_name("app_icon")

    def open_new_game_window(self):
        if self.new_game_window is not None:
            self.new_game_window.close()
        self.new_game_window = NewGameWindow(parent=self)
        self.new_game_window.connect("game-started", self.on_game_started)
        self.new_game_window.present()

    def on_game_started(self, _dialog, step, time_limit, max_errors):
        self.start_new_game(step, time_limit, max_errors)

    def start_new_game(self, step, time_limit, max_errors):
        self.stop_timer()
        self.engine.start_game(step, time_limit, max_errors)
        self.update_ui()
        if max_errors > 0:
            self.error_label.set_label(f"0 / {max_errors}")
            self.error_label.set_visible(True)
        else:
            self.error_label.set_label("Hata: 0")
            self.error_label.set_visible(False)

        self.score_label.set_label("Skor: 0")

        if time_limit > 0:
            self.time_progress.set_visible(True)
            self.reset_timer()
        else:
            self.time_progress.set_visible(False)

    def update_ui(self):
        curr_num, options = self.engine.current_number, self.engine.options
        self.number_label.set_label(str(curr_num))
        self.step_label.set_label(get_Step_Suffix(self.engine.current_step))

        self.btn_option1.set_label(str(options[0]))
        self.btn_option2.set_label(str(options[1]))
        self.btn_option3.set_label(str(options[2]))

        for btn in (self.btn_option1, self.btn_option2, self.btn_option3):
            btn.remove_css_class("option-btn-wrong")

    def handle_answer(self, button):
        if not self.engine.is_active:
            return

        try:
            selected = int(button.get_label())
        except (ValueError, TypeError):
            return

        correct = self.engine.check_answer(selected)

        if correct:
            self.sound_correct.play()
            self.score_label.set_label(f"Skor: {self.engine.score}")
            self.update_ui()
            if self.engine.time_limit > 0:
                self.reset_timer()
        else:
            self.sound_wrong.play()
            if self.engine.max_errors > 0:
                self.error_label.set_label(f"{self.engine.errors} / {self.engine.max_errors}")
            else:
                self.error_label.set_label(f"Hata: {self.engine.errors}")

            if self.engine.errors >= self.engine.max_errors and self.engine.max_errors > 0:
                self.game_over("Hata sınırına ulaştın!")
            else:
                button.add_css_class("option-btn-wrong")
                GLib.timeout_add(500, self.reset_button_style, button)

    def reset_button_style(self, button):
        button.remove_css_class("option-btn-wrong")
        return GLib.SOURCE_REMOVE

    def set_progress_color_class(self, class_name: str):
        for cls in ("progress-green", "progress-yellow", "progress-red"):
            self.time_progress.remove_css_class(cls)
        self.time_progress.add_css_class(class_name)

    def update_progress_bar(self):
        if self.max_time_ticks <= 0:
            return
        fraction = max(0.0, min(1.0, self.remaining_time / self.max_time_ticks))
        self.time_progress.set_fraction(fraction)

        percentage = fraction * 100
        if percentage > 50:
            self.set_progress_color_class("progress-green")
        elif percentage > 25:
            self.set_progress_color_class("progress-yellow")
        else:
            self.set_progress_color_class("progress-red")

    def stop_timer(self):
        if self.timer_source_id is not None:
            GLib.source_remove(self.timer_source_id)
            self.timer_source_id = None

    def reset_timer(self):
        self.stop_timer()
        self.max_time_ticks = self.engine.time_limit * 10
        self.remaining_time = self.max_time_ticks
        self.update_progress_bar()
        self.timer_source_id = GLib.timeout_add(100, self.update_time_limit)

    def update_time_limit(self):
        if not self.engine.is_active:
            self.timer_source_id = None
            return GLib.SOURCE_REMOVE

        self.remaining_time -= 1
        self.update_progress_bar()

        if self.remaining_time <= 0:
            self.timer_source_id = None
            self.game_over("Süre doldu!")
            return GLib.SOURCE_REMOVE

        return GLib.SOURCE_CONTINUE

    def reset_board_state(self):
        self.step_label.set_label("?")
        self.number_label.set_label("?")
        self.btn_option1.set_label("?")
        self.btn_option2.set_label("?")
        self.btn_option3.set_label("?")
        self.error_label.set_label("? / ?")
        self.error_label.set_visible(True)
        self.score_label.set_label("Skor: ?")
        self.time_progress.set_visible(True)
        self.time_progress.set_fraction(1.0)
        self.set_progress_color_class("progress-green")

    def game_over(self, message: str):
        self.engine.is_active = False
        self.stop_timer()

        final_score = self.engine.score
        self.reset_board_state()

        dialog = GameOverDialog(message, final_score, parent=self)
        dialog.connect("play-again-requested", lambda _d: self.open_new_game_window())
        dialog.present()
