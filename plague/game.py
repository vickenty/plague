import pygame
from pygame.locals import *

import sim
import render
from constants import *

class Game (object):
    text_color = (255, 255, 255)

    def __init__(self):
        self.model = sim.Map()
        self.model.load("level1")

        self.renderer = render.Renderer()
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(pygame.font.get_default_font(), 16)

    def update(self, disp):
        self.clock.tick(FRAMES_PER_SECOND)

        for ev in pygame.event.get():
            if ev.type == QUIT:
                return None

        for _ in range(0, UPDATES_PER_FRAME):
            dx, dy = self.model.update()
            self.renderer.draw_one(self.model, dx, dy)
        
        disp.fill(0)
        self.renderer.blit(disp)

        self.draw_fps(disp)
        self.draw_population(disp, self.model.census)

        return self

    def draw_text(self, targ, text, pos):
        buf = self.font.render(text, True, self.text_color)
        targ.blit(buf, pos)

    def draw_fps(self, targ):
        self.draw_text(targ, "%.2f" % self.clock.get_fps(), (600, 2))

    def draw_population(self, targ, pop):
        if pop is None:
            return
        cnc_text = "%.2f / %.2f / %.2f" % (pop.good, pop.sick, pop.dead)
        self.draw_text(targ, cnc_text, (600, 20))
