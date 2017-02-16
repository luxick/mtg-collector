import gi
from gi.repository import Pango
import util
import details
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from mtgsdk import Card


class SearchView(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)

        # Search Box
        self.searchbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.searchEntry = Gtk.Entry()
        self.searchEntry.connect("activate", self.online_search_clicked)
        self.searchbutton = Gtk.Button("Search Online")
        self.searchbutton.connect("clicked", self.online_search_clicked)
        self.searchEntryLabel = Gtk.Label("Search for Cards:", xalign=0)
        self.searchbox.add(self.searchEntryLabel)
        self.searchbox.add(self.searchEntry)
        self.searchbox.add(self.searchbutton)

        # Filters
        self.filterBox = Gtk.ListBox()
        self.filterBox.set_selection_mode(Gtk.SelectionMode.NONE)

        self.testRow = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        hbox.add(Gtk.Label("Filters will go here", xalign=0))
        self.testRow.add(hbox)

        self.filterBox.add(self.testRow)


        #Card List
        self.searchresults = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.searchresults.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.store = Gtk.ListStore(int, GdkPixbuf.Pixbuf, str, str, GdkPixbuf.Pixbuf)
        self.list = Gtk.TreeView(self.store)
        self.list.set_rules_hint(True)
        self.searchresults.add(self.list)

        image = Gtk.CellRendererPixbuf()

        title = Gtk.CellRendererText(xalign=0.5)
        title.set_padding = 2

        info = Gtk.CellRendererText()
        info.set_property("wrap-mode", Pango.WrapMode.WORD)
        info.set_property("wrap-width", 100)
        info.set_padding = 2

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
        self.details = Gtk.Box()
        self.details.add(details.DetailBar())

        # Bring it all together
        self.attach(self.searchbox, 0, 0, 1, 1)
        self.attach(self.filterBox, 0, 1, 1, 1)
        self.attach(self.searchresults, 1, 0, 1, 2)
        self.attach(self.details, 2, 0, 1, 2)

        self.selection = self.list.get_selection()
        self.selection.connect("changed", self.on_card_selected)

    def online_search_clicked(self, button):
        term = self.searchEntry.get_text()
        if not term == "":
            print("Search for \"" + term + "\" online. \n")

            self.cards = Card.where(name=term).where(pageSize=50).where(page=1).all()
            self.store.clear()
            for card in self.cards:
                if card.multiverse_id is not None:
                    print("Found: " + card.name
                         + " (" + card.multiverse_id.__str__() + ")")

                    self.store.append([card.multiverse_id,
                                       util.load_card_image(card, 63 * 2, 88 * 2),
                                       card.name,
                                       card.original_text,
                                       util.create_mana_icons(card.mana_cost)])
                    print("\n")
            util.reload_image_cache()

    def on_card_selected(self, selection):
        (model, pathlist) = selection.get_selected_rows()
        for path in pathlist:
            iter = model.get_iter(path)
            card_id = model.get_value(iter, 0)

            selected_card = None
            for card in self.cards:
                if card.multiverse_id == card_id:
                    selected_card = card

            print(selected_card.name + " selected \n")




