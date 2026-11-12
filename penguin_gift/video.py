"""Renders 'What If Penguins Gave Christmas Gifts?' - 1080x1920 / 60 fps pixel art.

A penguin in a Santa hat hunts for the perfect pebble, gets it stolen, finds an even better one and
gives it to his favourite penguin. Plot twist: gentoo penguins really do give pebbles. Every pebble
of their nest lands on a note of We Wish You a Merry Christmas. Clean style: chunky 6x pixels, black
outlines, flat shading, and smooth sub-pixel motion for everything that moves.

usage: python3 video.py out.mp4 audio.wav
       python3 video.py --stills DIR t1 t2 ...
"""
import sys, subprocess, math
import numpy as np
from score import *

W, H, S = 180, 320, 6
TAU = 2 * math.pi
def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
def pal(*c): return np.stack([hexc(x) for x in c])
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16
YY, XX = np.mgrid[0:H, 0:W]

FONT = {
 'A': ["01110","10001","10001","11111","10001","10001","10001"], 'B': ["11110","10001","10001","11110","10001","10001","11110"],
 'C': ["01110","10001","10000","10000","10000","10001","01110"], 'D': ["11110","10001","10001","10001","10001","10001","11110"],
 'E': ["11111","10000","10000","11110","10000","10000","11111"], 'F': ["11111","10000","10000","11110","10000","10000","10000"],
 'G': ["01110","10001","10000","10111","10001","10001","01111"], 'H': ["10001","10001","10001","11111","10001","10001","10001"],
 'I': ["01110","00100","00100","00100","00100","00100","01110"], 'J': ["00111","00010","00010","00010","00010","10010","01100"],
 'K': ["10001","10010","10100","11000","10100","10010","10001"], 'L': ["10000","10000","10000","10000","10000","10000","11111"],
 'M': ["10001","11011","10101","10101","10001","10001","10001"], 'N': ["10001","10001","11001","10101","10011","10001","10001"],
 'O': ["01110","10001","10001","10001","10001","10001","01110"], 'P': ["11110","10001","10001","11110","10000","10000","10000"],
 'Q': ["01110","10001","10001","10001","10101","10010","01101"], 'R': ["11110","10001","10001","11110","10100","10010","10001"],
 'S': ["01111","10000","10000","01110","00001","00001","11110"], 'T': ["11111","00100","00100","00100","00100","00100","00100"],
 'U': ["10001","10001","10001","10001","10001","10001","01110"], 'V': ["10001","10001","10001","10001","10001","01010","00100"],
 'W': ["10001","10001","10001","10101","10101","10101","01010"], 'X': ["10001","10001","01010","00100","01010","10001","10001"],
 'Y': ["10001","10001","01010","00100","00100","00100","00100"], 'Z': ["11111","00001","00010","00100","01000","10000","11111"],
 '0': ["01110","10001","10011","10101","11001","10001","01110"], '1': ["00100","01100","00100","00100","00100","00100","01110"],
 '2': ["01110","10001","00001","00010","00100","01000","11111"], '3': ["11110","00001","00001","01110","00001","00001","11110"],
 '4': ["00010","00110","01010","10010","11111","00010","00010"], '5': ["11111","10000","11110","00001","00001","10001","01110"],
 '6': ["00110","01000","10000","11110","10001","10001","01110"], '7': ["11111","00001","00010","00100","01000","01000","01000"],
 '8': ["01110","10001","10001","01110","10001","10001","01110"], '9': ["01110","10001","10001","01111","00001","00010","01100"],
 ' ': ["00000"] * 7, '?': ["01110","10001","00001","00010","00100","00000","00100"],
 '!': ["00100","00100","00100","00100","00100","00000","00100"], ',': ["00000","00000","00000","00000","00110","00100","01000"],
 '.': ["00000","00000","00000","00000","00000","01100","01100"], '-': ["00000","00000","00000","11111","00000","00000","00000"],
 ':': ["00000","01100","01100","00000","01100","01100","00000"], '=': ["00000","00000","11111","00000","11111","00000","00000"],
}
NOTE = ["00110", "00101", "00100", "00100", "01100", "11100", "11000"]

def text_mask(text, sc):
    lines = text.split('\n')
    tw = max(len(l) for l in lines) * 6 * sc - sc
    th = len(lines) * 9 * sc - 2 * sc
    m = np.zeros((th, tw), bool)
    for li, ln in enumerate(lines):
        off = (tw - (len(ln) * 6 * sc - sc)) // 2
        for ci, ch in enumerate(ln):
            g = np.kron(np.array([[c == '1' for c in r] for r in FONT[ch]]), np.ones((sc, sc), bool))
            y0, x0 = li * 9 * sc, off + ci * 6 * sc
            m[y0:y0 + 7 * sc, x0:x0 + 5 * sc] |= g
    return m
