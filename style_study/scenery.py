"""Detailed places/props shared by the shorts (GRID px coordinates, 1 grid px = 6 screen px).
school(): brick school with a snowy roof, clock tower + bell, flag, framed lit windows with sills, double door with
steps, a wreath, snowy bushes and a full, readable SCHOOL sign plate.
naughty_list(): wider parchment scroll with a fully readable NAUGHTY LIST header, name lines and red X marks."""
import math
import numpy as np
from characters import Layers, seg
from blueprint_kit import hexc
import blueprint_kit as bk

S = 6
TAU = 2 * math.pi
_cache = {}
def _blit(F, c, M, x0, y0):
    x0, y0 = int(round(x0)), int(round(y0)); h_, w_ = M.shape
    for yy in range(h_):
        Y = (y0 + yy) * S
        if Y < 0 or Y + S > F.shape[0]: continue
        for xx in np.nonzero(M[yy])[0]:
            X = (x0 + xx) * S
            if 0 <= X and X + S <= F.shape[1]: F[Y:Y + S, X:X + S] = c[yy, xx]
def text_center(F, text, cx, y, px, colr):
    tw = len(text) * 6 * px - px
    bk.pixel_text(F, text, int(round(cx * S - tw / 2)), int(round(y * S)), px=px, colr=colr)

