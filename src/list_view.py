# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk

@Gtk.Template(resource_path='/io/github/fkinoshita/FlashCards/ui/list_view.ui')
class ListView(Adw.NavigationPage):
    __gtype_name__ = 'ListView'

    delete_button = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()
    selection_mode_button = Gtk.Template.Child()
    menu_button = Gtk.Template.Child()
    decks = Gtk.Template.Child()
    new_deck_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.decks.connect('selected-rows-changed', self.__decks_selected_rows_changed)
        self.cancel_button.connect('clicked', lambda *_: self.set_selection_mode(False))


    def __decks_selected_rows_changed(self, list):
        self.delete_button.set_sensitive(not len(list.get_selected_rows()) <= 0)


    def set_selection_mode(self, active):
        self.decks.set_selection_mode(Gtk.SelectionMode.MULTIPLE if active else Gtk.SelectionMode.NONE)

        self.cancel_button.set_visible(active)
        self.delete_button.set_visible(active)
        self.new_deck_button.set_visible(not active)
        self.selection_mode_button.set_visible(not active)
        self.menu_button.set_visible(not active)

        for row in self.decks.observe_children():
            row.edit_button.set_visible(not active)
            row.next_icon.set_visible(not active)
            row.revealer.set_reveal_child(active)

            if row.revealer.get_reveal_child() and active:
                row.revealer.set_margin_end(12)
            elif not row.revealer.get_reveal_child() and not active:
                row.revealer.set_margin_end(0)

            if not active:
                row.checkbox.set_active(False)


        if active:
            self.decks.get_first_child().checkbox.set_active(True)
