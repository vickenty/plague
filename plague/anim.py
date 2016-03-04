import data
import pygame

class Anim (pygame.sprite.Sprite):
    def __init__(self, name, frame_w, dx=0, dy=0):
        self.orig = data.load_image(name)
        self.frame_w = frame_w
        self.frame_h = self.orig.get_height()
        self.frame = 0
        self.total = self.orig.get_width() // frame_w
        self.dx = dx
        self.dy = dy
        self.rect = pygame.Rect(dx, dy, self.frame_w, self.frame_h)

        self.update()

    def update(self):
        self.image = self.orig.subsurface(
            (int(self.frame) * self.frame_w, 0, self.frame_w, self.frame_h)
        )
        self.frame = (self.frame + 1) % self.total

if __name__ == '__main__':
    import pygame
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
