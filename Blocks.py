from typing import Any

import pygame as pg

from BlockSoriteGenerator import StyleSheet, gen_block_value
from SerialiseObjects import SavedObject
from src.UI.ElementsUI import TextInput
from src.splines import draw_bicubik_line


def load_img(path, size, colorkey=None, alpha=None):
    print(path)
    img = pg.image.load(path)
    if size:
        img = pg.transform.scale(img, size)
    if colorkey:
        img.set_colorkey(colorkey)
    if alpha:
        img.convert_alpha()
        img.set_alpha(alpha)
    return img





# point flags
POINTIN = 2
POINTOUT = 4
POINTVAR = 8
POINTRUN = 16
POINTINOUT = POINTIN + POINTOUT

# font]
pg.font.init()
font = pg.font.SysFont("Arial", 14)

textfont = font  # pg.font.SysFont("Fenix", 19, )  # yes rus

PointSize = (10, 10)


class Point(SavedObject):
    size = PointSize
    sprite = load_img("sprites/PointCircle.png", size)
    # sprite = pg.Surface(size)
    # sprite.fill("#FFFFFF")
    connection_color = "#11FF11"
    typeP = POINTIN + POINTVAR

    def __init__(self, pos, owner=None):
        self.owner = owner
        self.rect = pg.Rect(pos, self.size)
        self.rect.topleft
        self.connections = []
        self.static = True
        self.value = 0
        self.init_sprite()

    def init_sprite(self):
        pass

    def draw(self, surface: pg.Surface):
        surface.blit(self.sprite, (self.rect.x + self.owner.onscreenx, self.rect.y + self.owner.onscreeny))

    def draw_connections(self, surface):
        for con in self.connections:
            draw_bicubik_line(surface, self.connection_color, self.pos_on_field(), con.pos_on_field(), width=3)
            # pg.draw.line(surface, self.connection_color, self.pos_on_field(), con.pos_on_field(), width=3)

    def add_connection(self, conn, first=True):
        # проверка на то что провод идет из выхода во вход
        if ((self.typeP & conn.typeP) & POINTOUT) or \
                ((self.typeP & conn.typeP) & POINTIN):
            return None
        # проверка на то что провод соединяет разные типы работы точек
        if ((self.typeP | conn.typeP) & POINTVAR) and \
                ((self.typeP | conn.typeP) & POINTRUN):
            return None
        # проверка на то что провод идет из выхода во вход
        if ((self.typeP & conn.typeP) & POINTVAR) or \
                ((self.typeP & conn.typeP) & POINTRUN):
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

    def del_connection(self, i_connection):
        # удалить соединение с точкой
        conn = self.connections[i_connection]
        conn.connections.pop(conn.connections.index(self))
        out = self.connections.pop()
        return out

    def del_connections(self):
        # удалить все соединения с точкой
        for conn in self.connections:
            i = conn.connections.index(self)
            conn.connections.pop(i)
        out = self.connections
        self.connections = []
        return out

    def collide_pos(self, pos):
        pos = pos[0] - self.owner.onscreenx, pos[1] - self.owner.onscreeny
        return self.rect.collidepoint(pos)

    def pos_on_field(self):
        # реальное положение точки с учетом смещения родителя(блока)
        return pg.Vector2(self.rect.centerx + self.owner.onscreenx, self.rect.centery + self.owner.onscreeny)



class PointRun(Point):
    sprite = load_img("sprites/PointArrow.png", PointSize)
    typeP = POINTIN + POINTRUN
    connection_color = "#FFFFFF"


class PointRunIN(PointRun):
    typeP = POINTIN + POINTRUN

    def begin(self):
        self.owner.begin()


class PointRunOUT(PointRun):
    typeP = POINTOUT + POINTRUN

    def begin(self):
        for conn in self.connections:
            conn.owner.begin()


class PointVarIN(Point):
    typeP = POINTIN + POINTVAR

    def get_value(self):
        if self.connections:
            return self.connections[0].get_value()
        return 0

    def add_connection(self, conn, first=True):
        if len(self.connections) == 0:
            return super().add_connection(conn, first)


