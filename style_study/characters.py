"""Clean layered pixel characters (simple body parts, flat colours, each part outlined, readable faces).
Every function returns (colour array, mask) in grid pixels (1 grid px = 6 screen px)."""
import math
import numpy as np
from blueprint_kit import hexc, OUTLINE

class Layers:
    def __init__(self, w, h):
        self.c = np.zeros((h, w, 3), np.float32); self.m = np.zeros((h, w), bool)
    def add(self, mask, fill, outline=True):
        col = np.zeros_like(self.c); fill(col, mask) if callable(fill) else col.__setitem__(mask, fill)
        if outline:
            p = np.pad(mask, 1); ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~mask
            self.c[ring] = OUTLINE; self.m |= ring
        self.c[mask] = col[mask]; self.m |= mask
    def out(self, flip=False):
        return (self.c[:, ::-1].copy(), self.m[:, ::-1].copy()) if flip else (self.c, self.m)

def seg(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; t = np.clip(((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy + 1e-9), 0, 1)
    return np.hypot(px - (ax + t * dx), py - (ay + t * dy))

def santa():
    W_, H_ = 46, 52; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); cx = 23; L = Layers(W_, H_)
    RED, RED_D, RED_L, WH, WH_S = hexc('#d22a38'), hexc('#a0182a'), hexc('#ee4a52'), hexc('#ffffff'), hexc('#dfe6f0')
    legs = (yy >= 40) & (yy < 46) & ((np.abs(xx - 17) <= 3) | (np.abs(xx - 29) <= 3))
    boots = (yy >= 45) & (yy < 50) & ((np.abs(xx - 16.5) <= 4) | (np.abs(xx - 29.5) <= 4))
    L.add(legs | boots, lambda c, m: (c.__setitem__(m, RED_D), c.__setitem__(boots, hexc('#1b1418'))))
    body = ((xx - cx) / 12) ** 2 + ((yy - 32) / 11) ** 2 <= 1
    def bc(c, m):
        c[m] = RED; c[m & (xx > cx + 5)] = RED_D; c[m & (xx < cx - 6) & (yy < 30)] = RED_L; c[m & (np.abs(xx - cx) < 1.6)] = WH
        b = m & (np.abs(yy - 34) < 1.6); c[b] = hexc('#1b1418'); c[b & (np.abs(xx - cx) < 2.6)] = hexc('#ffcc4a')
        c[b & (np.abs(xx - cx) < 1.1) & (np.abs(yy - 34) < 0.6)] = hexc('#1b1418'); c[m & (yy > 40.5)] = WH
    L.add(body, bc)
    head = ((xx - cx) / 7) ** 2 + ((yy - 15) / 6.5) ** 2 <= 1
    beard = (((xx - cx) / 8.5) ** 2 + ((yy - 21) / 6.5) ** 2 <= 1) & (yy >= 17)
    def hc(c, m):
        c[m] = hexc('#f6c9a8'); c[m & (xx > cx + 4)] = hexc('#e8b090'); c[beard] = WH; c[beard & (xx > cx + 4) & (yy > 21)] = WH_S
        for ex in (cx - 3, cx + 3):
            c[(xx >= ex - 1) & (xx < ex + 1) & (yy >= 14) & (yy < 17)] = hexc('#1b1428'); c[(xx >= ex - 1) & (xx < ex) & (yy >= 14) & (yy < 15)] = WH
        c[((xx - cx) / 1.8) ** 2 + ((yy - 18) / 1.5) ** 2 <= 1] = hexc('#e8807a')
        for ck in (cx - 5, cx + 5): c[((xx - ck) / 1.2) ** 2 + ((yy - 17.6) / 0.9) ** 2 <= 1] = hexc('#f2a0a0')
        c[(yy >= 21.5) & (yy < 23) & (np.abs(xx - cx) < 2)] = hexc('#8a3a3a')
    L.add(head | beard, hc)
    hat = (yy >= 1) & (yy < 10) & (np.abs(xx - cx - (10 - yy) * 0.5) <= 1.5 + (yy - 1) * 0.85)
    L.add(hat, lambda c, m: (c.__setitem__(m, RED), c.__setitem__(m & (xx > cx + 3), RED_D)))
    brim = (yy >= 9) & (yy < 12) & (np.abs(xx - cx) <= 8)
    L.add(brim, lambda c, m: (c.__setitem__(m, WH), c.__setitem__(m & (yy >= 11), WH_S)))
    L.add(((xx - (cx + 7.5)) / 2.4) ** 2 + ((yy - 2) / 2.4) ** 2 <= 1, WH)
    for side in (-1, 1):
        sx = cx + side * 11
        arm = (np.abs((xx - sx) - side * (yy - 26) * 0.3) <= 2.4) & (yy >= 25) & (yy <= 34)
        L.add(arm, lambda c, m: (c.__setitem__(m, RED if side < 0 else RED_D), c.__setitem__(m & (yy >= 33), WH)))
        mit = ((xx - (sx + side * 3.2)) / 2.7) ** 2 + ((yy - 36.5) / 2.7) ** 2 <= 1
        L.add(mit, lambda c, m: (c.__setitem__(m, hexc('#1f7a3e')), c.__setitem__(m & (yy < 36), hexc('#2f9a52'))))
    return L.out()

THERMAL = {'body': hexc('#3a2a8a'), 'body_d': hexc('#241a5e'), 'belly': hexc('#5a3aa8'), 'leg': hexc('#1d1650'),
           'head': hexc('#7a3aa8'), 'nose': hexc('#ffe45a'), 'nose_ring': hexc('#ff4a2a'), 'antler': hexc('#120e30'), 'eye': hexc('#ff8a3a')}
def reindeer(nose='red', eye_col='#1b1428', antlers=True, thermal=False, step=0.0, head_down=0.0, glow=0.0, flip=False):
    """side view facing right, ~64x60 grid px. nose: 'red' or 'black'. head_down 0..1 lowers the head to the snow."""
    W_, H_ = 66, 62; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_)
    BR, BR_D, BR_L, CREAM, HOOF = hexc('#8a5a36'), hexc('#6a4226'), hexc('#a8744a'), hexc('#efe0c4'), hexc('#2a1a12')
    if thermal: BR, BR_D, BR_L, CREAM, HOOF = THERMAL['body'], THERMAL['body_d'], THERMAL['belly'], THERMAL['belly'], THERMAL['leg']
    oy = 12 * head_down                                          # head offset when sniffing the snow
    hx, hy = 47 + 4 * head_down, 22 + oy
    for k, (lx, ph, back) in enumerate(((17, 0, True), (35, math.pi, True), (21, math.pi, False), (39, 0, False))):
        off = 2.4 * math.sin(step * math.tau + ph) if step else 0
        leg = seg(xx, yy, lx, 40, lx + off, 55) <= 1.8
        hoof = seg(xx, yy, lx + off, 54, lx + off + 1, 56) <= 1.9
        L.add(leg | hoof, lambda c, m: (c.__setitem__(m, BR_D if back else BR), c.__setitem__(hoof, HOOF)))
    L.add(((xx - 12) / 2.6) ** 2 + ((yy - 31) / 3) ** 2 <= 1, CREAM)                          # tail
    body = ((xx - 28) / 16) ** 2 + ((yy - 35) / 8.5) ** 2 <= 1
    L.add(body, lambda c, m: (c.__setitem__(m, BR), c.__setitem__(m & (yy > 38), BR_L if not thermal else BR_L),
                              c.__setitem__(m & (xx < 18) & (yy < 33), BR_D)))
    neck = seg(xx, yy, 38, 33, hx - 4, hy + 2) <= 4.6
    L.add(neck, CREAM)
    if antlers:
        A = np.zeros_like(body)
        ax, ay = hx - 3, hy - 4
        for (a, b) in (((0, 0), (-3, -9)), ((-3, -9), (-8, -15)), ((-3, -9), (1, -15)), ((-5, -12), (-10, -11)),
                       ((3, 0), (6, -8)), ((6, -8), (4, -14)), ((6, -8), (10, -12))):
            A |= seg(xx, yy, ax + a[0], ay + a[1], ax + b[0], ay + b[1]) <= 1.2
        L.add(A, THERMAL['antler'] if thermal else hexc('#d9c08a'))
    head = ((xx - hx) / 6) ** 2 + ((yy - hy) / 5) ** 2 <= 1
    snout = ((xx - (hx + 6)) / 4.4) ** 2 + ((yy - (hy + 2)) / 3.2) ** 2 <= 1
    ear = ((xx - (hx - 5)) / 3) ** 2 + ((yy - (hy - 3)) / 1.6) ** 2 <= 1
    L.add(ear, BR_D)
    def head_fill(c, m):
        c[m] = THERMAL['head'] if thermal else BR; c[snout] = THERMAL['head'] if thermal else BR_L
        ex, ey = hx + 1, hy - 1                                                                 # clear eye: 2x2 + highlight
        e = (xx >= ex - 1) & (xx < ex + 2) & (yy >= ey - 1) & (yy < ey + 2)                      # 3x3 eye
        c[e] = THERMAL['eye'] if thermal else hexc(eye_col)
        if eye_col != '#1b1428' and not thermal: c[(xx >= ex) & (xx < ex + 2) & (yy >= ey) & (yy < ey + 2)] = hexc('#1b1428')
        c[(xx >= ex - 1) & (xx < ex) & (yy >= ey - 1) & (yy < ey)] = hexc('#ffffff')
    L.add(head | snout, head_fill)
    nx, ny = hx + 10, hy + 1.5
    nm = ((xx - nx) / 2.4) ** 2 + ((yy - ny) / 2.2) ** 2 <= 1
    if thermal: L.add(nm, lambda c, m: (c.__setitem__(m, THERMAL['nose']), c.__setitem__(m & (((xx - nx) / 2.4) ** 2 + ((yy - ny) / 2.2) ** 2 > 0.45), THERMAL['nose_ring'])))
    elif nose == 'red': L.add(nm, lambda c, m: (c.__setitem__(m, hexc('#ff2a3c')), c.__setitem__(m & (xx < nx - 0.5) & (yy < ny - 0.5), hexc('#ffb0b8'))))
    else: L.add(nm, lambda c, m: (c.__setitem__(m, hexc('#2a1c20')), c.__setitem__(m & (xx < nx - 0.5) & (yy < ny - 0.5), hexc('#5a4048'))))
    col, M = L.out(flip)
    return col, M, ((nx if not flip else W_ - 1 - nx), ny), ((hx + 1) if not flip else W_ - 1 - (hx + 1), hy - 1)

