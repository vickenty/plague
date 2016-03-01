import os
import sys
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

if data_dir is None:
    print "Sorry, can't find game data. Please run it from the directory where run_game.py is located."
    sys.exit(1)

def get_path(name):
    return os.path.join(data_dir, name)

@contextmanager
def open(name):
    with file(get_path(name)) as f:
        yield f

def load_image(name):
    return pygame.image.load(get_path(name)).convert_alpha()
