import pygame

class ButtonRegistry(object):
    def __init__(self):
        self.buttons = []

        default_font = pygame.font.get_default_font()
        self.font = pygame.font.Font(default_font, 14)

    def add_button(self, *args):
        b = Button(self.font, *args)
        self.buttons.append(b)

        b.show()

    def process_click(self, ev):
        for b in self.buttons:
            if b.shown and b.rect.collidepoint(ev.pos):
                b.cb()
                return True

    def draw(self, targ):
        for b in self.buttons:
            b.draw(targ)

class Button(object):
    bg_color = (64, 128, 64)
    bd_color = (32, 64, 32)
    fg_color = (255, 255, 255)
    margin = 8

    def __init__(self, font, text, cb, x, y, w=None, h=None):
        self.text = font.render(text, True, self.fg_color)
        text_w, text_h = self.text.get_size()

        if w is None:
            w = text_w + self.margin * 2
        if h is None:
            h = text_h + self.margin * 2

        self.cb = cb
        self.rect = pygame.Rect(x, y, w, h)
        self.tpos = x + w / 2 - text_w / 2, y + h / 2 - text_h / 2
        self.shown = False

    def show(self):
        self.shown = True

    def hide(self):
        self.shown = False

    def draw(self, targ):
        pygame.draw.rect(targ, self.bg_color, self.rect)
        pygame.draw.rect(targ, self.bd_color, self.rect, 1)
        targ.blit(self.text, self.tpos)

if __name__ == "__main__":
    import sys

    def fancy_cb():
        print "Named callback"

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    screen.fill(0)
    br = ButtonRegistry(screen)
    br.add_button("Foobar-o-matic", fancy_cb, 4, 4, 128)
    br.add_button("Exit", sys.exit, 4, 48, 128)
    while 1:
        br.draw_buttons()
        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.MOUSEBUTTONDOWN:
                br.process_click(ev)