def school_sprite():
    if 'school' in _cache: return _cache['school']
    W_, H_ = 76, 66; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_); cx = 38
    # flag pole + flag
    L.add((np.abs(xx - cx) < 0.6) & (yy >= 0) & (yy < 6), hexc('#c4ccd8'), outline=False)
    L.add((xx >= cx + 1) & (xx < cx + 7) & (yy >= 0) & (yy < 4), lambda c, m: (c.__setitem__(m, hexc('#e8303a')), c.__setitem__(m & (yy >= 2), hexc('#2f9a52'))))
    # clock tower: snow cap, clock face fully above the roof line
    tower = (np.abs(xx - cx) <= 7) & (yy >= 6) & (yy < 26)
    def tf(c, m):
        c[m] = hexc('#c86a4a'); c[m & (xx > cx + 4)] = hexc('#a8503a')
        c[m & (yy < 9)] = hexc('#ffffff')                                                   # snow cap
        face = np.hypot(xx - cx, yy - 16) <= 5.2; c[face & m] = hexc('#3a4664')
        face2 = np.hypot(xx - cx, yy - 16) <= 4.3; c[face2 & m] = hexc('#f4f6fb'); c[face2 & m & (yy > 18)] = hexc('#d8dee8')
        for k in range(4):
            th = TAU * k / 4; c[m & (np.abs(xx - (cx + 3.2 * math.sin(th))) < 0.6) & (np.abs(yy - (16 - 3.2 * math.cos(th))) < 0.6)] = hexc('#3a4664')
        c[m & (seg(xx, yy, cx, 16, cx, 13) <= 0.6)] = hexc('#1b1428'); c[m & (seg(xx, yy, cx, 16, cx + 2.4, 16) <= 0.6)] = hexc('#1b1428')
    L.add(tower, tf)
    # main roof (snowy) and building
    roof = (yy >= 24) & (yy < 33) & (np.abs(xx - cx) <= 36 - (32 - yy) * 0.2)
    L.add(roof, lambda c, m: (c.__setitem__(m, hexc('#8a3a3a')), c.__setitem__(m & ((xx.astype(int) + yy.astype(int)) % 4 == 0), hexc('#7a2e2e')),
                              c.__setitem__(m & (yy < 27), hexc('#ffffff')), c.__setitem__(m & (yy >= 27) & (yy < 28) & ((xx.astype(int) % 5) < 2), hexc('#ffffff'))))
    body = (xx >= 3) & (xx < 73) & (yy >= 33) & (yy < 63)
    def bf(c, m):
        c[m] = hexc('#d0805a')
        brick = ((yy.astype(int) % 3) == 0) | (((xx.astype(int) + 3 * ((yy.astype(int) // 3) % 2)) % 6) == 0)
        c[m & brick] = hexc('#b8684a'); c[m & (xx > 66)] = c[m & (xx > 66)] * 0.85
        for wx in (8, 20, 50, 62):                                                          # framed windows, 2 rows
            for wy in (37, 49):
                fr = (xx >= wx - 1) & (xx < wx + 7) & (yy >= wy - 1) & (yy < wy + 8); c[fr & m] = hexc('#f4f6fb')
                gl = (xx >= wx) & (xx < wx + 6) & (yy >= wy) & (yy < wy + 7); c[gl & m] = hexc('#ffd86a'); c[gl & m & (yy > wy + 3)] = hexc('#ffc23a')
                c[gl & m & ((np.abs(xx - (wx + 3)) < 0.5) | (np.abs(yy - (wy + 3)) < 0.5))] = hexc('#f4f6fb')
                c[gl & m & (np.abs((xx - wx) - (yy - wy)) < 0.6) & (yy < wy + 3)] = hexc('#fff6d0')   # glass shine
                c[(xx >= wx - 2) & (xx < wx + 8) & (yy >= wy + 8) & (yy < wy + 9) & m] = hexc('#ffffff')  # snowy sill
        plate = (xx >= cx - 15) & (xx < cx + 15) & (yy >= 34) & (yy < 42); c[plate & m] = hexc('#f4f6fb')   # sign plate
        c[plate & m & ((yy < 35) | (yy >= 41) | (xx < cx - 14) | (xx >= cx + 14))] = hexc('#3a4664')
        door = (np.abs(xx - cx) <= 6) & (yy >= 46) & (yy < 63) & ~((yy < 49) & (np.hypot(xx - cx, yy - 49) > 6))
        c[door & m] = hexc('#6a4226'); c[door & m & (xx > cx)] = hexc('#5a3820'); c[door & m & (np.abs(xx - cx) < 0.6)] = hexc('#3a2418')
        for kx in (cx - 2, cx + 2): c[m & (np.abs(xx - kx) < 0.6) & (np.abs(yy - 55) < 0.6)] = hexc('#ffcc4a')
        wr = (np.hypot(xx - cx, yy - 51) <= 3) & (np.hypot(xx - cx, yy - 51) >= 1.6); c[wr & m] = hexc('#2f8f4a')   # wreath
        c[m & (np.abs(xx - cx) < 0.8) & (np.abs(yy - 53.5) < 0.8)] = hexc('#e8303a')
    L.add(body, bf)
    steps = ((np.abs(xx - cx) <= 9) & (yy >= 63) & (yy < 64)) | ((np.abs(xx - cx) <= 11) & (yy >= 64) & (yy < 66))
    L.add(steps, lambda c, m: (c.__setitem__(m, hexc('#c4ccd8')), c.__setitem__(m & (yy >= 65), hexc('#a8b2c4'))))
    for bx in (12, 64):                                                                       # snowy bushes
        bush = (((xx - bx) / 7) ** 2 + ((yy - 61) / 4) ** 2 <= 1)
        L.add(bush, lambda c, m, bx=bx: (c.__setitem__(m, hexc('#2f8f4a')), c.__setitem__(m & (yy < 59.5), hexc('#ffffff')),
                                         c.__setitem__(m & (xx > bx + 3) & (yy >= 59.5), hexc('#1d6a3a'))))
    _cache['school'] = L.out(); return _cache['school']

def school(F, cx, feet, shadow_fn=None):
    c, M = school_sprite(); h_, w_ = M.shape
    if shadow_fn: shadow_fn(F, cx, feet, w_ * 0.95)
    x0, y0 = cx - w_ / 2, feet - h_ + 1
    _blit(F, c, M, x0, y0)
    text_center(F, 'SCHOOL', round(x0) + w_ / 2, round(y0) + 35.5, px=4, colr=(30, 40, 80))

def naughty_sprite():
    if 'naughty' in _cache: return _cache['naughty']
    W_, H_ = 36, 46; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = Layers(W_, H_)
    def pf(c, m):
        g = np.clip((yy - 4) / 38, 0, 1)[..., None]                                          # smooth parchment blend
        c[m] = (hexc('#fbf2dc') * (1 - g) + hexc('#ead8b0') * g)[m]
        c[m & (yy >= 5) & (yy < 16)] = hexc('#c8303a')                                      # red header band
        c[m & (yy >= 15) & (yy < 16)] = hexc('#a01828')
        for k in range(5):                                                                    # name lines + clean 3x3 red X marks
            ly = 20 + k * 4
            c[m & (yy == ly) & (xx >= 6) & (xx < 24)] = hexc('#b89a6a')
            for d in (-1, 0, 1):
                c[m & (xx == 28 + d) & (yy == ly + d)] = hexc('#e8303a'); c[m & (xx == 28 - d) & (yy == ly + d)] = hexc('#e8303a')
    L.add((xx >= 3) & (xx < 33) & (yy >= 4) & (yy < 42), pf)
    for ry in (3, 42):
        L.add((xx >= 1) & (xx < 35) & (np.abs(yy - ry) <= 1.6), lambda c, m, ry=ry: (c.__setitem__(m, hexc('#d8c098')), c.__setitem__(m & (yy > ry), hexc('#b89a6a'))))
    _cache['naughty'] = L.out(); return _cache['naughty']

def naughty_list(F, cx, feet, shadow_fn=None):
    c, M = naughty_sprite(); h_, w_ = M.shape
    if shadow_fn: shadow_fn(F, cx, feet, w_ * 0.8)
    x0, y0 = round(cx - w_ / 2), round(feet - h_ + 1)
    _blit(F, c, M, x0, y0)
    text_center(F, 'NAUGHTY', x0 + w_ / 2, y0 + 6.2, px=3, colr=(255, 255, 255))
    text_center(F, 'LIST', x0 + w_ / 2, y0 + 10.6, px=3, colr=(255, 230, 150))