def wolf(uv=False, flip=True, step=0.0):
    """side view facing right (flipped to face left by default), ~52x36."""
    W_, H_ = 54, 38; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_)
    G, G_D, G_L = (hexc('#7a8090'), hexc('#555a68'), hexc('#c4c8d2')) if not uv else (hexc('#14102a'), hexc('#0c0a1c'), hexc('#1e1838'))
    for lx, ph in ((14, 0), (20, math.pi), (32, math.pi), (38, 0)):
        off = 2 * math.sin(step * math.tau + ph) if step else 0
        L.add(seg(xx, yy, lx, 24, lx + off, 35) <= 1.6, G_D)
    L.add(seg(xx, yy, 8, 18, 1, 24) <= 2.6, G)                                                   # tail
    L.add(((xx - 26) / 15) ** 2 + ((yy - 20) / 6.5) ** 2 <= 1, lambda c, m: (c.__setitem__(m, G), c.__setitem__(m & (yy > 22), G_L)))
    head = ((xx - 42) / 6) ** 2 + ((yy - 13) / 5) ** 2 <= 1
    snout = ((xx - 49) / 4.5) ** 2 + ((yy - 15) / 2.4) ** 2 <= 1
    ears = ((yy >= 3) & (yy < 10) & (np.abs(xx - 38.5) <= (yy - 3) * 0.32)) | ((yy >= 3) & (yy < 10) & (np.abs(xx - 44) <= (yy - 3) * 0.32))
    def hf(c, m):
        c[m] = G; c[snout] = G_L
        c[(xx >= 42) & (xx < 45) & (yy >= 10) & (yy < 13)] = hexc('#ffd84a')
        c[(xx >= 43) & (xx < 45) & (yy >= 11) & (yy < 13)] = hexc('#1b1428')
        c[(xx >= 42) & (xx < 43) & (yy >= 10) & (yy < 11)] = hexc('#ffffff')
        c[((xx - 53) / 1.3) ** 2 + ((yy - 14.5) / 1.1) ** 2 <= 1] = hexc('#1b1428')
    L.add(head | snout | ears, hf)
    return L.out(flip)

