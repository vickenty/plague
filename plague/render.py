import pygame
from pygame.locals import *

class Renderer (object):
    max_pop = 30

    def draw(self, m, surf):
        for x in xrange(0, m.width):
            for y in xrange(0, m.height):
                self.draw_one(m, x, y, surf)

    def draw_one(self, m, x, y, surf):
        rect = (x * 16, y * 16, 14, 14)
        color = self.get_color(m.grid[x, y])
        surf.fill(color, rect)

    def get_color(self, cell):
        return (
            min(255, int(cell.pop.good ** 0.5 / self.max_pop * 255)),
            min(255, int(cell.pop.sick ** 0.5 / self.max_pop * 255)),
            min(255, int(cell.pop.dead ** 0.5 / self.max_pop * 255)),
        )

if __name__ == '__main__':
    from sim import Map
    pygame.init()
    disp = pygame.display.set_mode((800, 600), DOUBLEBUF)
    clock = pygame.time.Clock()
    font = pygame.font.Font(pygame.font.get_default_font(), 16)

    model = Map()
    model.load("level1.map")

    renderer = Renderer()
    buf = pygame.Surface(disp.get_size())

    while 1:
        clock.tick(6000)
        for _ in range(0, 20):
            x, y = model.update()
            renderer.draw_one(model, x, y, buf)
        disp.blit(buf, (0, 0))
        fps = font.render("%.2f" % clock.get_fps(), False, (255, 255, 255))
        disp.blit(fps, (600, 2))
        pygame.display.flip()
