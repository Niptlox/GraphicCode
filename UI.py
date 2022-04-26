from units.common import *
from units.UI.ClassUI import UI
from units.UI.Button import createImagesButton, createVSteckButtons, Button

pygame.font.init()
textfont_btn = pygame.font.SysFont("Fenix", 35, )

class MainUI(UI):
    def init_ui(self):
        self.top_surface = pg.Rect((0, 0, WSIZE[0], 100))
        self.surface = pg.Surface(WSIZE).convert_alpha()


        w, h = text.get_size()
        self.surface.blit(text, (self.rect_surface.w // 2 - w // 2, self.rect_surface.h // 2 - h // 2))
        rect_btn = pg.Rect((self.rect_surface.x + 10, self.rect_surface.bottom + 15,
                            self.rect_surface.w - 20, 35))
        self.btn_relive = Button(lambda _: self.app.relive(), rect_btn,
                                 *createImagesButton(rect_btn.size, "Возродиться"))

    def draw(self):
        self.screen.blit(self.display, (0, 0))
        self.screen.blit(self.surface, self.rect_surface)
        self.btn_relive.draw(self.screen)
        pg.display.flip()

    def pg_event(self, event: pg.event.Event):
        self.btn_relive.pg_event(event)

