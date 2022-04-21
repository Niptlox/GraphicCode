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
        for con in self.connections:
            pg.draw.line(surface, "#11FF11", self.pos_on_field(), con.pos_on_field(), width=3)

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
help_text = textfont.render("; ".join([f"{i + 1}: {BLOCKS[i].__name__}" for i in range(len(BLOCKS))]), True, "#EEEEEE")
