import pygame
from pygame.locals import *

import sim
import render
import unit
import buttons
import data
from constants import *


class Game (object):
    text_color = (255, 255, 255)

    def __init__(self):
        self.model = sim.Map()
        self.model.load("level1")

        self.units = [
            unit.Unit(self.model.width // 2, self.model.height // 2),
            unit.Unit(self.model.width // 3, self.model.height // 3),
        ]

        self.units[0].set_command("move", 1, 1, ("idle",))
        self.units[1].set_command("move", 3, 12, ("idle",))

        self.renderer = render.Renderer()
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(pygame.font.get_default_font(), 16)
        self.selection = None

        self.buttons = buttons.ButtonRegistry()

        img = (data.load_image("button-unpressed-grey.png"),
               data.load_image("button-pressed-grey.png"),)

        self.buttons.add_sprite_button("Reap", self.send_reap, 600, 40, img)
        self.buttons.add_sprite_button("Burn", self.send_burn, 600, 80, img)
        self.buttons.add_sprite_button("Cancel", self.cancel_selection, 600, 120, img)

    def send_reap(self):
        if not self.selection:
            return
        unit = self.selection
        x, y = unit.x, unit.y
        self.selection.set_command("reap", self.model.grid[x, y].pop)

    def send_burn(self):
        if not self.selection:
            return

    def cancel_selection(self):
        self.selection = None
        self.buttons.unset_pending_button()

    def find_unit(self, pos):
        for unit in self.units:
            if unit.rect.collidepoint(pos):
                return unit
        return None

    def update(self, disp):
        self.clock.tick(FRAMES_PER_SECOND)

        for ev in pygame.event.get():
            if ev.type == QUIT:
                return None

            if ev.type == pygame.MOUSEBUTTONUP:
                if self.selection:
                    if self.buttons.process_click(ev):
                        continue

                self.selection = self.find_unit(ev.pos)

        for _ in range(0, UPDATES_PER_FRAME):
            dx, dy = self.model.update()
            self.renderer.draw_one(self.model, dx, dy)

        disp.fill(0)
        self.renderer.blit(disp)

        for unit in self.units:
            unit.update()
            unit.draw(disp, self.selection == unit)

        if self.selection:
            self.buttons.draw(disp)

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
