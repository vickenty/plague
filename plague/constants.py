SCREEN_W = 256
SCREEN_H = 200
FRAMES_PER_SECOND = 60
UPDATES_PER_FRAME = 80
GRID_W = 8          # Should have been called CELL_W
GRID_H = 8          # Should have been called CELL_H
GRID_MAX_W = 32
GRID_MAX_H = 20
SCALE_FACTOR = 3
UI_FONT = ("dejavu-sans.ttf", 9)
DEAD_TTL = 6
NEWS_FONT = ("dejavu-sans.ttf", 8)
GAME_NAME = "Life, a game of"
SCREEN_BG = 64, 64, 64
STICK_HOVER_INFO_TO_CELL = False
OVER_FONT = ("dejavu-sans.ttf", 20)

# game balance
REAP_FACTOR = 0.01
# fire
# proportion of population (healthy, sick, and dead) that's reduced per update
# when burning
BURN_FACTOR = 0.9
FIRE_SPREAD_CHANCE_PER_FRAME = 0.3

# disease
MAX_INFECT_RATIO_PER_FRAME = 0.1

# (INFECTION_COEFF_SICK * sick + INFECTION_COEFF_DEAD * dead) / good / INFECTION_SCALE_FACTOR
INFECTION_COEFF_SICK = 0.5
INFECTION_COEFF_DEAD = 1
INFECTION_SCALE_FACTOR = 50

POP_FLOW_ALIVE_NR_TRIGGER = 50
POP_FLOW_PROBABILiTY_TRIGGER = 0.2
