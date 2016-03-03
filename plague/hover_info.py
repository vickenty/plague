from pyg import pygame

class HoverInfo(object):
    def __init__(self, pos):
        self.pos = pos

    def draw(self, pop, targ):
        #TODO: more suitable scaling formula
        scaled_good = -1 * (30 * pop.good / 150)
        scaled_good = max(scaled_good, -30)
        scaled_good = min(scaled_good, 0)

        scaled_sick = -1 * (30 * pop.sick / 150)
        scaled_sick = max(scaled_sick, -30)
        scaled_sick = min(scaled_sick, 0)

        scaled_dead = -1 * (30 * pop.dead / 150)
        scaled_dead = max(scaled_dead, -30)
        scaled_dead = min(scaled_dead, 0)

        good = pygame.Rect(self.pos[0], self.pos[1], 8, scaled_good)
        sick = pygame.Rect(self.pos[0] + 10, self.pos[1], 8, scaled_sick)
        dead = pygame.Rect(self.pos[0] + 20, self.pos[1], 8, scaled_dead)

        good_color = (0, 221, 43)
        sick_color = (55, 121, 143)
        dead_color = (255, 21, 13)

        pygame.draw.rect(targ, good_color, good)
        pygame.draw.rect(targ, sick_color, sick)
        pygame.draw.rect(targ, dead_color, dead)
