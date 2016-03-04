from pyg import pygame
from constants import *

INFO_WIDTH = 12
INFO_HEIGHT = 10

class HoverInfo(object):
    def draw(self, x, y, pop, targ):
        #TODO: more suitable scaling formula
        scaled_good = -1 * (pop.good / 10)
        scaled_good = max(scaled_good, -10)
        scaled_good = min(scaled_good, 0)

        scaled_sick = -1 * (pop.sick / 10)
        scaled_sick = max(scaled_sick, -10)
        scaled_sick = min(scaled_sick, 0)

        scaled_dead = -1 * (pop.dead / 10)
        scaled_dead = max(scaled_dead, -10)
        scaled_dead = min(scaled_dead, 0)

        if x > SCREEN_W / 2:
            x = x - INFO_WIDTH
        else:
            x = x + GRID_W

        y = y + INFO_HEIGHT + GRID_H

        if y > SCREEN_H / 2:
            y = y - INFO_HEIGHT - GRID_H

        background = pygame.Rect(x - 1, y - INFO_HEIGHT + 3, INFO_WIDTH, INFO_HEIGHT)
        good = pygame.Rect(x, y, -1 * scaled_good, 2)
        sick = pygame.Rect(x, y - 3, -1 * scaled_sick, 2)
        dead = pygame.Rect(x, y - 6, -1 * scaled_dead, 2)

        good_color = (0, 221, 43)
        sick_color = (55, 121, 143)
        dead_color = (255, 21, 13)

        pygame.draw.rect(targ, (0, 0, 0), background)
        pygame.draw.rect(targ, good_color, good)
        pygame.draw.rect(targ, sick_color, sick)
        pygame.draw.rect(targ, dead_color, dead)
