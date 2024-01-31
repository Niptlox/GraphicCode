import pygame
from pygame import Vector2


def bicubik2D(tx: float, A: Vector2, B: Vector2, nA: Vector2, nB: Vector2):
    t2 = tx * tx
    Bk = t2 * (3 - 2 * tx)
    Ak = 1 - Bk
    nAk = tx * (1 + (tx - 2) * tx)
    nBk = t2 * (tx - 1)
    rx = A.x * Ak + nAk * nA.x + B.x * Bk + nBk * nB.x
    ry = A.y * Ak + nAk * nA.y + B.y * Bk + nBk * nB.y
    return Vector2(rx, ry)


def len2(p1, p2):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5


def draw_bicubik_line(surface, color, p0: Vector2, p1: Vector2, width=1, kk=150):
    w = len2(p0, p1) / 10 + 25
    # w = 5
    last_pos = p0
    for ix in range(int(w)):
        i = ix / w
        pos = bicubik2D(i, p0, p1, Vector2(kk, 0), Vector2(kk, 0))
        pygame.draw.line(surface, color, last_pos, pos, width)
        last_pos = pos
    pygame.draw.line(surface, color, last_pos, p1, width)
