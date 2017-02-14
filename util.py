import os
import gi

import config

gi.require_version('Gtk', '3.0')
from gi.repository import GdkPixbuf
from PIL import Image as PImage
from urllib import request

# Loacally stored images for faster loading times
imagecache = []


def reload_image_cache():
    if not os.path.exists(config.cachepath):
        os.makedirs(config.cachepath)

    # return array of images
    imageslist = os.listdir(config.cachepath)
    loadedimages = []
    for image in imageslist:
        img = PImage.open(config.cachepath + image)
        loadedimages.append(img)
    return loadedimages


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
            print("Using local file: " + filename)
            return GdkPixbuf.Pixbuf.new_from_file_at_size(image.filename, 63 * 2, 88 * 2)

    # No file in local cache found
    return load_card_image_online(card)
