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
        return tx + i * self.w

    def get_width(self, text):
        return len(text) * self.w

    def render_wrap(self, targ, text, (tx, ty), maxx=150):
        x = tx
        for word in text.split(" "):
            if x + len(word) * self.w > maxx:
                ty += self.h
                x = tx
            x = self.render(targ, word, (x, ty)) + self.w * 2

class Tiny (Bont):
    name = "font-tiny.png"
    w = 5
    h = 7

