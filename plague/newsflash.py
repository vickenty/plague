from random import choice


class Newsflash(object):
    news = [
        "NEWS AT 11: YOU SUCK",
        "TRUMP HAS BEEN ELECTED",
    ]

    def __init__(self, font, color, pop, pos):
        self.font = font
        self.color = color
        self.pos = pos
        self.pop = pop

        self.show = 200
        self.finished = False

        self.text = self.compute_news()

    def compute_news(self):
        return choice(self.news)

    def advance(self):
        print "Showing: %d" % self.show
        self.show -= 1
        self.finished = self.show == 0

    def draw(self, targ):
        buf = self.font.render(self.text, True, self.color)
        targ.blit(buf, self.pos)
