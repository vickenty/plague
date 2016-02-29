import pygame

class ButtonRegistry(object):
    def __init__(self, surface):
        self.surface = surface
        self.buttons = []

    def add_button(self, *args):
        b = Button(*args)
        self.buttons.append(b)

        b.show()

    def process_click(self, ev):
        for b in self.buttons:
            if not b.shown or not b.rect.collidepoint(ev.pos):
                continue
            if b.cb is None:
                print "Clicked %s" % b
            else:
                b.cb()

    def draw_buttons(self):
        for b in self.buttons:
            pygame.draw.rect(self.surface, (0, 0, 0), b.rect)
            w, h = b.text.get_size()
            self.surface.blit(b.text, (w/2, h/2))


class Button(object):
    pygame.init()

    default_font = pygame.font.get_default_font()
    font = pygame.font.Font(default_font, 12)

    def __init__(self, x, y, w, h, text="", cb=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = self.font.render(text, True, (255, 0, 0))
        self.cb = cb
        self.rect = pygame.Rect(x, y, w, h)
        self.shown = False

    def show(self):
        self.shown = True

    def hide(self):
        self.shown = False


if __name__ == "__main__":
    def fancy_cb():
        print "Named callback"

    screen = pygame.display.set_mode((800, 600))
    screen.fill((200, 255, 255))
    br = ButtonRegistry(screen)
    br.add_button(0, 0, 100, 100, "foo", fancy_cb)
    while 1:
        br.draw_buttons()
        pygame.display.update()
        for ev in pygame.event.get():
            if ev.type == pygame.MOUSEBUTTONDOWN:
                br.process_click(ev)
