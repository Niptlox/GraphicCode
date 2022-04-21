from units.App import App, Scene, SceneUI, EXIT
from units.UI.ClassUI import UI
from units.common import *
# from GraphicCode.Blocks import *

import pygame as pg
from units.Image import load_img

# point flags
POINTIN = 2
POINTOUT = 4
POINTINOUT = POINTIN + POINTOUT

# font
textfont = pg.font.SysFont("Fenix", 19, )  # yes rus


class Point:
    size = (8, 8)
    sprite = load_img("sprites/PointArrow.png", size)
    # sprite = pg.Surface(size)
    # sprite.fill("#FFFFFF")
    typeP = POINTIN

    def __init__(self, pos, owner):
        self.owner = owner
        self.rect = pg.Rect(pos, self.size)
        self.connections = []
        self.static = True
        self.value = 0
        self.init_sprite()

    def init_sprite(self):
        pass

    def draw(self, surface: pg.Surface):
        surface.blit(self.sprite, (self.rect.x + self.owner.rect.x, self.rect.y + self.owner.rect.y))

    def draw_connections(self, surface):
        x, y = self.pos_on_field()
        for con in self.connections:
            cx, cy = con.pos_on_field()
            pg.draw.line(surface, "#11FF11", (x, y), (cx, cy), width=4)

    def add_connection(self, conn, first=True):
        if conn not in self.connections:
            if first:
                res = conn.add_connection(self, first=False)
                if not res:
                    return
            self.connections.append(conn)

            if self.typeP & POINTIN:
                self.owner.new_connection_in(self, conn)
            if self.typeP & POINTOUT:
                self.owner.new_connection_out(self, conn)
            return True

    def del_connections(self):
        # удалить все соединения с точкой
        for conn in self.connections:
            i = conn.connections.index(self)
            conn.connections.pop(i)
        out = self.connections
        self.connections = []
        return out

    def collide_pos(self, pos):
        pos = pos[0] - self.owner.rect.x, pos[1] - self.owner.rect.y
        return self.rect.collidepoint(pos)

    def pos_on_field(self):
        # реальное положение точки с учетом смещения родителя(блока)
        return self.rect.centerx + self.owner.rect.x, self.rect.centery + self.owner.rect.y


class PointIN(Point):
    typeP = POINTIN

    def get_value(self):
        if self.connections:
            return self.connections[0].get_value()
        return 0

    def add_connection(self, conn, first=True):
        if len(self.connections) == 0:
            return super().add_connection(conn, first)


class PointOUT(Point):
    typeP = POINTOUT

    def get_value(self):
        self.owner.function()
        return self.value


class Block:
    size = (64, 64)
    sprite = pg.Surface(size)
    sprite.fill("#222034")
    pos_points_in = []
    pos_points_out = []

    def __init__(self, pos, scene):
        self.scene = scene
        self.rect = pg.Rect(pos, self.size)
        self.points_in = [PointIN(pos, self) for pos in self.pos_points_in]
        self.points_out = [PointOUT(pos, self) for pos in self.pos_points_out]
        self.points = self.points_in + self.points_out

    def draw(self, surface: pg.Surface):
        surface.blit(self.sprite, self.rect)
        for point in self.points:
            point.draw(surface)

    def draw_connections(self, surface):
        for point in self.points:
            point.draw_connections(surface)

    def collide_pos(self, pos):
        return self.rect.collidepoint(pos)

    def new_connection_in(self, block_point, connect_point):
        pass

    def new_connection_out(self, block_point, connect_point):
        pass

    def function(self):
        return


class BlockValue(Block):
    # pos_points_out = [(46, 28)]
    default_value = 0

    def __init__(self, pos, scene):
        super().__init__(pos, scene)
        self.value = self.default_value

    def function(self):
        if self.points_out:
            self.points_out[0].value = self.value
        return self.value

    def draw(self, surface: pg.Surface):
        super().draw(surface)
        text = textfont.render(str(self.value), True, "#EEEEEE")
        surface.blit(text, (self.rect.centerx - 3, self.rect.bottom + 3))


class BlockBegin(BlockValue):
    pos_points_out = [(46, 28)]
    size = (64, 64)
    sprite = load_img("sprites/BlockBegin1.png", size)
    default_value = 1


class BlockTrue(BlockValue):
    pos_points_out = [(46, 28)]
    size = (64, 64)
    sprite = load_img("sprites/Block1.png", size)
    default_value = 1


class BlockFalse(BlockValue):
    pos_points_out = [(46, 28)]
    size = (64, 64)
    sprite = load_img("sprites/Block0.png", size)
    default_value = 0


class BlockEnd(BlockValue):
    pos_points_in = [(10, 28)]
    size = (64, 64)
    sprite = load_img("sprites/BlockEnd1.png", size)
    default_value = 0

    def function(self):
        self.value = self.points_in[0].get_value()
        return self.value


