# SPDX-License-Identifier: GPL-3.0-or-later


from gi.repository import Adw, Gtk, Gio

from .window import Window


class Application(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='io.github.fkinoshita.FlashCards',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('close', lambda *_: self.props.active_window.close(), ['<primary>w'])
        self.create_action('import', lambda *_: print("import!"), ['<primary>i'])
        self.create_action('export', self.on_export_clicked, ['<primary>e'])
        self.create_action('about', self.on_about_action)


    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = Window(application=self)
        win.present()


    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        builder = Gtk.Builder.new_from_resource(
            "/io/github/fkinoshita/FlashCards/about_dialog.ui"
        )
        about_dialog = builder.get_object("about_dialog")
        about_dialog.set_transient_for(self.props.active_window)
        about_dialog.present()


    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def on_export_clicked(self, widget, blb):
        self.props.active_window.on_export_clicked()



