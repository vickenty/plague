from random import choice
import bont

class Newsflash(object):
    news = [
        "LIEGE, PLAGUE IS SPREADING",
        "OUR COUNTRY IS IN DANGER",
        "PEOPLE ARE SUFFERING, MY LORD",
        "MY LORD, WE NEED TO SAVE OUR PEOPLE",
        "LORD BLESS US",
    ]

    def __init__(self, color, pop, pos):
        self.font = bont.Tiny()
        self.color = color
        self.pos = pos
        self.pop = pop

        self.show = 90
        self.finished = False

        self.text = self.compute_news()

    def compute_news(self):
        return choice(self.news)

    def advance(self):
        self.show -= 1
        self.finished = self.show == 0

    def draw(self, targ):
        self.font.render(targ, self.text, self.pos)
