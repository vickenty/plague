from pyg import pygame
from constants import *
import data


class Unit (object):
    speed = 0.02
    selection_color = (255, 255, 0)

    def __init__(self, model, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(0, 0, GRID_W, GRID_H)
        if pygame.version.vernum >= (2, 0, 0):
            # facepalm
            self.rect.w -= 1
            self.rect.h -= 1
        self.command = self.cmd_idle, ()
        self.sprite_idle = data.load_image("unit.png")
        self.sprite_block = data.load_image("block.png")
        self.is_moving = False
        self.is_blocking = False
        self.model = model

    def set_command(self, cmd, *args):
        impl = getattr(self, "cmd_" + cmd)
        self.command = impl, args

    def cmd_move(self, tx, ty, new_cmd):
        if self.x == tx and self.y == ty:
            self.is_moving = False
            self.set_command(*new_cmd)
            return

        self.is_moving = True

        dx = tx - self.x
        dy = ty - self.y
        dl = (dx ** 2 + dy ** 2) ** 0.5
        if dl > self.speed:
            dx *= self.speed / dl
            dy *= self.speed / dl

        self.x += dx
        self.y += dy

    def cmd_reap(self, grid):
        model = self.model
        grid = model.grid
        grid[self.x, self.y].pop.reap(REAP_FACTOR)
        for dx, dy in model.directions:
            nx, ny = self.x + dx, self.y + dy
            if not (0 <= nx < model.width and 0 <= ny < model.height):
                continue
            grid[nx, ny].pop.reap(REAP_FACTOR)

    def cmd_burn(self, grid):
        grid[self.x, self.y].catch_fire()

    def cmd_block(self, grid):
        self.is_blocking = True
        grid[self.x, self.y].block()

    def cmd_unblock(self, grid):
        self.is_blocking = False
        grid[self.x, self.y].unblock()

    def cmd_idle(self):
        pass

    def cmd_debug(self):
        raise ValueError, "woot"

    def update(self):
        cmd, args = self.command
        cmd(*args)
        self.rect.x = int(self.x * GRID_W)
        self.rect.y = int(self.y * GRID_H)

    def draw(self, targ, selected):
        cmd, _ = self.command
        if cmd == self.cmd_block:
            sprite = self.sprite_block
        else:
            sprite = self.sprite_idle

        if hasattr(sprite, "draw"):
            sprite.draw(targ, self.rect.topleft)
        else:
            targ.blit(sprite, self.rect.topleft)

        if selected:
            pygame.draw.rect(targ, self.selection_color, self.rect, 1)

if __name__ == '__main__':
    u = Unit(0.0, 0.0)
    u.command = u.cmd_move, (1.0, 0.5, (u.cmd_debug, ()))
    while True:
        print u.x, u.y, u.command
        u.update()
