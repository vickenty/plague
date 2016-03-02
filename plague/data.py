import os
import sys
import json
import pygame
from contextlib import contextmanager

this_dir = os.path.abspath(os.path.dirname(__file__))
data_dirs = [
    "data",
    os.path.join(this_dir, "..", "data"),
]

data_dir = None
for path in data_dirs:
    try:
        with open(os.path.join(path, "plague.magic")):
            data_dir = path
            break
    except IOError:
        pass

image_cache = {}

if data_dir is None:
    print "Sorry, can't find game data. Please run it from the directory where run_game.py is located."
    sys.exit(1)

def get_path(name):
    return os.path.join(data_dir, name)

@contextmanager
def open(name):
    with file(get_path(name)) as f:
        yield f

def load_json(name):
    with open(name) as f:
        return json.load(f)

def load_image(name):
    path = get_path(name)
    if path in image_cache:
        return image_cache[path]
    img = pygame.image.load(path).convert_alpha()
    image_cache[path] = img
    return img
