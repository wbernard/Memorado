# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk

from .const import APP_ID

@Gtk.Template(resource_path='/im/bernard/Memorado/ui/welcome.ui')
class Welcome(Adw.NavigationPage):
    __gtype_name__ = 'Welcome'

    status_page = Gtk.Template.Child()
    start_button = Gtk.Template.Child()
    import_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.status_page.set_icon_name(APP_ID)
