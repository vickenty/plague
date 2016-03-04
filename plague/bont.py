import data
class Bont (object):
    def __init__(self):
        self.image = data.load_image(self.name)
    
    def render(self, targ, text, (tx, ty)):
        for i, c in enumerate(text):
            c = ord(c)
            x = (c % 32) * self.w
            y = (c / 32) * self.h
            targ.blit(self.image, (tx + i * self.w, ty), (x, y, self.w, self.h))

class Tiny (Bont):
    name = "font-tiny.png"
    w = 5
    h = 7