def sleigh(santa_in=True):
    """side view facing right, ~48x40; Santa (front view, waist up) sits in it; gift sack behind him"""
    W_, H_ = 50, 44; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_)
    RED, RED_D, GOLD = hexc('#d22a38'), hexc('#a0182a'), hexc('#ffcc4a')
    sack = ((xx - 11) / 7.5) ** 2 + ((yy - 17) / 8) ** 2 <= 1
    L.add(sack, lambda c, m: (c.__setitem__(m, hexc('#8a5a36')), c.__setitem__(m & (xx > 13), hexc('#6a4226'))))
    for gx, gy, gc in ((8, 9, '#3a8aff'), (14, 8, '#5ae07a')):
        g = (np.abs(xx - gx) <= 2.5) & (np.abs(yy - gy) <= 2.5)
        L.add(g, lambda c, m, gc=gc: (c.__setitem__(m, hexc(gc)), c.__setitem__(m & ((np.abs(xx - gx) < 0.6) | (np.abs(yy - gy) < 0.6)), GOLD)))
    body = (yy >= 22) & (yy < 34) & (xx >= 4) & (xx <= 40 + (yy - 22) * 0.4) & ~((((xx - 40) / 5) ** 2 + ((yy - 22) / 4) ** 2 <= 1) & (yy < 24))
    front = ((xx - 42) / 4.5) ** 2 + ((yy - 24) / 6) ** 2 <= 1
    L.add(body | front, lambda c, m: (c.__setitem__(m, RED), c.__setitem__(m & (yy > 30), RED_D),
                                       c.__setitem__(m & (np.abs(yy - 26) < 0.8) & (xx < 41), GOLD)))
    run = ((yy >= 38) & (yy < 40) & (xx >= 2) & (xx <= 44)) | (((xx - 45) / 3) ** 2 + ((yy - 36) / 3) ** 2 <= 1) & ~(((xx - 45) / 1.6) ** 2 + ((yy - 36) / 1.6) ** 2 <= 1) & (xx > 44)
    struts = ((np.abs(xx - 12) < 1) | (np.abs(xx - 32) < 1)) & (yy >= 34) & (yy < 38)
    L.add(run | struts, GOLD)
    return L.out()

