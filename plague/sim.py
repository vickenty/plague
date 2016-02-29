TYPE_ROAD = 1
TYPE_CITY = 2
TYPE_FIELD = 3

import os
import math
import sys
from pop import Population
from collections import defaultdict


class Map(object):
    def __init__(self):
        self.height = 5
        self.width = 5
        self.grid = {}

    def populate(self):
        for x in range(0, self.width):
            for y in range(0, self.height):
                self.grid[x, y] = Cell(x, y, TYPE_FIELD)

        # build two cities in the top-left and bottom-right
        # corners
        self.grid[0, 0] = Cell(0, 0, TYPE_CITY)
        x, y = self.width-1, self.height-1
        self.grid[x, y] = Cell(x, y, TYPE_CITY)
        self.grid[x, y].pop = Population(0.0)

        # connect the two cities with a road
        for x in range(1, self.width):
            self.grid[x, 0] = Cell(x, 0, TYPE_ROAD)
        for y in range(1, self.height-1):
            self.grid[self.width-1, y] = Cell(self.width-1, y, TYPE_ROAD)

        # block a semi-random road cell
        self.grid[3, 0].block()

    def neighbours_coordinates(self, x, y):
        res = []
        if x+1 < self.width:
            res.append((x+1, y))
        if x-1 >= 0:
            res.append((x-1, y))
        if y+1 < self.height:
            res.append((x, y+1))
        if y-1 >= 0:
            res.append((x, y-1))
        return res

    def neighbours(self, other):
        n = self.neighbours_coordinates(other.x, other.y)
        return filter(lambda c: not self.grid[c.x, c.y].is_blocked, map(lambda c: self.grid[c], n))

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

    def update(self):
        buf = defaultdict(lambda: Population(0.0))
        for x in range(0, self.width):
            for y in range(0, self.height):
                curr = self.grid[x, y]
                curr.expire()
                curr.infect()
                for n in self.neighbours(curr):
                    moving_healthy = n.attract * curr.pop.good  # account dead ppl
                    moving_sick = n.attract * curr.pop.sick  # account dead ppl
                    #if x == 0 and y == 0 and n.x == 1 and n.y == 0:
                    #    print "Leaving the city: %.2f" % moving_sick
                    #if x == 1 and y == 0 and n.x == 0 and n.y == 0:
                    #    print "Leaving into the city: %.2f" % moving_sick
                    buf[curr] -= Population(moving_healthy, moving_sick)
                    buf[n] += Population(moving_healthy, moving_sick)
        for c, pop in buf.items():
            c.pop += pop


class Cell(object):
    chars = {
        TYPE_CITY: "o",
        TYPE_ROAD: "=",
        TYPE_FIELD: "_",
    }

    type2attract = {
        TYPE_CITY: 0.2,
        TYPE_ROAD: 0.05,
        TYPE_FIELD: 0.01,
    }

    def __init__(self, x, y, cell_type):
        self.x = x
        self.y = y
        self.type = cell_type
        self.attract = self.type2attract[cell_type]
        self.is_blocked = False
        healthy = 1000.0 if cell_type == TYPE_CITY else 0.0
        sick = 1.0 if cell_type == TYPE_CITY else 0.0
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

    def infect(self):
        pop = self.pop
        if pop.good == 0.0:
            return
        ratio = (pop.sick + pop.dead) / pop.good / 100
        if ratio == 0.0:
            return
        self.pop = pop.infect(min(0.1, ratio))

    def expire(self):
        self.pop = self.pop.kill(0.2)


if __name__ == '__main__':
    m = Map()
    m.populate()

    while 1:
        m.update()
        print
        m.draw()
        raw_input()
