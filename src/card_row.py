# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk

@Gtk.Template(resource_path='/im/bernard/Memorado/ui/card_row.ui')
class CardRow(Adw.ActionRow):
    __gtype_name__ = 'CardRow'

    revealer = Gtk.Template.Child()
    checkbox = Gtk.Template.Child()
    title_label = Gtk.Template.Child()
    subtitle_label = Gtk.Template.Child()
    edit_button = Gtk.Template.Child()

    def __init__(self, card, **kwargs):
        super().__init__(**kwargs)

        self.card = card

        self.title_label.set_label(card.front)
        self.subtitle_label.set_label(card.back)

