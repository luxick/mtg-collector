import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
import util


class DetailBar(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)

        self.image_area = Gtk.Box()
        image = Gtk.Image()
        pixbuf = util.add_test_image(63 * 5, 88 * 5)
        image.set_from_pixbuf(pixbuf)
        self.image_area.add(image)

        self.carddetails = Gtk.ListBox()
        self.carddetails.set_selection_mode(Gtk.SelectionMode.NONE)

        self.rulings = Gtk.ListBoxRow()
        self.rulings.add(Gtk.Label("Test"))

        self.carddetails.add(self.rulings)

        self.attach(self.image_area, 0, 0, 1, 1)
        self.attach(self.carddetails, 0, 1, 1, 1)
