import data

class Anim (object):
    def __init__(self, name, frame_w, dx=0, dy=0):
        self.image = data.load_image(name)
        self.frame_w = frame_w
        self.frame_h = self.image.get_height()
        self.frame = 0
        self.total = self.image.get_width() // frame_w
        self.dx = dx
        self.dy = dy
    
    def draw(self, dest, (px, py)):
        dest.blit(self.image, (px + self.dx, py + self.dy), (int(self.frame) * self.frame_w, 0, self.frame_w, self.frame_h))

    def update(self):
        self.frame = (self.frame + 0.2) % self.total

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