class PointVarOUT(Point):
    typeP = POINTOUT + POINTVAR

    def get_value(self):
        self.owner.update_value()
        return self.value


class Block:
    size = (64, 64)
    sprite = pg.Surface(size)
    sprite.fill("#222034")
    pos_points_in = []
    pos_points_out = []
    pos_pointrun_in = None
    pos_pointsrun_out = []

    def __init__(self, pos, owner=None):
        self.owner = owner
        self.rect = pg.Rect(pos, self.size)
        self.points_in = [PointVarIN(pos, self) for pos in self.pos_points_in]
        self.points_out = [PointVarOUT(pos, self) for pos in self.pos_points_out]
        self.points = self.points_in + self.points_out

        if self.pos_pointrun_in:
            self.pointrun_in = PointRunIN(self.pos_pointrun_in, self)
            self.points += [self.pointrun_in]
        else:
            self.pointrun_in = None
        self.pointsrun_out = [PointRunOUT(pos, self) for pos in self.pos_pointsrun_out]
        self.points += self.pointsrun_out

    def draw(self, surface: pg.Surface):
        surface.blit(self.sprite, (self.onscreenx, self.onscreeny))
        for point in self.points:
            point.draw(surface)

    def draw_connections(self, surface):
        for point in self.points_out:
            point.draw_connections(surface)

    def collide_pos(self, pos):
        pos = pos[0] - self.owner.rect.x, pos[1] - self.owner.rect.y
        return self.rect.collidepoint(pos)

    def copy(self):
        return self.__class__(self.rect.topleft, self.owner)

    @property
    def onscreenx(self):
        return self.rect.x + self.owner.rect.x

    @property
    def onscreeny(self):
        return self.rect.y + self.owner.rect.y

    def new_connection_in(self, block_point, connect_point):
        pass

    def new_connection_out(self, block_point, connect_point):
        pass

    def _update_value(self):
        return


class BlockValue(Block):
    # pos_points_out = [(46, 28)]
    default_value = 0

    def __init__(self, pos, owner):
        super().__init__(pos, owner)
        self.value = self.default_value

    def update_value(self):
        try:
            return self._update_value()
        except Exception as ex:
            self.value = "Err"
            print(f"Error ({self.__class__}): {ex}")

    def _update_value(self):
        if self.points_out:
            self.points_out[0].value = self.value
        return self.value

    def draw(self, surface: pg.Surface):
        super().draw(surface)
        text = textfont.render(str(self.value), True, "#EEEEEE")
        surface.blit(text, (self.rect.centerx - 3 + self.owner.rect.x, self.rect.bottom + 3 + self.owner.rect.y))


class BlockRun(BlockValue):
    pos_pointrun_in = (4, 4)
    pos_pointsrun_out = [(72, 4)]

    def begin(self):
        self.update_value()
        for p in self.pointsrun_out:
            p.begin()


class BlockBegin(BlockRun):
    pos_pointrun_in = None
    # pos_pointsrun_out = [(50, 27)]
    pos_pointsrun_out = [(50, 4)]
    pos_points_out = [(50, 50)]
    size = (64, 64)
    sprite = load_img("sprites/BlockBegin1.png", size)
    default_value = 1
    but_rect = pg.Rect((7, 21), (12, 24))

    def collide_pos(self, pos):
        if super().collide_pos(pos):
            pos = pos[0] - self.onscreenx, pos[1] - self.onscreeny
            if self.but_rect.collidepoint(pos):
                self.begin()
            else:
                return True


class BlockEnd(BlockRun):
    pos_points_in = [(9, 27)]
    pos_pointrun_in = (4, 4)
    pos_pointsrun_out = []
    size = (64, 64)
    sprite = load_img("sprites/BlockEnd1.png", size)
    default_value = 0

    def _update_value(self):
        self.value = self.points_in[0].get_value()
        return self.value


