import gi
import collection
import search

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MTG Collector (working title) v0.1")
        self.set_border_width(2)
        self.set_size_request(1000, 700)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

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
win.show_all()
Gtk.main()
