# -*- coding: utf-8 -*-


class Population (object):
    def __init__(self, good, sick=0.0, dead=0.0, burnt=0.0, done=0.0):
        self.good = good
        self.sick = sick
        self.dead = dead
        self.burnt = burnt
        self.done = done

    def __add__(self, other):
        return Population(
            self.good + other.good,
            self.sick + other.sick,
            self.dead + other.dead,
            self.burnt + other.burnt,
            self.done + other.done,
        )

    def __iadd__(self, other):
        self.good += other.good
        self.sick += other.sick
        self.dead += other.dead
        self.burnt += other.burnt
        self.done += other.done
        return self

    def __sub__(self, other):
        return Population(
            self.good - other.good,
            self.sick - other.sick,
            self.dead - other.dead,
            self.burnt - other.burnt,
            self.done - other.done,
        )

    def __isub__(self, other):
        self.good -= other.good
        self.sick -= other.sick
        self.dead -= other.dead
        self.burnt -= other.burnt
        self.done -= other.done
        return self

    def infect(self, factor):
        sick = self.good * factor
        self.good -= sick
        self.sick += sick

    def kill(self, factor):
        dead = self.sick * factor
        self.sick -= dead
        self.dead += dead

    def reap(self, factor):
        reaped = self.dead * factor
        self.dead -= reaped
        self.done += reaped

    def burn(self, factor):
        self.burnt += self.good * factor
        self.burnt += self.sick * factor
        self.burnt += self.dead * factor
        self.good -= self.good * factor
        self.sick -= self.sick * factor
        self.dead -= self.dead * factor

    @property
    def not_good(self):
        return self.sick + self.dead + self.burnt + self.done

    @property
    def alive(self):
        return self.good + self.sick

    def __str__(self):
        return "% 6.1fg % 6.1fs % 6.1fd" % (self.good, self.sick, self.dead)

if __name__ == '__main__':
    p1 = Population(100)
    print p1
    for i in range(0, 10):
        p1.kill(0.1)
        p1.infect(0.05)
        print p1
