from urllib.error import URLError

import gi
from gi.repository import Pango
import util
import details
import config

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject
from mtgsdk import Card
import threading

class SearchView(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)
        self.set_column_spacing(5)
        # Search Box
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

        # Filters
        # Color of the cards
        self.mana_filter_label = Gtk.Label("Mana Color", xalign=0, yalign=0)
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
        self.color_chooser.attach(self.mana_filter_label, 0, 0, 5, 1)
        self.color_chooser.attach(self.white_mana_button, 0, 1, 1, 1)
        self.color_chooser.attach(self.blue_mana_button, 1, 1, 1, 1)
        self.color_chooser.attach(self.black_mana_button, 2, 1, 1, 1)
        self.color_chooser.attach(self.red_mana_button, 0, 2, 1, 1)
        self.color_chooser.attach(self.green_mana_button, 1, 2, 1, 1)
        self.color_chooser.attach(self.colorless_mana_button, 2, 2, 1, 1)

        # Rarity
        rarity_label = Gtk.Label("Rarity", xalign=0)
        self.rarity_store = Gtk.ListStore(str, str)
        self.rarity_store.append(["", "Any"])
        self.rarity_store.append(["common", "Common"])
        self.rarity_store.append(["uncommon", "Uncommon"])
        self.rarity_store.append(["rare", "Rare"])
        self.rarity_store.append(["mythic rare", "Mythic Rare"])
        self.rarity_combo = Gtk.ComboBox.new_with_model(self.rarity_store)
        renderer_text = Gtk.CellRendererText()
        self.rarity_combo.pack_start(renderer_text, True)
        self.rarity_combo.add_attribute(renderer_text, "text", 1)

        type_label = Gtk.Label("Type", xalign=0)
        self.type_store = Gtk.ListStore(str)
        types = [ "Any", "Creature", "Artifact", "Instant",
                            "Aura", "Enchantment", "Sorcery", "Land", "Planeswalker"]
        for cardtype in types:
            self.type_store.append([cardtype])
        self.type_combo = Gtk.ComboBox.new_with_model(self.type_store)
        self.type_combo.pack_start(renderer_text, True)
        self.type_combo.add_attribute(renderer_text, "text", 0)

        self.additional_filters = Gtk.Grid(row_spacing=5, column_spacing=5)
        self.additional_filters.attach(rarity_label, 0, 0, 1, 1)
        self.additional_filters.attach(self.rarity_combo, 1, 0, 1, 1)
        self.additional_filters.attach(type_label, 0, 1, 1, 1)
        self.additional_filters.attach(self.type_combo, 1 ,1, 1, 1)

        self.filters_title = Gtk.Label(xalign=0, yalign=0)
        self.filters_title.set_markup("<big>Filter search results</big>")

        self.filters = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5,
                               margin_end=5, margin_start=5, margin_top=5, margin_bottom=5)
        self.filters.add(self.filters_title)
        self.filters.add(self.color_chooser)
        self.filters.add(self.additional_filters)
        # Set all Buttons active
        self.do_init_filter_controls()

        # Card List
        self.searchresults = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.searchresults.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.store = Gtk.ListStore(int, GdkPixbuf.Pixbuf, str, str, GdkPixbuf.Pixbuf)
        self.list = Gtk.TreeView(self.store)
        self.list.set_rules_hint(True)
        self.searchresults.add(self.list)

        image = Gtk.CellRendererPixbuf()

        title = Gtk.CellRendererText(xalign=0.5)
        title.set_padding(5, 5)

        info = Gtk.CellRendererText()
        info.set_property("wrap-mode", Pango.WrapMode.WORD)
        info.set_property("wrap-width", 100)
        info.set_padding(5, 5)

        index = Gtk.CellRendererText()
        self.indexcolumn = Gtk.TreeViewColumn(title=index, cell_renderer=index, text=0)
        self.indexcolumn.set_visible(False)
        self.column1 = Gtk.TreeViewColumn(title="Image", cell_renderer=image, pixbuf=1)
        self.column1.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column2 = Gtk.TreeViewColumn(title="Name", cell_renderer=title, text=2)
        self.column2.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column3 = Gtk.TreeViewColumn(title="Card Text", cell_renderer=info, text=3)
        self.column3.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.column3.set_resizable(True)
        self.column3.set_expand(True)
        self.column4 = Gtk.TreeViewColumn(title="Mana Cost", cell_renderer=image, pixbuf=4)
        self.column4.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)

        self.list.append_column(self.column1)
        self.list.append_column(self.column2)
        self.list.append_column(self.column3)
        self.list.append_column(self.column4)

        # Detail View for selected Card
        self.details = details.DetailBar()
        # Bring it all together
        self.attach(self.searchbox, 0, 0, 1, 1)
        self.attach(self.filters, 0, 1, 1, 1)
        self.attach(self.searchresults, 2, 0, 1, 2)
        self.attach(self.details, 4, 0, 1, 2)

        # Vertical Separators
        self.attach(Gtk.VSeparator(), 1, 0, 1, 2)
        self.attach(Gtk.VSeparator(), 3, 0, 1, 2)

        self.selection = self.list.get_selection()
        self.selection.connect("changed", self.on_card_selected)

    def do_show_no_results(self, searchterm):
        # Should move to main UI, so parent can be used
        dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.OK, "No Results")
        dialog.format_secondary_text("No cards with name \"" + searchterm + "\" were found")
        dialog.run()
        dialog.destroy()

    def do_activate_controls(self, active):
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

    def online_search_clicked(self, button):
        # Clear old data from liststore
        self.store.clear()
        # Reset details pane
        self.details.reset()
        # Define the function to load cards in a seperate thread, so the UI is not blocked
        self.loadthread = threading.Thread(target=self.load_cards)
        # Deamonize Thread so it tops if the main thread exits
        self.loadthread.setDaemon(True)
        # Start to load cards
        self.loadthread.start()

    def load_cards(self):
        # Get search term
        term = self.searchEntry.get_text()

        # Lock down search controls
        GObject.idle_add(self.do_activate_controls, False, priorty=GObject.PRIORITY_DEFAULT)

        # Get filter rules
        colorlist = self.get_color_filter()
        tree_iter = self.rarity_combo.get_active_iter()
        rarityfilter = self.rarity_store.get_value(tree_iter, 0)

        tree_iter = self.type_combo.get_active_iter()
        typefilter = self.type_store.get_value(tree_iter, 0)
        if typefilter == "Any":
            typefilter = ""

        # Load card info from internet
        print("\nStart online search")
        GObject.idle_add(util.push_status, "Searching for cards", priorty=GObject.PRIORITY_DEFAULT)
        try:
            self.cards = Card.where(name=term)\
                .where(colorIdentity=",".join(colorlist)) \
                .where(types=typefilter)\
                .where(rarity=rarityfilter) \
                .where(pageSize=50)\
                .where(page=1).all()
        except URLError as err:
            print("Error connecting to the internet")
            GObject.idle_add(util.show_message, "Connection Error", str(err.reason), priority=GObject.PRIORITY_DEFAULT)
            GObject.idle_add(self.do_activate_controls, True, priorty=GObject.PRIORITY_DEFAULT)
            return

        print("Done. Found " + str(len(self.cards)) + " cards")
        if len(self.cards) == 0:
            messagetext = "No cards with name \"" + term + "\" found"
            GObject.idle_add(util.show_message, "No Results", messagetext, priority=GObject.PRIORITY_DEFAULT)
            # Reactivate search controls
            GObject.idle_add(self.do_activate_controls, True, priority=GObject.PRIORITY_DEFAULT)
            return

        # Remove duplicate entries
        if config.show_from_all_sets is False:
            unique_cards = []
            unique_names = []
            # Reverse cardlist so we get the version with the most modern art
            for card in reversed(self.cards):
                if card.name not in unique_names:
                    unique_names.append(card.name)
                    unique_cards.append(card)
            duplicatecounter = len(self.cards) - len(unique_cards)
            self.cards.clear()
            for unique_card in reversed(unique_cards):
                self.cards.append(unique_card)

            # Show count of removed duplicates
            print("Removed " + str(duplicatecounter) + " duplicate entries")

        loadprogress_step = 1 / len(self.cards)
        progress = 0.0
        GObject.idle_add(self.progressbar.set_visible, True, priorty=GObject.PRIORITY_DEFAULT)
        GObject.idle_add(self.progressbar.set_fraction, 0.0, priorty=GObject.PRIORITY_DEFAULT)

        GObject.idle_add(util.push_status, "Loading cards...", priorty=GObject.PRIORITY_DEFAULT)

        for card in self.cards:
            if card.multiverse_id is not None:
                print("Found: " + card.name
                      + " (" + card.multiverse_id.__str__() + ")")
                print("Types: " + str(card.type))

                self.store.append([card.multiverse_id,
                                   util.load_card_image(card, 63 * 2, 88 * 2),
                                   card.name,
                                   card.original_text,
                                   util.create_mana_icons(card.mana_cost)])
            # update progress bar
            progress += loadprogress_step
            GObject.idle_add(self.progressbar.set_fraction, progress, priorty=GObject.PRIORITY_DEFAULT)
        print("")
        # Reload image cache to include new cards
        util.reload_image_cache()
        # Reactivate search controls
        GObject.idle_add(self.do_activate_controls, True, priority=GObject.PRIORITY_DEFAULT)
        GObject.idle_add(util.push_status, "", priorty=GObject.PRIORITY_DEFAULT)
        # Hide Progress bar
        GObject.idle_add(self.progressbar.set_visible, False, priorty=GObject.PRIORITY_DEFAULT)

    def on_card_selected(self, selection):
        (model, pathlist) = selection.get_selected_rows()
        for path in pathlist:
            iter = model.get_iter(path)
            card_id = model.get_value(iter, 0)

            selected_card = None
            for card in self.cards:
                if card.multiverse_id == card_id:
                    selected_card = card
            if selected_card is not None:
                self.details.set_card_detail(selected_card)

    def get_color_filter(self):
        colorlist = []
        # Go through mana color buttons an get the active filters
        for widget in self.color_chooser:
            if isinstance(widget, Gtk.ToggleButton):
                if widget.get_active():
                    colorlist.append(widget.get_name())
        return colorlist

    def mana_toggled(self, toggle_button):
        iconname = ""
        if toggle_button.get_active():
            iconname = "{" + toggle_button.get_name() + "}"
        else:
            iconname = "{" + toggle_button.get_name() + "_alt}"
        image = Gtk.Image()
        image.set_from_pixbuf(util.create_mana_icons(iconname))
        toggle_button.set_image(image)

    def do_init_filter_controls(self):
        # Toggle each Button to deactivate filter an load icon
        for widget in self.color_chooser:
            if isinstance(widget, Gtk.ToggleButton):
                widget.toggled()
                widget.set_active(False)
        # Set default rarity and type filters to "Any"
        self.rarity_combo.set_active(0)
        self.type_combo.set_active(0)
