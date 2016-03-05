from pyg import pygame
from constants import *

INFO_BAR_NR = 3

INFO_BAR_THICKNESS = 2
INFO_BAR_SPACE = 1

INFO_BORDER = 1
INFO_OFFSET = 3
INFO_WIDTH = 10
INFO_HEIGHT = INFO_BORDER * 2 + (INFO_BAR_THICKNESS + INFO_BAR_SPACE) * INFO_BAR_NR - INFO_BAR_SPACE

INFO_BAR_MAX_WIDTH = INFO_WIDTH - INFO_BORDER * 2

# TODO Perhaps it should be dynamic and depend on the cell with the highest population
MAX_VALUE = 20

INFO_COLOR = (0, 0, 0)
GOOD_COLOR = (0, 221, 43)
SICK_COLOR = (55, 121, 143)
DEAD_COLOR = (255, 21, 13)

class HoverInfo(object):
    def scale(self, val):
        scaled = min(val, MAX_VALUE)
        scaled = scaled * (1.0 * INFO_BAR_MAX_WIDTH / MAX_VALUE)
        scaled = int(scaled)
        return scaled

    def draw(self, x, y, pop, targ):
        scaled_good = self.scale(pop.good)
        scaled_sick = self.scale(pop.sick)
        scaled_dead = self.scale(pop.dead)

        if x > GRID_MAX_W * GRID_W - INFO_WIDTH - GRID_W - INFO_OFFSET:
            x = x - INFO_WIDTH - INFO_OFFSET
        else:
            x = x + GRID_W + INFO_OFFSET

        if y > GRID_MAX_H * GRID_H - INFO_HEIGHT - GRID_H - INFO_OFFSET:
            y = y - INFO_HEIGHT - INFO_OFFSET
        else:
            y = y + GRID_H + INFO_OFFSET

        # Avoid showing an empty popup
        if scaled_good + scaled_sick + scaled_dead == 0:
            return

        background = pygame.Rect(x, y, INFO_WIDTH, INFO_HEIGHT)
        pygame.draw.rect(targ, INFO_COLOR, background)

        if scaled_good > 0:
            good = pygame.Rect(x + INFO_BORDER, y + INFO_BORDER + (INFO_BAR_THICKNESS + INFO_BAR_SPACE) * 0, scaled_good, INFO_BAR_THICKNESS)
            pygame.draw.rect(targ, GOOD_COLOR, good)

        if scaled_sick > 0:
            sick = pygame.Rect(x + INFO_BORDER, y + INFO_BORDER + (INFO_BAR_THICKNESS + INFO_BAR_SPACE) * 1, scaled_sick, INFO_BAR_THICKNESS)
            pygame.draw.rect(targ, SICK_COLOR, sick)

        if scaled_dead > 0:
            dead = pygame.Rect(x + INFO_BORDER, y + INFO_BORDER + (INFO_BAR_THICKNESS + INFO_BAR_SPACE) * 2, scaled_dead, INFO_BAR_THICKNESS)
            pygame.draw.rect(targ, DEAD_COLOR, dead)