def house(broken=False, lit=True):
    """front view ~42x40 with snowy roof, chimney, door and two windows"""
    W_, H_ = 42, 40; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_)
    L.add((xx >= 28) & (xx < 33) & (yy >= 2) & (yy < 14), lambda c, m: (c.__setitem__(m, hexc('#a8504a')), c.__setitem__(m & (yy < 4), hexc('#ffffff'))))
    L.add((xx >= 6) & (xx < 36) & (yy >= 17) & (yy < 38), lambda c, m: (c.__setitem__(m, hexc('#f0dcb8')), c.__setitem__(m & (xx > 30), hexc('#d8c09a'))))
    roof = (yy >= 4) & (yy < 18) & (np.abs(xx - 20.5) <= (yy - 3) * 1.45)
    L.add(roof, lambda c, m: (c.__setitem__(m, hexc('#c8303a')), c.__setitem__(m & (np.abs(xx - 20.5) > (yy - 3) * 1.45 - 2.5), hexc('#ffffff'))))
    L.add((xx >= 18) & (xx < 24) & (yy >= 28) & (yy < 38), lambda c, m: (c.__setitem__(m, hexc('#6a4226')), c.__setitem__(m & (np.abs(xx - 22.5) < 0.6) & (np.abs(yy - 33) < 0.6), hexc('#ffcc4a'))))
    for wx in (9, 26):
        win = (xx >= wx) & (xx < wx + 7) & (yy >= 21) & (yy < 28)
        def wf(c, m, wx=wx):
            c[m] = hexc('#1d2848') if broken else (hexc('#ffd84a') if lit else hexc('#9fd8ff'))
            if not broken: c[m & ((np.abs(xx - (wx + 3)) < 0.6) | (np.abs(yy - 24) < 0.6))] = hexc('#6a4226')
            else:
                c[m & (np.abs((xx - wx) - (yy - 21)) < 0.7)] = hexc('#cfe9ff'); c[m & (np.abs((xx - wx) + (yy - 21) - 6) < 0.7) & (yy < 25)] = hexc('#cfe9ff')
        L.add(win, wf)
    return L.out()

