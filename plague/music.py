from pyg import pygame
from constants import *
import data
from heapq import *

class Channel (object):
    ATTACK = 0.02
    DECAY = 0.04
    CLIP = 0.01

    def __init__(self, name, path, attack=ATTACK, decay=DECAY):
        self.attack = attack
        self.decay = decay
        self.name = name
        self.path = path
        self.samp = None
        self.chan = None
        self.volume = 0.0
        self.target = 0.0
        self.modifier = 0.0

    def load(self):
        self.samp = data.load_sample(self.path)

    def play(self):
        self.chan = self.samp.play(-1)
        self.chan.set_volume(self.volume)

    def set_pause(self, pause):
        if pause:
            self.chan.pause()
        else:
            self.chan.unpause()

    def set_volume(self, volume):
        if self.chan:
            self.chan.set_volume(volume)
        self.volume = volume

    def update(self, modifier):
        eff_target = max(0, self.target + modifier)
        dv = eff_target - self.volume
        if abs(dv) < self.CLIP:
            self.set_volume(eff_target)
        else:
            factor = self.attack if dv > 0 else self.decay
            self.set_volume(self.volume + dv * factor)

class Music (object):
    BPM = 120
    UPD_BARS = 8

    BAR_TICKS = BPM / 60 * 1000
    UPD_TICKS = BAR_TICKS * UPD_BARS

    channels = [
        Channel("melody_dim", "music/melody_dim_32bar.ogg"),
        Channel("melody_major", "music/melody_major_32bar.ogg"),
        Channel("melody_minor1", "music/melody_minor_32bar.ogg"),
        Channel("melody_minor2", "music/melody_minor_second_32bar.ogg"),
        #Channel("perc_cymbal", "music/perc_cymbal_1bar.ogg"),
        #Channel("perc_gong", "music/perc_gong_1bar.ogg"),
        Channel("perc_snare", "music/perc_snare_4bar.ogg"),
        #Channel("perc_triangle", "music/perc_triangle_4bar.ogg"),
        Channel("pizzicato", "music/pizzicato_8bar.ogg"),
        Channel("pizzicato_dim", "music/pizzicato_dim_8bar.ogg"),
        Channel("strings_low", "music/strings_low_8bar.ogg"),
        Channel("strings_mid_dim", "music/strings_mid_dim_32bar.ogg"),
        Channel("strings_mid_major", "music/strings_mid_major_32bar.ogg"),
        Channel("strings_mid_minor1", "music/strings_mid_minor_32bar.ogg"),
        Channel("strings_mid_minor2", "music/strings_mid_minor_second_32bar.ogg"),
        Channel("timpani", "music/timpani_8bar.ogg"),
    ]

    presets = {
        "major": {
            "melody_major": 0.3,
            "perc_snare": 0.3,
            "pizzicato": 0.4,
            "strings_low": 0.2,
            "strings_mid_major": 0.1,
        },

        "minor1": {
            "melody_minor1": 0.4,
            "perc_snare": 0.3,
            "pizzicato": 0.4,
            "strings_low": 0.2,
            "strings_mid_minor1": 0.1,
        },

        "minor2": {
            "melody_minor2": 0.3,
            "strings_low": 0.3,
            "strings_mid_minor2": 0.1,
            "timpani": 0.2,
        },

        "diminished": {
            "melody_dim": 0.3,
            "pizzicato_dim": 0.4,
            "strings_low": 0.4,
            "strings_mid_dim": 0.2,
            "timpani": 0.2,
        },
    }

    still_mod = {
        "major": {
            "strings_mid_major": -0.1,
            "perc_snare": -0.3,
        },
        "minor1": {
            "perc_snare": -0.3,
            "strings_mid_minor1": -0.1,
        },
        "minor2": {
            "strings_low": -0.1,
            "timpani": -0.2,
            "string_mid_minor2": -0.1,
        },
        "diminished": {
            "pizzicato_dim": -0.2,
            "strings_low": -0.2,
            "timpani": -0.2,
        },
    }

    def __init__(self):
        self.loaded = False
        self.preset = None

        self.last_tick = 0
        self.play_time = 0

        self.next_time = self.UPD_TICKS
        self.next_preset = None

    def load(self):
        try:
            for chan in self.channels:
                chan.load()
            self.loaded = True
        except:
            print "Unable to load music files, you will hear no music. Sorry."

    def play(self):
        if not self.loaded:
            return

        for chan in self.channels:
            chan.play()

    def reset(self, name):
        self.preset = name
        preset = self.presets[name]

        for chan in self.channels:
            volume = preset.get(chan.name, 0.0)
            chan.set_volume(volume)
            chan.target = volume

    def switch(self, name):
        if not self.loaded:
            self.reset(name)
            return

        self.preset = name
        preset = self.presets[name]

        for chan in self.channels:
            chan.target = preset.get(chan.name, 0.0)

    def enqueue(self, name):
        self.next_preset = name

    def update(self, modifier):
        if self.play_time > self.next_time:
            self.next_time += self.UPD_TICKS
            if self.next_preset is not None:
                self.switch(self.next_preset)
                self.next_preset = None

        for chan in self.channels:
            mod = self.still_mod[self.preset].get(chan.name, 0)
            chan.update(mod * modifier)

        curr_tick = pygame.time.get_ticks()
        self.play_time += curr_tick - self.last_tick
        self.last_tick = curr_tick

music = Music()

if __name__ == '__main__':
    from pyg import pygame
    from pyg.locals import *
    
    pygame.mixer.pre_init(44100)
    pygame.init()
    pygame.mixer.set_num_channels(32)

    clock = pygame.time.Clock()
    disp = pygame.display.set_mode((200, 200))

    
    sequence = ["major", "minor1", "minor2", "diminished" ]
    sequence.reverse()

    print "Loading"
    music.load()

    music.reset(sequence.pop())
    music.play()

    mod = 0
    while True:
        for ev in pygame.event.get():
            if ev.type == KEYDOWN and ev.key == K_SPACE:
                mod = 1 - mod
                print mod

        clock.tick(10)
        music.update(mod)

        if music.next_preset is None and sequence:
            music.enqueue(sequence.pop())
