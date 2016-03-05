import itertools
import data
from pyg import pygame


class Anim (pygame.sprite.Sprite):
    def __init__(self, name, seq, pos_x, pos_y):
        self.conf = conf = data.load_json(name)

        self.sheet = data.load_image(conf["image"])
        self.frame_w, self.frame_h = conf["frame"]
        self.offset_x, self.offset_y = conf["offset"]
        self.rect = pygame.Rect(
            pos_x + self.offset_x,
            pos_y + self.offset_y,
            self.frame_w,
            self.frame_h,
        )

        self.delay = conf.get("delay", 0)
        self.time = self.delay # force first update

        self.seq = None
        self.set_seq(seq)
        self.update()

    def set_pos(self, pos):
        self.rect.topleft = pos

    def set_seq(self, seq):
        if seq != self.seq:
            self.frames = itertools.cycle(self.conf["frames"][seq])
            self.seq = seq

    def update(self):
        self.time += 1
        if self.time > self.delay:
            self.time = 0
            fx, fy = next(self.frames)
            self.image = self.sheet.subsurface((fx, fy, self.frame_w, self.frame_h))

    def draw(self, targ):
        targ.blit(self.image, self.rect.topleft)

if __name__ == '__main__':
    from pyg import pygame
    pygame.init()

    disp = pygame.display.set_mode((300, 300))
    anim = Anim("flame-8.png", 16)
    clk = pygame.time.Clock()

    while 1:
        clk.tick(20)
        disp.fill(0)
        anim.draw(disp, (100, 100))
        anim.update()
        pygame.display.flip()
