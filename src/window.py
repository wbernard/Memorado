# SPDX-License-Identifier: GPL-3.0-or-later

import os
import json
import uuid
import sqlite3
import random


from gi.repository import Adw, Gtk, Gio, GObject, GLib
from pathlib import Path

from .welcome import Welcome
from .list_view import ListView
from .deck_view import DeckView
from .card_view import CardView
from .card_new_view import CardNewView
from .deck_row import DeckRow
from .card_row import CardRow
from .card_edit import CardEdit

from .const import IS_DEVEL

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
    card_order = []

    def __init__(self, name = '', **kargs):
        super().__init__(**kargs)

        self.id = str(uuid.uuid4().hex)
        self.name = name
        self.icon = ''
        self.cards_model = Gio.ListStore.new(Card)
        self.current_index = 0

        self.data_dir = (
        Path(os.getenv("XDG_DATA_HOME"))
        if "XDG_DATA_HOME" in os.environ
        else Path.home() / ".local" / "share"
        )

        self.decks_dir = self.data_dir


    def save(self):

        cards = []

        conn = sqlite3.connect(self.decks_dir / 'database.db')
        c = conn.cursor() # eine cursor instanz erstellen

        ## Nachschauen ob deck.id in decks existiert

        c.execute("""SELECT * FROM decks WHERE deck_id = :deck_id""",{'deck_id': self.id})
        liste = c.fetchall()   ##Liste der bereits existierenden deck.id
        deck_exist = len(liste) > 0    ## überprüfen!

        ## wenn ja, Namen  und icon überschreiben
        ## wenn nein, neuen Eintrag in decks erstellen mit Namen und icon
        if deck_exist:  ## existierende decks werden upgedated
            c.execute("""UPDATE decks SET name = :name, icon = :icon
                    WHERE deck_id = :deck_id""",
                    {'deck_id': self.id, 'name': self.name, 'icon': self.icon })
        else:
            c.execute("""INSERT INTO decks VALUES (
                :deck_id, :name, :icon )""",
                {'deck_id': self.id, 'name': self.name, 'icon': self.icon })

        ## in cards alle Einträge mit deck.id löschen
        c.execute("""DELETE FROM cards
                    WHERE deck_id = :deck_id""",
                    {'deck_id': self.id})

        ## für jede karte in self.cards_model neuen eintrag in cards erstellen
        for crd in self.cards_model:
            c.execute("""INSERT INTO cards VALUES (
                :deck_id, :front, :back )""",
                {'deck_id': self.id, 'front': crd.front, 'back': crd.back })
            card = {
                'front': crd.front,
                'back': crd.back,
            }
            cards.append(card)

        conn.commit()
        conn.close()   # Verbindung schließen

    def delete_from_db(self):

        conn = sqlite3.connect(self.decks_dir / 'database.db')
        c = conn.cursor() # eine cursor instanz erstellen"
        c.execute("""DELETE FROM cards
                    WHERE deck_id = :deck_id""",
                    {'deck_id': self.id})
        c.execute("""DELETE FROM decks
                    WHERE deck_id = :deck_id""",
                    {'deck_id': self.id})
        conn.commit()
        conn.close()   # Verbindung schließen

    def shuffle(self):
        self.card_order = list(range(len(self.cards_model)))
        random.shuffle(self.card_order);


