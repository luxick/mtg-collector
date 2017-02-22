import gi
import collection
import search
import config
import util
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=config.applicationtitle)
        self.set_border_width(2)
        self.set_size_request(1000, 700)

        # Load local image Data
        util.reload_image_cache()
        util.load_mana_icons()
        # Set reference to main window in util
        util.window = self

        util.load_sets()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)
        self.notebook = Gtk.Notebook()

        vbox.pack_start(self.notebook, True, True, 0)
        self.status_bar = Gtk.Statusbar()
        self.status_bar.set_no_show_all(True)
        vbox.pack_start(self.status_bar, False, False, 0)

        # Set reference to status bar in util
        util.status_bar = self.status_bar
        util.push_status("Application started")

        self.collectionView = Gtk.Box()
        self.collectionView.add(collection.CollectionView())

        self.searchView = Gtk.Box()
        self.searchView.add(search.SearchView())

        self.deckView = Gtk.Box()
        self.deckView.add(Gtk.Label("View and organize your Decklists!"))



        self.notebook.append_page(self.searchView, Gtk.Label("Search"))
        self.notebook.append_page(self.collectionView, Gtk.Label("Collection"))
        self.notebook.append_page(self.deckView, Gtk.Label("Decks"))

win = MainWindow()
win.connect('delete-event', Gtk.main_quit)
GObject.threads_init()
win.show_all()
Gtk.main()
