from random import choice, random
import bont
import data
from constants import *

class Base (object):
    face_pos = 2, 164
    name_pos = 38, 164
    text_pos = 38, 171
    finished = False
    text_maxx = 203

    def __init__(self):
        self.font = bont.Tiny()
        self.show = 150
        self.finished = False

        self.prompt_sample_played = False
        self.prompt_sample = data.load_sample("prompt.wav")
        self.prompt_sample.set_volume(0.2)

    def advance(self):
        self.show -= 1
        self.finished = self.show == 0

    def draw(self, targ):
        targ.blit(self.face, self.face_pos)
        self.font.render(targ, self.name, self.name_pos)
        self.font.render_wrap(targ, self.text, self.text_pos, self.text_maxx)

class Unit (Base):
    name = "DOCTOR"
    face_name = "faces/doctor.png"
    text_maxx = 150

    messages = {
        "prompt": "Ready to go.",
        "block": "Organise blockade to prevent people from spreading the disease.",
        "reap": "Prevent people from getting sick by disposing of dead bodies.",
        "burn": "Purge the entire city with fire.",
    }

    def __init__(self, what):
        super(Unit, self).__init__()
        self.show = -1
        self.text = self.messages[what]
        self.face = data.load_image(self.face_name)


class Random (Base):
    name = "ADVISOR"

    stats = [
        "{dead} dead citizens have been reported, my lord",
        "My lord, we counted {dead} dead bodies to date",
        "{sick} people are suffering from plague, your majesty",
        "Your honour, as many as {sick} settlers are feeling unwell",
        "{good} people have no wellbeing complaints, your greatness",
        "Only {cure} seconds left to cure our kindgom, my lord",
    ]
    bad_news = [
        "There are dead bodies on the streets"
        "Our country is in danger",
        "People are suffering, my lord",
        "My lord, we need to save our people",
        "Lord bless us!",
    ]
    wtf_news = [
        "Liege, plague is spreading",
        "There are reports of a sickness, my lord"
        "Something suspicious is going on",
    ]

    def __init__(self, pop, time_to_cure):
        super(Random, self).__init__()
        self.face = data.load_image("faces/6p.png")
        self.pop = pop
        self.time_to_cure = time_to_cure
        self.text = self.compute_news()

    def compute_news(self):
        arr = self.stats

        if random() >= 0.5:
            pop = self.pop
            if pop.sick > (pop.good + pop.dead)*0.5:
                arr = self.wtf_news
            elif pop.dead > (pop.good + pop.sick):
                arr = self.bad_news

        return choice(arr).format(
            good=int(self.pop.good),
            sick=int(self.pop.sick),
            dead=int(self.pop.dead),
            cure=int(self.time_to_cure),
        )


class LevelMessage (Base):
    def __init__(self, face, name, text, finished_cb):
        super(LevelMessage, self).__init__()
        self.name = name

        # deliberately long: tutorial and story elements
        self.show = 15 * FRAMES_PER_SECOND
        self.face = data.load_image("faces/" + face)
        self.text = text
        self.finished_cb = finished_cb

    def advance(self):
        self.show -= 1
        self.finished = self.show == 0
        if self.finished:
            self.finished_cb()

        if not self.prompt_sample_played:
            self.prompt_sample_played = True
            self.prompt_sample.play()

class Victory(Base):
    name = "GAME OVER"

    def __init__(self, pop):
        super(Victory, self).__init__()
        self.face = data.load_image("faces/6p.png")
        self.pop = pop
        self.text = self.compute_news()

    def advance(self):
        # stays forever
        pass

    def compute_news(self):
        return "You managed to save %d people!" % self.pop.good


class Loss(Victory):
    name = "GAME OVER"

    def __init__(self, minimum_living, pop):
        self.minimum_living = minimum_living
        super(Loss, self).__init__(pop)

    def compute_news(self):
        total = self.pop.done + self.pop.burnt + self.pop.dead + self.pop.sick + self.pop.good
        return "Our country is doomed! Of %d souls, %d perished in the plague, %d are ill, and %d died in a fire!" % (total, self.pop.dead, self.pop.sick, self.pop.burnt)
