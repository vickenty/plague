import pygame
import anim
import data
from constants import *


class Ghost (pygame.sprite.Sprite):
    def __init__(self, count, pos_x, pos_y, *groups):
        if count > 1:
            label = "%d" % count
        else:
            label = ""

        pos_y -= 2

        spr = data.load_image("ghost.png")
        w, h = spr.get_size()

        fnt = data.load_image("digits.png")
        fnt_w = 4
        fnt_h = 5

        txt_x = w + 1
        txt_y = 2

        self.image = pygame.Surface((txt_x + fnt_w * len(label), h), pygame.SRCALPHA)
        self.image.blit(spr, (0, 0))
        for i, c in enumerate(label):
            fnt_x = int(c) * fnt_w
            self.image.blit(fnt, (txt_x + i * fnt_w, txt_y), (fnt_x, 0, fnt_w, fnt_h))

        self.rect = pygame.Rect(pos_x, pos_y, *self.image.get_size())
        self.targ_y = pos_y - DEAD_TTL // 2

        pygame.sprite.Sprite.__init__(self, *groups)

    def update(self):
        self.rect.y -= 1
        if self.rect.y <= self.targ_y:
            self.kill()


class Fire(anim.Anim):
    def __init__(self, x, y, *groups):
        anim.Anim.__init__(self, "flame-8.cfg", "flame", x, y, *groups)


class Walker (anim.Anim):
    anims = {
        (-1, 0): "l",
        (1, 0): "r",
        (0, -1): "u",
        (0, 1): "d",
    }

    def __init__(self, x, y, dirx, diry, *groups):
        self.dirx = dirx
        self.diry = diry
        self.ttl = 4
        anim.Anim.__init__(self, "walk.cfg", self.anims[dirx, diry], x, y, *groups)

    def update(self):
        self.rect.x += self.dirx
        self.rect.y += self.diry
        super(Walker, self).update()
        self.ttl -= 1
        if self.ttl <= 0:
            self.kill()
