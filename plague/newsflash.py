from random import choice, random
import bont
import data

class Base (object):
    face_pos = 2, 164
    name_pos = 38, 164
    text_pos = 38, 171
    finished = False
    text_maxx = 203

    def __init__(self):
        self.font = bont.Tiny()
        self.show = 90
        self.finished = False

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
        "burn": "Cleanse the entire city with fire.",
    }

    def __init__(self, what):
        super(Unit, self).__init__()
        self.show = -1
        self.text = self.messages[what]
        self.face = data.load_image(self.face_name)


class Random (Base):
    name = "ADVISOR"

    stats = [
        "Dead: {dead}",
        "Sick: {sick}",
        "Healthy: {good}",
        "Time to cure: {cure} seconds",
    ]
    bad_news = [
        "There are dead bodies on the streets"
        "Our country is in danger",
        "People are suffering, my lord",
        "My lord, we need to save our people",
        "LORD BLESS US",
    ]
    wtf_news = [
        "Liege, plague is spreading",
        "There are reports of a sickness, my lord"
        "Something suspicious is going on",
    ]

    def __init__(self, curr_time, pop, human_win_time):
        super(Random, self).__init__()
        self.face = data.load_image("faces/6p.png")
        self.pop = pop
        self.time_to_cure = human_win_time - curr_time
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
    name = "TUTORIAL"

    def __init__(self, text, finished_cb):
        super(LevelMessage, self).__init__()
        self.show = 180
        self.face = data.load_image("faces/6p.png")
        self.text = text
        self.finished_cb = finished_cb

    def advance(self):
        self.show -= 1
        self.finished = self.show == 0
        if self.finished:
            self.finished_cb()

class Victory(Random):
    def compute_news(self):
        return "You managed to save %d people!" % self.pop.good


class Loss(Random):
    def compute_news(self):
        return "Our country is doomed!"