def professor():
    """front view ~32x52: grey hair, glasses, lab coat, pointer"""
    W_, H_ = 34, 54; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); cx = 16; L = Layers(W_, H_)
    L.add((yy >= 42) & (yy < 52) & ((np.abs(xx - 12.5) <= 2.2) | (np.abs(xx - 19.5) <= 2.2)), lambda c, m: (c.__setitem__(m, hexc('#3a4664')), c.__setitem__(m & (yy >= 49), hexc('#1b1418'))))
    coat = (yy >= 22) & (yy < 45) & (np.abs(xx - cx) <= 7 + (yy - 22) * 0.12)
    L.add(coat, lambda c, m: (c.__setitem__(m, hexc('#f4f6fb')), c.__setitem__(m & (xx > cx + 4), hexc('#d8dee8')),
                              c.__setitem__(m & (np.abs(xx - cx) < 2) & (yy < 30), hexc('#5a8ad8')), c.__setitem__(m & (np.abs(xx - cx) < 0.6) & (yy >= 30), hexc('#c4ccd8'))))
    for side in (-1, 1):
        arm = (np.abs((xx - (cx + side * 9)) - side * (yy - 24) * 0.25) <= 2) & (yy >= 23) & (yy <= 36)
        L.add(arm, hexc('#e8ecf4'))
        L.add(((xx - (cx + side * 12)) / 2.2) ** 2 + ((yy - 37.5) / 2.2) ** 2 <= 1, hexc('#f6c9a8'))
    L.add(seg(xx, yy, cx + 12, 37, cx + 17, 24) <= 0.8, hexc('#8a5a36'), outline=False)
    head = ((xx - cx) / 7) ** 2 + ((yy - 13) / 8) ** 2 <= 1
    hair = (((xx - (cx - 7)) / 3.2) ** 2 + ((yy - 10) / 4.5) ** 2 <= 1) | (((xx - (cx + 7)) / 3.2) ** 2 + ((yy - 10) / 4.5) ** 2 <= 1) | (((xx - cx) / 5) ** 2 + ((yy - 5) / 2.2) ** 2 <= 1)
    def hf(c, m):
        c[m] = hexc('#f6c9a8'); c[hair & m] = hexc('#dfe3ea')
        for ex in (cx - 3, cx + 3):
            g = (np.abs(xx - ex) <= 2.5) & (np.abs(yy - 13) <= 2); c[g] = hexc('#1b1428')
            c[(np.abs(xx - ex) <= 1.5) & (np.abs(yy - 13) <= 1)] = hexc('#cfe9ff'); c[(xx >= ex - 0.5) & (xx < ex + 0.5) & (yy >= 12.5) & (yy < 13.5)] = hexc('#1b1428')
        c[(np.abs(yy - 13) < 0.6) & (np.abs(xx - cx) < 1)] = hexc('#1b1428')
        c[(yy >= 17.5) & (yy < 18.5) & (np.abs(xx - cx) < 2.5)] = hexc('#8a3a3a'); c[(yy >= 16.5) & (yy < 17.5) & (np.abs(np.abs(xx - cx) - 3) < 0.6)] = hexc('#8a3a3a')
    L.add(head | hair, hf)
    return L.out()

def scroll():
    """unrolled list ~26x36"""
    W_, H_ = 26, 38; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_)
    L.add((xx >= 3) & (xx < 23) & (yy >= 4) & (yy < 34), lambda c, m: (c.__setitem__(m, hexc('#f6ead0')),
          c.__setitem__(m & (yy >= 10) & ((yy.astype(int) - 10) % 4 == 0) & (xx >= 6) & (xx < 20), hexc('#c8a878'))))
    for ry in (3, 34): L.add((xx >= 1) & (xx < 25) & (np.abs(yy - ry) <= 1.6), lambda c, m: (c.__setitem__(m, hexc('#d8c098')), c.__setitem__(m & (yy > ry), hexc('#b89a6a'))))
    return L.out()