def text_sprite(text, sc=1, pad=2):
    tm = text_mask(text, sc); th, tw = tm.shape
    out = np.zeros((th + 2 * pad, tw + 2 * pad, 4), np.float32); out[..., 3] = 1
    bh, bw = out.shape[:2]
    for cy, cx in ((0, 0), (0, bw - 1), (bh - 1, 0), (bh - 1, bw - 1)): out[cy, cx, 3] = 0
    out[pad:pad + th, pad:pad + tw][tm] = [1, 1, 1, 1]
    return out

FONT["'"] = ["00100", "00100", "01000", "00000", "00000", "00000", "00000"]

# ================================================================ helpers
INK = hexc('#06070e')
def dilate(m):
    p = np.pad(m, 1)
    return m | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
def smooth(s): s = min(1.0, max(0.0, s)); return s * s * (3 - 2 * s)
def up(F): return np.repeat(np.repeat(F, S, 0), S, 1)
def put(F, x, y, col, a=1.0, sz=None):
    """one pixel (sz screen px, default a chunky 6); on the full-res frame it lands at a sub-pixel position"""
    if F.shape[0] == H * S:
        sz = sz or S
        X, Y = int(round(x * S)), int(round(y * S))
        x0, y0, x1, y1 = max(0, X), max(0, Y), min(W * S, X + sz), min(H * S, Y + sz)
        if x1 > x0 and y1 > y0: F[y0:y1, x0:x1] = F[y0:y1, x0:x1] * (1 - a) + col * a
        return
    x, y = int(round(x)), int(round(y))
    if 0 <= x < F.shape[1] and 0 <= y < F.shape[0]: F[y, x] = F[y, x] * (1 - a) + col * a
def last_age(hits, t):
    i = int(np.searchsorted(hits, t, side='right') - 1)
    return t - hits[i] if i >= 0 else 99.0
FINE = 2                                      # characters are drawn with 2x finer pixels (3 screen px)
def blit_hr(OUT, L, M, x0f, y0f, fine=1):
    k = S // fine
    Lh = np.repeat(np.repeat(L, k, 0), k, 1); Mh = np.repeat(np.repeat(M, k, 0), k, 1)
    X0, Y0 = int(round(x0f * S)), int(round(y0f * S)); h, w_ = Mh.shape
    xa, ya, xb, yb = max(0, X0), max(0, Y0), min(W * S, X0 + w_), min(H * S, Y0 + h)
    if xb <= xa or yb <= ya: return
    m = Mh[ya - Y0:yb - Y0, xa - X0:xb - X0]
    OUT[ya:yb, xa:xb][m] = Lh[ya - Y0:yb - Y0, xa - X0:xb - X0][m]

# ================================================================ the world (2 screens wide), the approved background recipe
WW = 360
GY = 266                                    # where the penguins stand
WYY, WXX = np.mgrid[0:H, 0:WW]
WBAY = BAYER[WYY % 4, WXX % 4]
def bands(shades, y0, y1, seed):
    r = np.random.default_rng(seed); span = y1 - y0; v = np.zeros((H, WW))
    for k in range(3):
        cy = y0 + span * (k + 1) / 4
        cv = cy + span * 0.05 * np.sin(WXX / r.uniform(30, 40) + r.uniform(0, 6)) + span * 0.02 * np.sin(WXX / r.uniform(15, 21) + r.uniform(0, 6))
        v = v + np.clip((WYY - cv) / (span * 0.07) + 0.5, 0, 1)
    return shades[np.clip(np.floor(v + WBAY), 0, len(shades) - 1).astype(int)]
def build_world():
    P = bands(pal('#cdeefd', '#b4e2fa', '#9dd5f5', '#86c7ee'), 0, 178, 3).astype(np.float32)
    # far icebergs
    for cx, w_, h_ in ((40, 46, 22), (128, 30, 14), (205, 58, 28), (300, 40, 18), (352, 30, 12)):
        top = 176 - h_ * np.clip(1 - np.abs((WXX - cx) / (w_ / 2)) ** 1.6, 0, 1)
        m = (WYY >= top) & (WYY < 178) & (np.abs(WXX - cx) < w_ / 2)
        P[dilate(m) & ~m & (WYY < 178)] = hexc('#3a6a96')
        P[m] = hexc('#f4fbff'); P[m & (WXX > cx + w_ * 0.08)] = hexc('#cfe6f7')
    # the sea
    sea = (WYY >= 178) & (WYY < 206)
    P[sea] = bands(pal('#3f8fd0', '#357fc0', '#2c6fae', '#24609c'), 178, 206, 8)[sea]
    # snowy shore with a curved edge, light at the top -> darker at the bottom
    shore = WYY >= 206 + 2 * np.sin(WXX / 19) + 1.2 * np.sin(WXX / 7 + 1)
    P[shore] = bands(pal('#ffffff', '#eef6fd', '#dcebf8', '#c8ddf1'), 206, H, 11)[shore]
    edge = shore & ~np.roll(shore, 1, 0)
    P[edge] = hexc('#a8cbe8')
    # pebble beach patch (static pebbles)
    r = np.random.default_rng(4)
    for _ in range(70):
        x, y = r.uniform(18, 200), r.uniform(GY - 6, GY + 30)
        c = [hexc('#8a8f9a'), hexc('#a6abb6'), hexc('#6e7380')][r.integers(0, 3)]
        x, y = int(x), int(y)
        P[y, x:x + 2] = c; P[y - 1, x] = c * 1.15; P[y + 1, x:x + 2] = INK * 0 + hexc('#5a6070')
    return P
