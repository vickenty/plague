import pygame.draw

class Unit (object):
    speed = 0.1

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.command = self.cmd_idle, ()

    def cmd_move(self, tx, ty, new_cmd):
        if self.x == tx and self.y == ty:
            self.command = new_cmd
            return
    
        dx = tx - self.x
        dy = ty - self.y
        dl = (dx ** 2 + dy ** 2) ** 0.5
        if dl > self.speed:
            dx *= self.speed / dl
            dy *= self.speed / dl

        self.x += dx
        self.y += dy

    def cmd_reap(self):
        pass

    def cmd_burn(self):
        pass

    def cmd_idle(self):
        pass

    def cmd_debug(self):
        raise ValueError, "woot"

    def update(self):
        cmd, args = self.command
        cmd(*args)

if __name__ == '__main__':
    u = Unit(0.0, 0.0)
    u.command = u.cmd_move, (1.0, 0.5, (u.cmd_debug, ()))
    while True:
        print u.x, u.y, u.command
        u.update()
