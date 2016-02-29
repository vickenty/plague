# -*- coding: utf-8 -*-


class Population (object):
    def __init__(self, good, sick=0.0, dead=0.0):
        self.good = good
        self.sick = sick
        self.dead = dead

    def __add__(self, other):
        return Population(
            self.good + other.good,
            self.sick + other.sick,
            self.dead + other.dead,
        )

    def __iadd__(self, other):
        self.good += other.good
        self.sick += other.sick
        self.dead += other.dead
        return self

    def __sub__(self, other):
        return Population(
            self.good - other.good,
            self.sick - other.sick,
            self.dead - other.dead,
        )

    def __isub__(self, other):
        self.good -= other.good
        self.sick -= other.sick
        self.dead -= other.dead
        return self

    def infect(self, factor):
        sick = self.good * factor
        self.good -= sick
        self.sick += sick

    def kill(self, factor):
        dead = self.sick * factor
        self.sick -= dead
        self.dead += dead

    def __str__(self):
        return "% 6.1fg % 6.1fs % 6.1fd" % (self.good, self.sick, self.dead)

if __name__ == '__main__':
    p1 = Population(100)
    print p1
    for i in range(0, 10):
        p1.kill(0.1)
        p1.infect(0.05)
        print p1
