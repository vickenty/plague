from random import choice
import bont
import data

class Base (object):
    face_pos = 2, 164
    name_pos = 38, 164
    text_pos = 38, 171
    finished = False

    def __init__(self):
        print "base init"
        self.font = bont.Tiny()
        self.show = 90
        self.finished = False

    def advance(self):
        self.show -= 1
        self.finished = self.show == 0

    def draw(self, targ):
        targ.blit(self.face, self.face_pos)
        self.font.render(targ, self.name, self.name_pos)
        self.font.render(targ, self.text, self.text_pos)

class Unit (Base):
    name = "DOCTOR"
    messages = {
        "doctor_prompt": ("faces/doctor.png", "Ready to go"),
    }

    def __init__(self, what):
        super(Unit, self).__init__()
        self.show = -1
        self.face_name, self.text = self.messages[what]
        self.face = data.load_image(self.face_name)

class Random (Base):
    name = "ADVISOR"

    news = [
        "Liege, plague is spreading",
        "Our country is in danger",
        "People are suffering, my lord",
        "My lord, we need to save our people",
        "LORD BLESS US",
    ]

    def __init__(self, pop):
        super(Random, self).__init__()
        self.face = data.load_image("faces/6p.png")
        self.text = self.compute_news()

    def compute_news(self):
        return choice(self.news)
