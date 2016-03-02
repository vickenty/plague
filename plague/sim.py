import os
import math
import sys
import random
import itertools
import json

from pop import Population
from collections import defaultdict
import data

class Config (object):
    def __init__(self, conf):
        self.conf = conf

    def make_cell(self, char):
        conf = self.conf[char]
        return Cell(**conf)

class Map(object):
    def __init__(self):
        self.width = None
        self.height = None
        self.grid = {}
        self.census = None
        self.running_census = None

    def load(self, name):
        with data.open(name + ".cfg") as src:
            config = Config(json.load(src))

        with data.open(name  + ".map") as src:
            for y, line in enumerate(src):
                for x, char in enumerate(line.strip()):
                    self.grid[x, y] = config.make_cell(char)

        self.width = x + 1
        self.height = y + 1

        for (x, y), cell in self.grid.items():
            if not cell.has_walls:
                continue

            for dx, dy in self.directions:
                nx, ny = x + dx, y + dy
                neighbor = self.grid[nx, ny]
                # neighboring cells with walls are not separated
                # roads are special
                if not (neighbor.has_walls or neighbor.gates):
                    cell.walls[dx, dy] = True

        print self.width, self.height

        self.init()

    def init(self):
        self.order = [ (x, y) for x in range(0, self.width) for y in range(0, self.height) ]
        self.order_iter = itertools.cycle(self.order)
        random.shuffle(self.order)

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    def update(self):
        moving = Population(0.0)
        x, y = next(self.order_iter)
        curr = self.grid[x, y]

        if (x, y) == self.order[0]:
            self.census = self.running_census
            self.running_census = Population(0.0)


        curr.update()

        cpop = curr.pop
        tpop = cpop.good + cpop.sick + cpop.dead

        if tpop > 0:
            for dx, dy in self.directions:
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                    continue

                n = self.grid[nx, ny]
                if n.is_blocked or curr.walls.get((dx, dy)) or n.walls.get((-dx, -dy)):
                    continue

                attract_coef = min(0.25, n.attract * (1.0 + 100 * cpop.dead / tpop))
                moving.good = attract_coef * curr.pop.good
                moving.sick = attract_coef * curr.pop.sick

                curr.pop -= moving
                n.pop += moving

        self.running_census += curr.pop

        return x, y

class Cell(object):
    def __init__(self, view, attract=0.0, good=0.0, sick=0.0, dead=0.0, has_walls=False, gates=False):
        self.view = view
        self.attract = attract
        self.is_blocked = False
        self.pop = Population(good, sick, dead)
        self.has_walls = has_walls
        self.gates = gates
        self.walls = {}

    def block(self):
        self.is_blocked = True

    def unblock(self):
        self.is_blocked = False

    def char(self):
        if self.is_blocked:
            return "x"
        return self.chars[self.type]

    def update(self):
        pop = self.pop

        pop.kill(0.002)

        if pop.good == 0.0:
            return

        ratio = (pop.sick + pop.dead) / pop.good / 100
        if ratio == 0.0:
            return

        pop.infect(min(0.1, ratio))

if __name__ == '__main__':
    m = Map()
    m.populate()

    while 1:
        m.update()
        print
        m.draw()
        raw_input()
