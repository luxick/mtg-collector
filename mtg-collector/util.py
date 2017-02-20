import os
import gi
import re
import config
gi.require_version('Gtk', '3.0')
from gi.repository import GdkPixbuf, Gtk
from PIL import Image as PImage
from urllib import request

# Loacally stored images for faster loading times
imagecache = []
manaicons ={}
window = None
status_bar = None


def push_status(msg):
    status_bar.push(0, msg)


def show_message(title, message):
    dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.INFO,
                               Gtk.ButtonsType.OK, title)
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()


def load_mana_icons():
    path = os.path.dirname(__file__) + "/resources/mana_icons/"
    if not os.path.exists(path):
        print("ERROR: Directory for mana icons not found")
        return
    # return array of icons
    imagelist = os.listdir(path)
    manaicons.clear()
    for image in imagelist:
        img = PImage.open(path + image)
        manaicons[os.path.splitext(image)[0]] = img


def reload_image_cache():
    if not os.path.exists(config.cachepath):
        os.makedirs(config.cachepath)

    # return array of images
    imageslist = os.listdir(config.cachepath)
    imagecache.clear()
    for image in imageslist:
        try:
            img = PImage.open(config.cachepath + image)
            imagecache.append(img)
        except OSError as err:
            print("Error loading image: " + str(err))


def load_dummy_image(sizex, sizey):
    return GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.dirname(__file__) +
                                                  '/resources/images/dummy.jpg', sizex, sizey)

def load_card_image_online(card, sizex, sizey):
    url = card.image_url
    if url is None:
        print("No Image URL provided")
        return load_dummy_image(sizex, sizey)
    filename = config.cachepath + card.multiverse_id.__str__() + ".PNG"
    print("Loading image from: " + url)
    response = request.urlretrieve(url, filename)
    return GdkPixbuf.Pixbuf.new_from_file_at_size(filename, sizex, sizey)


def load_card_image(card, sizex, sizey):
    # Try loading from disk, if file exists
    for image in imagecache:
        filename = os.path.basename(image.filename)
        if filename == card.multiverse_id.__str__() + ".PNG":
            return GdkPixbuf.Pixbuf.new_from_file_at_size(image.filename, sizex, sizey)

    # No file in local cache found
    return load_card_image_online(card, sizex, sizey)


def create_mana_icons(mana_string):
    # Convert the string to a List
    list = re.findall("\{(.*?)\}", str(mana_string))
    if len(list) == 0:
        return
    # Compute horizontal size for the final image
    imagesize = len(list) * 105
    image = PImage.new("RGBA", (imagesize, 105))
    # incerment for each position of an icon (Workaround: 2 or more of the same icon will be rendered in the same poisition)
    poscounter = 0
    # Go through all entries an add the correspondent icon to the final image
    for icon in list:
        xpos = poscounter * 105
        loaded = manaicons.get(icon)
        if loaded is None:
            print("ERROR: No icon file named \"" + icon + "\" found.")
        else:
            image.paste(loaded, (xpos, 0))
        poscounter += 1

    image.save(config.cachepath + "manaicon.png", "PNG")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(config.cachepath + "manaicon.png")
    pixbuf = pixbuf.scale_simple(image.width / 5, image.height / 5, GdkPixbuf.InterpType.HYPER)
    os.remove(config.cachepath + "manaicon.png")
    return pixbuf
