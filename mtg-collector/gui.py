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
        self.status_bar.set_no_show_all(False)

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

        # region Menu Bar

        mb_main = Gtk.Menu()
        mb_view = Gtk.Menu()
        mb_search = Gtk.Menu()
        mb_lib = Gtk.Menu()

        root_main = Gtk.MenuItem("Main")
        root_main.set_submenu(mb_main)

        root_view = Gtk.MenuItem("View")
        root_view.set_submenu(mb_view)

        root_search = Gtk.MenuItem("Search")
        root_search.set_submenu(mb_search)

        root_lib = Gtk.MenuItem("Library")
        root_lib.set_submenu(mb_lib)

        self.main_import = Gtk.MenuItem("Import Library")
        self.main_import.connect("activate", self.mb_import_lib)
        self.main_export = Gtk.MenuItem("Export Library")
        self.main_export.connect("activate", self.mb_export_lib)
        self.main_quit = Gtk.ImageMenuItem('Quit', Gtk.Image.new_from_icon_name(Gtk.STOCK_QUIT, 0))
        self.main_quit.connect("activate", Gtk.main_quit)

        self.view_search = Gtk.MenuItem(name="search", label="Search")
        self.view_search.connect("activate", self.mb_view_switch)
        self.view_library = Gtk.MenuItem(name="library", label="Library")
        self.view_library.connect("activate", self.mb_view_switch)

        self.search_add = Gtk.MenuItem("Add card")
        self.search_add.connect("activate", self.mb_search_add_card)
        self.search_add.set_sensitive(False)
        self.search_show_all = Gtk.CheckMenuItem("Show from all Sets")
        self.search_show_all.connect("toggled", self.mb_search_show_all)
        self.search_show_all.set_active(config.show_from_all_sets)

        self.lib_save = Gtk.ImageMenuItem("Save", Gtk.Image.new_from_icon_name(Gtk.STOCK_SAVE, 0))
        self.lib_save.connect("activate", self.mb_save_lib)

        mb_main.append(self.main_import)
        mb_main.append(self.main_export)
        mb_main.append(Gtk.SeparatorMenuItem())
        mb_main.append(self.main_quit)

        mb_view.append(self.view_search)
        mb_view.append(self.view_library)

        mb_search.append(self.search_add)
        mb_search.append(self.search_show_all)

        mb_lib.append(self.lib_save)

        mb = Gtk.MenuBar()
        mb.append(root_main)
        mb.append(root_view)
        mb.append(root_search)
        mb.append(root_lib)

        # endregion

        # region Accelerators

        accelgrp = Gtk.AccelGroup()

        key, mod = Gtk.accelerator_parse("<Control>Q")
        self.main_quit.add_accelerator("activate", accelgrp, key, mod, Gtk.AccelFlags.VISIBLE)
        key, mod = Gtk.accelerator_parse("<Control>1")
        self.view_search.add_accelerator("activate", accelgrp, key, mod, Gtk.AccelFlags.VISIBLE)
        key, mod = Gtk.accelerator_parse("<Control>2")
        self.view_library.add_accelerator("activate", accelgrp, key, mod, Gtk.AccelFlags.VISIBLE)
        key, mod = Gtk.accelerator_parse("<Control>S")
        self.lib_save.add_accelerator("activate", accelgrp, key, mod, Gtk.AccelFlags.VISIBLE)
        key, mod = Gtk.accelerator_parse("<Control>A")
        self.search_add.add_accelerator("activate", accelgrp, key, mod, Gtk.AccelFlags.VISIBLE)

        self.add_accel_group(accelgrp)

        # endregion

        self.views = {
            "library": library.LibraryView(),
            "search": search.SearchView()
        }

        self.view_buttons = {
            "library": self.view_library,
            "search": self.view_search
        }

        self.view = self.views[config.start_view]
        self.view_buttons[config.start_view].set_sensitive(False)

        self.view_container = Gtk.Box()
        self.view_container.set_border_width(2)
        self.view_container.add(self.view)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.vbox.pack_start(mb, False, False, 0)
        self.vbox.pack_start(Gtk.HSeparator(), False, False, 0)
        self.vbox.pack_start(self.view_container, True, True, 0)
        self.vbox.pack_end(self.status_bar, False, False, 0)

        self.add(self.vbox)

    def switch_view(self, view):
        self.view_container.remove(self.view)
        self.view = view
        self.view_container.add(view)
        self.view_container.show_all()

    def mb_view_switch(self, menu_item):
        new_view = self.views[menu_item.get_name()]
        self.switch_view(new_view)
        for item in self.view_buttons.values():
            item.set_sensitive(True)
        menu_item.set_sensitive(False)
        self.view.reload()

    @staticmethod
    def mb_export_lib(menu_item):
        util.export_library()

    def mb_import_lib(self, menu_item):
        util.import_library()
        self.view.reload()

    def mb_search_add_card(self, menu_item):
        self.search.on_add_delete(self.search.add_delete_button)

    @staticmethod
    def mb_search_show_all(menu_item):
        config.show_from_all_sets = menu_item.get_active()

    @staticmethod
    def mb_save_lib(menu_item):
        util.save_library()

    @staticmethod
    def do_delete_event(event):
        if util.unsaved_changes:
            response = util.show_question_dialog("Unsaved Changes", "You have unsaved changes in your library. "
                                                                    "Save before exiting?")
            if response == Gtk.ResponseType.YES:
                util.save_library()


win = MainWindow()
win.connect('delete-event', Gtk.main_quit)
GObject.threads_init()
win.show_all()
Gtk.main()
