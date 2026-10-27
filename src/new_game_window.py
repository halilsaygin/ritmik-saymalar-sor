import re
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject


class NewGameWindow(Gtk.Window):
    __gsignals__ = {
        "game-started": (GObject.SignalFlags.RUN_FIRST, None, (int, int, int)),
    }

    COUNTING_OPTIONS = [
        "2'şer",
        "3'er",
        "4'er",
        "5'er",
        "6'şar",
        "7'şer",
        "8'er",
        "9'ar",
        "10'ar",
    ]

    def __init__(self, parent=None):
        super().__init__(
            title="Yeni Oyun Ayarları",
            transient_for=parent,
            modal=True,
            default_width=460,
            default_height=560,
            resizable=False,
        )
        self.add_css_class("dialog-window")

        header_bar = Gtk.HeaderBar()
        header_bar.set_show_title_buttons(True)
        title_lbl = Gtk.Label(label="Yeni Oyun Ayarları")
        title_lbl.add_css_class("title")
        header_bar.set_title_widget(title_lbl)
        self.set_titlebar(header_bar)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        self.set_child(main_box)

        # Header title
        header_label = Gtk.Label(label="Yeni Oyun")
        header_label.add_css_class("dialog-header")
        header_label.set_halign(Gtk.Align.CENTER)
        main_box.append(header_label)

        # Counting step row
        counting_frame = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        counting_frame.add_css_class("settings-frame")

        counting_label = Gtk.Label(label="Sayma Düzeni:")
        counting_label.add_css_class("field-label")
        counting_label.set_halign(Gtk.Align.START)
        counting_label.set_hexpand(True)

        self.string_list = Gtk.StringList.new(self.COUNTING_OPTIONS)
        self.counting_dropdown = Gtk.DropDown(model=self.string_list)
        self.counting_dropdown.set_selected(0)
        self.counting_dropdown.set_valign(Gtk.Align.CENTER)

        counting_frame.append(counting_label)
        counting_frame.append(self.counting_dropdown)
        main_box.append(counting_frame)

        # Game Mode selection group
        mode_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        mode_box.add_css_class("settings-frame")

        mode_title = Gtk.Label(label="Oyun Modu")
        mode_title.add_css_class("settings-group-title")
        mode_title.set_halign(Gtk.Align.START)
        mode_box.append(mode_title)

        self.radio_time_only = Gtk.CheckButton(label="Sadece Süreli Mod")
        self.radio_time_only.add_css_class("mode-radio")

        self.radio_error_only = Gtk.CheckButton(label="Sadece Yanlış Sayılı Mod")
        self.radio_error_only.add_css_class("mode-radio")
        self.radio_error_only.set_group(self.radio_time_only)

        self.radio_both = Gtk.CheckButton(label="Hem Süreli Hem Yanlış Sayılı Mod")
        self.radio_both.add_css_class("mode-radio")
        self.radio_both.set_group(self.radio_time_only)
        # Default mode is the last one (Both Timed and Error Count)
        self.radio_both.set_active(True)

        self.radio_time_only.connect("toggled", self.on_mode_changed)
        self.radio_error_only.connect("toggled", self.on_mode_changed)
        self.radio_both.connect("toggled", self.on_mode_changed)

        mode_box.append(self.radio_time_only)
        mode_box.append(self.radio_error_only)
        mode_box.append(self.radio_both)
        main_box.append(mode_box)

        # Game settings group
        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        settings_box.add_css_class("settings-frame")

        group_title = Gtk.Label(label="Oyun Ayarları")
        group_title.add_css_class("settings-group-title")
        group_title.set_halign(Gtk.Align.START)
        settings_box.append(group_title)

        # Time limit row
        self.time_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        time_label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        time_label_box.set_hexpand(True)
        time_label_box.set_valign(Gtk.Align.CENTER)

        time_label = Gtk.Label(label="Süre Sınırı (sn):")
        time_label.add_css_class("field-label")
        time_label.set_halign(Gtk.Align.START)

        time_hint = Gtk.Label(label="(her soru için saniye)")
        time_hint.add_css_class("hint-label")
        time_hint.set_halign(Gtk.Align.START)

        time_label_box.append(time_label)
        time_label_box.append(time_hint)

        time_adj = Gtk.Adjustment(value=5, lower=1, upper=60, step_increment=1, page_increment=5)
        self.spin_time = Gtk.SpinButton(adjustment=time_adj, climb_rate=1, digits=0)
        self.spin_time.set_valign(Gtk.Align.CENTER)

        self.time_row.append(time_label_box)
        self.time_row.append(self.spin_time)
        settings_box.append(self.time_row)

        # Error limit row
        self.error_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        error_label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        error_label_box.set_hexpand(True)
        error_label_box.set_valign(Gtk.Align.CENTER)

        error_label = Gtk.Label(label="Hata Sınırı:")
        error_label.add_css_class("field-label")
        error_label.set_halign(Gtk.Align.START)

        error_hint = Gtk.Label(label="(maksimum yanlış hakkı)")
        error_hint.add_css_class("hint-label")
        error_hint.set_halign(Gtk.Align.START)

        error_label_box.append(error_label)
        error_label_box.append(error_hint)

        error_adj = Gtk.Adjustment(value=3, lower=1, upper=20, step_increment=1, page_increment=2)
        self.spin_errors = Gtk.SpinButton(adjustment=error_adj, climb_rate=1, digits=0)
        self.spin_errors.set_valign(Gtk.Align.CENTER)

        self.error_row.append(error_label_box)
        self.error_row.append(self.spin_errors)
        settings_box.append(self.error_row)

        main_box.append(settings_box)

        # Spacer
        spacer = Gtk.Box()
        spacer.set_vexpand(True)
        main_box.append(spacer)

        # Start button
        self.btn_start = Gtk.Button(label="Başlat")
        self.btn_start.add_css_class("start-btn")
        self.btn_start.connect("clicked", self.on_start_clicked)
        main_box.append(self.btn_start)

        self.on_mode_changed(None)
        self.connect("map", self.on_window_map)

    def on_window_map(self, _widget):
        from gi.repository import GLib

        GLib.idle_add(self.center_window)

    def center_window(self):
        from gi.repository import GLib
        import subprocess

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
            width = self.get_width() or 460
            height = self.get_height() or 560
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

    def on_mode_changed(self, _button):
        use_time = self.radio_time_only.get_active() or self.radio_both.get_active()
        use_errors = self.radio_error_only.get_active() or self.radio_both.get_active()

        self.time_row.set_sensitive(use_time)
        self.spin_time.set_sensitive(use_time)

        self.error_row.set_sensitive(use_errors)
        self.spin_errors.set_sensitive(use_errors)

    def on_start_clicked(self, _button):
        selected_idx = self.counting_dropdown.get_selected()
        if selected_idx != Gtk.INVALID_LIST_POSITION and selected_idx < len(self.COUNTING_OPTIONS):
            step_text = self.COUNTING_OPTIONS[selected_idx]
        else:
            step_text = "2'şer"

        match = re.search(r"\d+", step_text)
        step = int(match.group()) if match else 2

        if self.radio_time_only.get_active():
            time_limit = int(self.spin_time.get_value())
            max_errors = 0
        elif self.radio_error_only.get_active():
            time_limit = 0
            max_errors = int(self.spin_errors.get_value())
        else:
            time_limit = int(self.spin_time.get_value())
            max_errors = int(self.spin_errors.get_value())

        self.emit("game-started", step, time_limit, max_errors)
        self.close()
