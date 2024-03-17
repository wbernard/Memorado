# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk

@Gtk.Template(resource_path='/im/bernard/Memorado/ui/card_view.ui')
class CardView(Adw.NavigationPage):
    __gtype_name__ = 'CardView'

    card_box = Gtk.Template.Child()
    front_label = Gtk.Template.Child()
    back_label = Gtk.Template.Child()
    show_answer_button = Gtk.Template.Child()
    edit_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def hide_answer(self):
        for child in self.card_box.observe_children():
            child.set_visible(False)

        self.front_label.set_visible(True)
        self.show_answer_button.set_label(_('Show Answer'))


    def show_answer(self, isDone):
        for child in self.card_box.observe_children():
            child.set_visible(True)
        if isDone:
            self.show_answer_button.set_label(_('Done'))
        else:
            self.show_answer_button.set_label(_('Next'))

