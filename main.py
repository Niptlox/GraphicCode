from units.App import App, Scene, SceneUI, EXIT
from units.common import *
from UI import MainUI
from Blocks import *

surf = pg.Surface((100, 100))
surf2 = surf.convert_alpha()


class Game(App):
    def __init__(self) -> None:
        self.block_scene = BlockScene(self)
        super().__init__(self.block_scene)


class BlockScene(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.field = Field(self)

        self.ui = MainUI(self)
        self.ui._init_ui()
        self.tact = 0

    def pg_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = EXIT

            if self.ui.pg_event(event):
                continue
            self.field.pg_event(event)

    def update(self):
        self.field.draw(self.display)
        self.ui.draw()
        self.tact += 1


class Field:
    background_color = "#1F2937"

    def __init__(self, scene):
        self.scene = scene
        self.rect = pg.Rect((0, 0), WSIZE)
        self.surface = pg.Surface(self.rect.size)

        self.minimap_scale = 1.8
        self.minimap_surface = pg.Surface((self.rect.w * self.minimap_scale, self.rect.h * self.minimap_scale))
        self.minimap_display_rect = pg.Rect((0, 0), (WSIZE[0] // 5, WSIZE[1] // 5))
        self.minimap_display_rect.bottomright = WSIZE
        self.minimap_display = pg.Surface(self.minimap_display_rect.size)

        self.components = []
        self.components_of_types = {}

        self.add_component(BlockBegin((20, 20), self))
        self.add_component(BlockEnd((120, 120), self))
        self.add_component(BlockOR((15, 220), self))
        self.add_component(BlockAND((220, 20), self))

        self.mouse_connection = None
        self.get_block = None

        self.move_field = False
        self.scale = 1
        self.handlers_pgevent = []

        self.variables = {}

    def auto_pos_component(self):
        x, y = WSIZE[0] // 2 - self.rect.x, WSIZE[1] // 2 - self.rect.y
        # x, y = -self.rect.x + WSIZE[0] // 2, -self.rect.y + WSIZE[1] // 2

        return x, y

    def pg_event(self, event):
        for handler in self.handlers_pgevent:
            handler(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.begin_process()
            elif event.key == pg.K_o:
                self.rect.center = 0, 0
            elif event.key in NUM_KEYS and event.mod & pg.KMOD_CTRL:
                num = NUM_KEYS.index(event.key)
                try:
                    if event.mod & pygame.KMOD_SHIFT:
                        obj = BLOCKS_OPERATIONS[num](self.auto_pos_component(), self)
                    else:
                        obj = BLOCKS[num](self.auto_pos_component(), self)
                    self.add_component(obj)
                except:
                    print("User press big num")
            elif event.key == pg.K_DELETE:
                if self.get_block:
                    self.del_component(self.get_block[0])
                    self.get_block = None
                if self.mouse_connection:
                    self.mouse_connection = None
        elif event.type == pg.MOUSEBUTTONDOWN:
            mpos = event.pos
            if event.button == 1 or event.button == 3:
                if not self.get_block:
                    # реверсивно, чтобы те кто отрисовались последними, обробатывались первыми
                    for i in range(len(self.components) - 1, -1, -1):
                        obj = self.components[i]
                        if obj.collide_pos(mpos):
                            for point in obj.points:
                                # перенос, создание соединений меж точками
                                if point.collide_pos(mpos) and self.mouse_connection != point:
                                    if self.mouse_connection:
                                        if self.mouse_connection.add_connection(point):
                                            self.mouse_connection = None
                                    else:
                                        if point.connections and event.button == 3:
                                            # удаление соединения с var точкой если к ней уже были присоеденены
                                            conn = point.del_connection(-1)
                                            self.mouse_connection = conn
                                        else:
                                            self.mouse_connection = point
                                    break
                            else:
                                # беру в руку сам блок, есои не рабатаю с соединением
                                if not self.mouse_connection:
                                    # копия блока если нажат ctrl
                                    if pg.key.get_mods() & pg.KMOD_CTRL:
                                        move_obj = obj.copy()
                                        self.add_component(move_obj)
                                        i = len(self.components) - 1
                                    else:
                                        move_obj = obj
                                        # вставить в конец отрисовки, чтоб был впереди
                                        self.components.pop(i)
                                        self.components.append(move_obj)
                                    offset = [move_obj.rect.x - mpos[0], move_obj.rect.y - mpos[1]]
                                    self.get_block = [move_obj, offset]
                                    pygame.mouse.set_cursor(pg.SYSTEM_CURSOR_SIZEALL)
                                    break
                                continue
                            break
                    else:
                        if event.button == 3:
                            self.mouse_connection = None
                            self.get_block = None
                        else:
                            self.get_block = None
            elif event.button == 2:
                self.move_field = self.rect.x - mpos[0], self.rect.y - mpos[1]
                pygame.mouse.set_cursor(pg.SYSTEM_CURSOR_SIZEALL)
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 2:
                self.move_field = False
            else:
                self.get_block = None
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif event.type == pg.MOUSEMOTION:
            if self.move_field:
                self.rect.topleft = [event.pos[0] + self.move_field[0],
                                     event.pos[1] + self.move_field[1]]
                if self.get_block:
                    self.get_block[1] = [self.get_block[0].rect.x - event.pos[0],
                                         self.get_block[0].rect.y - event.pos[1]]
            else:
                if self.get_block:
                    self.get_block[0].rect.topleft = (event.pos[0] + self.get_block[1][0],
                                                      event.pos[1] + self.get_block[1][1])
        elif event.type == pg.MOUSEWHEEL:
            self.scale += event.x / 10
            if self.scale < 1:
                self.scale = 1
            elif self.scale > 3:
                self.scale = 3

    def add_block_to_mouse(self, move_obj):
        mpos = pg.mouse.get_pos()
        move_obj.rect.center = -self.rect.x + mpos[0], -self.rect.y + mpos[1]
        offset = [move_obj.rect.x - mpos[0], move_obj.rect.y - mpos[1]]
        self.get_block = [move_obj, offset]
        pygame.mouse.set_cursor(pg.SYSTEM_CURSOR_SIZEALL)
        return move_obj

    def create_component(self, ClassObj, pos=(0, 0)):
        obj = ClassObj(pos, self)
        self.add_component(obj)
        return obj

    def add_component(self, obj):
        self.components.append(obj)
        self.components_of_types.setdefault(type(obj), [])
        self.components_of_types[type(obj)].append(obj)
        return obj

    def del_component(self, obj):
        if obj in self.components:
            for point in obj.points:
                point.del_connections()
            i = self.components.index(obj)
            self.components.pop(i)
            i = self.components_of_types[type(obj)].index(obj)
            self.components_of_types[type(obj)].pop(i)
        else:
            print("Ошибочка del_component", obj)

    def begin_process(self):
        for obj in self.components_of_types[BlockBegin]:
            try:
                obj.begin()
            except RecursionError as exp:
                print("Begin_process RecursionError", exp)

    def draw_minimap(self, surface):
        # self.minimap_display_rect.center = self.rect.center
        pos = self.rect.center
        self.rect.center = self.rect.bottomright
        self.minimap_surface.fill("#334155")
        self.draw_components(self.minimap_surface)
        self.minimap_display = pg.transform.scale(self.minimap_surface, self.minimap_display_rect.size)
        pg.draw.rect(self.minimap_display, "#94A3B8",
                     ((0, 0), (self.minimap_display_rect.w - 1, self.minimap_display_rect.h - 1)), 3)
        surface.blit(self.minimap_display, self.minimap_display_rect)
        self.rect.center = pos

    def draw_components(self, surface):
        for obj in self.components:
            obj.draw(surface)
        for obj in self.components:
            obj.draw_connections(surface)

    def draw_grid(self, big=False):
        step = 20
        color = "#374151"
        if big:
            step = step * 8
            color = "#111827"
        y1, y2 = 0, self.rect.h
        for x1 in range(self.rect.x % step, self.rect.x % step + self.rect.w, step):
            pg.draw.line(self.surface, color, (x1, y1), (x1, y2), 2)
        x1, x2 = 0, self.rect.w
        for y1 in range(self.rect.y % step, self.rect.y % step + self.rect.h, step):
            pg.draw.line(self.surface, color, (x1, y1), (x2, y1), 2)
        if not big:
            self.draw_grid(big=True)

    def draw(self, surface):
        self.surface.fill(self.background_color)
        self.draw_grid()
        self.draw_components(self.surface)
        if self.mouse_connection:
            pg.draw.line(self.surface, self.mouse_connection.connection_color, self.mouse_connection.pos_on_field(),
                         pg.mouse.get_pos(), width=2)
        ty = 5
        for text in help_text:
            self.surface.blit(text, (5, ty))
            ty += 15

        pg.draw.circle(self.surface, "red", self.rect.topleft, 5, 2)
        surface.blit(self.surface, (0, 0))
        self.draw_minimap(surface)

    def add_handler_pgevent(self, handler):
        self.handlers_pgevent.append(handler)


block = pg.Rect(0, 0, 120, 100)
if __name__ == "__main__":
    game = Game()
    game.main()
