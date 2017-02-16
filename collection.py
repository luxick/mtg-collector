import gi
from psutil._compat import xrange

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


class CollectionView(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)

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

        # The Small Card Flow
        self.cardScroller = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.cardScroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.cardFlow = Gtk.FlowBox()
        self.cardFlow.set_valign(Gtk.Align.START)
        self.cardFlow.set_max_children_per_line(50)
        self.cardFlow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.create_flowbox(self.cardFlow)
        self.cardScroller.add(self.cardFlow)

        # Detailed Card View
        self.detailBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

        # Big Picture of the selected Card
        self.image_area = Gtk.Box()
        self.bigCard = Gtk.Image()
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('./resources/images/demo.jpg', 63 * 4, 88 * 4)
        self.bigCard.set_from_pixbuf(self.pixbuf)
        self.image_area.add(self.bigCard)
        self.detailBox.add(self.image_area)

        # Sta-ts and Details about the selected Card
        self.stat_listbox = Gtk.ListBox()
        self.stat_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.test_statrow = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        hbox.add(Gtk.Label("Detail about the selected Card goes here", xalign=0))
        self.test_statrow.add(hbox)
        self.stat_listbox.add(self.test_statrow)

        self.detailBox.add(self.stat_listbox)


        # Bring it all together
        self.attach(self.searchbox, 0, 0, 1, 1)
        self.attach(self.filterBox, 0, 1, 1, 1)
        self.attach(self.cardScroller, 1, 0, 1, 2)
        self.attach(self.detailBox, 2, 0, 1, 2)

    def add_test_image(self):
        image = Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size('./resources/images/demo.jpg', 63*2, 88*2)
        image.set_from_pixbuf(pixbuf)

        return image

    def create_flowbox(self, flowbox):

        for nr in xrange(0, 50):
            image = self.add_test_image()
            flowbox.add(image)
