"""'What If Penguins Gave Christmas Gifts?' in the reference blueprint pixel-art style (1080x1920, 60 fps, 86.4 s).

Copied from the reference shorts: smooth navy blueprint grid background, SMALL CHUNKY pixel subjects
(6-px pixels) with a navy outline and checker-dithered shading, self-contained floating ice dioramas
with soft shadows, unboxed bold one-line captions with yellow key words, pixel labels with leader
lines, black boxed tags, pixel arrows, dotted motion trails and a pixel counter.

World: [thief's island] -snow bridge- [Pip's island + iceberg] -ICE bridge- [Penny's island].
Timing and music come from score2.py / audio2.py (same story beats).

usage: python3 video3.py out.mp4 audio.wav  |  python3 video3.py --stills DIR t1 t2 ...  (video seconds)
"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'style_study'))
os.chdir(HERE)
import video as pv                         # the penguin character model (drawn here on the chunky grid)
import blueprint_kit as bk
from score2 import (LOOP, FPS, KICKS, STABS, NEST, WALKS as _W, PICKS, TOSSES, PLACE_SHINY, PEEK, THIEF_FALL, SNATCH,
                    THIEF_GONE, SAD, SIGH, DETERMINED, SLIP, FALL, GETUP, OFFER, PONDER, GIVE, NEST_T, THIEF_SCENE,
                    THIEF_GIVE, FLURRY, EGG_IN, CRACKS, HATCH)

W, H, S = 180, 320, 6
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc = pv.hexc
NAVY = bk.OUTLINE
pv.INK = NAVY
pv.BODY, pv.BODY_L = hexc('#1c2440'), hexc('#36446c')
smooth, put, up = pv.smooth, pv.put, pv.up
BAY = pv.BAYER
def last_age(hits, t): return pv.last_age(hits, t)

# ---------------- world layout (grid units: 1 unit = 6 screen px) ----------------
WW = 560
GY = 166                                   # feet line on the island tops
TOP, BOT, DEPTH = 146, 186, 8              # island top surface rows and front-edge depth
ISLANDS = [(12, 118), (152, 310), (372, 522)]          # thief's, Pip's, Penny's
BRIDGES = [(114, 156, 'snow'), (306, 376, 'ice')]
PIP0 = 190
WALKS = [(17.0, 18.0, 190, 201), (20.4, 21.4, 201, 215), (23.8, 24.8, 215, 229), (39.0, 41.0, 229, 298), (48.6, 53.6, 337, 430)]
SLIDE = (43.3, 46.3, 298, 337)
PEBBLE_X = {'dull1': 214, 'dull2': 228, 'shiny': 242, 'best': 381}
SHINY_GROUND_X = 251
ICEBERG_X = 283
THIEF_PEEK_X = 296
PENNY_X, NEST_CX = 482, 456
THIEF_HOME, CRUSH_X = 44, 86
BW = 0.5                                   # character size vs the earlier videos
CHAR_SCALE = BW / pv.FINE

# ---------------- background: smooth blueprint (screen space) ----------------
def build_bg():
    yy, xx = np.mgrid[0:HF, 0:WF].astype(np.float32)
    top, mid, low = hexc('#0f2a55'), hexc('#1f4782'), hexc('#162f5c')
    f = yy / HF
    base = np.where((f < 0.45)[..., None], top + (mid - top) * (f / 0.45)[..., None], mid + (low - mid) * ((f - 0.45) / 0.55)[..., None])
    glow = np.exp(-(((xx - 540) / 560) ** 2 + ((yy - 900) / 640) ** 2))
    base = base + glow[..., None] * hexc('#123a70') * 0.55
    vig = np.clip(1 - 0.35 * ((np.abs(xx - WF / 2) / (WF / 2)) ** 2 + (np.abs(yy - HF / 2) / (HF / 2)) ** 2) / 2, 0, 1)
    base = base * vig[..., None]
    rows = (yy.astype(int) % 60) == 0
    base[rows] = base[rows] * 1.12 + 0.012
    return np.clip(base, 0, 1).astype(np.float32)
BG = build_bg()

# ---------------- the floating islands (world layer, chunky, dithered, navy outline) ----------------
SNOW = [hexc('#a9c8ea'), hexc('#cfe2f6'), hexc('#eaf3fd'), hexc('#ffffff')]
SIDE = [hexc('#2c5d96'), hexc('#4a86c5'), hexc('#6fa6dd')]
ICE = [hexc('#7fbbe6'), hexc('#9fd0f2'), hexc('#c2e6fb'), hexc('#e6f7ff')]
def build_world():
    col = np.zeros((H, WW, 3), np.float32); A = np.zeros((H, WW), np.float32)
    yy, xx = np.mgrid[0:H, 0:WW]
    M = np.zeros((H, WW), bool)
    for x0, x1 in ISLANDS:                                     # soft shadow under each island
        cx, w2 = (x0 + x1) / 2, (x1 - x0) / 2 + 8
        d = ((xx - cx) / w2) ** 2 + ((yy - (BOT + DEPTH + 10)) / 9.0) ** 2
        a = np.clip(1.0 - d, 0, 1) * 0.5
        A = np.maximum(A, a); col[a > 0] = hexc('#050a18')
    for x0, x1, kind in BRIDGES:                               # narrow bridges between islands
        top = (xx >= x0) & (xx < x1) & (yy >= GY - 7) & (yy < GY + 7)
        side = (xx >= x0) & (xx < x1) & (yy >= GY + 7) & (yy < GY + 10)
        P = ICE if kind == 'ice' else SNOW
        v = 1.2 + 2.0 * (1 - (yy - (GY - 7)) / 14.0)
        c = np.stack(P)[np.clip(np.floor(v + BAY[yy % 4, xx % 4] - 0.5), 0, 3).astype(int)]
        col[top] = c[top]; col[side] = SIDE[0] if kind == 'ice' else SIDE[1]
        if kind == 'ice':
            st = top & (((xx + 2 * yy) % 11) < 1) & (((xx - yy) % 17) < 8); col[st] = hexc('#ffffff')
        M |= top | side
    for i, (x0, x1) in enumerate(ISLANDS):
        w_, h_ = x1 - x0, BOT - TOP
        c, m = bk.diorama(w_, h_, DEPTH, SNOW, SIDE, seed=3 + i)
        hh, ww = m.shape
        ys, xs = slice(TOP, TOP + hh), slice(x0, x0 + ww)
        col[ys, xs][m] = c[m]; M[ys, xs] |= m
    p = np.pad(M, 1); ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~M
    inner_bridge = np.zeros_like(M)
    col[ring] = NAVY; M |= ring
    A[M] = 1
    r = np.random.default_rng(9)                               # frozen rocks for texture
    for _ in range(30):
        x, y = int(r.uniform(16, WW - 16)), int(r.uniform(TOP + 6, BOT - 4))
        if not M[y, x] or any(a <= x < b for a, b, _ in BRIDGES): continue
        if 200 < x < 260 or 370 < x < 400 or 420 < x < 500: continue
        col[y, x:x + 2] = hexc('#8e95a4'); col[y - 1, x] = hexc('#c3c9d4')
    return col, A
WCOL, WA = build_world()
WCOL_HR, WA_HR = up(WCOL), up(WA[..., None])

def build_iceberg():
    w_, h_ = 24, 66
    yy, xx = np.mgrid[0:h_, 0:w_]
    topline = 8 + 5 * np.abs(np.sin(xx / 3.4 + 0.8)) + 3 * (xx < 5) + 2 * (xx > 19)
    M = (yy >= topline) & (xx >= 1) & (xx <= w_ - 2)
    P = np.stack([hexc('#7fb3df'), hexc('#a7d0f0'), hexc('#cfe7fa'), hexc('#f4fbff')])
    v = 1.2 + 2.0 * (1 - xx / w_) + 0.5 * ((xx + yy // 3) % 7 < 1)
    col = P[np.clip(np.floor(v + BAY[yy % 4, xx % 4] - 0.5), 0, 3).astype(int)].astype(np.float32)
    col[M & (np.abs(xx - (7 + yy * 0.1)) < 0.6)] = hexc('#ffffff')
    col[M & (np.abs(xx - (16 - yy * 0.05)) < 0.6) & (yy > 20)] = hexc('#7fb3df')
    col, M = bk.outline(bk.dither_seams(col, M), M)
    return col, M
ICEBERG = build_iceberg()

# ---------------- chunky sprites: pebbles, hearts, egg, bubble ----------------
PEB = {'dull1': ('#6e7380', '#4b505c', '#8e95a4'), 'dull2': ('#8a7a6c', '#5e5246', '#a8998a'),
       'shiny': ('#cfe0f2', '#8ea4c2', '#ffffff'), 'best': ('#eaf4ff', '#9db8dc', '#ffffff'), 'nest': ('#8e95a4', '#5d6270', '#c3c9d4')}
def pebble_sprite(kind, small=False):
    if small: m = np.array([[0, 1, 1, 0], [1, 1, 1, 1], [0, 1, 1, 0]], bool)
    else: m = np.array([[0, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 0]], bool)
    base, dark, lite = (hexc(c) for c in PEB[kind])
    col = np.zeros(m.shape + (3,), np.float32); col[m] = base
    col[-1][m[-1]] = dark; col[-2, -2:][m[-2, -2:]] = dark; col[0, 1:3] = lite
    return bk.outline(col, m)
PEBS = {(k, s): pebble_sprite(k, s) for k in PEB for s in (False, True)}
def pebble(F, x, y, kind, T, shine=0.0, small=False):
    col, M = PEBS[(kind, small)]; h, w_ = M.shape
    pv.blit_hr(F, col, M, x - w_ / 2, y - h / 2, 1)
    if shine > 0:
        k = 0.5 + 0.5 * math.sin(T * 7)
        for j in range(1, int(1 + 2 * shine * k) + 1):
            for dx, dy in ((j, 0), (-j, 0), (0, j), (0, -j)): put(F, x - 1 + dx, y - h / 2 - 2 + dy, hexc('#ffffff'), shine * (1 - j / 4))
HEART = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
HEART_C = np.zeros((6, 7, 3), np.float32); HEART_M = np.array([[c == '1' for c in r] for r in HEART])
HEART_C[HEART_M] = hexc('#ff4f7a'); HEART_C[1, 1] = HEART_C[1, 2] = hexc('#ffb0c4')
HEART_C, HEART_M = bk.outline(HEART_C, HEART_M)
def heart(F, x, y, a):
    if a < 0.5: return
    pv.blit_hr(F, HEART_C, HEART_M, x - 4, y - 4, 1)
def egg_sprite(ang, part, cracks):
    n = 22; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    u, v = xx + 0.5 - n / 2, yy + 0.5 - (n - 2)
    c, s = math.cos(ang), math.sin(ang); x = u * c + v * s; y = -u * s + v * c
    rx, ry = 6.5, 8.5
    M = (x / rx) ** 2 + ((y + ry) / ry) ** 2 <= 1
    zig = -ry + 1.4 * np.sign(np.sin(x * 1.3))
    if part == 'bottom': M &= y > zig
    if part == 'top': M &= y <= zig
    col = np.zeros((n, n, 3), np.float32); col[M] = hexc('#fff6e6')
    col[M & (x > 1.5 + 0.2 * (y + ry))] = hexc('#e6d6bc')
    col[M & (((x + 3) / 1.2) ** 2 + ((y + 12) / 1.6) ** 2 < 1)] = hexc('#ffffff')
    for k in range(cracks):
        reach = -rx + 2 * rx * (0.55 if k == 0 else 1.0)
        col[M & (np.abs(y - zig) < 0.6) & (x < reach)] = NAVY
    col = bk.dither_seams(col, M)
    return bk.outline(col, M)
def bubble(F, x, y, T, popk):
    rx, ry = 13, 10
    if popk > 0:
        for q in range(12):
            th = TAU * q / 12; d = rx * (1 + popk)
            put(F, x + d * math.cos(th), y + d * 0.8 * math.sin(th), hexc('#ffffff'), 1 - popk)
        return
    yy, xx = np.mgrid[0:2 * ry + 1, 0:2 * rx + 1]
    M = ((xx - rx) / (rx + 0.3)) ** 2 + ((yy - ry) / (ry + 0.3)) ** 2 <= 1
    col = np.zeros(M.shape + (3,), np.float32); col[M] = hexc('#ffffff')
    col[M & (yy > ry + 4)] = hexc('#e2ecfa')
    col, M = bk.outline(col, M)
    pv.blit_hr(F, col, M, x - rx, y - ry, 1)
    for dx, dy, r_ in ((-10, 12, 1.6), (-14, 16, 1.0)):
        cm = np.ones((int(2 * r_) + 1, int(2 * r_) + 1), bool); cc = np.ones(cm.shape + (3,), np.float32)
        cc, cm = bk.outline(cc, cm); pv.blit_hr(F, cc, cm, x + dx, y + dy, 1)
    pebble(F, x, y + 2, 'best', T, 0.6)
    for side in (-1, 1):                                        # red bow
        for dx, dy in ((side * 1, -2), (side * 2, -3), (side * 2, -2)): put(F, x - 0.5 + dx, y + dy, hexc('#e3313f'))
    put(F, x - 0.5, y - 2, hexc('#a81c2a'))

# ---------------- penguins on the chunky grid ----------------
def draw_char(F, wx, wy, pose, cam):
    pose = dict(pose); pose['scale'] = pose.get('scale', 1.0) * CHAR_SCALE
    col, M, tips = pv.penguin(pose)
    ys, xs = np.nonzero(M)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    col, M = bk.dither_seams(col[y0:y1, x0:x1], M[y0:y1, x0:x1]), M[y0:y1, x0:x1]
    sx, sy = wx - cam - (pv.OX - x0), wy - (pv.OY - y0)
    pv.blit_hr(F, col, M, sx, sy, 1)
    return {k: (wx - cam + (v_[0] - pv.OX), wy + (v_[1] - pv.OY)) for k, v_ in tips.items()}

# ---------------- choreography (same beats as before, on the new islands) ----------------
def pip_x(T):
    if SLIDE[0] <= T < SLIDE[1]:
        s = (T - SLIDE[0]) / (SLIDE[1] - SLIDE[0]); return SLIDE[2] + (SLIDE[3] - SLIDE[2]) * (1 - (1 - s) ** 2.2)
    if SLIDE[1] <= T < WALKS[4][0]: return SLIDE[3]
    x = PIP0
    for t0, t1, x0, x1 in WALKS:
        if T >= t1: x = x1
        elif T >= t0:
            s = (T - t0) / (t1 - t0); return x0 + (x1 - x0) * (s * s * (3 - 2 * s) * 0.3 + s * 0.7)
    if WALKS[3][1] <= T < SLIDE[0]: return WALKS[3][3]
    return x
def walking(T):
    for t0, t1, x0, x1 in WALKS:
        if t0 <= T < t1: return (T - t0) / 0.32
    return None
def blinking(T, ph): return ((T + ph) % 3.1) < 0.12
def beat_hop(T, hits, k=3.0): return k * math.exp(-last_age(hits, T) / 0.12)
LIE = 13.5                                                   # lift when lying on the belly (chunky size)

def pip(T):
    x = pip_x(T); ph = walking(T)
    pose = dict(hat=True, look=0, eyes='open', flop=1.2 * math.sin(T * 5), sq=1 + 0.018 * math.sin(T * 2.4))
    if ph is not None:
        pose['dy'] = 1.2 * abs(math.sin(math.pi * ph)); pose['tilt'] = 0.13 * math.sin(math.pi * ph)
        pose['liftL'] = 2 * max(0, math.sin(math.pi * ph)); pose['liftR'] = 2 * max(0, -math.sin(math.pi * ph))
        pose['flipL'] = 0.35 + 0.15 * math.sin(math.pi * ph); pose['flipR'] = 0.35 - 0.15 * math.sin(math.pi * ph); pose['look'] = 1
    holding = None
    if 0.6 <= T < 2.8: pose['flipR'] = 2.0 + 0.35 * math.sin(T * 9); pose['eyes'] = 'happy'
    if 3.6 <= T < 7.5: pose['look'] = 1
    if 7.5 <= T < 12.0: pose['eyes'] = 'happy'; pose['look'] = 1; pose['tilt'] = 0.07 * math.sin(T * 2.2)
    if 12.0 <= T < 17.0: pose['eyes'] = 'happy'; pose['look'] = 0.4
    for k, tp in PICKS.items():
        end = {'dull1': TOSSES['dull1'], 'dull2': TOSSES['dull2'], 'shiny': PLACE_SHINY, 'best': GIVE}[k]
        if tp - 0.4 <= T < tp and k != 'best': pose['sq'] = 1 - 0.14 * math.sin(math.pi * (T - (tp - 0.4)) / 0.4); pose['flipR'] = 0.6
        if tp <= T < end: holding = k
    if holding in ('dull1', 'dull2'):
        a = T - PICKS[holding]; pose['flipR'] = 1.55; pose['look'] = 1; pose['tilt'] = 0.05 * math.sin(a * 3)
        if a > 0.9: pose['brows'] = True
    for k, tt in TOSSES.items():
        a = T - tt
        if -0.3 <= a < 0: pose['flipR'] = 1.55 - 0.7 * math.sin(math.pi * (a + 0.3) / 0.6); pose['tilt'] = 0.08 * (a + 0.3) / 0.3
        if 0 <= a < 0.25: pose['flipR'] = 1.55 + 0.9 * math.sin(math.pi * a / 0.25); pose['tilt'] = -0.1 * math.sin(math.pi * a / 0.25)
    if holding == 'shiny': pose['flipR'] = 1.85; pose['eyes'] = 'happy' if T > PICKS['shiny'] + 0.25 else 'open'
    if PLACE_SHINY - 0.4 <= T < PLACE_SHINY: pose['sq'] = 1 - 0.14 * math.sin(math.pi * (T - PLACE_SHINY + 0.4) / 0.4); pose['flipR'] = 0.7
    if PLACE_SHINY + 0.2 <= T < SNATCH:
        pose['eyes'] = 'happy'; pose['look'] = 0.6; pose['dy'] = beat_hop(T, KICKS + STABS, 2)
        pose['flipL'] = 1.0 + 0.6 * math.sin(T * 10); pose['flipR'] = 1.0 + 0.6 * math.sin(T * 10 + 1.5); pose['tilt'] = 0.12 * math.sin(T * 5)
    if SNATCH <= T < SAD:
        a = T - SNATCH
        pose['eyes'] = 'wide'; pose['look'] = -1; pose['flipL'] = 2.0 + 0.3 * math.sin(a * 30); pose['flipR'] = 2.0 + 0.3 * math.sin(a * 30 + 1)
        pose['sq'] = 1 + 0.08 * math.exp(-a / 0.1)
        if a < 0.45: pose['dy'] = 6 * math.sin(math.pi * a / 0.45)
    if SAD <= T < SIGH: pose['flipL'] = pose['flipR'] = 0.05; pose['sq'] = 0.94; pose['look'] = -0.5
    if SIGH <= T < DETERMINED: pose['flipL'] = pose['flipR'] = 0.05; pose['sq'] = 0.94 - 0.05 * math.sin(math.pi * (T - SIGH) / 0.6); pose['eyes'] = 'blink'
    if DETERMINED <= T < 39.0:
        a = T - DETERMINED; pose['brows'] = True; pose['look'] = 1; pose['flipL'] = pose['flipR'] = 0.8
        if a < 0.4: pose['dy'] = 4 * math.sin(math.pi * a / 0.4)
    if SLIP <= T < FALL:
        a = T - SLIP
        pose['eyes'] = 'wide'; pose['flipL'] = 1.3 + 0.7 * math.sin(a * 20); pose['flipR'] = 1.3 + 0.7 * math.sin(a * 20 + 2)
        pose['tilt'] = 0.16 * math.sin(a * 14); pose['liftL'] = 3 * max(0, math.sin(a * 22)); pose['liftR'] = 3 * max(0, -math.sin(a * 22))
    if FALL <= T < SLIDE[0]:
        k_ = smooth((T - FALL) / (SLIDE[0] - FALL)); pose['tilt'] = 1.45 * k_; pose['dy'] = LIE * k_; pose['eyes'] = 'wide'
        pose['flipL'] = pose['flipR'] = 1.8 * (1 - k_) + 0.25 * k_
    if SLIDE[0] <= T < GETUP:
        a = T - SLIDE[0]
        pose['tilt'] = 1.45; pose['dy'] = LIE + 1.2 * math.exp(-a / 0.08) * math.cos(a * 30)
        pose['flipL'] = pose['flipR'] = 0.25 + 0.12 * math.sin(a * 14); pose['eyes'] = 'happy' if T < SLIDE[1] else 'open'; pose['sq'] = 1.0
    if GETUP <= T < GETUP + 0.7:
        k_ = smooth((T - GETUP) / 0.7); pose['tilt'] = 1.45 * (1 - k_); pose['dy'] = LIE * (1 - k_) + 4 * math.sin(math.pi * k_)
    if GETUP + 0.7 <= T < GETUP + 1.3:
        a = T - GETUP - 0.7; pose['tilt'] = 0.14 * math.sin(a * 40) * math.exp(-a * 5); pose['eyes'] = 'happy'
    if holding == 'best':
        pose['flipR'] = 1.85 if T < OFFER else 1.35; pose['look'] = 1
        if T >= OFFER: pose['tilt'] = 0.16 * smooth((T - OFFER) / 0.5); pose['sq'] = 0.96
    if T >= GIVE:
        a = T - GIVE; pose['eyes'] = 'happy'; pose['look'] = 1
        pose['flipL'] = pose['flipR'] = 0.4 + 0.5 * max(0, math.sin(a * 9)) * math.exp(-a / 1.5)
        if a < 0.5: pose['dy'] = 4 * math.sin(math.pi * a / 0.5)
    if T >= NEST_T: pose['dy'] = pose.get('dy', 0) + beat_hop(T, KICKS, 1.5)
    if CRACKS[0] <= T < HATCH: pose['eyes'] = 'wide'; pose['look'] = 1
    if HATCH <= T < HATCH + 0.6: pose['dy'] = 5 * math.sin(math.pi * (T - HATCH) / 0.6); pose['flipL'] = pose['flipR'] = 2.0
    pose['flop'] = pose['flop'] - 9 * pose.get('tilt', 0) + 0.25 * pose.get('dy', 0)
    if pose['eyes'] == 'open' and blinking(T, 0.0): pose['eyes'] = 'blink'
    return x, pose, holding

def penny(T):
    pose = dict(bow=True, look=0, eyes='open', sq=1 + 0.018 * math.sin(T * 2.2 + 1), tilt=0.04 * math.sin(T * 1.6))
    holding = None
    if 3.6 <= T < 7.4:
        pose['flipL'] = 1.7 + 0.3 * math.sin(T * 9); pose['look'] = -0.3
        if T > 5.4: pose['eyes'] = 'happy'
    if T >= 50.6: pose['look'] = -1 * smooth((T - 50.6) / 0.8)
    if PONDER[0] <= T < PONDER[1]: pose['look'] = -0.4; pose['tilt'] = -0.08 + 0.03 * math.sin(T * 3)
    if GIVE <= T < NEST_T - 0.2: holding = 'best'; pose['flipL'] = 1.1
    if T >= GIVE:
        pose['eyes'] = 'happy'
        if T < GIVE + 0.45: pose['dy'] = 5 * math.sin(math.pi * (T - GIVE) / 0.45)
    if T >= NEST_T: pose['dy'] = pose.get('dy', 0) + beat_hop(T, [k + 0.5 for k in KICKS], 1.5)
    if CRACKS[0] <= T < HATCH: pose['eyes'] = 'wide'; pose['look'] = -1
    if HATCH <= T < HATCH + 0.6: pose['dy'] = 5 * math.sin(math.pi * (T - HATCH) / 0.6); pose['flipL'] = pose['flipR'] = 2.0
    if pose['eyes'] == 'open' and blinking(T, 1.3): pose['eyes'] = 'blink'
    return pose, holding

THIEF_LAND = THIEF_FALL + 0.6
def thief_x(T):
    if T < THIEF_LAND: return THIEF_PEEK_X
    if T < SNATCH: return THIEF_PEEK_X - 3 * (T - THIEF_LAND) / (SNATCH - THIEF_LAND)
    a = T - SNATCH; return THIEF_PEEK_X - 3 - (40 * a + 70 * a * a)
def thief(T):
    """(x, pose, mode): 'peek' (behind the iceberg), 'slide' (in front), 'scene' (on his island)"""
    if T < PEEK[0] or (THIEF_GONE <= T < THIEF_SCENE - 0.5) or T >= FLURRY + 0.6: return None
    if T >= THIEF_SCENE - 0.5:
        pose = dict(look=1, eyes='open', sq=1 + 0.02 * math.sin(T * 2.5), flipR=1.5, tilt=0.05)
        if T >= THIEF_GIVE: pose['eyes'] = 'happy'; pose['flipR'] = 0.4; pose['dy'] = 3 * math.sin(math.pi * min(1, (T - THIEF_GIVE) / 0.45))
        elif blinking(T, 0.6): pose['eyes'] = 'blink'
        return THIEF_HOME, pose, 'scene'
    if T < THIEF_FALL:
        a = T - PEEK[0]
        lean = -(0.42 * smooth(a / 0.5) - 0.18 * smooth((a - 1.1) / 0.3) + 0.18 * smooth((a - 1.7) / 0.3))
        return THIEF_PEEK_X, dict(tilt=lean, brows=True, look=-1, eyes='open', flipL=0.2, flipR=0.2), 'peek'
    if T < THIEF_LAND:
        k_ = smooth((T - THIEF_FALL) / (THIEF_LAND - THIEF_FALL))
        return THIEF_PEEK_X, dict(tilt=-0.42 - 1.03 * k_, dy=LIE * k_, brows=True, look=-1, flipL=2.6 * k_, flipR=2.6 * k_), 'slide'
    return thief_x(T), dict(tilt=-1.45, dy=LIE + 0.6 * abs(math.sin(T * 22)), brows=True, look=-1, eyes='open', flipL=2.6, flipR=2.6), 'slide'

def crush(T):
    pose = dict(look=-1, eyes='open', sq=1 + 0.018 * math.sin(T * 2.1 + 2), tilt=0.04 * math.sin(T * 1.4 + 1))
    holding = None
    if T >= THIEF_GIVE:
        holding = 'shiny'; pose['flipL'] = 1.1; pose['eyes'] = 'happy'
        if T < THIEF_GIVE + 0.45: pose['dy'] = 5 * math.sin(math.pi * (T - THIEF_GIVE) / 0.45)
    elif blinking(T, 2.0): pose['eyes'] = 'blink'
    return pose, holding

# ---------------- camera: frames one island at a time, follows Pip between them ----------------
CAMK = [(0, 141), (3.6, 141), (5.0, 380), (7.4, 380), (8.9, 141), (36.0, 141), (37.2, 252), (38.6, 252), (39.8, ('pip', -60)),
        (46.5, ('pip', -60)), (52.6, ('pip', -60)), (53.8, 357), (71.8, 357), (72.8, 0), (75.8, 0), (77.0, 357), (LOOP + 1, 357)]
def cam_val(spec, T): return pip_x(T) + spec[1] if isinstance(spec, tuple) else spec
def cam_x(T):
    for (t0, a), (t1, b) in zip(CAMK, CAMK[1:]):
        if t0 <= T < t1:
            s = smooth((T - t0) / (t1 - t0)) if a != b else 0.0
            return min(max(cam_val(a, T) * (1 - s) + cam_val(b, T) * s, 0), WW - W)
    return 357

# ---------------- captions: unboxed bold, ONE line at a time, yellow key words ----------------
FONT = ImageFont.truetype(bk.FONT_BOLD, 80)
HEADPHONES = ["0011111100", "0100000010", "1000000001", "1000000001", "1110000111", "1110000111", "1110000111", "0110000110"]
def caption_sprite(line, highlight, icon=False):
    img = Image.new('RGBA', (WF, 130 + (90 if icon else 0)), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    words = line.split(' '); sp = 22
    wd = [d.textlength(w_, font=FONT) for w_ in words]; x = (WF - (sum(wd) + sp * (len(words) - 1))) / 2
    for w_, ww in zip(words, wd):
        colr = bk.YELLOW if w_.strip('.,!?:-\'').upper() in highlight else bk.WHITE
        d.text((x + 5, 18), w_, font=FONT, fill=(6, 10, 24, 255), stroke_width=7, stroke_fill=(6, 10, 24, 255))
        d.text((x, 11), w_, font=FONT, fill=colr + (255,), stroke_width=7, stroke_fill=(8, 14, 30, 255))
        x += ww + sp
    a = np.asarray(img).astype(np.float32) / 255
    if icon:
        y0 = 130; x0 = WF // 2 - 5 * 7
        for r_, row in enumerate(HEADPHONES):
            for c_, b in enumerate(row):
                if b == '1': a[y0 + r_ * 7:y0 + r_ * 7 + 7, x0 + c_ * 7:x0 + c_ * 7 + 7] = [1, 1, 1, 1]
    return a
CAP_Y = 1290
CAPS = []
def cap(text, a, b, hl=(), icon=False, story=True):
    """multi-line captions play one line after another, like the reference"""
    off = 2.4 if story else 0.0
    lines = text.split('\n'); n = len(lines); span = (b - a) / n
    for i, ln in enumerate(lines):
        CAPS.append((a + off + i * span, a + off + (i + 1) * span, caption_sprite(ln, set(hl), icon and i == 0)))
cap("HE GOT ROBBED!!", 0.0, 1.55, ('ROBBED',), icon=True, story=False)
cap("OK WAIT.\nLET ME EXPLAIN.", 1.62, 2.75, ('WAIT', 'EXPLAIN'), story=False)
for text, a, b, hl in [
    ("THIS IS PIP.", 0.4, 3.3, ('PIP',)), ("THIS IS PENNY.", 5.1, 7.4, ('PENNY',)),
    ("HE HAS A CRUSH\nON HER.", 9.0, 11.8, ('CRUSH',)), ("HE WANTS TO GIVE\nHER A GIFT.", 12.2, 14.8, ('GIFT',)),
    ("THE PERFECT PEBBLE.", 15.0, 16.9, ('PERFECT',)), ("NOPE.\nTOO DULL.", 18.7, 20.2, ('NOPE', 'DULL')),
    ("NOPE.\nTOO SMALL.", 22.1, 23.6, ('NOPE', 'SMALL')), ("THIS ONE.\nPERFECT.", 25.4, 28.4, ('PERFECT',)),
    ("WAIT--\nHEY!!", 29.6, 31.0, ('HEY',)), ("HE GOT ROBBED.", 31.2, 33.2, ('ROBBED',)),
    ("FINE.\nAN EVEN BETTER ONE.", 33.6, 35.8, ('BETTER',)), ("BUT IT'S\nACROSS THE ICE.", 36.4, 38.8, ('ICE',)),
    ("HOW HARD\nCAN IT BE?", 40.4, 42.8, ()), ("WHEEEE!!", 43.4, 46.2, ('WHEEEE',)), ("GOT IT.", 46.5, 48.2, ('GOT',)),
    ("NOW THE\nIMPORTANT PART.", 49.4, 52.6, ('IMPORTANT',)), ("...", 54.6, 56.2, ()), ("SHE SAID YES!!", 56.4, 59.6, ('YES',)),
    ("PLOT TWIST:\nPENGUINS REALLY\nDO THIS.", 60.2, 63.4, ('TWIST', 'REALLY')), ("THEY GIVE PEBBLES\nTO THE ONE\nTHEY LIKE.", 63.6, 67.0, ('PEBBLES', 'LIKE')),
    ("AND BUILD A\nNEST TOGETHER.", 67.2, 71.6, ('NEST',)), ("AND THE THIEF?", 72.4, 74.2, ('THIEF',)),
    ("HE HAD A\nCRUSH TOO.", 74.4, 76.4, ('CRUSH',)), ("A FEW WEEKS\nLATER...", 77.2, 79.2, ('WEEKS',)),
    ("WAIT...\nIS IT MOVING??", 79.4, 81.3, ('MOVING',)), ("BEST CHRISTMAS\nGIFT EVER.", 81.7, 83.8, ('CHRISTMAS', 'GIFT'))]:
    cap(text, a, b, hl)
def draw_captions(F, v):
    for a, b, spr in CAPS:
        if a <= v < b:
            al = min(1.0, (v - a) / 0.08, (b - v) / 0.08); dy = int(8 * (1 - min(1.0, (v - a) / 0.1)))
            h_ = spr.shape[0]; y0 = CAP_Y + dy; A = spr[..., 3:4] * al
            F[y0:y0 + h_] = F[y0:y0 + h_] * (1 - A) + spr[..., :3] * A

# ---------------- labels, tags, arrows, counter ----------------
def head_of(x): return x, GY - 64
LABELS = [('PIP', 0.5, 3.4, lambda T: head_of(pip_x(T))), ('PENNY', 5.0, 7.4, lambda T: head_of(PENNY_X)),
          ('???', 26.4, 28.5, lambda T: (THIEF_PEEK_X - 22, GY - 48)), ('BETTER ONE', 34.2, 38.8, lambda T: (PEBBLE_X['best'], GY - 3)),
          ('THE THIEF', 72.4, 74.3, lambda T: head_of(THIEF_HOME)), ('HIS CRUSH', 74.5, 76.3, lambda T: head_of(CRUSH_X))]
TAGS = [('SLIPPERY', 36.4, 38.8, (318, 186)), ('GENTOO', 60.4, 63.4, (488, 194))]
def draw_overlays(F, T, cam):
    for text, a, b, anchor in LABELS:
        if a <= T < b:
            wx, wy = anchor(T); ax, ay = int((wx - cam) * S), int(wy * S)
            tw = len(text) * 6 * 5 - 5
            tx = min(max(ax - tw // 2, 30), WF - tw - 30); ty = max(min(ay - 170, 520), 60)
            bk.label(F, text, tx, ty, ax, ay - 6, px=5)
    for text, a, b, (wx, wy) in TAGS:
        if a <= T < b: bk.tag(F, text, min(max(int((wx - cam) * S), 40), WF - 300), int(wy * S), px=5)
    if 34.2 <= T < PICKS['best']:                          # pixel arrow pointing at the better pebble
        bob = 3 * math.sin(T * 5)
        bk.arrow(F, int((PEBBLE_X['best'] - cam) * S) - 60 + int(bob), int((GY - 3) * S) - 70 + int(bob))
    if NEST_T <= T < THIEF_SCENE:                          # pebble counter, like the reference counters
        n = sum(1 for nt, _, _ in NEST if T >= nt)
        bk.pixel_text(F, f'PEBBLES: {n}', 330, 480, px=5, colr=(200, 215, 240))

def dotted_trail(F, x_from, x_to, y, cam, a=0.8):
    step = 3 if x_to > x_from else -3
    for i, x in enumerate(np.arange(x_from, x_to, step)):
        put(F, x - cam, y, hexc('#eaf3ff'), a * (0.4 + 0.6 * i / max(1, abs(x_to - x_from) / 3)))

# ---------------- egg + chick ----------------
def draw_egg(F, x, y, T):
    a_in = T - EGG_IN
    grow = 1 - math.exp(-a_in / 0.08) * math.cos(a_in * 18) if a_in < 0.6 else 1.0
    if T < HATCH:
        amp = 0.05 + 0.25 * smooth((T - (EGG_IN + 1.0)) / (HATCH - EGG_IN - 1.0))
        kk = last_age(KICKS, T); idx = int(np.searchsorted(KICKS, T, side='right'))
        ang = amp * math.exp(-kk / 0.18) * math.sin(kk * 25) * (1 if idx % 2 else -1) if T > EGG_IN + 1.0 else 0
        col, M = egg_sprite(ang, 'all', sum(1 for c in CRACKS if T >= c))
        if grow < 0.95:
            n = M.shape[0]; yy, xx = np.mgrid[0:n, 0:n]; sc = max(0.1, grow)
            sy = np.clip(((yy - (n - 2)) / sc + (n - 2)).astype(int), 0, n - 1); sx = np.clip(((xx - n / 2) / sc + n / 2).astype(int), 0, n - 1)
            col, M = col[sy, sx], M[sy, sx]
        pv.blit_hr(F, col, M, x - 11, y - 20, 1); return
    a = T - HATCH
    pop_ = min(1.0, a / 0.3); rise = 9 * (1 - (1 - pop_) ** 3)
    bob = 1.2 * math.exp(-last_age(KICKS, T) / 0.12) if a > 0.6 else 0
    cp = dict(scale=0.42, hat=True, eyes='happy' if a > 0.5 else 'wide', flipL=0.9 + 0.6 * math.sin(a * 12) * math.exp(-a),
              flipR=0.9 + 0.6 * math.sin(a * 12 + 1) * math.exp(-a), flop=1.5 * math.sin(T * 6), sq=1 - 0.05 * math.exp(-last_age(KICKS, T) / 0.08))
    if cp['eyes'] == 'happy' and ((T + 0.7) % 2.3) < 0.12: cp['eyes'] = 'blink'
    draw_char(F, x, y + 5 - rise - bob, cp, 0)
    col, M = egg_sprite(0.0, 'bottom', 0); pv.blit_hr(F, col, M, x - 11, y - 20, 1)
    if a < 1.2:
        col, M = egg_sprite(a * 9, 'top', 0); pv.blit_hr(F, col, M, x - 11 + 14 * a, y - 20 - 18 * a + 28 * a * a, 1)

# ---------------- render one story moment ----------------
rng = np.random.default_rng(41)
FLAKES = [(rng.uniform(0, W), rng.uniform(0, 1), rng.uniform(10, 22), rng.uniform(0, 6.28)) for _ in range(40)]
NEST_POS = [(NEST_CX + 34 * math.cos(math.pi + TAU * i / len(NEST) * 0.999), GY + 5 + 6 * math.sin(math.pi + TAU * i / len(NEST) * 0.999)) for i in range(len(NEST))]
HEARTS = [(t, 'pip') for t in (7.6, 8.2, 8.8, 9.6, 10.4)] + [(t, 'couple') for t in (GIVE + 0.15, GIVE + 0.5, GIVE + 0.9, 61.0, 64.0, 67.0)] + \
         [(t, 'thief') for t in (THIEF_GIVE + 0.15, THIEF_GIVE + 0.5, THIEF_GIVE + 0.9)] + [(t, 'egg') for t in (HATCH + 0.2, HATCH + 0.5, HATCH + 0.9, HATCH + 1.6)]
HR_BAYER = up(BAY[np.arange(H)[:, None] % 4, np.arange(W)[None, :] % 4][..., None])[..., 0]
def onscreen(x, cam): return -40 < x - cam < W + 40

def render(T):
    cam = cam_x(T); X = int(round(cam * S))
    F = BG.copy()
    off = int(round(cam * S * 0.35)) % 60
    cols = np.arange((60 - off) % 60, WF, 60); F[:, cols] = F[:, cols] * 1.12 + 0.012
    for x0, ph0, sp, ph in FLAKES:
        y = ((T * sp / H + ph0) % 1.0) * (H + 10) - 5
        put(F, (x0 + 4 * math.sin(T * 0.8 + ph)) % W, y, np.array([0.85, 0.92, 1.0]), 0.3)
    A = WA_HR[:, X:X + WF]; F = F * (1 - A) + WCOL_HR[:, X:X + WF] * A
    for k, tp in PICKS.items():
        if T < tp:
            sh = 0.6 if (k == 'shiny' and T > 23.8) else (1.0 if (k == 'best' and T > 33.6) else 0.0)
            pebble(F, PEBBLE_X[k] - cam, GY + 1, k, T, sh, small=(k == 'dull2'))
    if PLACE_SHINY <= T < SNATCH: pebble(F, SHINY_GROUND_X - cam, GY + 1, 'shiny', T, 0.8)
    for i, (nt, n, d) in enumerate(NEST):
        a = T - nt
        if a >= 0 and onscreen(NEST_CX, cam):
            x, y = NEST_POS[i]
            yy = y - 16 * (1 - min(1, a / 0.18)) ** 2 - (2 * math.sin(math.pi * (a - 0.18) / 0.14) if 0.18 < a < 0.32 else 0)
            pebble(F, x - cam, yy, 'best' if i == 0 else 'nest', T, 0.6 * math.exp(-a / 0.3) if a < 1 else 0)
    th = thief(T)
    if th and th[2] == 'peek': draw_char(F, th[0], GY - th[1].get('dy', 0), th[1], cam)
    if onscreen(ICEBERG_X + 12, cam): pv.blit_hr(F, ICEBERG[0], ICEBERG[1], ICEBERG_X - cam, GY + 3 - ICEBERG[1].shape[0], 1)
    hx, hpose, hheld = pv.eased(pip, T)
    ppose, pheld = pv.eased(penny, T)
    if onscreen(PENNY_X, cam):
        ptips = draw_char(F, PENNY_X, GY - ppose.get('dy', 0), ppose, cam)
        if pheld: tx, ty = ptips[-1]; pebble(F, tx, ty, pheld, T, 1.0)
    if SLIDE[0] <= T < SLIDE[1] + 0.6: dotted_trail(F, SLIDE[2] - 6, min(hx, SLIDE[3]) - 4, GY + 1, cam, 0.8 * min(1, (SLIDE[1] + 0.6 - T) / 0.6))
    if onscreen(hx, cam):
        htips = draw_char(F, hx, GY - hpose.get('dy', 0), hpose, cam)
        if hheld: tx, ty = htips[1]; pebble(F, tx, ty, hheld, T, 1.0 if hheld in ('shiny', 'best') else 0, small=(hheld == 'dull2'))
    for k, tt in TOSSES.items():
        a = T - tt
        if 0 <= a < 0.6: pebble(F, PEBBLE_X[k] + 4 - 30 * a / 0.6 - cam, GY - 34 + 90 * (a - 0.25) ** 2 - 5, k, T, small=(k == 'dull2'))
    if th and th[2] in ('slide', 'scene'):
        if th[2] == 'slide' and T >= THIEF_LAND: dotted_trail(F, THIEF_PEEK_X + 4, th[0] + 6, GY + 1, cam)
        tp = pv.eased(lambda t_: (thief(t_)[1] if thief(t_) else th[1], None), T)[0] if th[2] == 'scene' else th[1]
        ttips = draw_char(F, th[0], GY - tp.get('dy', 0), tp, cam)
        if th[2] == 'slide':
            for k in range(1, 7): put(F, th[0] + 4 + k * 3 - cam, GY - (k % 2), np.array([1.0, 1.0, 1.0]), 0.8 - k * 0.1)
            if T >= SNATCH: pebble(F, th[0] - 46 - cam, GY - 7, 'shiny', T, 0.8)
        elif T < THIEF_GIVE: tx, ty = ttips[1]; pebble(F, tx, ty, 'shiny', T, 1.0)
    if onscreen(CRUSH_X, cam) and THIEF_SCENE - 0.5 <= T < FLURRY + 0.6:
        cpose, cheld = pv.eased(crush, T)
        ctips = draw_char(F, CRUSH_X, GY - cpose.get('dy', 0), cpose, cam)
        if cheld: tx, ty = ctips[-1]; pebble(F, tx, ty, cheld, T, 1.0)
    if 0 <= T - SNATCH < 0.3:
        a = T - SNATCH
        for q in range(10):
            ang = TAU * q / 10; d = 2 + 9 * a / 0.3
            put(F, SHINY_GROUND_X + d * math.cos(ang) - cam, GY - 3 + d * math.sin(ang) * 0.6, np.array([1.0, 1.0, 1.0]), 1 - a / 0.3)
    if 33.6 <= T < PICKS['best']:
        k = 0.5 + 0.5 * math.sin(T * 6)
        for q in range(3):
            ang = q * TAU / 3 + T * 0.8; d = 6 + 1.5 * k
            put(F, PEBBLE_X['best'] + d * math.cos(ang) - cam, GY - 3 + d * math.sin(ang) * 0.7, hexc('#ffc83a'), 0.6 + 0.4 * k)
    if 0 <= T - PICKS['best'] < 0.45:
        a = T - PICKS['best']
        for q in range(12):
            ang = TAU * q / 12; d = 2 + 10 * a / 0.45
            put(F, PEBBLE_X['best'] + d * math.cos(ang) - cam, GY - 3 + d * math.sin(ang), hexc('#ffc83a'), 1 - a / 0.45)
    if T >= EGG_IN and onscreen(NEST_CX, cam): draw_egg(F, NEST_CX - cam, GY + 8, T)
    if 12.0 <= T < 17.0:
        popk = 0 if T < 16.6 else (T - 16.6) / 0.3
        if T - 12.0 > 0.15: bubble(F, pip_x(T) + 18 - cam, GY - 80 + math.sin(T * 4), T, popk)
    for ht, who in HEARTS:
        a = T - ht
        if 0 <= a < 1.4:
            mx = {'pip': pip_x(T) + 4, 'couple': (pip_x(T) + PENNY_X) / 2, 'thief': (THIEF_HOME + CRUSH_X) / 2, 'egg': NEST_CX}[who]
            heart(F, mx - cam + (int(ht * 7) % 3 - 1) * 5, GY - 72 - 16 * a, max(0.0, 1 - (a / 1.4) ** 2))
    if FLURRY <= T < FLURRY + 1.0:
        k = math.sin(math.pi * (T - FLURRY) / 1.0) * 0.9
        m = HR_BAYER < k; F[m] = F[m] * 0.15 + hexc('#f4fbff') * 0.85
    draw_overlays(F, T, cam)
    return F

# ---------------- video time -> story time (cold open on the theft, rewind) ----------------
COLD0, COLD_LEN, REW = THIEF_FALL + 0.3, 1.6, 0.8
VLOOP = COLD_LEN + REW + LOOP
def story_time(v):
    if v < COLD_LEN: return COLD0 + v
    if v < COLD_LEN + REW: return (COLD0 + COLD_LEN) * (1 - smooth((v - COLD_LEN) / REW))
    return v - COLD_LEN - REW
REWIND_ICON = ["1000100", "1100110", "1110111", "1111111", "1110111", "1100110", "1000100"]
def frame(v):
    F = render(story_time(v))
    if COLD_LEN <= v < COLD_LEN + REW:
        for j, row in enumerate(REWIND_ICON):
            for i, ch in enumerate(row[::-1]):
                if ch == '1': F[120 + j * 10:130 + j * 10, 900 + i * 10:910 + i * 10] = 1.0
        sl = (np.arange(HF) // 3) % 4 == 0; F[sl] = F[sl] * 0.85
    if v > VLOOP - 0.4:
        G = render(story_time(0.0)); m = HR_BAYER < smooth((v - (VLOOP - 0.4)) / 0.4); F[m] = G[m]
    draw_captions(F, v)
    return (np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == '__main__':
    if sys.argv[1] == '--stills':
        for ts in sys.argv[3:]: Image.fromarray(frame(float(ts))).save(f'{sys.argv[2]}/still_{float(ts):06.2f}.png')
        sys.exit()
    out, wav = sys.argv[1], sys.argv[2]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WF}x{HF}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(int(round(VLOOP * FPS))):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 600 == 0: print('frame', f, flush=True)
    p.stdin.close(); p.wait(); print('done', out)
