import gi
from gi.repository import Pango
import util
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from mtgsdk import Card


class SearchView(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)

        # Search Box
        self.searchbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.searchEntry = Gtk.Entry()
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

        self.store = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
        self.list = Gtk.TreeView(self.store)
        self.searchresults.add(self.list)

        image = Gtk.CellRendererPixbuf()

        title = Gtk.CellRendererText(xalign=0.5)
        title.set_padding = 2

        info = Gtk.CellRendererText()
        info.set_property("wrap-mode", Pango.WrapMode.WORD)
        info.set_property("wrap-width", 100)
        info.set_padding = 2

        self.column1 = Gtk.TreeViewColumn(title="Image", cell_renderer=image, pixbuf=0)
        self.column2 = Gtk.TreeViewColumn(title="Card Name", cell_renderer=title, text=1)
        self.column3 = Gtk.TreeViewColumn(title="Card Text", cell_renderer=info, text=2)
        self.column3.set_max_width(100)

        self.column1.pack_start(image, True)
        self.column2.pack_start(title, True)
        self.column3.pack_start(info, True)

        self.list.append_column(self.column1)
        self.list.append_column(self.column2)
        self.list.append_column(self.column3)

        # Bring it all together
        self.attach(self.searchbox, 0, 0, 1, 1)
        self.attach(self.filterBox, 0, 1, 1, 1)
        self.attach(self.searchresults, 1, 0, 1, 2)

    def online_search_clicked(self, button):
        term = self.searchEntry.get_text()
        if not term == "":
            print("Search for \"" + term + "\" online.")

            cards = Card.where(name=term).all()
            self.store.clear()
            for card in cards:
                if card.multiverse_id is not None:
                    print("Found ID: " + card.multiverse_id.__str__() + " | " + card.name)
                    self.store.append([util.load_card_image(card),
                                   card.name,
                                   card.original_text])
            util.reload_image_cache()




