from pyg import pygame
from pyg.locals import *

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
        self.renderer.draw(self.model)

        self.clock = pygame.time.Clock()

        self.font = data.load_font(*UI_FONT)
        self.selection = None
        self.need_destination = False
        self.pending_cmd = None

        self.buttons = buttons.ButtonRegistry()

        img = data.load_image("button-scroll.png")

        self.buttons.add_sprite_button("Reap", self.send_reap, 150, 160, (img, img))
        self.buttons.add_sprite_button("Burn", self.send_burn, 150, 180, (img, img))
        self.buttons.add_sprite_button("Block", self.send_block, 205, 160, (img, img))
        self.buttons.add_sprite_button("Cancel", self.cancel_selection, 205, 180, (img, img))

    def set_pending_cmd(self, cmd):
        self.need_destination = True
        self.pending_cmd = cmd

    def unset_pending_cmd(self):
        self.need_destination = False
        self.pending_cmd = None
        self.buttons.unset_pending_button()

    def execute_pending_cmd(self, dst):
        x, y = dst
        unit = self.selection

        # FIXME do not unblock cells other units are blocking
        unit.is_blocking = False
        self.model.grid[self.find_cell((unit.x, unit.y))].unblock()

        unit.set_command("move", x, y, self.pending_cmd)
        self.unset_pending_cmd()
        self.selection = None

    def send_reap(self):
        if not self.selection:
            return
        self.set_pending_cmd(("reap", self.model.grid))

    def send_burn(self):
        if not self.selection:
            return
        self.set_pending_cmd(("burn", self.model.grid))

    def send_block(self):
        if not self.selection:
            return
        self.set_pending_cmd("block", self.model.grid)

    def cancel_selection(self):
        self.selection = None
        self.unset_pending_cmd()

    def find_unit(self, pos):
        for unit in self.units:
            if unit.rect.collidepoint(pos):
                return unit
        return None

    def find_cell(self, pos):
        x, y = pos
        return int(x / self.renderer.stride_x), int(y / self.renderer.stride_y)

    def handle_click(self, ev):
        mx, my = ev.pos
        pos = mx // SCALE_FACTOR, my // SCALE_FACTOR

        if self.selection:
            if self.buttons.process_click(pos):
                return

            if self.need_destination:
                dst = self.find_cell(pos)
                self.execute_pending_cmd(dst)
                return

        self.selection = self.find_unit(pos)

    def update(self, disp):
        self.clock.tick(FRAMES_PER_SECOND)

        for ev in pygame.event.get():
            if ev.type == QUIT:
                return None

            if ev.type == pygame.MOUSEBUTTONUP:
                self.handle_click(ev)

        for _ in range(0, UPDATES_PER_FRAME):
            dx, dy = self.model.update()

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
        self.draw_text(targ, "%.2f" % self.clock.get_fps(), (220, 2))

    def draw_population(self, targ, pop):
        if pop is None:
            return
        cnc_text = "%.2f / %.2f / %.2f" % (pop.good, pop.sick, pop.dead)
        self.draw_text(targ, cnc_text, (2, 160))
