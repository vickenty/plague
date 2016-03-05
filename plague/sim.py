import os
import math
import sys
import random
import itertools

from pop import Population
from collections import defaultdict
import data
from constants import *

# proportion of population (healthy, sick, and dead) that's reduced per update
# when burning
BURN_FACTOR = 0.5

class Config (object):
    def __init__(self, data):
        time = data["time"]
        self.time = time
        self.messages = {}
        if "messages" in data:
            # int object keys not allowed in JSON, but these are times
            for key in data["messages"]:
                val = data["messages"][key]
                del data["messages"][key]
                data["messages"][int(key)] = val

            self.messages = data["messages"]

        del data["time"]

        self.units = data["units"]
        del data["units"]

        self.cell = data


class Map(object):
    def __init__(self, name):
        self.width = None
        self.height = None
        self.grid = {}
        self.census = None
        self.running_census = None
        self.conf = Config(data.load_json(name + ".cfg"))

        self.load(name)

    def make_cell(self, char):
        cell_conf = self.conf.cell[char]
        return Cell(**cell_conf)

    def load(self, name):
        with data.open(name + ".map") as src:
            for y, line in enumerate(src):
                for x, char in enumerate(line.strip()):
                    self.grid[x, y] = self.make_cell(char)

        self.width = x + 1
        self.height = y + 1

        for (x, y), cell in self.grid.items():
            bits = 0

            for f, (dx, dy) in enumerate(self.directions):
                nx, ny = x + dx, y + dy

                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue

                neighbor = self.grid[nx, ny]
                # neighboring cells with walls are not separated
                if cell.has_walls and not (neighbor.has_walls or neighbor.gates):
                    cell.walls[dx, dy] = True

                if cell.view == neighbor.view:
                    bits |= (1 << f)

            cell.nview = cell.view + self.tile_suffix[bits & cell.sprite_mask]

        self.init()

    def init(self):
        self.order = [ (x, y) for x in range(0, self.width) for y in range(0, self.height) ]
        self.order_iter = itertools.cycle(self.order)
        random.shuffle(self.order)

    directions = [
        (-1, 0),
        (0, -1),
        (1, 0),
        (0, 1),
    ]

    tile_suffix = {
        0x0: "",    # l t r b
        0x1: "-ll", # 1 0 0 0
        0x2: "-tt", # 0 1 0 0
        0x3: "-br", # 1 1 0 0
        0x4: "-rr", # 0 0 1 0
        0x5: "-hh", # 1 0 1 0
        0x6: "-bl", # 0 1 1 0
        0x7: "--t", # 1 1 1 0
        0x8: "-bb", # 0 0 0 1
        0x9: "-tr", # 1 0 0 1
        0xa: "-vv", # 0 1 0 1
        0xb: "-|l", # 1 1 0 1
        0xc: "-tl", # 0 0 1 1
        0xd: "--b", # 1 0 1 1
        0xe: "-|r", # 0 1 1 1
        0xf: "-cc", # 1 1 1 1
    }

    caught_fire = defaultdict(lambda: True)

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

                if curr.walls.get((dx, dy)) or n.walls.get((-dx, -dy)):
                    continue

                if curr.burning:
                    # FIXME better conditions for catching fire
                    if random.random() < 0.3:
                        n.catch_fire()

                if n.is_blocked:
                    continue

                attract_coef = min(0.25, n.attract * (1.0 + 100 * cpop.dead / tpop))
                moving.good = attract_coef * curr.pop.good
                moving.sick = attract_coef * curr.pop.sick

                curr.pop -= moving
                n.incoming += moving

        self.running_census += curr.pop

        caught_fire = curr.burning and self.caught_fire[x, y]
        if curr.burning:
            self.caught_fire[x, y] = False

        return x, y, curr.new_dead, caught_fire


class Cell(object):
    def __init__(
        self,
        view,
        attract=0.0,
        good=0.0,
        sick=0.0,
        dead=0.0,
        has_walls=False,
        gates=False,
        sprite_mask=0,
        health=0,
    ):
        self.view = view
        self.nview = view
        self.attract = attract
        self.is_blocked = False
        self.pop = Population(good, sick, dead)
        self.incoming = Population(0.0)
        self.last_incoming = Population(0.0)
        self.has_walls = has_walls
        self.gates = gates
        self.walls = {}
        self.sprite_mask = sprite_mask
        # new_dead is > 0 when there are new dead bodies in the cell
        # draw a soul sprite when that happens
        self.new_dead = 0
        self.old_dead = 0
        self.ttl_dead = random.randint(1, DEAD_TTL + 1)

        self.health = health
        self.burning = False
        self.burnt = False

    def block(self):
        self.is_blocked = True

    def unblock(self):
        self.is_blocked = False

    def catch_fire(self):
        if self.health <= 0 or self.burnt or self.burning:
            return False
        self.burning = True
        return True

    def burn(self, factor):
        if not self.burning:
            return
        self.health -= 1
        self.pop.burn(factor)
        if self.health <= 0:
            self.burning = False
            self.burnt = True

    def char(self):
        if self.is_blocked:
            return "x"
        return self.chars[self.type]

    def update(self):
        pop = self.pop

        pop += self.incoming
        self.last_incoming = self.incoming
        self.incoming = Population(0.0)

        pop.kill(0.02)

        self.ttl_dead -= 1
        if self.ttl_dead == 0:
            self.new_dead = int(pop.dead - self.old_dead)
            self.old_dead = int(pop.dead)
            self.ttl_dead = DEAD_TTL
        else:
            self.new_dead = 0

        if pop.good == 0.0:
            return

        ratio = (pop.sick + pop.dead) / pop.good / 10
        if ratio == 0.0:
            return

        pop.infect(min(0.1, ratio))

        self.burn(BURN_FACTOR)

if __name__ == '__main__':
    m = Map()
    m.populate()

    while 1:
        m.update()
        print
        m.draw()
        raw_input()
