import sys, pygame
from pygame.locals import *

def get_max( complexity, energy, threshold = 0 ):
    def fun( axes ):
        m, c, e = axes
        trig = max( complexity * c, energy * e )
        return 0 if trig <= threshold \
            else ( trig - threshold ) / ( 1 - threshold )

    return fun

def get_lim( lo_mood, hi_mood, c_threshold = 0 ):
    def fun( axes ):
        m, e, c = axes
        cond = 1 if m >= lo_mood and m < hi_mood \
            else 0

        if cond == 0 or c <= c_threshold:
            return 0
        else:
            return ( c - c_threshold ) / ( 1 - c_threshold )

    return fun

_instruments = {
    "snare" : get_max( 1, 1 ),
    "hihat" : get_max( 1, 1, 0.33 ),
    "timp"  : get_max( 1, 1, 0.66 ),
    "lopizz": get_max( 0, 1 ),
    "lopizz": get_max( 0, 1 ),
    "bass"  : get_max( 0, 1, 0.33 ),
    "kick"  : get_max( 0, 1, 0.66 ),
    "hipizz": get_max( 1, 0, 0.25 ),
    "himarc": get_max( 1, 0, 0.40 ),
    "strmaj": get_lim( 0, 0.25 ),
    "melmaj": get_lim( 0, 0.25, 0.2 ),
    "strmin": get_lim( 0.25, 0.5 ),
    "melmin": get_lim( 0.25, 0.5, 0.3 ),
    "straug": get_lim( 0.5, 0.75 ),
    "melaug": get_lim( 0.5, 0.75, 0.5 ),
    "strdim": get_lim( 0.75, 1.01 ),
    "meldim": get_lim( 0.75, 1.01, 0.7 ),
}

_mixer = {}

def init():
    pygame.init()

    pygame.mixer.init(
        frequency = 44100, size = -16, channels = 2, buffer = 4096 )

    pygame.mixer.set_num_channels(16)

def create_mixer( config ):
    mixer = {}

    for inst, handler in config.iteritems():
        track = { "sound" : pygame.mixer.Sound( "%s.ogg" % inst ) }
        track["sound"].set_volume(1)
        track["handler"] = handler
        mixer[inst] = track

    return mixer

def create():
    global _mixer
    
    _mixer = create_mixer( _instruments )

# axes: mood, complexity, energy

def adjust( axes ):
    global _mixer

    for track in _mixer:
        vol = _mixer[track]["handler"]( axes )

        print "Setting volume of track %s to %.2f" % ( track, vol )

        _mixer[track]["channel"].set_volume( vol )

def start( axes = (0, 1, 1 ) ):
    global _mixer

    for track in _mixer:
        _mixer[track]["channel"] = _mixer[track]["sound"].play( loops = -1 )

    adjust( axes );

