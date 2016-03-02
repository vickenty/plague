try:
    import pygame_sdl2 as pygame
    VERSION = 2
except ImportError:
    import pygame
    VERSION = 1
