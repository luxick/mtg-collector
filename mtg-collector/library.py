import os
import util
import details
import gi
from psutil._compat import xrange
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf


class LibraryView(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)
        self.set_column_spacing(5)

        # Dictionary to keep link IDs in Flowbox to IDs of Cards
        self.flowbox_ids = {}

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

        # The Small Card Flow
        self.cardScroller = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.cardScroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.cardFlow = Gtk.FlowBox()
        self.cardFlow.set_valign(Gtk.Align.START)
        self.cardFlow.set_max_children_per_line(50)
        self.cardFlow.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.cardFlow.connect("child-activated", self.card_clicked)
        self.cardScroller.add(self.cardFlow)

        # Detailed Card View
        self.details = details.DetailBar()

        left_pane = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_pane.pack_start(self.searchbox, False, False, 0)
        left_pane.pack_start(self.filterBox, False, False, 0)

        # Bring it all together
        self.attach(left_pane, 0, 0, 1, 1)
        self.attach(Gtk.VSeparator(), 1, 0, 1, 1)
        self.attach(self.cardScroller, 2, 0, 1, 1)
        self.attach(Gtk.VSeparator(), 3, 0, 1, 1)
        self.attach(self.details, 4, 0, 1, 1)

        self.fill_flowbox()

    def fill_flowbox(self):
        id_counter = 0
        for id, card in util.library.items():
            image = Gtk.Image()
            pixbuf = util.load_card_image(card, 63 * 2, 88 * 2)
            image.set_from_pixbuf(pixbuf)

            self.cardFlow.insert(image, id_counter)

            self.flowbox_ids[id_counter] = card.multiverse_id
            id_counter += 1

    def card_clicked(self, flowbox, flowboxchild):
        card_id = self.flowbox_ids[flowboxchild.get_index()]
        card = util.library[card_id]

        self.details.set_card_detail(card)


    def add_test_image(self):
        image = Gtk.Image()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.dirname(__file__) + '/resources/images/demo.jpg', 63*2, 88*2)
        image.set_from_pixbuf(pixbuf)

        return image

    def create_flowbox(self, flowbox):

        for nr in xrange(0, 50):
            image = self.add_test_image()
            flowbox.add(image)
