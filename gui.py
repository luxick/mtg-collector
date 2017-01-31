import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="MTG Collector v0.1")
        self.set_border_width(2)

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        self.collectionView = Gtk.Box()
        self.collectionView.add(Gtk.Label("My Magic Card Collection!"))

        self.searchView = Gtk.Box()
        self.searchView.add(Gtk.Label("Search the whole Magic Card Library!"))

        self.deckView = Gtk.Box()
        self.deckView.add(Gtk.Label("View and organize your Decklists!"))


        self.notebook.append_page(self.collectionView, Gtk.Label("Collection"))
        self.notebook.append_page(self.deckView, Gtk.Label("Decks"))
        self.notebook.append_page(self.searchView, Gtk.Label("Search"))


win = MainWindow()
win.connect('delete-event', Gtk.main_quit)
win.show_all()
Gtk.main()
