from collections import defaultdict
from random import choice
import pygame
from pygame.locals import *

from constants import *
import data

class Tileset (object):
    def __init__(self, name):
        self.name = name
        self.conf = data.load_json(name)
        self.surf = pygame.transform.scale(data.load_image(self.conf["image"]), (768, 768))

        self.tiles = defaultdict(list)
        self.dummy = pygame.Surface((GRID_W, GRID_H))
        self.dummy.fill((255, 0, 0))

        for name, coords in self.conf["tiles"].items():
            for ix, iy in coords:
                x = ix * GRID_W
                y = iy * GRID_H
                tile = pygame.Surface((GRID_W, GRID_H), SRCALPHA)
                tile.blit(self.surf, (0, 0), (x, y, GRID_W, GRID_H))
                self.tiles[name].append(tile)

        gen = defaultdict(list)

        # straits
        for tile in self.tiles["road-hh"]:
            tile = pygame.transform.flip(tile, True, False)
            gen["road-hh"].append(tile)
            tile = pygame.transform.flip(tile, False, True)
            gen["road-hh"].append(tile)
            tile = pygame.transform.flip(tile, True, False)
            gen["road-hh"].append(tile)

        for tile in self.tiles["road-vv"]:
            tile = pygame.transform.flip(tile, True, False)
            gen["road-vv"].append(tile)
            tile = pygame.transform.flip(tile, False, True)
            gen["road-vv"].append(tile)
            tile = pygame.transform.flip(tile, True, False)
            gen["road-vv"].append(tile)

        # turns
        for tile in self.tiles["road-tl"]:
            tile = pygame.transform.rotate(tile, 90)
            gen["road-bl"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-br"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-tr"].append(tile)

        for tile in self.tiles["road-tr"]:
            tile = pygame.transform.rotate(tile, 90)
            gen["road-tl"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-bl"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-br"].append(tile)

        for tile in self.tiles["road-br"]:
            tile = pygame.transform.rotate(tile, 90)
            gen["road-tr"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-tl"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-bl"].append(tile)

        for tile in self.tiles["road-bl"]:
            tile = pygame.transform.rotate(tile, 90)
            gen["road-br"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-tr"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-tl"].append(tile)

        # dead-ends
        for tile in self.tiles["road-bb"]:
            tile = pygame.transform.rotate(tile, 90)
            gen["road-rr"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-tt"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-ll"].append(tile)

        # tees
        for tile in self.tiles["road--t"]:
            tile = pygame.transform.rotate(tile, 90)
            gen["road-|l"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road--b"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-|r"].append(tile)

        for tile in self.tiles["road-|l"]:
            tile = pygame.transform.rotate(tile, 90)
            gen["road--b"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road-|r"].append(tile)
            tile = pygame.transform.rotate(tile, 90)
            gen["road--t"].append(tile)

        for name, tiles in gen.items():
            self.tiles[name].extend(tiles)

    def get(self, name):
        tiles = self.tiles[name]
        if not tiles:
            #raise ValueError, "missing tile '%s'" % (name,)
            print name
            return self.dummy
        return choice(tiles)

class Renderer (object):
    max_pop = 10
    margin = 1
    cell_w = GRID_W - margin
    cell_h = GRID_H - margin
    stride_x = cell_w + margin
    stride_y = cell_h + margin

    def __init__(self):
        self.buf = pygame.Surface((SCREEN_W, SCREEN_H))
        self.buf.fill(0)
        self.tls = Tileset("tileset.cfg")

    def fill(self, color):
        self.buf.fill(color)

    def draw(self, m):
        for (x, y), c in m.grid.items():
            self.draw_one(x, y, c)

    def draw_one(self, ix, iy, cell):
        dst = ix * GRID_W, iy * GRID_H

        self.buf.blit(self.tls.get("field"), dst)

        if cell.walls.get((0, -1)):
            self.buf.blit(self.tls.get("wall-tt"), dst)

        self.buf.blit(self.tls.get(cell.nview), dst)

        if cell.walls.get((-1, 0)):
            self.buf.blit(self.tls.get("wall-ll"), dst)
        if cell.walls.get((1, 0)):
            self.buf.blit(self.tls.get("wall-rr"), dst)
        if cell.walls.get((0, 1)):
            self.buf.blit(self.tls.get("wall-bb"), dst)

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
