from collections import defaultdict

from pyg import pygame
from pyg.locals import *
import random

import sim
import render
import unit
import buttons
import data
import newsflash
import hover_info
import anim
from constants import *


class Ghost (pygame.sprite.Sprite):
    def __init__(self, count, pos_x, pos_y, *groups):
        if count > 1:
            label = "%d" % count
        else:
            label = ""

        pos_y -= 2

        spr = data.load_image("ghost.png")
        w, h = spr.get_size()

        fnt = data.load_image("digits.png")
        fnt_w = 4
        fnt_h = 5

        txt_x = w + 1
        txt_y = 2

        self.image = pygame.Surface((txt_x + fnt_w * len(label), h), SRCALPHA)
        self.image.blit(spr, (0, 0))
        for i, c in enumerate(label):
            fnt_x = int(c) * fnt_w
            self.image.blit(fnt, (txt_x + i * fnt_w, txt_y), (fnt_x, 0, fnt_w, fnt_h))

        self.rect = pygame.Rect(pos_x, pos_y, *self.image.get_size())
        self.targ_y = pos_y - DEAD_TTL // 2

        pygame.sprite.Sprite.__init__(self, *groups)

    def update(self):
        self.rect.y -= 1
        if self.rect.y <= self.targ_y:
            self.kill()


class Fire(anim.Anim):
    def __init__(self, x, y, *groups):
        anim.Anim.__init__(self, "flame-8.png", 16, x-4, y-3)
        pygame.sprite.Sprite.__init__(self, *groups)


class Game (object):
    text_color = (255, 255, 255)

    def __init__(self):
        self.model = sim.Map()
        self.model.load("level1")

        self.units = [
            unit.Unit(self.model, self.model.width // 2, self.model.height // 2),
            unit.Unit(self.model, self.model.width // 3, self.model.height // 3),
        ]

        self.all_effects = pygame.sprite.Group()
        self.individual_effects = defaultdict(pygame.sprite.Group)

        self.units[0].set_command("move", 1, 1, ("idle",))
        self.units[1].set_command("move", 3, 12, ("idle",))

        self.renderer = render.Renderer()
        self.renderer.draw(self.model)

        self.clock = pygame.time.Clock()

        self.font = data.load_font(*UI_FONT)
        self.news_font = data.load_font(*NEWS_FONT)
        self.selection = None
        self.need_destination = False
        self.pending_cmd = None

        self.buttons = buttons.ButtonRegistry()

        img = data.load_image("button-scroll.png")

        self.buttons.add_sprite_button("Reap", self.send_reap, 150, 160, (img, img))
        self.buttons.add_sprite_button("Burn", self.send_burn, 150, 180, (img, img))
        self.buttons.add_sprite_button("Block", self.send_block, 205, 160, (img, img))
        self.buttons.add_sprite_button("Cancel", self.cancel_selection, 205, 180, (img, img))

        self.frame = 0
        self.newsflash = None

        self.hover_info = hover_info.HoverInfo((110, 190))

    def set_pending_cmd(self, cmd):
        self.need_destination = True
        self.pending_cmd = cmd

    def unset_pending_cmd(self):
        self.need_destination = False
        self.pending_cmd = None
        self.buttons.unset_pending_button()

    def execute_pending_cmd(self, dst):
        x, y = dst
        self.unblock_cell()
        self.selection.set_command("move", x, y, self.pending_cmd)
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
        self.set_pending_cmd(("block", self.model.grid))

    def cancel_selection(self):
        self.selection = None
        self.unset_pending_cmd()

    def unblock_cell(self):
        unit = self.selection
        unit.is_blocking = False
        x, y = self.find_cell((unit.x, unit.y))
        for u in self.units:
            if not u.is_blocking:
                continue
            ux, uy = self.find_cell((u.x, u.y))
            if ux == x and uy == y:
                return
        self.model.grid[x, y].unblock()

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
        self.frame += 1
        self.clock.tick(FRAMES_PER_SECOND)

        for ev in pygame.event.get():
            if ev.type == QUIT:
                return None

            if ev.type == pygame.MOUSEBUTTONUP:
                self.handle_click(ev)

        for _ in range(0, UPDATES_PER_FRAME):
            dx, dy, new_dead, caught_fire = self.model.update()
            self.individual_effects[dx, dy].update()
            if new_dead > 0 and self.model.grid[dx, dy].view != "field":
                Ghost(new_dead, dx * GRID_W, dy * GRID_H, self.all_effects, self.individual_effects[dx, dy])
            if caught_fire:
                Fire(dx * GRID_W, dy * GRID_H, self.all_effects, self.individual_effects[dx, dy])

        self.renderer.blit(disp)

        for unit in self.units:
            unit.update()
            unit.draw(disp, self.selection == unit)

        self.all_effects.draw(disp)

        if self.selection:
            self.buttons.draw(disp)

        self.draw_hover_info(disp)

        self.draw_fps(disp)
        self.draw_population(disp, self.model.census)
        self.draw_newsflash(disp, self.model.census)

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

    def draw_newsflash(self, targ, pop):
        news = self.newsflash
        if news is not None:
            news.advance()
            news.draw(targ)
            if news.finished:
                self.newsflash = None
            return

        # TODO compute random cool off time

        self.newsflash = newsflash.Newsflash(self.news_font, self.text_color, pop, (2, 180))

    def draw_hover_info(self, targ):
        (mx, my) = pygame.mouse.get_pos()
        pos = mx // SCALE_FACTOR, my // SCALE_FACTOR
        m_cell_pos = self.find_cell(pos)

        if m_cell_pos in self.model.grid:
            cell = self.model.grid[m_cell_pos]
            pop = cell.pop

            self.hover_info.draw(pop, targ)