def elf(outfit='#2f9a52', outfit_d='#1f7a3e', hat='#2f9a52', messy=False, mood='happy', arms='down', cap=False):
    """front view ~36x50. messy: hair tufts + tape on the hat. mood: happy / sad / shock / proud"""
    W_, H_ = 38, 54; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); cx = 19; L = Layers(W_, H_)
    SKIN, SKIN_D = hexc('#f6c9a8'), hexc('#e8b090')
    shoes = (((xx - 13) / 4.2) ** 2 + ((yy - 50) / 2) ** 2 <= 1) | (((xx - 25) / 4.2) ** 2 + ((yy - 50) / 2) ** 2 <= 1)
    legs = (yy >= 42) & (yy < 50) & ((np.abs(xx - 15) <= 1.8) | (np.abs(xx - 23) <= 1.8))
    L.add(legs | shoes, lambda c, m: (c.__setitem__(m, hexc('#c81e2e')), c.__setitem__(m & ((((xx - 13) / 4.2) ** 2 + ((yy - 50) / 2) ** 2 <= 1) | (((xx - 25) / 4.2) ** 2 + ((yy - 50) / 2) ** 2 <= 1)), hexc('#6a4226'))))
    body = (yy >= 27) & (yy < 44) & (np.abs(xx - cx) <= 6 + (yy - 27) * 0.28)
    def bf(c, m):
        c[m] = hexc(outfit); c[m & (xx > cx + 3)] = hexc(outfit_d)
        c[m & (np.abs(yy - 37) < 1.2)] = hexc('#1b1418'); c[m & (np.abs(yy - 37) < 1.2) & (np.abs(xx - cx) < 1.6)] = hexc('#ffcc4a')
        zig = (yy < 30 + (np.abs(((xx - cx) % 4) - 2))) & m; c[zig] = hexc('#ffffff')
    L.add(body, bf)
    for side in (-1, 1):
        sx = cx + side * 8
        if arms == 'up':
            arm = seg(xx, yy, sx, 29, sx + side * 5, 20) <= 1.9; hx_, hy_ = sx + side * 5.5, 18.5
        elif arms == 'hold':
            arm = seg(xx, yy, sx, 29, cx + side * 4, 36) <= 1.9; hx_, hy_ = cx + side * 3.5, 37
        else:
            arm = seg(xx, yy, sx, 29, sx + side * 2, 38) <= 1.9; hx_, hy_ = sx + side * 2.2, 39.5
        L.add(arm, hexc(outfit_d if side > 0 else outfit))
        L.add(((xx - hx_) / 2.2) ** 2 + ((yy - hy_) / 2.2) ** 2 <= 1, SKIN)
    head = ((xx - cx) / 7) ** 2 + ((yy - 20) / 6.8) ** 2 <= 1
    ears = ((yy >= 15) & (yy < 22) & (xx < cx - 5) & (xx > cx - 12) & (np.abs(yy - 19 + (cx - 5 - xx) * 0.5) < 2.2 - (cx - 5 - xx) * 0.25)) | \
           ((yy >= 15) & (yy < 22) & (xx > cx + 5) & (xx < cx + 12) & (np.abs(yy - 19 + (xx - cx - 5) * 0.5) < 2.2 - (xx - cx - 5) * 0.25))
    L.add(ears, SKIN)
    def hf(c, m):
        c[m] = SKIN if mood != 'angry' else hexc('#f08a7a'); c[m & (xx > cx + 4)] = SKIN_D if mood != 'angry' else hexc('#d86a5a')
        for ex in (cx - 3, cx + 3):
            if mood in ('proud', 'real'):
                c[(np.abs(xx - ex) <= 1.5) & (np.abs(yy - 20 + 0.6 * (1 - ((xx - ex) / 1.5) ** 2)) < 0.6)] = hexc('#1b1428')
            else:
                hgt = 4 if mood == 'shock' else 3
                c[(xx >= ex - 1) & (xx < ex + 1) & (yy >= 18) & (yy < 18 + hgt)] = hexc('#1b1428')
                c[(xx >= ex - 1) & (xx < ex) & (yy >= 18) & (yy < 19)] = hexc('#ffffff')
        for ck in (cx - 5, cx + 5): c[((xx - ck) / 1.2) ** 2 + ((yy - 23) / 0.9) ** 2 <= 1] = hexc('#f2a0a0')
        if mood == 'real':                                                  # crow's feet: the eyes crinkle
            for sd_ in (-1, 1):
                ex = cx + sd_ * 5.5
                c[(np.abs(xx - ex) < 0.6) & (yy >= 18) & (yy < 19)] = hexc('#c8806a'); c[(np.abs(xx - ex) < 0.6) & (yy >= 20) & (yy < 21)] = hexc('#c8806a')
        if mood == 'angry':
            for sd_ in (-1, 1):
                c[(np.abs(yy - (16.6 + sd_ * (xx - cx) * 0.35)) < 0.6) & (np.abs(xx - (cx + sd_ * 3)) < 2)] = hexc('#1b1428')
        if mood in ('fake', 'real'):                                        # big toothy grin
            c[(yy >= 23.5) & (yy < 26.5) & (np.abs(xx - cx) < 3.5 - (yy - 23.5) * 0.6)] = hexc('#8a3a3a')
            c[(yy >= 23.5) & (yy < 24.5) & (np.abs(xx - cx) < 3)] = hexc('#ffffff')
            if mood == 'fake':
                c[(np.abs(xx - (cx + 6)) < 0.6) & (yy >= 15) & (yy < 18)] = hexc('#9fd8ff'); c[(np.abs(xx - (cx + 6)) < 1.1) & (yy >= 17) & (yy < 18)] = hexc('#9fd8ff')
        elif mood == 'angry':
            c[(yy >= 25) & (yy < 26) & (np.abs(xx - cx) < 2)] = hexc('#5a1a2a'); c[(yy >= 26) & (yy < 27) & (np.abs(np.abs(xx - cx) - 2.5) < 0.6)] = hexc('#5a1a2a')
        elif mood in ('happy', 'proud'):
            c[(yy >= 24.5) & (yy < 25.5) & (np.abs(xx - cx) < 2)] = hexc('#8a3a3a'); c[(yy >= 23.5) & (yy < 24.5) & (np.abs(np.abs(xx - cx) - 2.5) < 0.6)] = hexc('#8a3a3a')
        elif mood == 'sad':
            c[(yy >= 24.5) & (yy < 25.5) & (np.abs(xx - cx) < 2)] = hexc('#8a3a3a'); c[(yy >= 25.5) & (yy < 26.5) & (np.abs(np.abs(xx - cx) - 2.5) < 0.6)] = hexc('#8a3a3a')
        else:
            c[((xx - cx) / 1.5) ** 2 + ((yy - 25) / 1.5) ** 2 <= 1] = hexc('#5a1a2a')
    L.add(head, hf)
    if cap:
        capm = ((yy >= 9) & (yy < 12) & (np.abs(xx - cx) <= 9)) | ((yy >= 12) & (yy < 15) & (np.abs(xx - cx) <= 5))
        L.add(capm, hexc('#1b1428'))
        L.add(seg(xx, yy, cx + 8, 10, cx + 9, 17) <= 0.7, hexc('#ffcc4a'), outline=False)
    else:
        hatm = (yy >= 2) & (yy < 15) & (np.abs(xx - cx - (15 - yy) * 0.55) <= 1 + (yy - 2) * 0.55)
        L.add(hatm, lambda c, m: (c.__setitem__(m, hexc(hat)), c.__setitem__(m & (xx > cx + 5), hexc(outfit_d))))
        L.add((yy >= 13) & (yy < 16) & (np.abs(xx - cx) <= 7.5), hexc('#ffffff'))
        L.add(((xx - (cx + 9)) / 2) ** 2 + ((yy - 2.5) / 2) ** 2 <= 1, hexc('#ffcc4a'))
        if messy:
            L.add((np.abs((xx - cx + 2) - (yy - 6) * 0.9) < 1.3) & (yy >= 4) & (yy < 9), hexc('#e8eef6'), outline=False)
    if messy:
        tufts = ((yy >= 15) & (yy < 18) & ((np.abs(xx - (cx - 7)) < 1) | (np.abs(xx - (cx + 7)) < 1) | (np.abs(xx - (cx - 5)) < 0.6)))
        L.add(tufts, hexc('#e8a83a'))
    return L.out()

