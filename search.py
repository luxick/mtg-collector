import gi
from psutil._compat import xrange

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


class SearchView(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)

        # Search Box
        self.searchbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.searchEntry = Gtk.Entry()
        self.searchEntryLabel = Gtk.Label("Search for Cards:", xalign=0)
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


        #Card List
        self.searchresults = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.searchresults.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.store = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
        self.list = Gtk.TreeView(self.store)
        self.searchresults.add(self.list)

        image = Gtk.CellRendererPixbuf()
        name = Gtk.CellRendererText()
        info = Gtk.CellRendererText()
        self.column1 = Gtk.TreeViewColumn(title="Image", cell_renderer=image, pixbuf=0)
        self.column2 = Gtk.TreeViewColumn(title="Card Name", cell_renderer=name, text=1)
        self.column3 = Gtk.TreeViewColumn(title="Additional Info", cell_renderer=info, text=2)
        self.column1.pack_start(image, True)
        self.column2.pack_start(name, True)
        self.column3.pack_start(info, True)

        self.list.append_column(self.column1)
        self.list.append_column(self.column2)
        self.list.append_column(self.column3)

        self.fill_test_data(self.store)

        # Bring it all together
        self.attach(self.searchbox, 0, 0, 1, 1)
        self.attach(self.filterBox, 0, 1, 1, 1)
        self.attach(self.searchresults, 1, 0, 1, 2)

    def fill_test_data(self, treestore):
        for nr in xrange(0, 100):
            treestore.append([self.add_test_image(), "Card Title", "More Info..."])

    def add_test_image(self):
        return GdkPixbuf.Pixbuf.new_from_file_at_size('./resources/images/demo.jpg', 63*2, 88*2)
