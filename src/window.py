# SPDX-License-Identifier: GPL-3.0-or-later

import os
import json
import uuid
import sqlite3


from gi.repository import Adw, Gtk, Gio, GObject
from pathlib import Path

from .welcome import Welcome
from .list_view import ListView
from .deck_view import DeckView
from .card_view import CardView
from .card_edit_view import CardEditView
from .deck_row import DeckRow
from .card_row import CardRow

import const

from . import shared

class Card(GObject.Object):
    __gtype_name__ = 'Card'

    front = GObject.Property(type=str)
    back = GObject.Property(type=str)

    def __init__(self, **kargs):
        super().__init__(**kargs)


class Deck(GObject.Object):
    __gtype_name__ = 'Deck'

    name = GObject.Property(type=str)
    icon = GObject.Property(type=str)
    cards_model = GObject.Property(type=Gio.ListStore)
    current_index = GObject.Property(type=int)

    def __init__(self, name = _('New Deck'), **kargs):
        super().__init__(**kargs)

        self.id = str(uuid.uuid4().hex)
        self.name = name
        self.icon = ''
        self.cards_model = Gio.ListStore.new(Card)
        self.current_index = 0


    def save(self):
        '''
        shared.decks_dir.mkdir(parents=True, exist_ok=True)

        cards = []

        for c in self.cards_model:
            card = {
                'front': c.front,
                'back': c.back,
            }
            cards.append(card)

        deck = {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'cards': cards
        }

        json.dump(
            deck,
            (shared.decks_dir / f"{self.id}.json").open("w"),
            indent=4,
            sort_keys=True,
        )
        '''
        ########## ab hier ist die Änderung ########
        print('## es geht los mit save 80 ##')

        data_dir = (
        Path(os.getenv("XDG_DATA_HOME"))
        if "XDG_DATA_HOME" in os.environ
        else Path.home() / ".local" / "share"
        )

        self.decks_dir = data_dir / "flashcards" / "decks"

        print('## self.id in windows ##', self.id)

        self.conn = sqlite3.connect(self.decks_dir / 'karteibox.db')
        self.c = self.conn.cursor() # eine cursor instanz erstellen

        ## Nachschauen ob deck.id in decks existiert
        self.c.execute("""SELECT COUNT(*) FROM decks WHERE deck_id = :deck_id""",{'deck_id': self.id})
        liste = self.c.fetchall()
        deck_exist = len(liste) > 1    ## überprüfen!

        ## wenn ja Namen  und icon überschreiben
        ## wenn nein, neuen Eintrag in decks erstellen mit Namen und icon
        if deck_exist:
            self.c.execute("""UPDATE decks SET name = :name, icon = :icon
                    WHERE deck_id = :deck_id""",
                    {'deck_id': self.id, 'name': self.name, 'icon': self.icon })
        else:
            self.c.execute("""INSERT INTO decks VALUES (
                :deck_id, :name, :icon )""",
                {'deck_id': self.id, 'name': self.name, 'icon': self.icon })

        ## in cards alle Einträge mit deck.id löschen
        self.c.execute("""DELETE FROM cards
                    WHERE deck_id = :deck_id""",
                    {'deck_id': self.id})

        ## für jede karte in self.cards_model neuen eintrag in cards erstellen
        for crd in self.cards_model:
            self.c.execute("""INSERT INTO cards VALUES (
                :deck_id, :front, :back )""",
                {'deck_id': self.id, 'front': crd.front, 'back': crd.back })

        self.conn.commit()
        self.conn.close()   # Verbindung schließen

        # name = self.name
        # cards = []
        # print ('##  name in window 84 ##', name)

        # if name == 'New Deck':
        #     pass
        # else:
        #     for cd in self.cards_model:
        #         crd = {
        #             'front': cd.front,
        #             'back': cd.back,
        #         }
        #         print ('## card in window 93 ##', crd)
        #         cards.append(crd)
        #         print ('## cards in w 93 #', cards)

        #     deck = {
        #         'id': self.id,
        #         'name': self.name,
        #         'icon': self.icon,
        #         'cards': cards
        #     }


        #     data_dir = (
        #     Path(os.getenv("XDG_DATA_HOME"))
        #     if "XDG_DATA_HOME" in os.environ
        #     else Path.home() / ".local" / "share"
        #     )

        #     self.decks_dir = data_dir / "flashcards" / "decks"

        #     print('## self.id in windows ##', self.id)

        #     self.conn = sqlite3.connect(self.decks_dir / 'karteibox.db')
        #     self.c = self.conn.cursor() # eine cursor instanz erstellen

        #     self.c.execute("""SELECT COUNT(*) FROM karteibox WHERE deck_id = :deck_id""",{'deck_id': self.id})
        #     liste = self.c.fetchall()
        #     print('### liste in save 124 ###', liste, len(liste))
        #     if liste[0] == (0,) and len(liste)  > 1:
        #         print('## cd.front windows 123 ##', cd.front)
        #         self.c.execute("""INSERT INTO karteibox VALUES (
        #         :deck_id, :deck, :front, :back)""",
        #         {'deck_id': self.id, 'deck': name, 'front': cd.front,
        #         'back': cd.front})
        #     else:
        #         if len(liste) > 1:
        #             self.c.execute("""UPDATE karteibox SET deck = :deck, front = :front, back = :back
        #             WHERE deck_id = :deck_id""",
        #             {'deck_id': self.id, 'deck': name, 'front': cd.front ,
        #             'back': cd.back})
        #         else:
        #             pass

        #     for cd in self.cards_model:
        #         print ('### cd in window 138 #', cd)
        #         self.c.execute("""INSERT INTO karteibox VALUES (
        #             :deck_id, :deck, :front, :back)""",
        #             {'deck_id': self.id, 'deck': name, 'front': cd.front ,
        #             'back': cd.back})

        # self.conn.commit()
        # self.conn.close()   # Verbindung schließen


