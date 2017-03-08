import os
import pickle
import gi
import re
import config
import network

from gi.repository import GdkPixbuf, Gtk
from PIL import Image as PImage
from urllib import request
from mtgsdk import Card
gi.require_version('Gtk', '3.0')

# Locally stored images for faster loading times
imagecache = []
manaicons = {}

#Card library object
library = {}

set_list = []

window = None
status_bar = None


def add_card_to_lib(card):
    library[card.multiverse_id] = card


def remove_card_from_lib(card):
    del library[card.multiverse_id]


def print_lib(menuItem):
    print("Printing library:\n")
    counter = 1
    for card_id, card in library.items():
        print(str(counter) + ": " + card.name + " (" + str(card_id) + ")")
        counter += 1
    print("\nDone.")


def save_library():
    if not os.path.exists(config.cache_path):
        os.makedirs(config.cache_path)
    path = config.cache_path + "library"
    # Serialize library object using pickle
    try:
        pickle.dump(library, open(path, 'wb'))
        push_status("Library saved.")
        print("Library saved")
    except:
        show_message("Error", "Error while saving library to disk")


def load_library():
    path = config.cache_path + "library"
    library.clear()
    if os.path.isfile(path):
        # Deserialize using pickle
        try:
            library_loaded = pickle.load(open(path, 'rb'))
            for id, card in library_loaded.items():
                library[id] = card
            push_status("Library loaded.")
        except :
            show_message("Error", "Error while loading library from disk")
    else:
        save_library()
        print("No library file found on disk, created new one")


def load_sets():
    path = config.cache_path + "sets"
    if not os.path.isfile(path):
        # use mtgsdk api to retrieve al list of all sets
        new_sets = network.net_load_sets()
        if new_sets == "":
            show_message("API Error", "Could not retrieve Set infos")
            return
        # Serialize the loaded data to a file
        pickle.dump(new_sets, open(path, 'wb'))
    # Deserialize set data from local file
    sets = pickle.load(open(path, 'rb'))
    # Sort the loaded sets based on the sets name
    for set in sorted(sets, key=lambda x: x.name):
        set_list.append(set)


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
    if not os.path.exists(config.image_cache_path):
        os.makedirs(config.image_cache_path)

    # return array of images
    imageslist = os.listdir(config.image_cache_path)
    imagecache.clear()
    for image in imageslist:
        try:
            img = PImage.open(config.image_cache_path + image)
            imagecache.append(img)
        except OSError as err:
            print("Error loading image: " + str(err))


def load_dummy_image(sizex, sizey):
    return GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.dirname(__file__)
                                                  + '/resources/images/dummy.jpg', sizex, sizey)


def load_card_image_online(card, sizex, sizey):
    url = card.image_url
    if url is None:
        print("No Image URL provided")
        return load_dummy_image(sizex, sizey)
    filename = config.image_cache_path + card.multiverse_id.__str__() + ".PNG"
    print("Loading image for " + card.name +  "from: " + url)
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

    image.save(config.cache_path + "manaicon.png", "PNG")
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(config.cache_path + "manaicon.png")
    pixbuf = pixbuf.scale_simple(image.width / 5, image.height / 5, GdkPixbuf.InterpType.HYPER)
    os.remove(config.cache_path + "manaicon.png")
    return pixbuf
