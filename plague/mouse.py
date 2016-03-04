from pyg import pygame
from constants import *
import data

cursor = None
cursors = {}
class Cursor(object):
    def __init__(self, name, dx, dy):
        self.image = data.load_image(name)
        self.dx = dx
        self.dy = dy

def init():
    global cursor
    cursors["default"] = Cursor("mouse.png", 0, 0)
    cursors["target"] = Cursor("target.png", -4, -4)
    set_cursor("default")

def set_cursor(name):
    global cursor
    cursor = cursors[name]

def draw(targ):
    mx, my = pygame.mouse.get_pos()
    rx = mx // SCALE_FACTOR
    ry = my // SCALE_FACTOR
    targ.blit(cursor.image, (rx + cursor.dx, ry + cursor.dy))
