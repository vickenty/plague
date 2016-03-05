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
        
        self.set_seq(seq)
        self.update()

    def set_seq(self, seq):
        self.frames = itertools.cycle(self.conf["frames"][seq])

    def update(self):
        fx, fy = next(self.frames)
        self.image = self.sheet.subsurface((fx, fy, self.frame_w, self.frame_h))

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