class BlockTrue(BlockValue):
    pos_points_out = [(45, 27)]
    size = (64, 64)
    sprite = load_img("sprites/Block1.png", size)
    default_value = 1


class BlockFalse(BlockValue):
    pos_points_out = [(45, 27)]
    size = (64, 64)
    sprite = load_img("sprites/Block0.png", size)
    default_value = 0


class BlockOR(BlockValue):
    pos_points_in = [(11, 11), (11, 43)]
    pos_points_out = [(77, 27)]
    size = (96, 64)
    sprite = load_img("sprites/BlockOR.png", size)

    def _update_value(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        self.value = val1 or val2
        self.points_out[0].value = self.value
        return self.value


class BlockAND(BlockValue):
    pos_points_in = [(11, 11), (11, 43)]
    pos_points_out = [(77, 27)]
    size = (96, 64)
    sprite = load_img("sprites/BlockAND.png", size)

    def _update_value(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        self.value = val1 and val2
        self.points_out[0].value = self.value
        return self.value


class BlockSum2(BlockValue):
    pos_points_in = [(11, 11), (11, 43)]
    pos_points_out = [(77, 27)]
    size = (96, 64)
    sprite = load_img("sprites/BlockSum2.png", size)

    def _update_value(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        try:
            self.value = val1 + val2
        except Exception as ex:
            self.value = "Err"
            print(f"Error ({self.__class__}): {ex}")

        self.points_out[0].value = self.value
        return self.value


class BlockSum3(BlockValue):
    pos_points_in = [(7, 7), (7, 27), (7, 47)]
    pos_points_out = [(79, 27)]
    size = (96, 64)
    # sprite = load_img("sprites/BlockSum3.png", size)
    sprite = load_img("sprites/BlockSum3.png", size)

    def _update_value(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        val3 = self.points_in[2].get_value()
        try:
            self.value = val1 + val2 + val3
        except Exception as ex:
            self.value = "Err"
            print(f"Error ({self.__class__}): {ex}")

        self.points_out[0].value = self.value
        return self.value


class BlockTrigger(BlockValue):
    pos_points_in = [(4, 25), (4, 50)]
    pos_points_out = [(114, 50)]
    size = (128, 64)
    sprite = load_img("sprites/BlockTRIGGER.png", size)

    def _update_value(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        if val1 != 0:
            self.value = val1
        elif val2 != 0:
            self.value = 0
        self.points_out[0].value = self.value
        return self.value


class BlockSetVariable(BlockRun):
    pos_points_in = [(4, 25), (4, 50)]
    size = (86, 64)
    sprite = load_img("sprites/BlockSetVariable.png", size)

    def _update_value(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        self.value = val1
        self.owner.variables[val2] = self.value
        return self.value


class BlockGetVariable(BlockValue):
    pos_points_in = [(4, 19)]
    pos_points_out = [(72, 19)]
    size = (86, 32)
    sprite = load_img("sprites/BlockGetVariable.png", size)

    def _update_value(self):
        val1 = self.points_in[0].get_value()
        self.value = self.owner.variables.get(val1)
        self.points_out[0].value = self.value
        return self.value


class BlockGetVariableS(BlockValue):
    sprite, pos_points_in, pos_points_out, pos_pointrun_in, pos_pointsrun_out = gen_block_value \
        (StyleSheet.Block.MiddleWidth + 5, "Get var", ["var"], ["value"], [], run_block=False)
    size = sprite.get_size()

    def __init__(self, pos, owner, input_type: Any = str):
        super().__init__(pos, owner)
        self.var_name = ""
        rect = self.onscreenx + 4, self.onscreeny + 29, 44, 13
        self.input = TextInput(rect, "", textfont, "black", on_finish_typing=self.set_value, bg_color="white",
                               input_type=input_type)
        self.owner.add_handler_pgevent(self.pg_event)

    def set_value(self, value):
        self.var_name = value

    def pg_event(self, event):
        self.input.rect.topleft = self.onscreenx + 4, self.onscreeny + 29
        self.input.pg_event(event)

    def draw(self, surface: pg.Surface):
        super().draw(surface)
        self.input.rect.topleft = self.onscreenx + 4, self.onscreeny + 29
        self.input.draw(surface)

    def _update_value(self):
        name = self.var_name or self.points_in[0].get_value()
        self.value = self.owner.variables.get(name)
        self.points_out[0].value = self.value
        return self.value


class BlockSetVariableS(BlockGetVariableS):
    sprite, pos_points_in, pos_points_out, pos_pointrun_in, pos_pointsrun_out = gen_block_value \
        (StyleSheet.Block.MiddleWidth + 10, "Set var", ["var", "value"], ["value"], [], run_block=True)
    size = sprite.get_size()

    def _update_value(self):
        name = self.var_name or self.points_in[0].get_value()
        self.value = self.points_in[1].get_value()
        self.owner.variables[name] = self.value
        self.points_out[0] = self.value
        return self.value

    def begin(self):
        self.update_value()
        for p in self.pointsrun_out:
            p.begin()


class BlockStrToInt(BlockValue):
    pos_points_in = [(4, 19)]
    pos_points_out = [(72, 19)]
    size = (86, 32)
    sprite = load_img("sprites/BlockToInt.png", size)

    def _update_value(self):
        val1: str = self.points_in[0].get_value()
        if isinstance(val1, (int, float)) or (isinstance(val1, str) and val1.isdigit()):
            self.value = int(val1)
        else:
            self.value = 0
        self.points_out[0].value = self.value
        return self.value


class BlockGetString(BlockValue):
    pos_points_out = [(72, 19)]
    size = (86, 32)
    sprite = load_img("sprites/BlockGetStr.png", size)

    def __init__(self, pos, owner, input_type: Any = str):
        super().__init__(pos, owner)
        rect = self.onscreenx + 4, self.onscreeny + 16, 44, 13
        self.input = TextInput(rect, "", textfont, "black", on_finish_typing=self.set_value, bg_color="white",
                               input_type=input_type)
        self.owner.add_handler_pgevent(self.pg_event)

    def set_value(self, value):
        self.value = value

    def pg_event(self, event):
        self.input.rect.topleft = self.onscreenx + 4, self.onscreeny + 16
        self.input.pg_event(event)

    def draw(self, surface: pg.Surface):
        super().draw(surface)
        self.input.rect.topleft = self.onscreenx + 4, self.onscreeny + 16
        self.input.draw(surface)


class BlockGetInt(BlockGetString):
    pos_points_out = [(72, 19)]
    size = (86, 32)
    sprite = load_img("sprites/BlockGetInt.png", size)

    def __init__(self, pos, owner):
        super().__init__(pos, owner, input_type=int)


class BlockNOT(BlockValue):
    pos_points_in = [(11, 27)]
    pos_points_out = [(77, 27)]
    size = (96, 64)
    sprite = load_img("sprites/BlockNOT.png", size)

    def _update_value(self):
        val1 = self.points_in[0].get_value()
        self.value = int(not val1)
        self.points_out[0].value = self.value
        return self.value


class BlockMul(BlockValue):
    sprite, pos_points_in, pos_points_out, pos_pointrun_in, pos_pointsrun_out = gen_block_value(
        StyleSheet.Block.MiddleWidth, "Mul *", ["Val 1", "Val 2"], ["Out"])
    size = sprite.get_size()

    def _update_value(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        try:
            self.value = val1 * val2
        except Exception as ex:
            self.value = 0
            print(f"Error ({self.__class__}): {ex}")
        self.points_out[0].value = self.value
        return self.value


class BlockEquality(BlockValue):
    sprite, pos_points_in, pos_points_out, pos_pointrun_in, pos_pointsrun_out = gen_block_value(
        StyleSheet.Block.MiddleWidth + 14, "Equality =", ["Val 1", "Val 2"], ["Out"])
    size = sprite.get_size()

    def _update_value(self):
        val1 = self.points_in[0].get_value()
        val2 = self.points_in[1].get_value()
        try:
            self.value = val1 == val2
        except Exception as ex:
            self.value = 0
            print(f"Error ({self.__class__}): {ex}")
        self.points_out[0].value = self.value
        return self.value


class BlockFor(BlockRun):
    sprite, pos_points_in, pos_points_out, pos_pointrun_in, pos_pointsrun_out = gen_block_value \
        (StyleSheet.Block.MiddleWidth + 20, "FOR", ["Start", "Stop", "Step"], ["Iter"], ["FOR"], run_block=True)
    size = sprite.get_size()

    def _update_value(self):
        self.iter = self.points_in[0].get_value()
        self.end = self.points_in[1].get_value()
        self.step = self.points_in[1].get_value()
        try:
            self.start = int(self.points_in[0].get_value())
            self.end = int(self.points_in[1].get_value())
            if self.end == 0:
                self.end = 10
            self.step = int(self.points_in[2].get_value())
            if self.step == 0:
                self.step = 1
        except Exception as ex:
            self.value = 0
            print(f"Error ({self.__class__}): {ex}")
        self.points_out[0].value = self.value
        return self.value

    def begin(self):
        self.update_value()
        self.value = self.start
        run_for = self.pointsrun_out[1]
        for i in range(self.start, self.end, self.step):
            self.value = i
            run_for.begin()
            # print(self.value, self.start, self.end, self.step)
        self.pointsrun_out[0].begin()
        print(self.value, self.start, self.end, self.step)


class BlockIf(BlockRun):
    sprite, pos_points_in, pos_points_out, pos_pointrun_in, pos_pointsrun_out = gen_block_value \
        (StyleSheet.Block.MiddleWidth + 20, "IF", ["Value"], [], ["True", "False"], run_block=True)
    size = sprite.get_size()

    def _update_value(self):
        self.condition = self.points_in[0].get_value()
        try:
            self.value = self.condition = bool(self.points_in[0].get_value())
        except Exception as ex:
            self.value = 0
            print(f"Error ({self.__class__}): {ex}")
        return self.value

    def begin(self):
        self.update_value()
        if self.condition:
            self.pointsrun_out[1].begin()
        else:
            self.pointsrun_out[2].begin()
        self.pointsrun_out[0].begin()


class BlockPrint(BlockRun):
    sprite, pos_points_in, pos_points_out, pos_pointrun_in, pos_pointsrun_out = gen_block_value \
        (StyleSheet.Block.MiddleWidth, "Print", ["Value"], [], [], run_block=True)
    size = sprite.get_size()

    def _update_value(self):
        self.value = self.points_in[0].get_value()
        try:
            self.value = str(self.value)
        except Exception as ex:
            self.value = "0"
            print(f"Error ({self.__class__}): {ex}")
        return self.value

    def begin(self):
        self.update_value()
        self.owner.console.print(self.value)
        self.pointsrun_out[0].begin()


BLOCKS = [BlockBegin, BlockEnd, BlockPrint, BlockGetVariable, BlockSetVariable, BlockGetVariableS, BlockSetVariableS,
          BlockGetString,
          BlockGetInt,
          BlockStrToInt, BlockMul, BlockEquality, BlockFor, BlockIf, BlockTrue, BlockFalse]
BLOCKS_OPERATIONS = [BlockAND, BlockOR, BlockNOT, BlockSum2, BlockSum3]
BLOCKS_ALL = BLOCKS + BLOCKS_OPERATIONS

help_text = [
    textfont.render(";  ".join([f"{i + 1}:{BLOCKS[i].__name__}" for i in range(len(BLOCKS))]), True, "#EEEEEE"),
    textfont.render("SHIFT + " + ";  ".join([f"{i + 1}:{BLOCKS_OPERATIONS[i].__name__}"
                                             for i in range(len(BLOCKS_OPERATIONS))]), True, "#EEEEEE")
]

get_pgevent_blocks = []
