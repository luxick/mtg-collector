import os
import gi
import re
import config
gi.require_version('Gtk', '3.0')
from gi.repository import GdkPixbuf
from PIL import Image as PImage
from urllib import request

# Loacally stored images for faster loading times
imagecache = []
manaicons ={}


def load_mana_icons():
    path = "resources/mana_icons/"
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
        img = PImage.open(config.cachepath + image)
        imagecache.append(img)


def add_test_image():
    return GdkPixbuf.Pixbuf.new_from_file_at_size('./resources/images/demo.jpg', 63 * 2, 88 * 2)


def load_card_image_online(card):
    url = card.image_url
    if url is None:
        print("No Image URL provided")
        return add_test_image()
    filename = ".cache/" + card.multiverse_id.__str__() + ".PNG"
    print("Loading image from: " + url)
    response = request.urlretrieve(url, filename)
    return GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 63 * 2, 88 * 2)


def load_card_image(card):
    # Try loading from disk, if file exists
    for image in imagecache:
        filename = os.path.basename(image.filename)
        if filename == card.multiverse_id.__str__() + ".PNG":
            print("Using local file for image: " + filename)
            return GdkPixbuf.Pixbuf.new_from_file_at_size(image.filename, 63 * 2, 88 * 2)

    # No file in local cache found
    return load_card_image_online(card)


def create_mana_icons(mana_string):
    # Convert the string to a List
    list = re.findall("\{(.*?)\}", mana_string)
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