WORLD = build_world()
WORLD_HR = up(WORLD)

# ================================================================ penguin sprite (clean shapes, black outline, rotatable)
SC = 2.2                                     # penguin size (in background pixels)
SPR = 360; OX, OY = 180, 300                 # sprite grid (fine pixels), feet origin inside it
_sy, _sx = np.mgrid[0:SPR, 0:SPR].astype(np.float32)
BODY, BODY_L = hexc('#1d2436'), hexc('#3a4664')
BELLY, BELLY_S = hexc('#f6f8fc'), hexc('#d3dcec')
ORANGE, ORANGE_D = hexc('#ff9a2a'), hexc('#cc6416')
def E(x, y, cx, cy, rx, ry): return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1
def to_local(px, py, tilt, sq):
    c, s = math.cos(tilt), math.sin(tilt)
    return px * c + py * s, (-px * s + py * c)
def penguin(pose):
    """pose: tilt, sq, flipL, flipR (rad, 0 = down), look (-1..1), eyes ('open','happy','wide'), hat, bow, brows, liftL, liftR"""
    tilt, sq = pose.get('tilt', 0), pose.get('sq', 1)
    u, v = (_sx + 0.5 - OX) / (SC * FINE), (_sy + 0.5 - OY) / (SC * FINE)
    c, s = math.cos(tilt), math.sin(tilt)
    x = (u * c + v * s) * sq; y = (-u * s + v * c) / sq
    col = np.zeros((SPR, SPR, 3), np.float32); M = np.zeros((SPR, SPR), bool)
    def paint(m, cc): col[m] = cc; M[m] = True
    for side, lift in ((-1, pose.get('liftL', 0)), (1, pose.get('liftR', 0))):       # feet
        f = E(x, y, side * 5, -1.6 - lift, 4.6, 2.3)
        paint(f, ORANGE); col[f & (y > -1.2 - lift)] = ORANGE_D
    body = E(x, y, 0, -18, 13, 18) | E(x, y, 0, -35, 11, 10.5)
    paint(body, BODY)
    lit = body & ~(E(x, y, 1.8, -18, 13, 18) | E(x, y, 1.8, -35, 11, 10.5))
    col[lit] = BODY_L
    belly = E(x, y, 0, -15, 9.5, 13) & body
    paint(belly, BELLY); col[belly & ~E(x, y, -1.6, -15, 9.5, 13)] = BELLY_S
    tips = {}
    for side, ang in ((-1, pose.get('flipL', 0)), (1, pose.get('flipR', 0))):        # flippers
        sx_, sy_ = side * 11.0, -27.0
        a = -side * ang                                    # positive = raise outward, away from the body
        ca, sa = math.cos(a), math.sin(a)
        fx = (x - sx_) * ca + (y - sy_) * sa; fy = -(x - sx_) * sa + (y - sy_) * ca
        fl = E(fx, fy, side * 1.0, 9.5, 3.6, 10.5)
        F_in = fl & body
        col[dilate(fl) & ~fl & body & ~belly] = INK
        col[dilate(fl) & ~fl & belly] = INK
        paint(fl, BODY); col[fl & (fx * side < -1.4)] = BODY_L
        tx, ty = sx_ + (-math.sin(a)) * 19 * 1.0 + side * 1.0 * math.cos(a), sy_ + math.cos(a) * 19
        # local penguin frame -> sprite pixels
        ux, uy = tx / sq, ty * sq
        tips[side] = ((ux * c - uy * s) * SC * FINE, (ux * s + uy * c) * SC * FINE)
    for side in (-1, 1):                                                             # gentoo white eye patches
        paint(E(x, y, side * 6.2, -41.5, 3.4, 1.9), BELLY)
    look = pose.get('look', 0); eyes = pose.get('eyes', 'open')
    for side in (-1, 1):
        ex, ey = side * 4.6, -35.5
        if eyes == 'happy':
            d = np.hypot(x - ex, (y - ey - 1.0) * 1.2)
            paint((np.abs(d - 2.4) < 0.75) & (y < ey + 0.6) & body, INK)
        else:
            rw = 3.9 if eyes == 'wide' else 3.3
            paint(E(x, y, ex, ey, rw, rw * 1.1), BELLY)
            pr = 1.3 if eyes == 'wide' else 2.0
            paint(E(x, y, ex + look * 1.2, ey + 0.4, pr, pr * 1.12), INK)
            paint(E(x, y, ex + look * 1.2 - 0.9, ey - 0.8, 0.7, 0.7), hexc('#ffffff'))
        paint(E(x, y, side * 8.3, -30.6, 1.7, 1.0), hexc('#ff9fb4'))                 # rosy cheeks
        if pose.get('brows'):
            paint((np.abs((y + 40.2) - side * (x - ex) * 0.35) < 0.7) & (np.abs(x - ex) < 3.2), INK)
    paint(E(x, y, 0, -30.4, 3.4, 2.2), ORANGE); col[E(x, y, 0, -30.4, 3.4, 2.2) & (y > -29.8)] = ORANGE_D
    if pose.get('hat'):                                                              # santa hat
        flop = pose.get('flop', 0)
        hy0, hy1 = -55.0, -43.5
        frac = np.clip((y - hy0) / (hy1 - hy0), 0, 1)
        cxh = (1 - frac) * (5 + flop) + frac * 0
        hat = (y >= hy0) & (y <= hy1) & (np.abs(x - cxh) <= 1 + frac * 10)
        paint(hat, hexc('#e3313f')); col[hat & (x - cxh > frac * 4)] = hexc('#a81c2a')
        paint(E(x, y, 0, -43.5, 11.8, 2.3), hexc('#ffffff')); col[E(x, y, 0, -43.5, 11.8, 2.3) & (y > -43)] = hexc('#dbe4f0')
        paint(E(x, y, 5 + flop + 0.5, -55.5, 2.5, 2.5), hexc('#ffffff'))
    if pose.get('bow'):                                                              # pink bow
        for side in (-1, 1): paint(E(x, y, side * 3.4, -46.5, 3.0, 2.0), hexc('#ff6fa6'))
        paint(E(x, y, 0, -46.5, 1.4, 1.4), hexc('#d13f7a'))
    ring = dilate(M) & ~M
    col[ring] = INK; M = M | ring
    return col, M, {k: (OX + v_[0], OY + v_[1]) for k, v_ in tips.items()}

