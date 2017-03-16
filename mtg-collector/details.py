import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, GObject
import util


class DetailBar(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.current_card = None

        self.add(self.box)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_no_show_all(True)

        # Create area for big card
        self.image_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.bigcard = Gtk.Image()
        pixbuf = util.load_dummy_image(63 * 5, 88 * 5)
        self.bigcard.set_from_pixbuf(pixbuf)
        self.load_spinner = Gtk.Spinner()
        self.load_spinner.set_visible(False)
        self.load_label = Gtk.Label("Loading image")
        self.image_area.pack_start(self.bigcard, True, True, 2)
        self.image_area.pack_start(self.load_spinner, True, True, 50)
        self.image_area.pack_start(self.load_label, False, False, 0)

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

        self.box.pack_start(self.image_area, False, False, 0)
        self.box.pack_start(self.carddetails, False, False, 10)

        self._init_sub_containers()

    def _init_sub_containers(self):
        self.box.set_visible(True)
        self.bigcard.set_visible(True)
        self.image_area.set_visible(True)
        self.carddetails.set_visible(True)
        self.rulings.set_visible(True)
        self.rulingslabel.set_visible(True)

    def set_load_animation(self, state):
        self.bigcard.set_visible(not state)
        self.load_spinner.set_visible(state)
        self.load_label.set_visible(state)

        if state:
            self.load_spinner.start()
        else:
            self.load_spinner.stop()

    def update_big_card(self, card):
        GObject.idle_add(self.set_load_animation, True, priorty = GObject.PRIORITY_DEFAULT)

        pixbuf = util.load_card_image(card, 63 * 5, 88 * 5)
        if not self.current_card is card:
            return

        GObject.idle_add(self.bigcard.set_from_pixbuf, pixbuf, priorty=GObject.PRIORITY_DEFAULT)
        GObject.idle_add(self.set_load_animation, False, priorty=GObject.PRIORITY_DEFAULT)

    def reset(self):
        self.current_card = None
        pixbuf = util.load_dummy_image(63 * 5, 88 * 5)
        self.bigcard.set_from_pixbuf(pixbuf)
        self.rulingslabel.set_visible(False)
        self.rulesstore.clear()
        self.set_visible(False)

    def set_card_detail(self, card):
        self.current_card = card
        load_thread = threading.Thread(target=self.update_big_card, args=(card,))
        load_thread.setDaemon(True)
        load_thread.start()

        self.rulesstore.clear()
        self.rulingslabel.set_visible(False)
        self.set_visible(True)

        if card.rulings is not None:
            self.rulingslabel.set_visible(True)
            for rule in card.rulings:
                self.rulesstore.append([rule.get('date'), rule.get('text')])

