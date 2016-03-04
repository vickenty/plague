from pyg import pygame
from pyg.locals import *
import game

from constants import *

def main(init_mode=game.Game):
    pygame.mixer.pre_init(44100)
    pygame.init()

    size = SCREEN_W * SCALE_FACTOR, SCREEN_H * SCALE_FACTOR

    disp = pygame.display.set_mode(size, DOUBLEBUF)
    temp = pygame.Surface((SCREEN_W, SCREEN_H))

    mode = init_mode()

    while mode is not None:
        temp.fill(SCREEN_BG)
        if mode.won:
            print "You suck slightly less than others"
            break
        mode = mode.update(temp)
        pygame.transform.scale(temp, disp.get_size(), disp)
        pygame.display.flip()

    print "Bye."
