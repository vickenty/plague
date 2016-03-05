from collections import defaultdict

from pyg import pygame
from pyg.locals import *
import random
import re

import render
import unit
import buttons
import data
import newsflash
import hover_info
import mouse
import bont
import effects
import sim
from music import music
from constants import *


class Game (object):
    text_color = (255, 255, 255)

    cell_highlight_image = pygame.Surface((GRID_W, GRID_H), pygame.SRCALPHA);
    cell_highlight_image.fill((0xff, 0xff, 0xff, 0x33), (0, 0, GRID_W, GRID_H))

    def __init__(self, m):
        self.model = m

        self.units = [unit.Unit(self.model, x, y) for x, y in self.model.conf.units]

        self.all_effects = pygame.sprite.Group()
        self.individual_effects = defaultdict(pygame.sprite.Group)
        self.all_walkers = pygame.sprite.Group()

        self.renderer = render.Renderer()
        self.renderer.draw(self.model)

        self.clock = pygame.time.Clock()

        # Win conditions
        self.win_duration_sec    = self.model.conf.game["duration"]
        self.win_duration_frames = self.model.conf.game["duration"] * FRAMES_PER_SECOND
        self.win_good_min_threshold  = self.model.conf.game["good_min_threshold"]
        self.win_sick_max_threshold  = self.model.conf.game["sick_max_threshold"]

        self.font = bont.Tiny()
        self.news_font = data.load_font(*NEWS_FONT)
        self.over_font = data.load_font(*OVER_FONT)
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
        # don't fire a newsflash right away
        self.next_newsflash = 5 * FRAMES_PER_SECOND

        self.hover_info = hover_info.HoverInfo()

        self.over = None
        self.paused = False
        self.final_click = False

        music.enqueue("minor1")

    def set_pending_cmd(self, cmd):
        mouse.set_cursor("target", 160)
        self.newsflash = newsflash.Unit(cmd[0])
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

        if self.over is not None:
            self.final_click = True

        if self.paused:
            # unpause and finish newsflash
            if self.newsflash is not None:
                self.newsflash.show = 1
            self.paused = False
            return

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
            self.newsflash = newsflash.Unit("prompt")

    def update_one(self):
        dx, dy, new_dead, new_sick, caught_fire = self.model.update()
        cell = self.model.grid[dx, dy]
        self.individual_effects[dx, dy].update()
        if new_dead > 0 and cell.view != "field":
            effects.Ghost(new_dead, dx * GRID_W, dy * GRID_H, self.all_effects, self.individual_effects[dx, dy])
        if new_sick > 0:
            effects.Infection(dx * GRID_W, dy * GRID_H, self.all_effects, self.individual_effects[dx, dy])
        if caught_fire:
            effects.Fire(dx * GRID_W, dy * GRID_H, self.all_effects, self.individual_effects[dx, dy])

        flow_dir = max(cell.incoming_acu.keys(), key=lambda d: cell.incoming_acu[d])
        if cell.incoming_acu[flow_dir] >= POP_FLOW_ALIVE_NR_TRIGGER:
            dirx, diry = flow_dir
            # Shift animation to the cell-origin of the flow
            dx, dy = dx - dirx, dy - diry
            # Do not fire up more than one animation effect at the same time
            if len(self.individual_effects[dx, dy]) == 0 and random.random() <= POP_FLOW_PROBABILiTY_TRIGGER:
                effects.Walker(dx * GRID_W, dy * GRID_H, dirx, diry, self.all_effects, self.individual_effects[dx, dy])
            cell.incoming_acu[flow_dir] = 0.0

    def update(self, disp):
        census = self.model.census

        if census is None:
            music.update(1.0)
        elif census.alive > 1.0:
            music.update(1 - min(1, max(0, census.good / census.alive)))
        else:
            music.update(0.0)

        if not self.paused:
            self.frame += 1
        self.clock.tick(FRAMES_PER_SECOND)

        if self.over is None and not self.paused:
            # let the doc warp to the starting location
            if self.frame > 1:
                if len(self.model.conf.messages) > 0:
                    self.play_level_message()

            if census is not None:
                # Determine the game outcome: win or defeat
                if census.good < self.win_good_min_threshold or census.sick > self.win_sick_max_threshold:
                    self.over = False
                elif self.frame >= self.win_duration_frames:
                    self.over = True

            for _ in range(0, UPDATES_PER_FRAME):
                self.update_one()

        self.renderer.blit(disp)
        self.all_effects.draw(disp)

        if self.over is not None:
            if self.over:
                self.draw_game_over(disp, "SUCCESS")
                newsflash.Victory(census).draw(disp)
                self.paused = True
                if self.final_click:
                    n = self.model.next_level()
                    if n is not None:
                        return Game(n)
                    return self
            else:
                self.draw_game_over(disp, "FAIL")
                newsflash.Loss(census).draw(disp)
                return self

        for unit in self.units:
            if not self.paused:
                unit.update()
            unit.draw(disp, self.selection == unit, self.paused)

        if self.selection:
            self.buttons.draw(disp)

        self.draw_fps(disp)

        self.draw_cell_hover(disp)

        self.draw_newsflash(disp, census)

        return self

    def draw_game_over(self, targ, text):
        t = self.over_font.render(text, True, self.text_color)
        w, h = t.get_size()
        sw, sh = SCREEN_W, SCREEN_H - 40
        targ.blit(t, (sw / 2 - w / 2, sh / 2 - h / 2))

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

        if self.frame >= self.next_newsflash and pop is not None:
            curr_time = self.frame / FRAMES_PER_SECOND
            self.newsflash = newsflash.Random(curr_time, pop, self.win_duration_sec)
            self.next_newsflash = self.frame + random.randint(1 * FRAMES_PER_SECOND, 5 * FRAMES_PER_SECOND)

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

    def play_level_message(self):
        game_time = self.frame / FRAMES_PER_SECOND
        if not self.newsflash:
            message = self.model.conf.messages[0]
            if game_time > int(message["min_time"]):
                self.model.conf.messages.pop(0)
                self.paused = True
                def finished_cb():
                    self.paused = False

                self.newsflash = newsflash.LevelMessage(message["face"], message["name"], message["msg"], finished_cb)
