# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk

@Gtk.Template(resource_path='/im/bernard/Memorado/ui/deck_row.ui')
class DeckRow(Adw.ActionRow):
    __gtype_name__ = 'DeckRow'

    revealer = Gtk.Template.Child()
    checkbox = Gtk.Template.Child()
    deck_icon = Gtk.Template.Child()
    deck_name = Gtk.Template.Child()
    cards_count = Gtk.Template.Child()
    edit_button = Gtk.Template.Child()
    next_icon = Gtk.Template.Child()

    def __init__(self, deck, **kwargs):
        super().__init__(**kwargs)

        self.deck = deck

        self.deck_name.set_label(deck.name)
        self.deck_icon.set_label(deck.icon)

        if deck.cards_model.props.n_items > 0:
            self.cards_count.set_visible(True)
            self.cards_count.set_label(str(deck.cards_model.props.n_items))

