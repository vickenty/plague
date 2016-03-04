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
import mouse
import bont
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

    cell_highlight_image = pygame.Surface((GRID_W, GRID_H), pygame.SRCALPHA);
    cell_highlight_image.fill((0xff, 0xff, 0xff, 0x33), (0, 0, GRID_W, GRID_H))

    def __init__(self):
        self.model = sim.Map("level1")

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
        self.win_time = self.model.conf.time * FRAMES_PER_SECOND

        self.font = bont.Tiny()
        self.news_font = data.load_font(*NEWS_FONT)
        self.selection = None
        self.need_destination = False
        self.pending_cmd = None

        self.buttons = buttons.ButtonRegistry()

        self.buttons.add_sprite_button("Reap", self.send_reap, 150, 160)
        self.buttons.add_sprite_button("Burn", self.send_burn, 150, 180)
        self.buttons.add_sprite_button("Block", self.send_block, 205, 160)
        self.buttons.add_sprite_button("Cancel", self.cancel_selection, 205, 180)

        self.advisor_face = data.load_image("faces/6p.png")

        self.frame = 0
        self.newsflash = None

        self.hover_info = hover_info.HoverInfo()

    def set_pending_cmd(self, cmd):
        mouse.set_cursor("target")
        self.need_destination = True
        self.pending_cmd = cmd

    def unset_pending_cmd(self):
        mouse.set_cursor("default")
        self.need_destination = False
        self.pending_cmd = None
        self.buttons.unset_pending_button()
        self.newsflash = None

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
                self.newsflash = None
                dst = self.find_cell(pos)
                self.execute_pending_cmd(dst)
                return

        if self.selection:
            self.newsflash = None

        self.selection = self.find_unit(pos)

        if self.selection:
            self.newsflash = newsflash.Unit("doctor_prompt")

    def update(self, disp):
        self.frame += 1
        self.clock.tick(FRAMES_PER_SECOND)

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

        census = self.model.census

        self.draw_fps(disp)

        self.draw_newsflash(disp, census)
        self.draw_cell_hover(disp)

        if census is not None and census.good < 1.0 and census.sick < 1.0:
            return GameOver(False, census)
        elif self.frame >= self.win_time:
            return GameOver(True, census)

        return self

    def draw_text(self, targ, text, pos):
        self.font.render(targ, text, pos)

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
        if random.random() > 0.8:
            self.newsflash = newsflash.Random(pop)

    def draw_cell_hover(self, targ):
        (mx, my) = pygame.mouse.get_pos()
        mpos = mx // SCALE_FACTOR, my // SCALE_FACTOR
        cpos = self.find_cell(mpos)

        if cpos not in self.model.grid:
            return

        (cx, cy) = cpos[0] * GRID_W, cpos[1] * GRID_H
        cell = self.model.grid[cpos]

        highlight_cell = True   # TODO This mode may depend on a game state
        if highlight_cell:
            targ.blit(self.cell_highlight_image, (cx, cy, 0, 0))

        show_cell_stats = True  # TODO This mode may depend on a game state
        if show_cell_stats:
            x, y = (cx, cy) if STICK_HOVER_INFO_TO_CELL else mpos
            self.hover_info.draw(x, y, cell.pop, targ)


class GameOver(object):
    def __init__(self, won, census):
        self.census = census
        self.won = won
        self.clock = pygame.time.Clock()

    def update(self, disp):
        self.clock.tick(FRAMES_PER_SECOND)
        if self.won:
            disp.fill((0, 255, 0))
        else:
            disp.fill((255, 0, 0))
        return self

    def handle_click(self):
        pass
