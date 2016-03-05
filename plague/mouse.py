from pyg import pygame
from constants import *
import data

class Cursor(object):
    def __init__(self, name, dx, dy):
        self.image = data.load_image(name)
        self.dx = dx
        self.dy = dy

class Mouse (object):
    def init(self):
        self.cursors = {}
        self.cursors["default"] = Cursor("mouse.png", 0, 0)
        self.cursors["target"] = Cursor("target.png", -4, -4)

        self.default = self.cursors["default"]
        self.set_cursor("default")

    def set_cursor(self, name, max_y=SCREEN_H):
        self.cursor = self.cursors[name]
        self.max_y = max_y

    def draw(self, targ):
        mx, my = pygame.mouse.get_pos()
        rx = mx // SCALE_FACTOR
        ry = my // SCALE_FACTOR

        cursor = self.cursor if ry < self.max_y else self.default

        targ.blit(cursor.image, (rx + cursor.dx, ry + cursor.dy))

global_mouse = Mouse()

init = global_mouse.init
draw = global_mouse.draw
set_cursor = global_mouse.set_cursor
