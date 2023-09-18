# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

@Gtk.Template(resource_path='/io/github/fkinoshita/FlashCards/ui/card_edit.ui')
class CardEdit(Gtk.Box):
    __gtype_name__ = 'CardEdit'

    front_side_view = Gtk.Template.Child()
    back_side_view = Gtk.Template.Child()
    front_placeholder = Gtk.Template.Child()
    back_placeholder = Gtk.Template.Child()
    save_card_button = Gtk.Template.Child()

    def __init__(self, window, card, **kwargs):
        super().__init__(**kwargs)

        self.window = window
        self.card = card

        print ('### card in card_edit ###', card)

        if len(card.front) < 1:
            self.front_placeholder.set_visible(True)

        if len(card.back) < 1:
            self.back_placeholder.set_visible(True)

        self.front_side_view.get_buffer().set_text(self.card.front)
        self.back_side_view.get_buffer().set_text(self.card.back)

        self.front_side_view.get_buffer().connect('changed', self.__on_front_side_changed)
        self.back_side_view.get_buffer().connect('changed', self.__on_back_side_changed)


    def __on_front_side_changed(self, buffer):
        (start, end) = buffer.get_bounds()
        text = buffer.get_text(start, end, False)
        self.card.front = text    # Frontseite der Karte

        print ('## front text in card edit 42 ##', self.card.front)

        self.front_placeholder.set_visible(len(text) < 1)

        # self.window.current_deck.save()

        self.window.deck_view.cards_list.bind_model(self.window.current_deck.cards_model, self.window.cards_list_create_row)


    def __on_back_side_changed(self, buffer):
        (start, end) = buffer.get_bounds()
        text = buffer.get_text(start, end, False)
        self.card.back = text   # Rückseite der Karte

        print ('## back text ##', self.card.back)

        self.back_placeholder.set_visible(len(text) < 1)

        # self.window.current_deck.save()
