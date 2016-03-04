from pyg import pygame
from pyg.locals import *
import game
import mouse

from constants import *


def main(init_mode=game.Game):
    pygame.mixer.pre_init(44100)
    pygame.init()
    mouse.init()

    pygame.display.set_caption(GAME_NAME)

    pygame.mouse.set_visible(False)

    size = SCREEN_W * SCALE_FACTOR, SCREEN_H * SCALE_FACTOR

    disp = pygame.display.set_mode(size, DOUBLEBUF)
    temp = pygame.Surface((SCREEN_W, SCREEN_H))

    mode = init_mode()

    while mode is not None:
        for ev in pygame.event.get():
            if ev.type == QUIT:
                return

            if ev.type == pygame.MOUSEBUTTONUP:
                mode.handle_click(ev)

        temp.fill(SCREEN_BG)

        mode = mode.update(temp)
        mouse.draw(temp)
        pygame.transform.scale(temp, disp.get_size(), disp)
        pygame.display.flip()

    print "Bye."
