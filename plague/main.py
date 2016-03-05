from pyg import pygame
from pyg.locals import *
import game
import mouse
import data
import title

from constants import *


def main(init_mode=title.Title):
    pygame.mixer.pre_init(44100)
    pygame.init()
    mouse.init()

    pygame.display.set_caption(GAME_NAME)

    pygame.mouse.set_visible(False)

    size = SCREEN_W * SCALE_FACTOR, SCREEN_H * SCALE_FACTOR

    disp = pygame.display.set_mode(size, DOUBLEBUF)
    temp = pygame.Surface((SCREEN_W, SCREEN_H))
    uibg = data.load_image("uibg.png")

    mode = init_mode()

    while mode is not None:
        for ev in pygame.event.get():
            if ev.type == QUIT:
                return

            if ev.type == pygame.MOUSEBUTTONUP:
                mode.handle_click(ev)

        temp.fill(SCREEN_BG)
        temp.blit(uibg, (0, GRID_MAX_H * GRID_H + 1))

        mode = mode.update(temp)
        mouse.draw(temp)
        pygame.transform.scale(temp, disp.get_size(), disp)
        pygame.display.flip()

    print "Bye."
