from pyg import pygame
from pyg.locals import *
import game

from constants import *

def main():
    pygame.mixer.pre_init(44100)
    pygame.init()

    disp = pygame.display.set_mode((SCREEN_W, SCREEN_H), DOUBLEBUF)

    mode = game.Game()

    while mode is not None:
        mode = mode.update(disp)
        pygame.display.flip()

    print "Bye."
