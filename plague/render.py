import pygame
from pygame.locals import *

from constants import *

class Renderer (object):
    max_pop = 10
    margin = 1
    cell_w = GRID_W - margin
    cell_h = GRID_H - margin
    stride_x = cell_w + margin
    stride_y = cell_h + margin

    def __init__(self):
        self.buf = pygame.Surface((SCREEN_W, SCREEN_H)).convert()
        self.buf.fill(0)

    def fill(self, color):
        self.buf.fill(color)

    def draw(self, m, surf):
        for x in xrange(0, m.width):
            for y in xrange(0, m.height):
                self.draw_one(m, x, y, surf)

    def draw_one(self, m, x, y):
        rect = pygame.Rect(x * self.stride_x, y * self.stride_y, self.cell_w, self.cell_h)
        cell = m.grid[x, y]
        color = self.get_color(cell)
        self.buf.fill(color, rect)

        pygame.draw.line(self.buf, self.get_wall_color(cell, 0, -1), rect.topleft, rect.topright)
        pygame.draw.line(self.buf, self.get_wall_color(cell, 1, 0), rect.topright, rect.bottomright)
        pygame.draw.line(self.buf, self.get_wall_color(cell, 0, 1), rect.bottomright, rect.bottomleft)
        pygame.draw.line(self.buf, self.get_wall_color(cell, -1, 0), rect.bottomleft, rect.topleft)

    def blit(self, targ):
        targ.blit(self.buf, (self.margin, self.margin))

    def get_color(self, cell):
        return (
            min(255, int(cell.pop.good ** 0.5 / self.max_pop * 255)),
            min(255, int(cell.pop.sick ** 0.5 / self.max_pop * 255)),
            min(255, int(cell.pop.dead ** 0.5 / self.max_pop * 255)),
        )

    def get_wall_color(self, cell, dx, dy):
        return (255, 255, 255) if cell.walls.get((dx, dy)) else (0, 0, 0)

if __name__ == '__main__':
    from sim import Map
    pygame.init()
    disp = pygame.display.set_mode((800, 600), DOUBLEBUF)
    clock = pygame.time.Clock()
    font = pygame.font.Font(pygame.font.get_default_font(), 16)

    model = Map()
    model.load("level1")

    renderer = Renderer()
    buf = pygame.Surface(disp.get_size())

    while 1:
        clock.tick(6000)
        for _ in range(0, 2):
            x, y = model.update()
            renderer.draw_one(model, x, y, buf)
        disp.blit(buf, (0, 0))
        disp.blit(fps, (600, 2))

        if model.census:
            cnc = font.render("%.2f / %.2f / %.2f" % (model.census.good, model.census.sick, model.census.dead), True, (255, 255, 255))
            disp.blit(cnc, (600, 18))

        pygame.display.flip()
