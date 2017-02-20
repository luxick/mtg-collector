import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango
import util


class DetailBar(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(10)
        self.add(self.grid)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Create area for big card an fill it with a dummy image
        self.image_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.bigcard = Gtk.Image()
        pixbuf = util.load_dummy_image(63 * 5, 88 * 5)
        self.bigcard.set_from_pixbuf(pixbuf)
        self.image_area.add(self.bigcard)
        self.image_area.add(Gtk.HSeparator())

        # Build the additional info pane
        self.carddetails = Gtk.Grid()
        self.carddetails.set_row_spacing(5)
        self.carddetails.set_column_spacing(5)

        # Card rules
        self.rulingslabel = Gtk.Label(xalign=0, yalign=0)
        self.rulingslabel.set_markup("<big>Rules:</big>")
        self.rulingslabel.set_no_show_all(True)

        self.rulesstore = Gtk.ListStore(str, str)
        self.rulings = Gtk.TreeView(self.rulesstore)
        self.rulings.set_rules_hint(True)

        self.renderer = Gtk.CellRendererText(xalign=0, yalign=0)
        self.renderer.set_padding(5, 5)
        self.renderer.set_property("wrap-mode", Pango.WrapMode.WORD)
        # Ugly. Cannot set wrap width dynamically
        self.renderer.set_property("wrap-width", 220)

        self.date_column = Gtk.TreeViewColumn(title="Date", cell_renderer=self.renderer, text=0)
        self.rule_column = Gtk.TreeViewColumn(title="Rule", cell_renderer=self.renderer, text=1)
        self.date_column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.rule_column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        self.rule_column.set_expand(True)

        self.rulings.append_column(self.date_column)
        self.rulings.append_column(self.rule_column)

        # Build info pane under big card
        self.carddetails.attach(self.rulingslabel, 0, 0, 1, 1)
        self.carddetails.attach(self.rulings, 0, 1, 1, 1)

        self.grid.attach(self.image_area, 0, 0, 1, 1)
        self.grid.attach(self.carddetails, 0, 1, 1, 1)

    def update_big_card(self, card):
        pixbuf = util.load_card_image(card, 63 * 5, 88 * 5)
        self.bigcard.set_from_pixbuf(pixbuf)

    def reset(self):
        pixbuf = util.load_dummy_image(63 * 5, 88 * 5)
        self.bigcard.set_from_pixbuf(pixbuf)
        self.rulingslabel.set_visible(False)
        self.rulesstore.clear()

    def set_card_detail(self, card):
        print("Loading infos for \"" + card.name + "\"")

        self.update_big_card(card)
        self.rulesstore.clear()
        self.rulingslabel.set_visible(False)

        if card.rulings is not None:
            self.rulingslabel.set_visible(True)
            for rule in card.rulings:
                self.rulesstore.append([rule.get('date'), rule.get('text')])