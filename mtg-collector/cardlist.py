import gi
import util

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Pango


class CardList(Gtk.ScrolledWindow):
    def __init__(self, with_filter):
        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_hexpand(True)
        self.set_vexpand(True)

        # Columns are these:
        # 0 Multiverse ID
        # 1 Card Name
        # 2 Card Supertypes (Legendary,..)
        # 3 Card types (Creature, etc)
        # 4 Rarity
        # 5 Power
        # 6 Toughness
        # 7 Printings (Sets with this card in it)
        # 8 Mana Cost(Form: {G}{2})
        # 9 CMC
        # 10 Edition
        self.store = Gtk.ListStore(int, str, str, str, str, str, str, str, GdkPixbuf.Pixbuf, int, str)
        if with_filter:
            self.filter = self.store.filter_new()
            self.filter_and_sort = Gtk.TreeModelSort(self.filter)
            self.filter_and_sort.set_sort_func(4, self.compare_rarity, None)
            self.list = Gtk.TreeView(self.filter_and_sort)
        else:
            self.store.set_sort_func(4, self.compare_rarity, None)
            self.list = Gtk.TreeView(self.store)
        self.add(self.list)

        self.list.set_rules_hint(True)
        self.selection = self.list.get_selection()



        bold_renderer = Gtk.CellRendererText(xalign=0.5, yalign=0.5)
        bold_renderer.set_property("weight", 800)

        text_renderer = Gtk.CellRendererText(xalign=0.5, yalign=0.5)
        text_renderer.set_property("weight", 500)
        image_renderer = Gtk.CellRendererPixbuf()

        col_id = Gtk.TreeViewColumn(title="Multiverse ID", cell_renderer=text_renderer, text=0)
        col_id.set_visible(False)

        col_title = Gtk.TreeViewColumn(title="Name", cell_renderer=bold_renderer, text=1)
        col_title.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col_title.set_expand(True)
        col_title.set_sort_column_id(1)

        col_supertypes = Gtk.TreeViewColumn(title="Supertypes", cell_renderer=text_renderer, text=2)
        col_supertypes.set_sort_column_id(2)
        col_supertypes.set_visible(False)

        col_types = Gtk.TreeViewColumn(title="Types", cell_renderer=text_renderer, text=3)
        col_types.set_sort_column_id(3)

        col_rarity = Gtk.TreeViewColumn(title="Rarity", cell_renderer=text_renderer, text=4)
        col_rarity.set_sort_column_id(4)

        col_power = Gtk.TreeViewColumn(title="Power", cell_renderer=text_renderer, text=5)
        col_power.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_power.set_fixed_width(50)
        col_power.set_sort_column_id(5)
        col_power.set_visible(False)

        col_thoughness = Gtk.TreeViewColumn(title="Toughness", cell_renderer=text_renderer, text=6)
        col_thoughness.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        col_thoughness.set_fixed_width(50)
        col_thoughness.set_sort_column_id(6)
        col_thoughness.set_visible(False)

        col_printings = Gtk.TreeViewColumn(title="Printings", cell_renderer=text_renderer, text=7)
        col_printings.set_sort_column_id(7)
        col_printings.set_visible(False)

        col_mana = Gtk.TreeViewColumn(title="Mana Cost", cell_renderer=image_renderer, pixbuf=8)
        col_mana.set_expand(False)
        col_mana.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        col_mana.set_sort_column_id(9)

        col_cmc = Gtk.TreeViewColumn(title="CMC", cell_renderer=text_renderer, text=9)
        col_cmc.set_visible(False)

        col_set_name = Gtk.TreeViewColumn(title="Edition", cell_renderer=text_renderer, text=10)
        col_set_name.set_expand(False)
        col_set_name.set_sort_column_id(10)

        self.list.append_column(col_id)
        self.list.append_column(col_title)
        self.list.append_column(col_supertypes)
        self.list.append_column(col_types)
        self.list.append_column(col_rarity)
        self.list.append_column(col_set_name)
        self.list.append_column(col_power)
        self.list.append_column(col_thoughness)
        self.list.append_column(col_printings)
        self.list.append_column(col_mana)
        self.list.append_column(col_cmc)

    def compare_rarity(self, model, row1, row2, user_data):
        # Column for rarity
        sort_column = 4
        value1 = model.get_value(row1, sort_column)
        value2 = model.get_value(row2, sort_column)
        if util.rarity_dict[value1.lower()] < util.rarity_dict[value2.lower()]:
            return -1
        elif value1 == value2:
            return 0
        else:
            return 1


