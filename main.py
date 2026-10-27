#!/usr/bin/env python3
import sys
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib
from src.mainwindow import MainWindow


class RitmikSaymalarApp(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="tr.org.pardus.etap.ritmik-saymalar-sor",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        GLib.set_application_name("Ritmik Saymalar Sor")
        GLib.set_prgname("ritmik-saymalar-sor")

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MainWindow(self)
        win.present()


def main():
    app = RitmikSaymalarApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
