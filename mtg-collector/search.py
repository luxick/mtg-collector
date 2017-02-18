import gi
from gi.repository import Pango
import util
import details
import config

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GObject
from mtgsdk import Card
import threading

GObject.threads_init()


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
        self.searchbox.add(self.searchEntryLabel)
        self.searchbox.add(self.searchEntry)
        self.searchbox.add(self.searchbutton)
        self.searchbox.add(Gtk.HSeparator())

        # Filters
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
        # Set all Buttons active
        self.init_mana_buttons()

        self.color_chooser = Gtk.Grid(row_spacing=5, column_spacing=5)
        self.color_chooser.attach(self.mana_filter_label, 0, 0, 5, 1)
        self.color_chooser.attach(self.white_mana_button, 0, 1, 1, 1)
        self.color_chooser.attach(self.blue_mana_button, 1, 1, 1, 1)
        self.color_chooser.attach(self.black_mana_button, 2, 1, 1, 1)
        self.color_chooser.attach(self.red_mana_button, 0, 2, 1, 1)
        self.color_chooser.attach(self.green_mana_button, 1, 2, 1, 1)
        self.color_chooser.attach(self.colorless_mana_button, 2, 2, 1, 1)

        self.filters_title = Gtk.Label(xalign=0, yalign=0)
        self.filters_title.set_markup("<big>Filter search results</big>")

        self.filters = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5,
                               margin_end=5, margin_start=5, margin_top=5, margin_bottom=5)
        self.filters.add(self.filters_title)
        self.filters.add(self.color_chooser)

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

    def on_appering(self):
        self.details.rulings.set_visible(False)

    def online_search_clicked(self, button):
        self.store.clear()
        self.searchEntry.set_editable(False)
        self.searchbutton.set_sensitive(False)

        threading.Thread(target=self.load_cards).start()

    def load_cards(self):
        term = self.searchEntry.get_text()
        print("Search for \"" + term + "\" online.")
        colorlist = self.get_color_filter()
        print("Filtering color(s): " + ','.join(colorlist) + "\n")

        # Load card info from internet
        self.cards = Card.where(name=term)\
            .where(colorIdentity=','.join(colorlist))\
            .where(pageSize=50)\
            .where(page=1).all()

        # Remove duplicate entries
        if config.show_from_all_sets is False:
            counter = 0
            unique_cards = []
            unique_names = []
            # Reverse cardlist so we get the version with the most modern art
            for card in reversed(self.cards):
                if card.name not in unique_names:
                    unique_names.append(card.name)
                    unique_cards.append(card)
                else:
                    counter += 1
            self.cards.clear()
            for unique_card in reversed(unique_cards):
                self.cards.append(unique_card)

            print("Removed " + str(counter) + " duplicate entries")

        for card in self.cards:
            if card.multiverse_id is not None:
                print("Found: " + card.name
                      + " (" + card.multiverse_id.__str__() + ")")

                self.store.append([card.multiverse_id,
                                   util.load_card_image(card, 63 * 2, 88 * 2),
                                   card.name,
                                   card.original_text,
                                   util.create_mana_icons(card.mana_cost)])
                print("")

        util.reload_image_cache()
        self.searchEntry.set_editable(True)
        self.searchbutton.set_sensitive(True)

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

        if not self.white_mana_button.get_active():
            colorlist.append("W")
        if not self.blue_mana_button.get_active():
            colorlist.append("U")
        if not self.black_mana_button.get_active():
            colorlist.append("B")
        if not self.red_mana_button.get_active():
            colorlist.append("R")
        if not self.green_mana_button.get_active():
            colorlist.append("G")
        if not self.colorless_mana_button.get_active():
            colorlist.append("C")
        return colorlist

    def mana_toggled(self, toggle_button):
        iconname = ""
        if not toggle_button.get_active():
            iconname = "{" + toggle_button.get_name() + "}"
        else:
            iconname = "{" + toggle_button.get_name() + "_alt}"
        image = Gtk.Image()
        image.set_from_pixbuf(util.create_mana_icons(iconname))
        toggle_button.set_image(image)

    def init_mana_buttons(self):
        # Toggle each Button to deactivate filter an load icon
        self.red_mana_button.toggled()
        self.blue_mana_button.toggled()
        self.green_mana_button.toggled()
        self.black_mana_button.toggled()
        self.white_mana_button.toggled()
        self.colorless_mana_button.toggled()
        return

