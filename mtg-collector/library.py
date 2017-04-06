import threading

import config
import util
import details
import cardlist
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


class LibraryView(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)
        self.set_column_spacing(5)
        self.current_card = None

        # region Tag Bar

        tag_bar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        tag_label = Gtk.Label("Organize Tags here")
        tag_bar.pack_start(tag_label, True, True, 0)

        # endregion

        self.lib_list = cardlist.CardList(True)
        self.lib_list.selection.connect("changed", self.on_card_selected)
        self.lib_list.filter.set_visible_func(self.lib_filter_func)

        # Detailed Card View
        self.details = details.DetailBar()

        self.remove_button = Gtk.Button("Remove from Library")
        self.remove_button.modify_bg(Gtk.StateType.NORMAL, config.red_color)
        self.remove_button.set_no_show_all(True)
        self.remove_button.connect("clicked", self.remove_button_clicked)

        # region Top bar

        topbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin_top=2, margin_bottom=2)
        search_label = Gtk.Label()
        search_label.set_markup("<big>Search</big>")

        search_completer = Gtk.EntryCompletion()
        search_completer.set_model(self.lib_list.store)
        search_completer.set_text_column(1)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_completion(search_completer)
        self.search_entry.connect("activate", self.search_activated)

        self.refresh_button = Gtk.Button("Refresh")
        self.refresh_button.set_image(Gtk.Image.new_from_icon_name(Gtk.STOCK_REFRESH, 0))
        self.refresh_button.connect("clicked", self.refresh_library)

        topbox.pack_start(search_label, False, False, 2)
        topbox.pack_start(self.search_entry, False, False, 2)
        topbox.pack_start(self.refresh_button, False, False, 2)

        # endregion

        right_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_pane.pack_start(self.details, True, True, 0)
        right_pane.pack_start(Gtk.VSeparator(), False, False, 2)
        right_pane.pack_start(self.remove_button, False, False, 2)

        # Bring it all together

        self.attach(topbox, 0, 0, 3, 1)

        self.attach(Gtk.VSeparator(), 0, 1, 3, 1)

        self.attach(tag_bar, 0, 2, 1, 1)

        self.attach(Gtk.VSeparator(), 1, 2, 1, 1)

        self.attach(self.lib_list, 2, 2, 1, 1)

        self.attach(Gtk.VSeparator(), 3, 0, 1, 3)

        self.attach(right_pane, 4, 0, 1, 3)

        self.refresh_library(self.refresh_button)

    def reload(self):
        self.refresh_library()

    def refresh_library(self, button=None):
        self.search_entry.set_text("")
        self.search_entry.activate()

        self.fill_lib_list()

    def lib_filter_func(self, model, iter, data):
        if self.search_entry.get_text() is None or self.search_entry.get_text() == "":
            return True
        else:
            return self.search_entry.get_text().lower() in self.lib_list.store[iter][1].lower()

    def search_activated(self, entry):
        self.lib_list.filter.refilter()

    def on_card_selected(self, selection):
        (model, pathlist) = selection.get_selected_rows()
        card_id = None
        for path in pathlist:
            iter = model.get_iter(path)
            card_id = model.get_value(iter, 0)

        if not card_id is None and util.library.__contains__(card_id):
            selected_card = util.library[card_id]

            if not selected_card is None:
                self.details.set_card_detail(selected_card)
                self.current_card = selected_card
                self.remove_button.set_visible(True)

    def fill_lib_list(self):
        self.lib_list.update(util.library)
        self.details.reset()
        self.current_card = None
        self.remove_button.set_visible(False)

    def card_clicked(self, flowbox, flowboxchild):
        card_id = self.flowbox_ids[flowboxchild.get_index()]
        card = util.library[card_id]
        self.current_card = card

        self.details.set_card_detail(card)
        self.remove_button.set_visible(True)

    def remove_button_clicked(self, button):
        util.remove_card_from_lib(self.current_card)
        # Reset selection in list
        self.fill_lib_list()
