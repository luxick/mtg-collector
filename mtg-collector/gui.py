import gi
import library
import search
import config
import util
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject


class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title=config.application_title)
        self.set_border_width(2)
        self.set_size_request(1000, 700)

        self.status_bar = Gtk.Statusbar()
        self.status_bar.set_no_show_all(True)

        # Set reference to status bar in util
        util.status_bar = self.status_bar
        util.push_status("Application started")

        # Load local image Data
        util.reload_image_cache()
        util.load_mana_icons()
        # Set reference to main window in util
        util.window = self

        util.load_sets()
        util.load_library()

        self.notebook = Gtk.Notebook()

        # region Menu Bar

        mb_main = Gtk.Menu()
        mb_lib = Gtk.Menu()

        self.menu_import = Gtk.MenuItem("Import Library")
        self.menu_export = Gtk.MenuItem("Export Library")
        self.menu_quit = Gtk.ImageMenuItem('Quit', Gtk.Image.new_from_icon_name(Gtk.STOCK_QUIT, 0))
        self.menu_quit.connect("activate", Gtk.main_quit)

        self.lib_save = Gtk.ImageMenuItem("Save", Gtk.Image.new_from_icon_name(Gtk.STOCK_SAVE, 0))
        self.lib_save.connect("activate", self.mb_save_lib)
        self.lib_debug_print = Gtk.MenuItem("DEBUG: Print Library")
        self.lib_debug_print.connect("activate", util.print_lib)

        mb_main.append(self.menu_import)
        mb_main.append(self.menu_export)
        mb_main.append(Gtk.SeparatorMenuItem())
        mb_main.append(self.menu_quit)

        mb_lib.append(self.lib_save)
        mb_lib.append(self.lib_debug_print)

        root_menu_main = Gtk.MenuItem("Main")
        root_menu_main.set_submenu(mb_main)

        root_menu_lib = Gtk.MenuItem("Library")
        root_menu_lib.set_submenu(mb_lib)

        mb = Gtk.MenuBar()
        mb.append(root_menu_main)
        mb.append(root_menu_lib)

        # endregion

        # region Accelerators

        accelgrp = Gtk.AccelGroup()

        key, mod = Gtk.accelerator_parse("<Control>Q")
        self.menu_quit.add_accelerator("activate", accelgrp, key, mod, Gtk.AccelFlags.VISIBLE)
        key, mod = Gtk.accelerator_parse("<Control>S")
        self.lib_save.add_accelerator("activate", accelgrp, key, mod, Gtk.AccelFlags.VISIBLE)

        self.add_accel_group(accelgrp)

        # endregion

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(mb, False, False, 0)
        vbox.pack_start(self.notebook, True, True, 0)
        vbox.pack_start(self.status_bar, False, False, 0)

        self.library = Gtk.Box()
        self.library.add(library.LibraryView())

        self.search = Gtk.Box()
        self.search.add(search.SearchView())

        self.decks = Gtk.Box()
        self.decks.add(Gtk.Label("View and organize your Decklists!"))

        self.notebook.append_page(self.search, Gtk.Label("Search"))
        self.notebook.append_page(self.library, Gtk.Label("Library"))
        self.notebook.append_page(self.decks, Gtk.Label("Decks"))

        self.add(vbox)

    def mb_save_lib(self, menu_item):
        util.save_library()

win = MainWindow()
win.connect('delete-event', Gtk.main_quit)
GObject.threads_init()
win.show_all()
Gtk.main()
