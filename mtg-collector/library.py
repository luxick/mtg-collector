import config
import util
import details
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


        # 0=ID, 1=Name, 2=Types, 3=Rarity, 4=Mana, 5=CMC(for sorting),
        self.store = Gtk.ListStore(int, str, str, str, GdkPixbuf.Pixbuf, int)
        self.lib_tree = Gtk.TreeView(self.store)
        self.lib_tree.set_rules_hint(True)

        self.lib_list = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.lib_list.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.lib_list.add(self.lib_tree)

        # region List Definitions

        renderer = Gtk.CellRendererText()
        image_renderer = Gtk.CellRendererPixbuf()

        col_id = Gtk.TreeViewColumn(title="Multiverse ID", cell_renderer=renderer, text= 0)
        col_id.set_visible(False)

        col_title = Gtk.TreeViewColumn(title="Card Name", cell_renderer=renderer, text= 1)
        col_title.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col_title.set_sort_column_id(1)

        col_types = Gtk.TreeViewColumn(title="Card Types", cell_renderer=renderer, text=2)
        col_types.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col_types.set_sort_column_id(2)

        col_rarity = Gtk.TreeViewColumn(title="Rarity", cell_renderer=renderer, text=3)
        col_rarity.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col_rarity.set_sort_column_id(3)

        col_mana = Gtk.TreeViewColumn(title="Mana Cost", cell_renderer=image_renderer, pixbuf=4)
        col_mana.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col_mana.set_sort_column_id(5)

        col_cmc = Gtk.TreeViewColumn(title="CMC", cell_renderer=renderer, text=5)
        col_cmc.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col_cmc.set_visible(False)

        self.lib_tree.append_column(col_id)
        self.lib_tree.append_column(col_title)
        self.lib_tree.append_column(col_types)
        self.lib_tree.append_column(col_rarity)
        self.lib_tree.append_column(col_mana)
        self.lib_tree.append_column(col_cmc)

        self.selection = self.lib_tree.get_selection()
        self.selection.connect("changed", self.on_card_selected)
        # endregion

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
        self.store.clear()
        self.details.reset()
        self.current_card = None
        self.remove_button.set_visible(False)

        for id, card in util.library.items():
            self.store.append([id, card.name,
                               " ".join(card.types),
                               card.rarity,
                               util.create_mana_icons(card.mana_cost),
                               card.cmc])

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