@Gtk.Template(resource_path='/io/github/fkinoshita/FlashCards/ui/window.ui')
class Window(Adw.ApplicationWindow):
    __gtype_name__ = 'Window'

    toast_overlay = Gtk.Template.Child()
    navigation_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if const.PROFILE == 'Devel':
            self.add_css_class('devel')

        self.decks_model = Gio.ListStore.new(Deck)  # da sind die Karteien samt Karten drin
        self.decks_name_model = Gio.ListStore.new(Deck)  # nur die Namen der Karteien
        self.current_deck = None

        self._load_decks()
        self.tabel_erstel()

        self.welcome_page = Welcome()
        self.list_view = ListView()
        self.list_view.decks.bind_model(self.decks_name_model, self.__decks_create_row)
        self.deck_view = DeckView()
        self.card_view = CardView()

        self._setup_signals()

        if self.decks_model.props.n_items < 1:   # wenn es keine Karteien gibt
            self.navigation_view.add(self.welcome_page)   # Willkommensseite wird angezeigt

        self.navigation_view.add(self.list_view)     # Liste der Karteien
        self.navigation_view.add(self.deck_view)     # Ansicht der Kartei mit Liste der Karten
        self.navigation_view.add(self.card_view)     # Ansicht einer Karte

    def tabel_erstel(self):
        # Pfad zur Datenbank
        data_dir = (
        Path(os.getenv("XDG_DATA_HOME"))
        if "XDG_DATA_HOME" in os.environ
        else Path.home() / ".local" / "share")

        self.decks_dir = data_dir / "flashcards" / "decks"

        # Tabellen erstellen
        self.db_nutzen("""CREATE TABLE if not exists cards (
                              deck_id TEXT, front TEXT, back TEXT)""")
        self.db_nutzen("""CREATE TABLE if not exists decks (
                  name TEXT,
                  icon TEXT)""")

        self.conn.commit()

    def db_nutzen(self, befehl):

        self.conn = sqlite3.connect(self.decks_dir / 'karteibox.db')
        self.c = self.conn.cursor() # eine cursor instanz erstellen
        self.c.execute(befehl) # befehl wird ausgeführt

    def __decks_create_row(self, deck):
        if not self.list_view.decks.has_css_class('boxed-list'):
            self.list_view.decks.add_css_class('boxed-list')

        row = DeckRow(deck)
        row.edit_button.connect('clicked', self.__on_edit_deck_button_clicked, deck)
        row.connect('activated', self.__on_deck_activated, deck)
        row.checkbox.connect('toggled', self.__on_deck_checkbox_toggled, row)

        if not len(row.deck_icon.get_label()) < 1:
            row.deck_icon.set_margin_end(12)

        return row


    def cards_list_create_row(self, card):

        print('### card in window 203 #', card)
        if not self.deck_view.cards_list.has_css_class('boxed-list'):
            self.deck_view.cards_list.add_css_class('boxed-list')

        self.deck_view.selection_mode_button.set_visible(True)

        row = CardRow(card)
        row.connect('activated', self.__on_edit_card_button_clicked, card)
        row.edit_button.connect('clicked', self.__on_edit_card_button_clicked, card)
        row.checkbox.connect('toggled', self.__on_card_checkbox_toggled, row)

        return row


    def __on_start_button_clicked(self, button):
        deck = Deck()

        self.current_deck = deck
        self._go_to_deck(True)
        self.decks_model.append(deck)

        return


    def __on_new_deck_button_clicked(self, button):
        deck = Deck()
        self.current_deck = deck
        self._go_to_deck(True)
        if self.current_deck.name == 'New Deck':
            pass
        else:
            self.decks_model.append(deck)


    def __on_deck_activated(self, row, deck):
        self.current_deck = deck

        if not self.list_view.decks.get_selection_mode() == Gtk.SelectionMode.NONE:
            row.checkbox.set_active(not row.checkbox.get_active())
            return

        if self.current_deck.cards_model.props.n_items == 0:
            self._go_to_deck(False)
            return

        self.card_view.front_label.set_label(self.current_deck.cards_model[self.current_deck.current_index].front)
        self.card_view.back_label.set_label(self.current_deck.cards_model[self.current_deck.current_index].back)

        self.navigation_view.push_by_tag("card_view")
        self.navigation_view.replace_with_tags(["list_view", "card_view"])


    def __on_edit_deck_button_clicked(self, button, deck):
        self.current_deck = deck
        self._go_to_deck(False)


    def __on_deck_checkbox_toggled(self, button, row):
        if button.get_active():
            self.list_view.decks.select_row(row)
            return

        self.list_view.decks.unselect_row(row)


    def __on_edit_card_button_clicked(self, _button, card):
        if not self.deck_view.cards_list.get_selection_mode() == Gtk.SelectionMode.NONE:
            return

        self._show_card_edit_dialog(card)


    def __on_card_checkbox_toggled(self, button, row):
        if button.get_active():
            self.deck_view.cards_list.select_row(row)
            return

        self.deck_view.cards_list.unselect_row(row)


    def __on_new_card_button_clicked(self, button):
        card = Card()
        card.front = ''
        card.back = ''

        self._show_card_edit_dialog(card)


    def __on_create_card_button_clicked(self, button, dialog, card):
        print ('## card window 300', card)
        print ('## card.front in window 301', card.front)

        if len(card.front) < 1 or len(card.back) < 1:
            return

        self.current_deck.cards_model.append(card) # enthält alle Karten der Kartei
        self.current_deck.save()
        self.decks_model.append(self.current_deck) # enthält die Karteien
        self.decks_model.emit('items-changed', 0, 0, 0)

        dialog.close()


    def __on_deck_name_changed(self, entry):
        self.current_deck.name = entry.get_text()
        ## nur wenn ein neuer Karteiname eingegeben wird wird gespeichert
        if self.current_deck.name == 'New Deck':
            pass
        else:
            self.current_deck.save()
            self.decks_model.emit('items-changed', 0, 0, 0)


    def __on_show_answer_button_clicked(self, button):
        if button.get_label() == _('Next') or button.get_label() == _('Done'):
            self.current_deck.current_index += 1

            button.set_label(_('Show Answer'))

            for child in self.card_view.card_box.observe_children():
                child.set_visible(False)

            self.card_view.front_label.set_visible(True)

            if self.current_deck.current_index + 1 > self.current_deck.cards_model.props.n_items:
                self.current_deck.current_index = 0
                self.navigation_view.pop()
                return

            self.card_view.front_label.set_label(self.current_deck.cards_model[self.current_deck.current_index].front)
            self.card_view.back_label.set_label(self.current_deck.cards_model[self.current_deck.current_index].back)
        else:
            for child in self.card_view.card_box.observe_children():
                child.set_visible(True)

            button.set_label(_('Next'))

            if self.current_deck.current_index + 1 == self.current_deck.cards_model.props.n_items:
                button.set_label(_('Done'))


    def __on_card_edit_button_changed(self, button):
        self._go_to_deck(False)
        self._show_card_edit_dialog(self.current_deck.cards_model[self.current_deck.current_index])


    def __on_emoji_picked(self, emoji_chooser, emoji_text):
        self.current_deck.icon = emoji_text
        self.current_deck.save()
        self.deck_view.deck_icon.set_label(self.current_deck.icon)
        self.decks_model.emit('items-changed', 0, 0, 0)


    def __on_deck_selection_mode_button_clicked(self, button):
        if self.list_view.decks.get_selection_mode() == Gtk.SelectionMode.NONE:
            self.list_view.set_selection_mode(True)
            return

        self.list_view.set_selection_mode(False)


    def __on_deck_delete_button_clicked(self, button):
        for row in self.list_view.decks.get_selected_rows():
            found, position = self.decks_model.find(row.deck)
            if found:
                self.decks_model.remove(position)
                if os.path.isfile(shared.decks_dir / f"{row.deck.id}.json"):
                    row.deck.delete()

        self.list_view.set_selection_mode(False)

        if self.decks_model.props.n_items < 1:
            deck = Deck()
            self.current_deck = deck
            self._go_to_deck(True)
            self.decks_model.append(deck)


    def __on_card_selection_mode_button_clicked(self, button):
        if self.deck_view.cards_list.get_selection_mode() == Gtk.SelectionMode.NONE:
            self.deck_view.set_selection_mode(True)
            return

        self.deck_view.set_selection_mode(False)


    def __on_card_delete_button_clicked(self, button):
        for row in self.deck_view.cards_list.get_selected_rows():
            if row.get_name() == 'GtkBox':
                continue

            found, position = self.current_deck.cards_model.find(row.card)
            if found:
                self.current_deck.cards_model.remove(position)
                self.current_deck.save()

        self.deck_view.set_selection_mode(False)

        if self.current_deck.cards_model.props.n_items < 1:
            self.deck_view.selection_mode_button.set_visible(False)


    def _setup_signals(self):
        self.decks_model.connect('items-changed', lambda *_: self.list_view.decks.bind_model(self.decks_model, self.__decks_create_row))

        self.welcome_page.start_button.connect('clicked', self.__on_start_button_clicked)

        self.list_view.new_deck_button.connect('clicked', self.__on_new_deck_button_clicked)
        self.list_view.selection_mode_button.connect('clicked', self.__on_deck_selection_mode_button_clicked)
        self.list_view.delete_button.connect('clicked', self.__on_deck_delete_button_clicked)

        self.deck_view.new_card_button.connect('clicked', self.__on_new_card_button_clicked)
        self.deck_view.selection_mode_button.connect('clicked', self.__on_card_selection_mode_button_clicked)
        self.deck_view.delete_button.connect('clicked', self.__on_card_delete_button_clicked)

        self.card_view.show_answer_button.connect('clicked', self.__on_show_answer_button_clicked)
        self.card_view.edit_button.connect('clicked', self.__on_card_edit_button_changed)

        self.deck_view.emoji_chooser.connect('emoji-picked', self.__on_emoji_picked)


    def _load_decks(self):

        data_dir = (
        Path(os.getenv("XDG_DATA_HOME"))
        if "XDG_DATA_HOME" in os.environ
        else Path.home() / ".local" / "share")

        self.decks_dir = data_dir / "flashcards" / "decks"

        self.decks = []
        self.deck_names = []

        if os.path.isfile(self.decks_dir / 'karteibox.db'):  # wenn es eine Datenbank für die Karteibox gibt wird sie aufgerufen
            self.db_nutzen("SELECT rowid, deck, front, back FROM karteibox")
            liste = self.c.fetchall()
            print ('############# in load decks ############')
            for zeile in liste:
                print ('### in load_decks zeilen in karteibox ###', zeile)
                if list(zeile) in self.decks:
                    pass
                else:
                    self.decks.append(list(zeile))

                if zeile[1] in self.deck_names:
                    pass
                else:
                    self.deck_names.append((zeile)[1])
            print ('## decks in load_decks 440 ##', self.deck_names)

            for d in self.deck_names:
                print ('## d in load_decks 460 ##', d)
                deck_name = Deck(d)
                #deck.id = d['id']
                #deck.icon = d['icon']
                self.decks_name_model.append(deck_name)

            for d in self.decks:
                deck = Deck(d)
                print ('## deck.cards_model in load_decks 467 ##', deck.cards_model)
                for cd in deck.cards_model:
                    print ('## cd in deck.cards_model ##', cd )
                    card = Card()
                    card.front = cd['front']
                    card.back = cd['back']
                    print ('## card in load_decks 471 ##', card, card.back)
                    crd = {
                        'front': cd.front,
                        'back': cd.back,
                    }
                    print ('## card in window 453 ##', crd)
                    cards.append(crd)
                    deck.cards_model.append(card)

                self.decks_model.append(deck)

                # for c in d['cards']:
                #     card = Card()
                #     card.front = c['front']
                #     card.back = c['back']

                #     deck.cards_model.append(card)

                # self.decks_model.append(deck)

        else:
            self.db_nutzen("""CREATE TABLE if not exists karteibox (
            deck_id TEXT, deck TEXT, front TEXT, back TEXT)""")

        self.conn.close()   # Verbindung schließen

    def _go_to_deck(self, is_new: bool):
        self.navigation_view.push_by_tag("deck_view")
        self.navigation_view.replace_with_tags(["list_view", "deck_view"])

        if self.current_deck.cards_model.props.n_items < 1:
            self.deck_view.cards_list.remove_css_class('boxed-list')

        print("### in go_to_deck window 524 model ###",self.current_deck.cards_model)

        self.deck_view.cards_list.bind_model(self.current_deck.cards_model, self.cards_list_create_row)

        title = ''
        if is_new:
            title = _('New Deck')
        else:
            title = _('Edit Deck')

        self.deck_view.page_title.set_title(title);
        self.deck_view.name_entry.set_text(self.current_deck.name)
        self.deck_view.deck_icon.set_text(self.current_deck.icon)
        self.deck_view.name_entry.connect('changed', self.__on_deck_name_changed)

        if is_new:
            self.deck_view.name_entry.grab_focus()


    def _show_card_edit_dialog(self, card):
        dialog = Adw.Window(transient_for=self,
                            modal=True)
        dialog.set_size_request(300, 300)
        dialog.set_default_size(360, 480)

        trigger = Gtk.ShortcutTrigger.parse_string("Escape");
        close_action = Gtk.CallbackAction().new(lambda dialog, _: dialog.close())
        shortcut = Gtk.Shortcut().new(trigger, close_action)
        dialog.add_shortcut(shortcut)

        view = Adw.ToolbarView()

        top = Adw.HeaderBar()
        title = Adw.WindowTitle()
        top.set_title_widget(title)
        view.add_top_bar(top)

        card_edit_view = CardEditView(self, card)  # in card_edit_view wird der Karteninhalt engelesen
        view.set_content(card_edit_view)

        card_edit_view.create_card_button.connect('clicked', self.__on_create_card_button_clicked, dialog, card)

        dialog.set_content(view)

        dialog.present()



