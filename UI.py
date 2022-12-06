from units.common import *
from units.UI.ClassUI import UI, SurfaceUI, ScrollSurface
from units.UI.Button import createImagesButton, Button
from Blocks import BLOCKS_ALL

pygame.font.init()
textfont_btn = pygame.font.SysFont("Fenix", 35, )

bg = (82, 82, 91, 150)


class MainUI(UI):
    def __init__(self, app):
        super().__init__(app)

    def _init_ui(self):
        self.field = self.app.field
        self.surface = pg.Surface(self.rect.size).convert_alpha()
        self.surface.fill((0, 0, 0, 0))
        self.top_surfaceui = SurfaceUI((0, 0, self.rect.w, 100))

        self.block_selection_scroll = ScrollSurface((0, 0, 100, self.top_surfaceui.rect.h), (0, 0))
        self.block_selection_scroll.convert_alpha()
        buttons_img = [Blck.sprite for Blck in BLOCKS_ALL]
        buttons_func = [lambda _Blck=Blck: self.add_block_to_mouse(_Blck) for Blck in BLOCKS_ALL]
        self.buttons = createHSteckBlockButtons(64, 5, 50, 10, buttons_img, buttons_func)
        self.block_selection_scroll.add_objects(self.buttons)
        # self.block_selection_scroll.rect.center = self.top_surfaceui.rect.center
        self.moving_block = [None, (0, 0)]  # block, mouse_offset

    def add_block_to_mouse(self, Blck):
        block = self.field.add_block_to_mouse(self.field.create_component(Blck))
        sx, sy = block.onscreenx, block.onscreeny
        mx, my = pg.mouse.get_pos()
        offset = sx - mx, sy - my
        self.moving_block = [block, offset]

    def draw(self):
        self.surface.fill((0, 0, 0, 0))
        self.block_selection_scroll.draw(self.surface)
        self.screen.blit(self.display, (0, 0))
        if self.moving_block[0]:
            x, y = pg.mouse.get_pos()
            if self.field.get_block and self.block_selection_scroll.rect.collidepoint(x, y):
                pos = x + self.moving_block[1][0], y + self.moving_block[1][1]
                self.surface.blit(self.moving_block[0].sprite, pos)
            else:
                self.moving_block[0] = None
        self.screen.blit(self.surface, self.rect)

        pg.display.flip()

    def pg_event(self, event: pg.event.Event):
        self.block_selection_scroll.pg_event(event)
        if event.type == pg.MOUSEWHEEL:
            if self.block_selection_scroll.mouse_scroll(event.y * 32, 0):
                return True


class BlockButton(SurfaceUI):
    def __init__(self, rect, surface, func, button_type=1):
        super(BlockButton, self).__init__(rect)
        self.blit(surface, (0, 0))
        self.button_type = button_type
        self.func = func

    def pg_event(self, event: pg.event.Event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == self.button_type:
                if self.rect.collidepoint(event.pos):
                    self.func()
                    return True


def createHSteckBlockButtons(height: int, start_x: int, center_y: int, step: int,
                             images_buttons, funcs, screen_position=[0, 0]):
    y = center_y - height // 2
    x = start_x
    buts = []
    for images_button, func in zip(images_buttons, funcs):
        but = BlockButton(((x, y), images_button.get_size()), images_button, func)
        x += step + images_button.get_width()
        buts.append(but)
    return buts
