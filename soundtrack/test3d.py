import sys, pygame, d3music
from pygame.locals import *

pygame.init()

size = width, height = 320, 240

screen = pygame.display.set_mode(size)

d3music.init()

d3music.create()

axes = ( 0, 1, 1 )

d3music.start( axes )

def process( e ):
    return axes

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            process( event )
            d3music.adjust( axes )


