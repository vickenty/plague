from __future__ import division
from pyg import pygame
import data
from constants import *

class ButtonRegistry(object):
    def __init__(self):
        self.buttons = []

        self.font = data.load_font(*UI_FONT)

        self.pending_button = None

    def set_pending_button(self, b):
        b.toggle_state()
        self.pending_button = b

    def unset_pending_button(self):
        if self.pending_button:
            self.pending_button.toggle_state()
            self.pending_button = None

    def add_button(self, *args):
        b = Button(self.font, *args)
        b.show()
        self.buttons.append(b)
        return b

    def add_sprite_button(self, *args):
        b = SpriteButton(self.font, *args)
        b.show()
        self.buttons.append(b)
        return b

    def process_click(self, pos):
        for b in self.buttons:
            if b.shown and b.rect.collidepoint(pos):
                if self.pending_button is not None:
                    self.pending_button.toggle_state()
                self.set_pending_button(b)
                b.cb()
                return True

    def draw(self, targ):
        for b in self.buttons:
            b.draw(targ)


class Button(object):
    bg_color = (255, 121, 43)
    bd_color = (64, 32, 16)
    fg_color = (0, 0, 0)
    margin = 2

    def __init__(self, font, text, cb, x, y, w=None, h=None):
        self.text = font.render(text, True, self.fg_color)
        text_w, text_h = self.text.get_size()

        if w is None:
            w = text_w + self.margin * 2
        if h is None:
            h = text_h + self.margin * 2

        self.cb = cb
        self.rect = pygame.Rect(x, y, w, h)
        self.tpos = x + w / 2 - text_w / 2, y + h / 2 - text_h / 2
        self.shown = False

    def show(self):
        self.shown = True

    def hide(self):
        self.shown = False

    def draw(self, targ):
        pygame.draw.rect(targ, self.bg_color, self.rect)
        pygame.draw.rect(targ, self.bd_color, self.rect, 1)
        targ.blit(self.text, self.tpos)

    def toggle_state(self):
        pass


class SpriteButton(Button):
    def __init__(self, font, text, cb, x, y, img=None):
        self.text = font.render(text, True, self.fg_color)
        text_w, text_h = self.text.get_size()

        # assuming iup and idown have the same dimensions
        if img:
            self.image_up, self.image_down = img
        else:
            self.image_up = data.load_image("button_up.png")
            self.image_down = data.load_image("button_dn.png")

        w, h = self.image_up.get_size()
        h += 3

        self.rect = pygame.Rect(x, y, w, h)

        self.ipos = x, y
        self.tpos = int(x + w / 2 - text_w / 2), int(y + h / 2 - text_h / 2)
        self.cb = cb
        self.shown = False
        self.pressed = False

    def toggle_state(self):
        self.pressed = not self.pressed
        return self.pressed

    def draw(self, targ):
        if not self.shown:
            return

        if self.pressed:
            img = self.image_down
            dy = 1
        else:
            img = self.image_up
            dy = 0

        targ.blit(img, (self.ipos[0], self.ipos[1] + dy))
        targ.blit(self.text, (self.tpos[0], self.tpos[1] + dy))


if __name__ == "__main__":
    import sys
    import data

    def fancy_cb():
        print "Named callback"

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    screen.fill(0)
    br = ButtonRegistry()
    br.add_button("Foobar-o-matic", fancy_cb, 4, 4, 128)
    br.add_button("Exit", sys.exit, 4, 48, 128)

    img = (data.load_image("button-pressed-grey.png"),
           data.load_image("button-unpressed-grey.png"),)
    br.add_sprite_button("KABOOM", fancy_cb, 4, 92, img)

    while 1:
        br.draw(screen)
        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEBUTTONUP:
                br.process_click(ev)