class BlockOR(BlockValue):
    pos_points_in = [(12, 12), (12, 44)]
    pos_points_out = [(78, 28)]
    size = (96, 64)
    sprite = load_img("sprites/BlockOR.png", size)

    def function(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        self.value = val1 or val2
        self.points_out[0].value = self.value
        return self.value


class BlockAND(BlockValue):
    pos_points_in = [(12, 12), (12, 44)]
    pos_points_out = [(78, 28)]
    size = (96, 64)
    sprite = load_img("sprites/BlockAND.png", size)

    def function(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        self.value = val1 and val2
        self.points_out[0].value = self.value
        return self.value


class BlockTrigger(BlockValue):
    pos_points_in = [(12, 12), (12, 44)]
    pos_points_out = [(110, 28)]
    size = (128, 64)
    sprite = load_img("sprites/BlockTRIGGER.png", size)

    def function(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        if val1 != 0:
            self.value = 1
        elif val2 != 0:
            self.value = 0
        self.points_out[0].value = self.value
        return self.value


class BlockNOT(BlockValue):
    pos_points_in = [(12, 28)]
    pos_points_out = [(78, 28)]
    size = (96, 64)
    sprite = load_img("sprites/BlockNOT.png", size)

    def function(self):
        val1 = self.points_in[0].get_value()
        self.value = int(not val1)
        self.points_out[0].value = self.value
        return self.value


BLOCKS = [BlockBegin, BlockEnd, BlockTrue, BlockFalse, BlockAND, BlockOR, BlockNOT, BlockTrigger]
help_text = textfont.render("Press the space bar to start... "+"; ".join([f"{i + 1}: {BLOCKS[i].__name__}" for i in range(len(BLOCKS))]), True, "#EEEEEE")


class Game(App):
    def __init__(self) -> None:
        self.block_scene = BlockScene(self)
        super().__init__(self.block_scene)


class BlockScene(Scene):
    def __init__(self, app) -> None:
        super().__init__(app)

        self.ui = UI(self)
        self.ui.init_ui()
        self.tact = 0

        self.components = []
        self.components_of_types = {}

        self.add_component(BlockBegin((20, 20), self))
        self.add_component(BlockEnd((220, 220), self))
        self.add_component(BlockOR((15, 220), self))
        self.add_component(BlockAND((220, 20), self))

        self.mouse_connection = None
        self.get_block = None

    def pg_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = EXIT
            if self.ui.pg_event(event):
                continue
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.begin_process()
                elif event.key in NUM_KEYS:
                    num = NUM_KEYS.index(event.key)
                    obj = BLOCKS[num]((10, 10), self)
                    self.add_component(obj)
                elif event.key == pg.K_DELETE:
                    if self.get_block:
                        self.del_component(self.get_block[0])
                        self.get_block = None
                    if self.mouse_connection:
                        self.mouse_connection = None
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not self.get_block:
                        # реверсивно, чтобы те кто отрисовались последними, обробатывались первыми
                        for i in range(len(self.components) - 1, -1, -1):
                            obj = self.components[i]
                            if obj.collide_pos(event.pos):
                                for point in obj.points:
                                    if point.collide_pos(event.pos) and self.mouse_connection != point:
                                        if self.mouse_connection:
                                            if (point.typeP & POINTOUT and self.mouse_connection.typeP & POINTIN) or \
                                                    (point.typeP & POINTIN and self.mouse_connection.typeP & POINTOUT):
                                                if self.mouse_connection.add_connection(point):
                                                    self.mouse_connection = None
                                        else:
                                            if point.typeP & POINTIN and point.connections:
                                                # удаление соединения с точкой если к ней уже были присоеденены
                                                conn = point.del_connections()[0]
                                                self.mouse_connection = conn
                                            else:
                                                self.mouse_connection = point
                                        break
                                else:
                                    if not self.mouse_connection:
                                        offset = obj.rect.x - event.pos[0], obj.rect.y - event.pos[1]
                                        self.get_block = (obj, offset)
                                        # вставить в конец отрисовки, чтоб был впереди
                                        self.components.pop(i)
                                        self.components.append(obj)
                                        break
                    else:
                        self.get_block = None
                elif event.button == 3:
                    self.mouse_connection = None
                    self.get_block = None
            elif event.type == pg.MOUSEBUTTONUP:
                self.get_block = None
            elif event.type == pg.MOUSEMOTION:
                if self.get_block:
                    self.get_block[0].rect.topleft = (event.pos[0] + self.get_block[1][0],
                                                      event.pos[1] + self.get_block[1][1])

    def add_component(self, obj):
        self.components.append(obj)
        self.components_of_types.setdefault(type(obj), [])
        self.components_of_types[type(obj)].append(obj)

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
        for obj in self.components_of_types[BlockEnd]:
            try:
                obj.function()
            except RecursionError as exp:
                print("Begin_process RecursionError", exp)

    def update(self):
        self.display.fill("#000000")

        for obj in self.components:
            obj.draw(self.display)
        for obj in self.components:
            obj.draw_connections(self.display)
        if self.mouse_connection:
            pg.draw.line(self.display, "#11FF11", self.mouse_connection.pos_on_field(), pg.mouse.get_pos(), width=2)
        self.display.blit(help_text, (5, 5))
        self.ui.draw()

        self.tact += 1


class Field:
    rect = pg.Rect((0, 0), WSIZE)


if __name__ == "__main__":
    game = Game()
    game.main()
