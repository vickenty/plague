import sys
import pygame
import d3music
from pygame.locals import *

pygame.init()

size = width, height = 320, 240

screen = pygame.display.set_mode(size)

d3music.init()

d3music.create()

axes = [0, 1, 1]

d3music.start(axes)

_controls = [{
    K_q: -20,
    K_w: -10,
    K_e: -5,
    K_r: 5,
    K_t: 10,
    K_y: 20
}, {
    K_a: -20,
    K_s: -10,
    K_d: -5,
    K_f: 5,
    K_g: 10,
    K_h: 20
}, {
    K_z: -20,
    K_x: -10,
    K_c: -5,
    K_v: 5,
    K_b: 10,
    K_n: 20
}]


def process(ev, ax):
    changes = 0

    for i, val in enumerate(_controls):
        if ev.key in val:
            ax[i] += val[ev.key] / 100.0

            changes = 1

        if ax[i] > 1:
            ax[1] = 1
        elif ax[i] < 0:
            ax[i] = 0

    if changes:
        print "mood: %.2f complexity: %.2f energy: %.2f" % ax[0], ax[1], ax[2]

    return changes

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if process(event, axes):
                d3music.adjust(axes)
