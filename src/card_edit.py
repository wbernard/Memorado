# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

@Gtk.Template(resource_path='/im/bernard/Memorado/ui/card_edit.ui')
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

        if(text[-1] == "\t"):
            print("input is tab: ", text[-1] == "\t")
        else:
            self.card.front = text    # Frontseite der Karte
            self.front_placeholder.set_visible(len(text) < 1)
            self.window.deck_view.cards_list.bind_model(self.window.current_deck.cards_model, self.window.cards_list_create_row)

        # Funktioniert nicht, weil der tab character trotzdem eingefügt wird
        # Muss früher im Prozess abgefangen werden


    def __on_back_side_changed(self, buffer):
        (start, end) = buffer.get_bounds()
        text = buffer.get_text(start, end, False)
        self.card.back = text   # Rückseite der Karte

        self.back_placeholder.set_visible(len(text) < 1)

        self.window.deck_view.cards_list.bind_model(self.window.current_deck.cards_model, self.window.cards_list_create_row)

    # def do_insert_text(self, text, len, position_iter):
    #     if text == "\t":
    #         print("Tab, don't insert, switch focus")
    #     else:
    #         print("insert charaters normally")