def gift_neat(paper='#3a8aff', ribbon='#ffcc4a', w=26, h=22):
    W_, H_ = w + 4, h + 12; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_); cx = W_ / 2
    box = (xx >= 2) & (xx < w + 2) & (yy >= 10) & (yy < h + 10)
    def bf(c, m):
        c[m] = hexc(paper); c[m & (xx > w - 3)] = hexc(paper) * 0.8
        c[m & ((np.abs(xx + 0.5 - cx) < 2) | (np.abs(yy - 10 - h * 0.45) < 1.6))] = hexc(ribbon)
        c[m & (yy < 13)] = c[m & (yy < 13)] * 1.0
    L.add(box, bf)
    bow = (((xx - (cx - 4)) / 4) ** 2 + ((yy - 7) / 2.8) ** 2 <= 1) | (((xx - (cx + 4)) / 4) ** 2 + ((yy - 7) / 2.8) ** 2 <= 1)
    L.add(bow, hexc(ribbon)); L.add(((xx - cx) / 1.8) ** 2 + ((yy - 8) / 1.8) ** 2 <= 1, hexc(ribbon) * 0.85)
    return L.out()

def gift_messy(w=28, h=24, seed=2):
    """lumpy, torn, over-taped, bow squashed off to one side"""
    W_, H_ = w + 8, h + 12; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_)
    rng = np.random.default_rng(seed); cx, cy = W_ / 2, 10 + h / 2
    ang = np.arctan2(yy - cy, xx - cx); rr = 1 + 0.10 * np.sin(ang * 3 + 1) + 0.07 * np.sin(ang * 7 + 2)
    blob = (np.maximum(np.abs(xx - cx) / (w / 2), np.abs(yy - cy) / (h / 2)) ** 1.0 <= rr * 0.98)
    def bf(c, m):
        c[m] = hexc('#e8303a'); c[m & (xx + yy * 0.6 > cx + cy * 0.6 + 4)] = hexc('#ff5a64')
        c[m & (np.abs(xx - cx - 3 + (yy - cy) * 0.4) < 0.8)] = hexc('#a0182a')
        torn = m & (((xx - (cx + w * 0.28)) / 5) ** 2 + ((yy - (cy + h * 0.22)) / 4) ** 2 <= 1)
        c[torn] = hexc('#b8835a'); c[torn & (xx < cx + w * 0.28 - 3)] = hexc('#ffffff')
        for k in range(6):
            tx, ty, ta = rng.uniform(4, W_ - 4), rng.uniform(12, H_ - 4), rng.uniform(-1, 1)
            tape = m & (np.abs((yy - ty) - ta * (xx - tx)) < 1.6) & (np.abs(xx - tx) < 6)
            c[tape] = c[tape] * 0.45 + hexc('#f4f8ff') * 0.55
    L.add(blob, bf)
    bow = (((xx - (W_ - 6)) / 3.5) ** 2 + ((yy - 10) / 2) ** 2 <= 1) | (((xx - (W_ - 3)) / 2.2) ** 2 + ((yy - 13) / 3) ** 2 <= 1)
    L.add(bow, hexc('#ffcc4a'))
    return L.out()

