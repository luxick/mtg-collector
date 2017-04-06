import cardlist
import util
import details
import config
import threading
import gi
gi.require_version('Gtk', '3.0')
from urllib.error import URLError, HTTPError
from mtgsdk import Card
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, Pango


class SearchView(Gtk.Grid):

    # region Constructor
    def __init__(self):
        Gtk.Grid.__init__(self)
        self.set_column_spacing(5)
        self.current_card = None
        self.card_lib = {}

        # region Search Box
        self.searchbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5,
                                 margin_end=5, margin_start=5, margin_top=5, margin_bottom=5)
        self.searchEntry = Gtk.Entry()
        self.searchEntry.connect("activate", self.online_search_clicked)
        self.searchbutton = Gtk.Button("Search Online")
        self.searchbutton.connect("clicked", self.online_search_clicked)
        self.searchEntryLabel = Gtk.Label(xalign=0, yalign=0)
        self.searchEntryLabel.set_markup("<big>Search for Cards:</big>")

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_no_show_all(True)

        self.searchbox.add(self.searchEntryLabel)
        self.searchbox.add(self.searchEntry)
        self.searchbox.add(self.searchbutton)
        self.searchbox.add(self.progressbar)
        self.searchbox.add(Gtk.HSeparator())
        # endregion

        # region Filters

        # Color of the cards
        color_cooser_label = Gtk.Label("Mana Color", xalign=0, yalign=0)

        self.red_mana_button = Gtk.ToggleButton(name="R", active=True)
        self.red_mana_button.connect("toggled", self.mana_toggled)
        self.blue_mana_button = Gtk.ToggleButton(name="U", active=True)
        self.blue_mana_button.connect("toggled", self.mana_toggled)
        self.green_mana_button = Gtk.ToggleButton(name="G", active=True)
        self.green_mana_button.connect("toggled", self.mana_toggled)
        self.black_mana_button = Gtk.ToggleButton(name="B", active=True)
        self.black_mana_button.connect("toggled", self.mana_toggled)
        self.white_mana_button = Gtk.ToggleButton(name="W", active=True)
        self.white_mana_button.connect("toggled", self.mana_toggled)
        self.colorless_mana_button = Gtk.ToggleButton(name="C", active=True)
        self.colorless_mana_button.connect("toggled", self.mana_toggled)

        self.color_chooser = Gtk.Grid(row_spacing=5, column_spacing=5)
        self.color_chooser.attach(self.white_mana_button, 0, 0, 1, 1)
        self.color_chooser.attach(self.blue_mana_button, 1, 0, 1, 1)
        self.color_chooser.attach(self.black_mana_button, 2, 0, 1, 1)
        self.color_chooser.attach(self.red_mana_button, 0, 1, 1, 1)
        self.color_chooser.attach(self.green_mana_button, 1, 1, 1, 1)
        self.color_chooser.attach(self.colorless_mana_button, 2, 1, 1, 1)

        # Text renderer for the Combo Boxes
        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property("wrap-width", 5)
        renderer_text.set_property("wrap-mode", Pango.WrapMode.CHAR)
        renderer_text.props.ellipsize = Pango.EllipsizeMode.END

        # Rarity
        rarity_label = Gtk.Label("Rarity", xalign=0)
        self.rarity_store = Gtk.ListStore(str, str)
        self.rarity_store.append(["", "Any"])
        self.rarity_store.append(["common", "Common"])
        self.rarity_store.append(["uncommon", "Uncommon"])
        self.rarity_store.append(["rare", "Rare"])
        self.rarity_store.append(["mythic rare", "Mythic Rare"])
        self.rarity_combo = Gtk.ComboBox.new_with_model(self.rarity_store)
        self.rarity_combo.pack_start(renderer_text, True)
        self.rarity_combo.add_attribute(renderer_text, "text", 1)

        # Set
        set_label = Gtk.Label("Set", xalign=0)
        self.set_store = Gtk.ListStore(str, str)
        self.set_store.append(["", "Any"])
        for set in util.set_list:
            self.set_store.append([set.code, set.name])

        self.set_combo = Gtk.ComboBox.new_with_model(self.set_store)
        self.set_combo.pack_start(renderer_text, True)
        self.set_combo.add_attribute(renderer_text, "text", 1)
        self.set_combo.set_entry_text_column(1)
        self.set_combo.set_wrap_width(5)
        self.set_combo.set_hexpand(False)

        # Autocomplete search in Set Combobox
        completer = Gtk.EntryCompletion()
        completer.set_model(self.set_store)
        completer.set_text_column(1)

        self.set_entry = Gtk.Entry()
        self.set_entry.set_completion(completer)

        # completer.connect("match-selected", self.match_selected)
        # self.set_combo.get_child().set_completion(completer)

        # Type
        type_label = Gtk.Label("Type", xalign=0)
        self.type_store = Gtk.ListStore(str)
        types = ["Any", "Creature", "Artifact", "Instant"
            , "Enchantment", "Sorcery", "Land", "Planeswalker"]
        for cardtype in types:
            self.type_store.append([cardtype])
        self.type_combo = Gtk.ComboBox.new_with_model(self.type_store)
        self.type_combo.pack_start(renderer_text, True)
        self.type_combo.add_attribute(renderer_text, "text", 0)

        self.filters_grid = Gtk.Grid(row_spacing=5, column_spacing=5)
        self.filters_grid.attach(color_cooser_label, 0, 0, 1, 1)
        self.filters_grid.attach(self.color_chooser, 1, 0, 1, 1)

        self.filters_grid.attach(rarity_label, 0, 1, 1, 1)
        self.filters_grid.attach(self.rarity_combo, 1, 1, 1, 1)

        self.filters_grid.attach(type_label, 0, 2, 1, 1)
        self.filters_grid.attach(self.type_combo, 1, 2, 1, 1)

        self.filters_grid.attach(set_label, 0, 3, 1, 1)
        self.filters_grid.attach(self.set_entry, 1, 3, 1, 1)

        self.filters_title = Gtk.Label(xalign=0, yalign=0)
        self.filters_title.set_markup("<big>Filter search results</big>")

        self.filters = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5,
                               margin_end=5, margin_start=5, margin_top=5, margin_bottom=5)
        self.filters.pack_start(self.filters_title, False, False, 5)
        self.filters.pack_start(self.filters_grid, False, False, 0)

        # endregion

        # Set all Buttons active
        self._do_init_filter_controls()

        # Card List
        self.search_results = cardlist.CardList(False)
        self.search_results.selection.connect("changed", self.on_card_selected)

        # Detail View for selected Card
        self.details = details.DetailBar()

        # Button to add to library
        self.add_delete_button = Gtk.Button()
        self.add_delete_button.set_no_show_all(True)
        self.add_delete_button.connect("clicked", self.on_add_delete)

        # Bring it all together
        left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_pane.pack_start(self.searchbox, False, False, 0)
        left_pane.pack_start(self.filters, False, False, 0)
        left_pane.set_hexpand(False)

        right_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_pane.pack_start(self.details, True, True, 0)
        right_pane.pack_start(Gtk.VSeparator(), False, False, 2)
        right_pane.pack_start(self.add_delete_button, False, False, 2)

        # Search
        self.attach(left_pane, 0, 0, 1, 1)
        # Separator
        self.attach(Gtk.VSeparator(), 1, 0, 1, 1)
        # List
        self.attach(self.search_results, 2, 0, 1, 1)
        # Separator
        self.attach(Gtk.VSeparator(), 3, 0, 1, 1)
        # Details and Add/Remove Button
        self.attach(right_pane, 4, 0, 1, 1)

    # endregion

    # region UI Events

    def on_add_delete(self, button):
        if util.library.__contains__(self.current_card.multiverse_id):
            util.remove_card_from_lib(self.current_card)
            print(self.current_card.name + " removed to library")
        else:
            util.add_card_to_lib(self.current_card)
            util.window.search_add.set_sensitive(False)
            print(self.current_card.name + " added to library")
        self._do_update_add_button()

    def online_search_clicked(self, button):
        # Clear old data from liststore
        self.search_results.store.clear()
        # Reset details pane
        self.details.reset()
        # Reset selected card
        self.current_card = None
        # Hide Add delete button
        self.add_delete_button.set_visible(False)
        # Define the function to load cards in a seperate thread, so the UI is not blocked
        self.loadthread = threading.Thread(target=self.load_cards)
        # Deamonize Thread so it tops if the main thread exits
        self.loadthread.setDaemon(True)
        # Start to load cards
        self.loadthread.start()

    def mana_toggled(self, toggle_button):
        iconname = ""
        if toggle_button.get_active():
            iconname = "{" + toggle_button.get_name() + "}"
        else:
            iconname = "{" + toggle_button.get_name() + "_alt}"
        image = Gtk.Image()
        image.set_from_pixbuf(util.create_mana_icons(iconname))
        toggle_button.set_image(image)

    def on_card_selected(self, selection):
        (model, pathlist) = selection.get_selected_rows()
        for path in pathlist:
            iter = model.get_iter(path)
            card_id = model.get_value(iter, 0)

            selected_card = None
            for id, card in self.card_lib.items():
                if id == card_id:
                    selected_card = card
            if selected_card is not None:
                self.details.set_card_detail(selected_card)
                self.current_card = selected_card

                self.add_delete_button.set_visible(True)
                self._do_update_add_button()
                util.window.search_add.set_sensitive(True)

    # endregion

    # region Public Functions

    def reload(self):
        self.searchEntry.grab_focus()

    def load_cards(self):
        # Get search term
        term = self.searchEntry.get_text()
        # Lock down search controls
        GObject.idle_add(self._do_activate_controls, False, priorty=GObject.PRIORITY_DEFAULT)

        # Get filter rules
        colorlist = self._get_color_filter()
        tree_iter = self.rarity_combo.get_active_iter()
        rarityfilter = self.rarity_store.get_value(tree_iter, 0)
        tree_iter = self.type_combo.get_active_iter()
        typefilter = self.type_store.get_value(tree_iter, 0)
        if typefilter == "Any":
            typefilter = ""
        set_filter = ""
        if not self.set_entry.get_text() == "":
            for row in self.set_store:
                if row[1] == self.set_entry.get_text():
                    set_filter = row[0]

        # Load card info from internet
        print("\nStart online search")
        GObject.idle_add(util.push_status, "Searching for cards", priorty=GObject.PRIORITY_DEFAULT)
        try:
            cards = Card.where(name=term) \
                .where(colorIdentity=",".join(colorlist)) \
                .where(types=typefilter) \
                .where(set=set_filter) \
                .where(rarity=rarityfilter) \
                .where(pageSize=50) \
                .where(page=1).all()
        except (URLError, HTTPError) as err:
            print("Error connecting to the internet")
            GObject.idle_add(util.show_message, "Connection Error", str(err.reason), priority=GObject.PRIORITY_DEFAULT)
            GObject.idle_add(self._do_activate_controls, True, priorty=GObject.PRIORITY_DEFAULT)
            return

        print("Done. Found " + str(len(cards)) + " cards")
        if len(cards) == 0:
            messagetext = "No cards with name \"" + term + "\" found"
            GObject.idle_add(util.show_message, "No Results", messagetext, priority=GObject.PRIORITY_DEFAULT)
            # Reactivate search controls
            GObject.idle_add(self._do_activate_controls, True, priority=GObject.PRIORITY_DEFAULT)
            GObject.idle_add(self.searchEntry.grab_focus, priority=GObject.PRIORITY_DEFAULT)
            return

        # Remove duplicate entries
        if config.show_from_all_sets is False:
            cards = self.remove_duplicates(cards)

        GObject.idle_add(self.progressbar.set_visible, True, priorty=GObject.PRIORITY_DEFAULT)
        GObject.idle_add(util.push_status, "Loading cards...", priorty=GObject.PRIORITY_DEFAULT)

        # Add search results to list
        self.card_lib.clear()
        for card in cards:
            self.card_lib[card.multiverse_id] = card
        self.search_results.update(self.card_lib, self.progressbar)

        # Reactivate search controls
        GObject.idle_add(self._do_activate_controls, True, priority=GObject.PRIORITY_DEFAULT)
        GObject.idle_add(util.push_status, "", priorty=GObject.PRIORITY_DEFAULT)
        # Hide Progress bar
        GObject.idle_add(self.progressbar.set_visible, False, priorty=GObject.PRIORITY_DEFAULT)
        # Focus first element in List
        GObject.idle_add(self.search_results.list.grab_focus, priority=GObject.PRIORITY_DEFAULT)

    # endregion

    # region Private Functions

    def remove_duplicates(self, cards):
        unique_cards = []
        unique_names = []
        # Reverse cardlist so we get the version with the most modern art
        for card in reversed(cards):
            if card.name not in unique_names:
                unique_names.append(card.name)
                unique_cards.append(card)
        counter = len(cards) - len(unique_cards)

        # Show count of removed duplicates
        print("Removed " + str(counter) + " duplicate entries")
        return unique_cards

    def _do_update_add_button(self):
        if not util.library.__contains__(self.current_card.multiverse_id):
            self.add_delete_button.set_label("Add to Library")
            self.add_delete_button.modify_bg(Gtk.StateType.NORMAL, config.green_color)
        else:
            self.add_delete_button.set_label("Remove from Library")
            self.add_delete_button.modify_bg(Gtk.StateType.NORMAL, config.red_color)

    def _do_show_no_results(self, searchterm):
        # Should move to main UI, so parent can be used
        dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "No Results")
        dialog.format_secondary_text("No cards with name \"" + searchterm + "\" were found")
        dialog.run()
        dialog.destroy()

    def _do_init_filter_controls(self):
        # Toggle each Button to deactivate filter an load icon
        for widget in self.color_chooser:
            if isinstance(widget, Gtk.ToggleButton):
                widget.toggled()
                widget.set_active(False)
        # Set default rarity and type filters to "Any"
        self.rarity_combo.set_active(0)
        self.type_combo.set_active(0)

    def _do_activate_controls(self, active):
        self.searchEntry.set_editable(active)
        self.searchEntry.set_sensitive(active)
        self.searchbutton.set_sensitive(active)
        self.red_mana_button.set_sensitive(active)
        self.blue_mana_button.set_sensitive(active)
        self.black_mana_button.set_sensitive(active)
        self.green_mana_button.set_sensitive(active)
        self.white_mana_button.set_sensitive(active)
        self.colorless_mana_button.set_sensitive(active)
        self.rarity_combo.set_sensitive(active)
        self.type_combo.set_sensitive(active)
        self.set_entry.set_sensitive(active)
        self.set_entry.set_editable(active)

    def _get_color_filter(self):
        color_list = []
        # Go through mana color buttons an get the active filters
        for widget in self.color_chooser:
            if isinstance(widget, Gtk.ToggleButton):
                if widget.get_active():
                    color_list.append(widget.get_name())
        return color_list

    # endregion

    pass
