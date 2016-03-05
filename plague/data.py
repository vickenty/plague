import os
import sys
import json
from pyg import pygame
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


def memoize(fn):
    cache = {}
    def inner(*args):
        try:
            val = cache[args]
        except KeyError:
            val = fn(*args)
            cache[args] = val
        return val
    return inner

@memoize
def load_image(name):
    path = get_path(name)
    return pygame.image.load(path)

@memoize
def load_font(name, size):
    path = get_path(name)
    return pygame.font.Font(path, size)

@memoize
def load_sample(name):
    path = get_path(name)
    return pygame.mixer.Sound(path)
