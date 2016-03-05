from pyg import pygame
from pyg.locals import *

from constants import *
import buttons
import data
import sim
import render
import game
import sim
from music import music

class Title (object):
    def __init__(self):
        self.title = data.load_image("title.png")

        self.next_mode = self
        self.model = sim.Map("level1")
        self.renderer = render.Renderer()
        self.renderer.draw(self.model)

        def play_level(n):
            def build_level():
                self.new_mode = game.Game(sim.Map("level" + str(n)))
            return build_level

        self.buttons = buttons.ButtonRegistry()
        self.buttons.add_sprite_button("Level 1", play_level(1), 100, 160)
        self.buttons.add_sprite_button("Level 2", play_level(2), 150, 160)
        self.buttons.add_sprite_button("Level 3", play_level(3), 205, 160)
        self.buttons.add_sprite_button("Tutorial", self.new_tutorial, 150, 180)
        self.buttons.add_sprite_button("Quit", self.quit_game, 205, 180)

        self.new_mode = self

        music.enqueue("major")

    def new_tutorial(self):
        self.new_mode = game.Game(sim.Map("tut1"))

    def quit_game(self):
        self.new_mode = None

    def handle_click(self, ev):
        mx, my = ev.pos
        pos = mx // SCALE_FACTOR, my // SCALE_FACTOR

        if self.buttons.process_click(pos):
            return

    def update(self, targ):
        music.update(0.0)

        for ev in pygame.event.get():
            if ev.type == QUIT:
                return None

            if ev.type == pygame.MOUSEBUTTONUP:
                self.handle_click(ev)

        self.renderer.blit(targ)
        targ.blit(self.title, (2, 2))

        self.buttons.draw(targ)

        pygame.display.flip()
        return self.new_mode

if __name__ == '__main__':
    import main
    main.main(Title)
