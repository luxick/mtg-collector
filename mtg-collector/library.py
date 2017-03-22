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

        # region Demo left bar
        # Search Box
        self.searchbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.searchEntry = Gtk.Entry()
        self.searchEntryLabel = Gtk.Label("Search in Collection:", xalign=0)
        self.searchbox.add(self.searchEntryLabel)
        self.searchbox.add(self.searchEntry)

        # Filters
        self.filterBox = Gtk.ListBox()
        self.filterBox.set_selection_mode(Gtk.SelectionMode.NONE)

        self.testRow = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        hbox.add(Gtk.Label("Filters will go here", xalign=0))
        self.testRow.add(hbox)

        self.filterBox.add(self.testRow)
        # endregion

        self.lib_list = cardlist.CardList()
        self.lib_list.selection.connect("changed", self.on_card_selected)

        # Detailed Card View
        self.details = details.DetailBar()

        self.remove_button = Gtk.Button("Remove from Library")
        self.remove_button.modify_bg(Gtk.StateType.NORMAL, config.red_color)
        self.remove_button.set_no_show_all(True)
        self.remove_button.connect("clicked", self.remove_button_clicked)

        left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_pane.pack_start(self.searchbox, False, False, 0)
        left_pane.pack_start(self.filterBox, False, False, 0)

        right_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_pane.pack_start(self.details, True, True, 0)
        right_pane.pack_start(Gtk.VSeparator(), False, False, 2)
        right_pane.pack_start(self.remove_button, False, False, 2)

        # Bring it all together
        self.attach(left_pane, 0, 0, 1, 1)

        self.attach(Gtk.VSeparator(), 1, 0, 1, 1)

        self.attach(self.lib_list, 2, 0, 1, 1)

        self.attach(Gtk.VSeparator(), 3, 0, 1, 1)

        self.attach(right_pane, 4, 0, 1, 1)

        self.fill_lib_list()

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
        self.lib_list.store.clear()
        self.details.reset()
        self.current_card = None
        self.remove_button.set_visible(False)

        for id, card in util.library.items():
            if card.supertypes is None:
                card.supertypes = ""
            self.lib_list.store.append([
                id,
                card.name,
                " ".join(card.supertypes),
                " ".join(card.types),
                card.rarity,
                card.power,
                card.toughness,
                ", ".join(card.printings),
                util.create_mana_icons(card.mana_cost),
                card.cmc,
                card.set_name])

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
