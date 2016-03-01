TYPE_ROAD = 1
TYPE_CITY = 2
TYPE_FIELD = 3

import os
import math
import sys
import random
import itertools
from pop import Population
from collections import defaultdict
import data

class Map(object):
    def __init__(self):
        self.width = None
        self.height = None
        self.grid = {}

    char_types = {
        '_': TYPE_FIELD,
        'c': TYPE_CITY,
        'v': TYPE_CITY,
        '#': TYPE_ROAD,
    }

    def make_cell(self, x, y, char):
        return Cell(x, y, cell_type)

    def load(self, name):
        for y, line in enumerate(data.open(name)):
            for x, char in enumerate(line.strip()):
                cell_type = self.char_types[char]
                self.grid[x, y] = Cell(x, y, cell_type)
        self.width = x
        self.height = y
        print self.width, self.height

    def init(self):
        self.order = [ (x, y) for x in range(0, self.width) for y in range(0, self.height) ]
        self.order_iter = itertools.cycle(self.order)
        random.shuffle(self.order)

    def populate(self):
        for x in range(0, self.width):
            for y in range(0, self.height):
                self.grid[x, y] = Cell(x, y, TYPE_FIELD)

        # build two cities in the top-left and bottom-right
        # corners
        self.grid[0, 0] = Cell(0, 0, TYPE_CITY)
        self.grid[0, 0].pop.sick = 10.0
        x, y = self.width-1, self.height-1
        self.grid[x, y] = Cell(x, y, TYPE_CITY)
        self.grid[0, y] = Cell(0, y, TYPE_CITY)

        # connect the two cities with a road
        for x in range(1, self.width):
            self.grid[x, 0] = Cell(x, 0, TYPE_ROAD)
        for y in range(1, self.height-1):
            self.grid[self.width-1, y] = Cell(self.width-1, y, TYPE_ROAD)

        # block a semi-random road cell
        self.grid[3, 0].block()

    def draw(self):
        for y in range(0, self.height):
            for x in range(0, self.width):
                print "% 6.1f" % self.grid[x, y].pop.good,
            print "\t",
            for x in range(0, self.width):
                print "% 6.1f" % self.grid[x, y].pop.sick,
            print "\t",
            for x in range(0, self.width):
                print "% 6.1f" % self.grid[x, y].pop.dead,
                #print str(self.grid[x, y].char()),
            print

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

        curr.update()

        cpop = curr.pop
        tpop = cpop.good + cpop.sick + cpop.dead

        if tpop > 0:
            for dx, dy in self.directions:
                nx, ny = curr.x + dx, curr.y + dy
                if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                    continue

                n = self.grid[nx, ny]
                if n.is_blocked:
                    continue

                attract_coef = min(0.25, n.attract * (1.0 + 100 * cpop.dead / tpop))
                moving.good = attract_coef * curr.pop.good
                moving.sick = attract_coef * curr.pop.sick

                curr.pop -= moving
                n.pop += moving

        return x, y

class Cell(object):
    chars = {
        TYPE_CITY: "o",
        TYPE_ROAD: "=",
        TYPE_FIELD: "_",
    }

    type2attract = {
        TYPE_CITY: 0.2,
        TYPE_ROAD: 0.1,
        TYPE_FIELD: 0.01,
    }

    def __init__(self, x, y, cell_type):
        self.x = x
        self.y = y
        self.type = cell_type
        self.attract = self.type2attract[cell_type]
        self.is_blocked = False
        healthy = 10000.0 if cell_type == TYPE_CITY else 0.0
        sick = 0.0
        dead = 0.0
        self.pop = Population(healthy, sick, dead)

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