@Gtk.Template(resource_path='/im/bernard/Memorado/ui/window.ui')
class Window(Adw.ApplicationWindow):
    __gtype_name__ = 'Window'

    toast_overlay = Gtk.Template.Child()
    navigation_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if IS_DEVEL:
            self.add_css_class('devel')

        self.decks_model = Gio.ListStore.new(Deck)  # da sind die Karteien samt Karten drin
        self.decks_name_model = Gio.ListStore.new(Deck)  # nur die Namen der Karteien
        self.es = None

        self.tabel_erstel('database.db')
        self._load_decks('database.db')

        self.welcome_page = Welcome()
        self.list_view = ListView()
        self.list_view.decks.bind_model(self.decks_model, self.__decks_create_row)
        self.deck_view = DeckView()
        self.card_view = CardView()

        self._setup_signals()

        self.navigation_view.add(self.welcome_page)   # Willkommensseite wird angezeigt

        self.navigation_view.add(self.list_view)     # Liste der Karteien
        self.navigation_view.add(self.deck_view)     # Ansicht der Kartei mit Liste der Karten
        self.navigation_view.add(self.card_view)     # Ansicht einer Karte

        if self.decks_model.props.n_items > 0:   # wenn es keine Karteien gibt
            self.navigation_view.replace_with_tags(["list_view"])

        self.export_dialog = Gtk.FileDialog(title=_("Export as File"), initial_name="database.db")
        self.import_dialog = Gtk.FileDialog(title=_("Import Database"))

        file_filters = Gio.ListStore.new(Gtk.FileFilter)
        # file filter for sqlite databases, e.g. `.db` or `.anki2`
        sql_file_filter = Gtk.FileFilter.new()
        sql_file_filter.set_name(_("Supported files"))
        sql_file_filter.add_mime_type("application/vnd.sqlite3")
        file_filters.append(sql_file_filter)

        all_file_filter = Gtk.FileFilter.new()
        all_file_filter.set_name(_("All files"))
        all_file_filter.add_pattern("*")
        file_filters.append(all_file_filter)

        self.import_dialog.set_filters(file_filters)

    def tabel_erstel(self, dateiname):
        # Pfad zur Datenbank
        data_dir = (
        Path(os.getenv("XDG_DATA_HOME"))
        if "XDG_DATA_HOME" in os.environ
        else Path.home() / ".local" / "share")

        self.decks_dir = data_dir

        # Tabellen erstellen
        self.db_nutzen("""CREATE TABLE if not exists cards (
                              deck_id TEXT, front TEXT, back TEXT)""", dateiname)
        self.db_nutzen("""CREATE TABLE if not exists decks (deck_id TEXT,
                  name TEXT,
                  icon TEXT)""", dateiname)

    def db_nutzen(self, befehl, dateiname):

        conn = sqlite3.connect(self.decks_dir / dateiname)
        c = conn.cursor() # eine cursor instanz erstellen
        c.execute(befehl) # befehl wird ausgeführt
        out = c.fetchall()
        conn.commit()
        conn.close()   # Verbindung schließen
        return(out)

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

    def __on_import_button_clicked(self, button):
        self.on_import_clicked()
        return

    def __on_new_deck_button_clicked(self, button):
        deck = Deck()
        self.current_deck = deck
        self._go_to_deck(True)
        self.decks_model.append(deck)


    def __on_deck_activated(self, row, deck):
        self.current_deck = deck
        self.current_deck.shuffle()

        if not self.list_view.decks.get_selection_mode() == Gtk.SelectionMode.NONE:
            row.checkbox.set_active(not row.checkbox.get_active())
            return

        if self.current_deck.cards_model.props.n_items == 0:
            self._go_to_deck(False)
            return

        card_index = self.current_deck.card_order[0]
        front_string = self.current_deck.cards_model[card_index].front
        back_string = self.current_deck.cards_model[card_index].back

        self.card_view.front_label.set_label(front_string)
        self.card_view.back_label.set_label(back_string)

        if len(front_string) > 30:
            self.card_view.front_label.remove_css_class("card-text")
            self.card_view.front_label.add_css_class("card-text-small")
        else:
            self.card_view.front_label.remove_css_class("card-text-small")
            self.card_view.front_label.add_css_class("card-text")

        if len(back_string) > 30:
            self.card_view.back_label.remove_css_class("card-text")
            self.card_view.back_label.add_css_class("card-text-small")
        else:
            self.card_view.back_label.remove_css_class("card-text-small")
            self.card_view.back_label.add_css_class("card-text")

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

        self._new_card_dialog(card)

    def __on_save_card_button_clicked(self, button, dialog, card):
        self.current_deck.save()
        dialog.close()


    def __on_create_card_button_clicked(self, button, dialog, card):
        self.current_deck.cards_model.append(card) # enthält alle Karten der Kartei
        self.current_deck.save()
        self.decks_model.emit('items-changed', 0, 0, 0)

        dialog.close()


    def __on_deck_name_changed(self, entry):
        self.current_deck.name = entry.get_text()
        self.current_deck.save()
        self.decks_model.emit('items-changed', 0, 0, 0)


    def __on_show_answer_button_clicked(self, button):
        if button.get_label() == _('Next') or button.get_label() == _('Done'):
            self.current_deck.current_index += 1

            self.card_view.hide_answer()

            if self.current_deck.current_index + 1 > self.current_deck.cards_model.props.n_items:
                self.current_deck.current_index = 0
                self.navigation_view.pop()
                return

            card_index = self.current_deck.card_order[self.current_deck.current_index]
            front_string = self.current_deck.cards_model[card_index].front
            back_string = self.current_deck.cards_model[card_index].back

            self.card_view.front_label.set_label(front_string)
            self.card_view.back_label.set_label(back_string)

            if len(front_string) > 30:
                self.card_view.front_label.add_css_class("card-text-small")
                self.card_view.front_label.remove_css_class("card-text")
            else:
                self.card_view.front_label.remove_css_class("card-text-small")
                self.card_view.front_label.add_css_class("card-text")

            if len(back_string) > 30:
                self.card_view.back_label.add_css_class("card-text-small")
                self.card_view.back_label.remove_css_class("card-text")
            else:
                self.card_view.back_label.remove_css_class("card-text-small")
                self.card_view.back_label.add_css_class("card-text")

        else:
            isDone = self.current_deck.current_index + 1 == self.current_deck.cards_model.props.n_items
            self.card_view.show_answer(isDone)


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
            self.delete_deck(row.deck)

        self.list_view.set_selection_mode(False)


    def delete_deck(self, deck):
        found, position = self.decks_model.find(deck)
        if found:
            self.decks_model[position].delete_from_db()
            self.decks_model.remove(position)

        if self.decks_model.props.n_items < 1:
            self.navigation_view.replace_with_tags(["welcome_page"])


    def __on_deck_view_popped(self, navigation_view, view):
        if isinstance(view, DeckView):
            if (self.current_deck.name == "" and
                self.current_deck.icon == "" and
                self.current_deck.cards_model.props.n_items < 1):
                self.delete_deck(self.current_deck)
        elif isinstance(view, CardView):
            self.card_view.hide_answer()


    def __on_window_closed(self, blub):
        if hasattr(self, "current_deck"):
            if (self.current_deck.name == "" and
                self.current_deck.icon == "" and
                self.current_deck.cards_model.props.n_items < 1):
                self.delete_deck(self.current_deck)


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
                self.decks_model.emit('items-changed', 0, 0, 0)

        self.deck_view.set_selection_mode(False)

        if self.current_deck.cards_model.props.n_items < 1:
            self.deck_view.selection_mode_button.set_visible(False)

    def __on_card_delete_button_on_dialog_clicked(self, button, dialog, card):
        found, position = self.current_deck.cards_model.find(card)
        if found:
            self.current_deck.cards_model.remove(position)
            self.current_deck.save()
            self.decks_model.emit('items-changed', 0, 0, 0)

        dialog.close()


    def _setup_signals(self):
        self.decks_model.connect('items-changed', lambda *_: self.list_view.decks.bind_model(self.decks_model, self.__decks_create_row))

        self.welcome_page.start_button.connect('clicked', self.__on_start_button_clicked)
        self.welcome_page.import_button.connect('clicked', self.__on_import_button_clicked)

        self.list_view.new_deck_button.connect('clicked', self.__on_new_deck_button_clicked)
        self.list_view.selection_mode_button.connect('clicked', self.__on_deck_selection_mode_button_clicked)
        self.list_view.delete_button.connect('clicked', self.__on_deck_delete_button_clicked)

        self.deck_view.new_card_button.connect('clicked', self.__on_new_card_button_clicked)
        self.deck_view.selection_mode_button.connect('clicked', self.__on_card_selection_mode_button_clicked)
        self.deck_view.delete_button.connect('clicked', self.__on_card_delete_button_clicked)
        self.navigation_view.connect('popped', self.__on_deck_view_popped)

        self.connect('close-request', self.__on_window_closed)

        self.card_view.show_answer_button.connect('clicked', self.__on_show_answer_button_clicked)
        self.card_view.edit_button.connect('clicked', self.__on_card_edit_button_changed)

        self.deck_view.emoji_chooser.connect('emoji-picked', self.__on_emoji_picked)

    def _load_decks(self, dateiname):

        data_dir = (
        Path(os.getenv("XDG_DATA_HOME"))
        if "XDG_DATA_HOME" in os.environ
        else Path.home() / ".local" / "share")

        self.decks_dir = data_dir

        #self.decks = []

        ## eine Liste der decks erstellen
        self.decks = self.db_nutzen("SELECT * FROM " + 'decks' + ";", dateiname) # enthält id, name und icon aller decks

        ## eine Liste der cards erstellen
        self.all_cards = self.db_nutzen("SELECT * FROM " + 'cards' + ";", dateiname) # enthält id, front und back aller karten

        self.decks_model.remove_all()
        ## für jedes deck eine Kartenliste erstellen
        for d in self.decks:
            deck = Deck(d[1])
            deck.id = d[0]
            deck.icon = d[2]
            for crd in self.all_cards:
                if crd[0] == deck.id:
                    card = Card()
                    card.front = crd[1]
                    card.back = crd[2]
                    deck.cards_model.append(card)

            self.decks_model.append(deck)

    def _go_to_deck(self, is_new: bool):
        self.navigation_view.push_by_tag("deck_view")
        self.navigation_view.replace_with_tags(["list_view", "deck_view"])

        if self.current_deck.cards_model.props.n_items < 1:    ## wenn noch keine decks vorhanden sind
            self.deck_view.cards_list.remove_css_class('boxed-list')

        self.deck_view.cards_list.bind_model(self.current_deck.cards_model, self.cards_list_create_row)

        title = ''
        ## When a new deck is created, the name 'New Deck' is set as the title of the card.
        if is_new:
            title = _('New Deck')
        else:
            title = _('Edit Deck')

        self.deck_view.page_title.set_title(title);
        self.deck_view.name_entry.set_text(self.current_deck.name)  ## bei neuem deck wird New Deck geschrieben
        self.deck_view.deck_icon.set_text(self.current_deck.icon)
        self.deck_view.name_entry.connect('changed', self.__on_deck_name_changed)

        if is_new:
            self.deck_view.name_entry.grab_focus()


    def _show_card_edit_dialog(self, card):
        dialog = Adw.Dialog()
        dialog.set_size_request(300, 300)
        dialog.set_content_height(480)
        dialog.set_content_width(360)

        trigger = Gtk.ShortcutTrigger.parse_string("Escape");
        close_action = Gtk.CallbackAction().new(lambda dialog, _: dialog.close())
        shortcut = Gtk.Shortcut().new(trigger, close_action)
        dialog.add_shortcut(shortcut)

        view = Adw.ToolbarView()

        top = Adw.HeaderBar()
        title = Adw.WindowTitle()
        top.set_title_widget(title)

        delete_button = Gtk.Button()
        delete_button.set_icon_name("user-trash-symbolic")
        delete_tooltip = _("Delete Card")
        delete_button.set_tooltip_text(delete_tooltip)
        delete_button.connect('clicked', self.__on_card_delete_button_on_dialog_clicked, dialog, card)
        top.pack_start(delete_button)

        view.add_top_bar(top)

        card_edit = CardEdit(self, card)
        view.set_content(card_edit)

        card_edit.save_card_button.connect('clicked', self.__on_save_card_button_clicked, dialog, card)

        dialog.set_child(view)

        dialog.present(self)

    def _new_card_dialog(self, card):

        dialog = Adw.Dialog()
        dialog.set_size_request(300, 300)
        dialog.set_content_height(480)
        dialog.set_content_width(360)

        trigger = Gtk.ShortcutTrigger.parse_string("Escape");
        close_action = Gtk.CallbackAction().new(lambda dialog, _: dialog.close())
        shortcut = Gtk.Shortcut().new(trigger, close_action)
        dialog.add_shortcut(shortcut)

        view = Adw.ToolbarView()

        top = Adw.HeaderBar()
        title = Adw.WindowTitle()
        top.set_title_widget(title)
        view.add_top_bar(top)

        card_new_view = CardNewView(self, card)  # in card_new_view wird der Karteninhalt engelesen
        view.set_content(card_new_view)

        card_new_view.create_card_button.connect('clicked', self.__on_create_card_button_clicked, dialog, card)

        dialog.set_child(view)

        dialog.present(self)

    def on_export_clicked(self):
        self.export_dialog.save(parent = self, callback = self.on_export_dialog_response, cancellable = None)

    def on_export_dialog_response(self, dialog, response):
        file = dialog.save_finish(response)
        deckspath = self.decks_dir / "database.db"
        sourcefile = Gio.File.new_for_path(str(deckspath))
        sourcefile.copy_async(
            file,
            Gio.FileCopyFlags.OVERWRITE,
            GLib.PRIORITY_DEFAULT,
            None,
            None,
            None,
            self.on_replace_contents,
            None
            )

        toast = Adw.Toast(
            title = _("Export successful"),
            timeout = 3,
        )

        self.toast_overlay.add_toast(toast);

    def on_replace_contents(self, file, result, unused):
        file.copy_finish(result)


    def on_import_clicked(self):
        self.import_dialog.open(parent = self, callback = self.on_import_dialog_response, cancellable = None)


    def on_import_dialog_response(self, dialog, response):
        file = dialog.open_finish(response)

        filename, file_extension = os.path.splitext(file)
        if file_extension == ".db":
            self.import_db_file(file)
        elif file_extension == ".anki2":
            self.import_anki2_file(file)
        else:
            print("Extension", file_extension, "not supported")

    def import_db_file(self, file):

        # Lese gegebene datenbank mit der normalen databank lese logik
        conn = sqlite3.connect(file.get_path())
        c = conn.cursor()
        befehl = "SELECT * FROM " + 'decks' + ";"
        c.execute(befehl)
        imported_decks = c.fetchall()
        befehl = "SELECT * FROM " + 'cards' + ";"
        c.execute(befehl)
        imported_cards = c.fetchall()
        conn.close()

        self.merge_databases(imported_decks, imported_cards)

    def merge_databases(self, imported_decks, imported_cards):
        # Vereine die bestehende Datenbank mit der neuen
        conn = sqlite3.connect(self.decks_dir / 'database.db')
        c = conn.cursor()
        befehl = "SELECT * FROM " + 'decks' + ";"
        c.execute(befehl)
        existing_decks = c.fetchall()
        befehl = "SELECT * FROM " + 'cards' + ";"
        c.execute(befehl) # befehl wird ausgeführt
        existing_cards = c.fetchall()

        # Nachschauen ob importiertes deck schon vorhanden ist und nur neue hinzufügen
        nonduplicate_decks = 0
        for deck in imported_decks:
            if not deck in existing_decks:
                nonduplicate_decks += 1
                c.execute("""INSERT INTO decks VALUES (
                :deck_id, :name, :icon )""",
                {'deck_id': deck[0], 'name': deck[1], 'icon': deck[2]})

        nonduplicate_cards = 0
        for card in imported_cards:
            if not card in existing_cards:
                nonduplicate_cards += 1
                c.execute("""INSERT INTO cards VALUES (
                :deck_id, :front, :back )""",
                {'deck_id': card[0], 'front': card[1], 'back': card[2]})

        conn.commit()
        conn.close()   # Verbindung schließen

        self._load_decks('database.db')
        self.navigation_view.replace_with_tags(["list_view"])

        # Adw.Toast notification
        cards_string = "cards"
        if nonduplicate_cards == 1:
            cards_string = "card"

        decks_string = "decks"
        if nonduplicate_decks == 1:
            decks_string = "deck"

        toast_title = "Imported " + str(nonduplicate_cards) + " " + cards_string + " from " + str(nonduplicate_decks) + " " + decks_string

        if nonduplicate_cards == 0:
            if nonduplicate_decks == 1:
                toast_title = _("Imported one empty deck")
            elif nonduplicate_decks == 0:
                toast_title = _("Imported nothing, all cards are duplicates")
            else:
                toast_title = _("Imported {0} empty decks").format(str(nonduplicate_decks))

        toast = Adw.Toast(
            title = toast_title,
            timeout = 3,
        )

        self.toast_overlay.add_toast(toast);

    def import_anki2_file(self, file):

        imported_deck_name = "Imported Deck"
        imported_deck_id = '%030x' % random.randrange(16**32)
        imported_deck_icon = '🤖'

        imported_decks = [[imported_deck_id,imported_deck_name,imported_deck_icon]]

        ## Filter imported database content
        conn = sqlite3.connect(file.get_path())
        c = conn.cursor()

        imported_cards = []
        # zeilen von anki2 datei werden eingelesen
        for row in c.execute("select * from notes"):
                string = row[6].replace("<br>", '')
                split = string.split('')
                front = split[0]
                back = split[1]
                card = [imported_deck_id, front, back]
                imported_cards.append(card)
        conn.close()   # Verbindung schließen

        self.merge_databases(imported_decks, imported_cards)