def draw_penguin(OUT, wx, wy, pose, cam):
    col, M, tips = penguin(pose)
    sx, sy = wx - cam - OX / FINE, wy - OY / FINE
    blit_hr(OUT, col, M, sx, sy, FINE)
    return {k: (sx + v_[0] / FINE, sy + v_[1] / FINE) for k, v_ in tips.items()}   # flipper tips in screen coords

# ================================================================ pebbles, hearts, sparkles
PEB = {'dull1': (hexc('#8a8f9a'), hexc('#5d6270')), 'dull2': (hexc('#9c8f86'), hexc('#6c6058')),
       'shiny': (hexc('#c9d6e4'), hexc('#7e8ea4')), 'best': (hexc('#e9f3ff'), hexc('#8aa6c8')),
       'nest': (hexc('#a3a8b4'), hexc('#6e7380'))}
PB = 3
def draw_pebble(OUT, x, y, kind, t, shine=0.0):
    light, dark = PEB[kind]
    def pp(px, py, c, a=1.0):
        for i in range(PB):
            for j in range(PB): put(OUT, x + (px * PB + i) / FINE, y + (py * PB + j) / FINE, c, a, S // FINE)
    pts = [(-1, -1), (0, -1), (1, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-1, 1), (0, 1), (1, 1)]
    ring = [(-2, -1), (-1, -2), (0, -2), (1, -2), (2, -1), (3, 0), (2, 1), (1, 2), (0, 2), (-1, 2), (-2, 1), (-3, 0)]
    for dx, dy in ring: pp(dx, dy, INK)
    for dx, dy in pts: pp(dx, dy, dark if dy > 0 or dx > 1 else light)
    pp(-1, -1, np.minimum(1, light * 1.25 + 0.1))
    if shine > 0:
        k = 0.6 + 0.4 * math.sin(t * 9)
        L = int(3 + 5 * shine * k)
        for j in range(1, L + 1):
            a = shine * (1 - j / (L + 1))
            for dx, dy in ((j, 0), (-j, 0), (0, j), (0, -j)): put(OUT, x - 1.5 + dx * 0.5, y - 5 + dy * 0.5, hexc('#ffffff'), a, S // FINE)
HEART = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
def draw_heart(OUT, x, y, a, scale=1.0):
    for j, row in enumerate(HEART):
        for i, ch in enumerate(row):
            if ch == '1':
                for q in range(2):
                    for r_ in range(2): put(OUT, x + (i - 3) * scale + q * scale / 2, y + (j - 3) * scale + r_ * scale / 2, hexc('#ff4f7a') if j > 0 or i not in (1, 4) else hexc('#ff9ab4'), a, S // FINE)
def draw_bubble(OUT, x, y, t, a, popk):
    r = 20 * (1 + 0.6 * popk)
    for q in range(90):
        th = TAU * q / 90
        put(OUT, x + r * math.cos(th), y + r * 0.82 * math.sin(th), INK, a)
    if popk == 0:
        for yy in range(-16, 17):
            for xx in range(-19, 20):
                if (xx / 19.5) ** 2 + (yy / 16.2) ** 2 < 1: put(OUT, x + xx, y + yy, hexc('#ffffff'), a)
        for k, (dx, dy, rr) in enumerate(((-17, 19, 3.2), (-23, 27, 2.0))):
            for q in range(20):
                th = TAU * q / 20; put(OUT, x + dx + rr * math.cos(th), y + dy + rr * math.sin(th), INK, a)
        draw_pebble(OUT, x, y + 2, 'best', t, 0.6)
        for side in (-1, 1):                                                    # red bow on the dream pebble
            for dx, dy in ((side * 1, -6), (side * 2, -7), (side * 3, -8), (side * 4, -7), (side * 3, -6), (side * 2, -5)): put(OUT, x - 1 + dx, y + dy, hexc('#e3313f'), a)
        put(OUT, x - 1, y - 6, hexc('#a81c2a'), a)
    else:
        for q in range(12):
            th = TAU * q / 12; d = r * (1 + popk)
            put(OUT, x + d * math.cos(th), y + d * math.sin(th) * 0.8, hexc('#ffffff'), 1 - popk)

# ================================================================ choreography
def walk_state(t):
    """hero x, walking phase (None if standing)"""
    x = WALKS[0][2]
    for t0, t1, x0, x1 in WALKS:
        if t >= t1: x = x1
        elif t >= t0:
            s = (t - t0) / (t1 - t0)
            e = s * s * (3 - 2 * s) * 0.3 + s * 0.7
            return x0 + (x1 - x0) * e, (t - t0) / 0.2
    return x, None

def beat_bob(t):
    a = last_age(KICKS + STABS, t)
    return 1 - 0.05 * math.exp(-a / 0.08)

def hero(t):
    x, ph = walk_state(t)
    pose = dict(hat=True, look=0, eyes='open', flop=1.2 * math.sin(t * 6))
    if ph is not None:
        pose['tilt'] = 0.14 * math.sin(math.pi * ph)
        pose['liftL'] = 2 * max(0, math.sin(math.pi * ph)); pose['liftR'] = 2 * max(0, -math.sin(math.pi * ph))
        pose['flipL'] = 0.35 + 0.15 * math.sin(math.pi * ph); pose['flipR'] = 0.35 - 0.15 * math.sin(math.pi * ph)
        pose['look'] = 1 if t < 15.6 else 1
    else:
        pose['sq'] = beat_bob(t)
    holding = None
    for k, tp in PICKS.items():
        end = {'dull1': TOSSES['dull1'], 'dull2': TOSSES['dull2'], 'shiny': SNATCH, 'best': GIVE}[k]
        if tp - 0.3 <= t < tp:                                      # bend down to pick it up
            pose['sq'] = 1 - 0.14 * math.sin(math.pi * (t - (tp - 0.3)) / 0.3); pose['flipR'] = 0.6
        if tp <= t < end: holding = k
    if holding in ('dull1', 'dull2'):
        pose['flipR'] = 1.55; pose['look'] = 1                      # holds it out to inspect it
    if holding == 'shiny':
        pose['flipR'] = 1.85; pose['eyes'] = 'happy' if t > 7.4 else 'open'
        a = t - 7.2
        if a > 0.5: pose['sq'] = 1 - 0.06 * math.exp(-last_age(KICKS, t) / 0.08)
    for k, tt in TOSSES.items():                                    # toss it behind
        a = t - tt
        if 0 <= a < 0.25: pose['flipR'] = 1.55 + 0.9 * math.sin(math.pi * a / 0.25)
    if SNATCH <= t < 12.0:                                          # what?! hey!!
        a = t - SNATCH
        pose['eyes'] = 'wide'; pose['flipL'] = 2.0 + 0.3 * math.sin(a * 30); pose['flipR'] = 2.0 + 0.3 * math.sin(a * 30 + 1)
        pose['look'] = -1; pose['tilt'] = -0.08 * math.sin(a * 22) * math.exp(-a * 2)
        pose['sq'] = 1 + 0.08 * math.exp(-a / 0.1)
    if 11.6 <= t < 12.2:                                            # sigh...
        pose['eyes'] = 'open'; pose['flipL'] = pose['flipR'] = 0.05; pose['sq'] = 0.95; pose['look'] = 1
    if holding == 'best':
        pose['flipR'] = 1.85 if t < 15.6 else 1.35; pose['eyes'] = 'open'; pose['look'] = 1
        if t >= 15.6:                                               # offers it with a little bow
            a = t - 15.6
            pose['tilt'] = 0.16 * smooth(a / 0.4); pose['sq'] = 0.96
    if t >= GIVE:
        pose['eyes'] = 'happy'; pose['look'] = 1
        a = t - GIVE
        pose['flipL'] = pose['flipR'] = 0.4 + 0.5 * max(0, math.sin(a * 10)) * math.exp(-a / 1.5)
        pose['sq'] = beat_bob(t)
    return x, pose, holding

PARTNER_X = 298
EASE_TAPS = [(0.0, 0.30), (0.03, 0.25), (0.06, 0.2), (0.09, 0.15), (0.13, 0.1)]
def eased(fn, t):
    """call fn(t) at a few recent moments and blend the numeric pose values: no more instant snaps"""
    outs = [fn(max(0.0, t - d)) for d, _ in EASE_TAPS]
    base = outs[0]; pose = dict(base[-2] if len(base) == 3 else base[0])
    keys = set().union(*[o[-2].keys() if len(o) == 3 else o[0].keys() for o in outs])
    for k in keys:
        vals = [(o[-2] if len(o) == 3 else o[0]).get(k) for o in outs]
        if all(isinstance(v_, (int, float)) and not isinstance(v_, bool) for v_ in vals if v_ is not None):
            num = [(v_ if v_ is not None else {'sq': 1.0}.get(k, 0.0)) for v_ in vals]
            pose[k] = sum(v_ * wgt for v_, (_, wgt) in zip(num, EASE_TAPS))
    return base[:-2] + (pose, base[-1]) if len(base) == 3 else (pose, base[1])
def partner(t):
    pose = dict(bow=True, look=-1 if t > 14.0 else 0, eyes='open', sq=beat_bob(t))
    holding = None
    if 15.6 <= t < GIVE: pose['eyes'] = 'open'; pose['look'] = -1
    if GIVE <= t < PLACE:
        holding = 'best'; pose['flipL'] = 1.1; pose['eyes'] = 'happy'
    if t >= GIVE + 0.1 and t < PLACE: pose['eyes'] = 'happy'
    if t >= PLACE:
        pose['eyes'] = 'happy'
        a = last_age(KICKS, t); pose['flipL'] = pose['flipR'] = 0.3 + 0.4 * math.exp(-a / 0.15)
    return pose, holding

def thief_state(t):
    t0, t1 = THIEF
    if not (t0 <= t < t1): return None
    xs = 126 + 62                                         # where his head meets the hero's raised pebble
    if t < SNATCH: return 330 + (xs - 330) * (t - t0) / (SNATCH - t0)
    return xs + (-110 - xs) * (t - SNATCH) / (t1 - SNATCH)

def cam_x(t):
    hx, _ = walk_state(t)
    if t < 15.0: target = hx - 72
    else:
        k = smooth((t - 15.0) / 1.2); target = (1 - k) * (hx - 72) + k * ((hx + PARTNER_X) / 2 - 90)
    return min(max(target, 0), WW - W)

NEST_CENTER = (262, GY + 2)
NEST_POS = []
for i in range(len(NEST)):
    th = math.pi + TAU * i / len(NEST) * 0.999
    NEST_POS.append((NEST_CENTER[0] + 64 * math.cos(th), NEST_CENTER[1] + 9 + 10 * math.sin(th)))

# ================================================================ ambient
rng = np.random.default_rng(31)
SNOW = [(rng.uniform(0, W), rng.uniform(0, 1), int(rng.integers(2, 5)), rng.uniform(0, 6.28)) for _ in range(36)]
GLINT = [(rng.uniform(0, WW), rng.uniform(181, 204), int(rng.integers(3, 11)), rng.uniform(0, 6.28)) for _ in range(30)]
def w(k): return TAU * k / LOOP

def render(t):
    cam = cam_x(t)
    X = int(round(cam * S))
    OUT = WORLD_HR[:, X:X + W * S].copy()
    for gx, gy, k, ph in GLINT:                               # the sea twinkles
        b = 0.5 + 0.5 * math.sin(w(k) * t + ph)
        if b > 0.75: put(OUT, gx - cam, gy, hexc('#e8f6ff'), (b - 0.75) * 3.5)
    # pebbles waiting on the beach
    for k, tp in PICKS.items():
        if t < tp:
            px = {'dull1': 99, 'dull2': 124, 'shiny': 149, 'best': 173}[k]
            sh = 0.0
            if k == 'shiny' and t > 6.0: sh = 0.6
            if k == 'best' and t > 11.9: sh = 1.0
            draw_pebble(OUT, px - cam, GY + 1, k, t, sh)
    # nest pebbles drop in on every note
    for i, (nt, n, d) in enumerate(NEST):
        a = t - nt
        if a >= 0:
            x, y = NEST_POS[i]
            yy = y - 30 * (1 - min(1, a / 0.18)) ** 2 - (3 * math.sin(math.pi * (a - 0.18) / 0.14) if 0.18 < a < 0.32 else 0)
            draw_pebble(OUT, x - cam, yy, 'best' if i == 0 else 'nest', t, 0.6 * math.exp(-a / 0.3) if a < 1 else 0)
    # characters
    ppose, pheld = eased(partner, t)
    ptips = draw_penguin(OUT, PARTNER_X, GY, ppose, cam)
    hx, hpose, hheld = eased(hero, t)
    htips = draw_penguin(OUT, hx, GY, hpose, cam)
    if hheld:
        tx, ty = htips[1]; draw_pebble(OUT, tx, ty - 1, hheld, t, 1.0 if hheld in ('shiny', 'best') else 0)
    if pheld:
        tx, ty = ptips[-1]; draw_pebble(OUT, tx, ty - 1, pheld, t, 1.0)
    for k, tt in TOSSES.items():                               # tossed pebbles fly off behind him
        a = t - tt
        if 0 <= a < 0.6:
            x0 = {'dull1': 99, 'dull2': 124}[k] + 8
            draw_pebble(OUT, x0 - 60 * a / 0.6 - cam, GY - 66 + 180 * (a - 0.25) ** 2 - 10, k, t)
    tx_ = thief_state(t)
    if tx_ is not None:
        a = t - SNATCH
        tp = dict(tilt=-1.45, sq=1.0, brows=True, eyes='open', look=-1, flipL=2.6, flipR=2.6)
        tips = draw_penguin(OUT, tx_ + 56, GY - 19, tp, cam)
        for k in range(1, 8):                                  # snow spray behind the slide
            put(OUT, tx_ + 70 + k * 5 - cam, GY - 1 - (k % 3), hexc('#ffffff'), 0.8 - k * 0.1)
        if t >= SNATCH: draw_pebble(OUT, tx_ - 40 - cam, GY - 14, 'shiny', t, 0.8)
    if 0 <= t - SNATCH < 0.3:                                  # snatch puff
        a = t - SNATCH
        for q in range(10):
            th = TAU * q / 10; d = 4 + 14 * a / 0.3
            put(OUT, hx + 28 + d * math.cos(th) - cam, GY - 80 + d * math.sin(th), hexc('#ffffff'), 1 - a / 0.3)
    # thought bubble (the hook), hearts
    if False:
        popk = 0
        draw_bubble(OUT, hx + 34 - cam, GY - 122 + 1.5 * math.sin(t * 5), t, 1.0, popk)
    for i, ht in enumerate([GIVE + 0.15, GIVE + 0.5, GIVE + 0.9, 20.0, 22.4, 24.8]):
        a = t - ht
        if 0 <= a < 1.4:
            midx = (hx + PARTNER_X) / 2 - cam + (i % 3 - 1) * 8
            sc = 1.0 + 0.25 * math.exp(-a / 0.12) * math.cos(a * 25)
            draw_heart(OUT, midx, GY - 135 - 26 * a, max(0.0, 1 - (a / 1.4) ** 2), sc * 2.0)
    for x0, ph0, n, ph in SNOW:                                # gentle snowfall that settles
        cyc = LOOP / n; tau = ((t / cyc + ph0) % 1.0) * cyc; fall = (GY + 30) / 26.0
        if tau < fall: put(OUT, x0 + 3 * math.sin(tau * 1.6 + ph), -6 + 26 * tau, np.array([1.0, 1.0, 1.0]), 0.95)
        elif tau < fall + 1.2: put(OUT, x0 + 3 * math.sin(fall * 1.6 + ph), GY + 24, np.array([1, 1, 1]), 0.9 * (1 - (tau - fall) / 1.2))
    return OUT

# ================================================================ captions (plain, casual, near the top)
HEADPHONES = ["0011111100", "0100000010", "1000000001", "1000000001", "1110000111", "1110000111", "1110000111", "0110000110"]
def caption_sprite(text, icon=False, sc=1, pad=3):
    out = text_sprite(text, sc, pad)
    if icon:
        g = np.kron(np.array([[c_ == '1' for c_ in r] for r in HEADPHONES]), np.ones((sc, sc), bool))
        ih, iw = g.shape[0] + 4, g.shape[1] + 4; bh, bw = out.shape[:2]
        full = np.zeros((bh + 2 + ih, bw, 4), np.float32); full[:bh] = out
        x0 = (bw - iw) // 2; y0 = bh + 2
        full[y0:y0 + ih, x0:x0 + iw] = [0, 0, 0, 1]
        for cy, cx in ((y0, x0), (y0, x0 + iw - 1), (y0 + ih - 1, x0), (y0 + ih - 1, x0 + iw - 1)): full[cy, cx, 3] = 0
        full[y0 + 2:y0 + 2 + g.shape[0], x0 + 2:x0 + 2 + g.shape[1]][g] = [1, 1, 1, 1]
        out = full
    return out

class Caption:
    def __init__(self, text, t_in, t_out, seed, icon=False, y=34):
        self.s = caption_sprite(text, icon, sc=2, pad=5); h, w_ = self.s.shape[:2]
        self.x, self.y, self.t_in, self.t_out = (W - w_) // 2, y, t_in, t_out
        r = np.random.default_rng(seed); self.yy, self.xx = np.mgrid[0:h, 0:w_]
        self.vis = self.s[..., 3] > 0
        self.t_app = 0.07 * r.random((h, w_))
        self.t_dis = 0.06 + 0.5 * (0.55 * r.random((h, w_)) + 0.45 * (self.xx / w_))
        self.dx = (r.random((h, w_)) - 0.25) * 12; self.dy = -(5 + r.random((h, w_)) * 10)
    def draw(self, F, t):
        for tt in (t, t + VLOOP, t - VLOOP):
            if self.t_in <= tt <= self.t_out + 1.2: self._draw(F, tt)
    def _draw(self, F, t):
        a_in, a_out = t - self.t_in, t - self.t_out
        solid = self.vis & (a_in >= self.t_app)
        if a_out > 0:
            age = a_out - self.t_dis
            solid &= age < 0
            solid &= ~(self.vis & (age >= -0.14) & (BAYER[self.yy % 4, self.xx % 4] < (age + 0.14) / 0.14))
            mist = self.vis & (age >= 0) & (age < 0.6)
            if mist.any():
                ag = age[mist]; k = ag / 0.6
                pxs = self.x + self.xx[mist] + self.dx[mist] * k + 1.5 * np.sin(ag * 8 + self.yy[mist] * 0.7)
                pys = self.y + self.yy[mist] + self.dy[mist] * k
                col = self.s[..., :3][mist] * 0.35 + np.array([0.8, 0.85, 1.0]) * 0.65
                al = (1 - k) ** 1.6 * 0.6
                ok = (pxs >= 0) & (pxs < W - 0.5) & (pys >= 0) & (pys < H - 0.5)
                xi, yi = np.round(pxs[ok]).astype(int), np.round(pys[ok]).astype(int)
                F[yi, xi] = F[yi, xi] * (1 - al[ok, None]) + col[ok] * al[ok, None]
        ys, xs = np.nonzero(solid); X, Y = self.x + xs, self.y + ys
        ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
        F[Y[ok], X[ok]] = self.s[ys[ok], xs[ok], :3]

CAPTIONS = []
def cap(text, a, b, icon=False): CAPTIONS.append(Caption(text, a, b, 40 + len(CAPTIONS), icon))
# times are VIDEO time (cold open 0-1.2 s, rewind 1.2-1.8 s, story after that at story time + 0.2)
cap("HE GOT\nROBBED!!", 0.0, 1.15, icon=True)
cap("OK WAIT.\nLET ME EXPLAIN", 1.25, 2.9)
cap("HE WANTS THE\nPERFECT PEBBLE", 3.0, 4.4)
cap("NOPE.", 4.5, 5.4)
cap("NOPE.", 6.25, 7.1)
cap("THIS ONE.\nPERFECT.", 7.6, 9.5)
cap("WAIT-- HEY!!", 10.65, 12.0)
cap("FINE. AN EVEN\nBETTER ONE", 12.3, 13.9)
cap("NOW THE\nIMPORTANT PART", 14.2, 15.9)
cap("SHE SAID\nYES!!", 17.15, 18.4)
cap("PLOT TWIST:\nPENGUINS\nREALLY DO THIS", 18.6, 20.9)
cap("THEY GIVE\nPEBBLES TO THE\nONE THEY LIKE", 21.2, 23.6)
cap("AND BUILD A\nNEST TOGETHER", 23.9, 26.1)

HR_BAYER = up(BAYER[YY % 4, XX % 4][..., None])[..., 0]
COLD = (SNATCH - 0.35, 1.2)          # story time where the cold open starts, and its length
REW = 0.6                               # rewind length
STORY0 = bar(1)                         # the story resumes on a downbeat (1.6 s)
VLOOP = COLD[1] + REW + (LOOP - STORY0) # 26.6 s
def story_time(v):
    if v < COLD[1]: return COLD[0] + v
    if v < COLD[1] + REW:
        s_ = (v - COLD[1]) / REW
        return COLD[0] + COLD[1] + (STORY0 - (COLD[0] + COLD[1])) * smooth(s_)
    return STORY0 + (v - COLD[1] - REW)
REWIND_ICON = ["1000100", "1100110", "1110111", "1111111", "1110111", "1100110", "1000100"]
def frame(v):
    OUT = render(story_time(v))
    if COLD[1] <= v < COLD[1] + REW:                          # rewind: icon + light scanlines
        for j, row in enumerate(REWIND_ICON):
            for i, ch in enumerate(row[::-1]):
                if ch == '1':
                    for q in range(2):
                        for r_ in range(2): put(OUT, 150 + i * 2 + q, 92 + j * 2 + r_, hexc('#ffffff'))
        sl = (np.arange(H * S) // 3) % 4 == 0
        OUT[sl] = OUT[sl] * 0.85
    if v > VLOOP - 0.4:                                       # soft pixel fade back to the cold open
        G = render(story_time(0.0)); m = HR_BAYER < smooth((v - (VLOOP - 0.4)) / 0.4); OUT[m] = G[m]
    scr = OUT[::S, ::S].copy(); before = scr.copy()
    for c_ in CAPTIONS: c_.draw(scr, v)
    ch = np.any(np.abs(scr - before) > 1e-6, axis=2)
    if ch.any():
        big = up(ch[..., None])[..., 0]; OUT[big] = up(scr)[big]
    return (np.clip(OUT, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == '__main__':
    if sys.argv[1] == '--stills':
        from PIL import Image
        for ts in sys.argv[3:]: Image.fromarray(frame(float(ts))).save(f'{sys.argv[2]}/still_{float(ts):06.2f}.png')
        sys.exit()
    out, wav = sys.argv[1], sys.argv[2]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W*S}x{H*S}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(int(round(VLOOP * FPS))):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 300 == 0: print('frame', f, flush=True)
    p.stdin.close(); p.wait(); print('done', out)
