import pygame as pg


class UI:
    def __init__(self, app) -> None:

        self.app = app
        self.screen = app.screen
        self.display = self.app.display
        self.rect = pg.Rect((0, 0), self.display.get_size())

    def init_ui(self):
        pass

    def draw(self):
        self.screen.blit(self.display, (0, 0))
        pg.display.flip()

    def pg_event(self, event: pg.event.Event):
        pass

    @property
    def onscreenx(self):
        return self.rect.x + self.app.rect.x

    @property
    def onscreeny(self):
        return self.rect.y + self.app.rect.y