def mug():
    W_, H_ = 22, 20; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_)
    L.add(~((((xx - 16) / 4) ** 2 + ((yy - 9) / 4) ** 2) <= 0.35) & ((((xx - 16) / 4) ** 2 + ((yy - 9) / 4) ** 2) <= 1) & (xx > 14), hexc('#f4f6fb'))
    L.add((xx >= 2) & (xx < 15) & (yy >= 3) & (yy < 18), lambda c, m: (c.__setitem__(m, hexc('#f4f6fb')), c.__setitem__(m & (xx > 11), hexc('#d8dee8')),
                                                                     c.__setitem__(m & (np.abs(yy - 10) < 1.5) & (xx < 12), hexc('#e8303a'))))
    return L.out()

def cat_candle(lit=True):
    """an orange candle shaped like a sitting cat, wick + flame on its head"""
    W_, H_ = 26, 36; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_); cx = 13
    body = ((xx - cx) / 9) ** 2 + ((yy - 27) / 8) ** 2 <= 1
    head = ((xx - cx) / 7) ** 2 + ((yy - 17) / 6) ** 2 <= 1
    ears = ((yy >= 9) & (yy < 14) & ((np.abs(xx - (cx - 4.5)) <= (yy - 9) * 0.45) | (np.abs(xx - (cx + 4.5)) <= (yy - 9) * 0.45)))
    def f(c, m):
        c[m] = hexc('#ff9a3a'); c[m & (xx > cx + 3)] = hexc('#e8782a')
        for ex in (cx - 2.5, cx + 2.5): c[(np.abs(xx - ex) < 0.8) & (yy >= 16) & (yy < 18)] = hexc('#1b1428')
        c[(np.abs(xx - cx) < 0.8) & (yy >= 19) & (yy < 20)] = hexc('#e8607a')
        for wy in (19.5, 20.5):
            c[(np.abs(yy - wy) < 0.4) & (np.abs(np.abs(xx - cx) - 6) < 1.2)] = hexc('#ffd8b0')
        c[m & (np.abs(yy - 29) < 0.7) & (np.abs(xx - cx) < 8)] = hexc('#e8782a')
    L.add(body | head | ears, f)
    L.add((np.abs(xx - cx) < 0.6) & (yy >= 7) & (yy < 11), hexc('#3a2a20'), outline=False)
    if lit:
        fl = ((xx - cx) / 1.6) ** 2 + ((yy - 4.5) / 3) ** 2 <= 1
        L.add(fl, lambda c, m: (c.__setitem__(m, hexc('#ffcc4a')), c.__setitem__(m & (yy > 4.5), hexc('#fff6a0'))), outline=False)
    return L.out()
