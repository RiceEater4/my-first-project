"""'What If Penguins Met Santa?' - blueprint pixel short narrated by Jett (1080x1920, 60 fps).
Layout: visual in the middle or a bit higher, one-line captions right below, exact narration words
timed to the voice (captions.json). Hook: blunt fact + shouted "WHAAAAT?!" on the first seconds.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study')); sys.path.insert(0, os.path.join(ROOT_, 'penguin_gift'))
import importlib.util
_s = importlib.util.spec_from_file_location('reindeer_video', os.path.join(ROOT_, 'reindeer', 'video.py'))
rv = importlib.util.module_from_spec(_s); _s.loader.exec_module(rv)        # shared helpers (bg, island, captions, props)
pv, bk = rv.pv, rv.bk
sys.path.insert(0, HERE)
from script import LINES

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
def chunk_start(line, k):
    cs = [c for c in CAPJ if c['line'] == line]; return cs[min(k, len(cs) - 1)]['t0']
(L_HOOK, L_WHAT, L_CARD, L_ARCTIC, L_SOUTH, L_PLANET, L_MOVE, L_NOFEAR, L_EVEN, L_SPEED, L_RUN, L_WATER,
 L_TWIST, L_AUK, L_EXTINCT, L_NAME, L_END) = range(17)
GROUND = rv.GROUND

# ---------------- sprites ----------------
def finish(col, M): return bk.outline(bk.dither_seams(col, M), M)
def sd(px, py, ax, ay, bx, by): return rv.seg_dist(px, py, ax, ay, bx, by)
def shade(P, v, yy, xx): return np.stack(P)[np.clip(np.floor(v + BAY[yy.astype(int) % 4, xx.astype(int) % 4] - 0.5), 0, len(P) - 1).astype(int)]
_pc = {}
def penguin(scale=0.42, **pose):
    key = (scale, tuple(sorted((k, round(v, 2) if isinstance(v, float) else v) for k, v in pose.items())))
    if key in _pc: return _pc[key]
    pose = dict(pose); pose['scale'] = scale / pv.FINE
    col, M, _ = pv.penguin(pose)
    ys, xs = np.nonzero(M); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    out = (bk.dither_seams(col[y0:y1, x0:x1], M[y0:y1, x0:x1]), M[y0:y1, x0:x1], (pv.OX - x0, pv.OY - y0)); _pc[key] = out; return out
def draw_penguin(F, x, y, scale=0.42, **pose):
    col, M, (ox, oy) = penguin(scale, **pose); pv.blit_hr(F, col, M, x - ox, y - oy, 1)
FURW = [hexc('#b9c4d6'), hexc('#dfe6f0'), hexc('#f4f6fa'), hexc('#ffffff')]
_bc = {}
def bear(scale=1.0, step=0.0, flip=True, eye='open'):
    key = (scale, round(step, 1), flip, eye)
    if key in _bc: return _bc[key]
    n = int(70 * scale) + 4; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    u, v = xx / scale, yy / scale
    body = ((u - 32) / 22) ** 2 + ((v - 30) / 12.5) ** 2 <= 1
    hump = ((u - 24) / 11) ** 2 + ((v - 22) / 7) ** 2 <= 1
    head = ((u - 55) / 8.5) ** 2 + ((v - 25) / 7) ** 2 <= 1
    snout = ((u - 62) / 5.5) ** 2 + ((v - 28) / 4) ** 2 <= 1
    ear = ((u - 51) / 2.4) ** 2 + ((v - 18) / 2.4) ** 2 <= 1
    legs = np.zeros_like(body)
    for lx, ph in ((16, 0), (24, math.pi), (40, math.pi), (48, 0)):
        off = 3 * math.sin(step * TAU + ph); lift = max(0, 2.5 * math.sin(step * TAU + ph)) if step else 0
        legs |= sd(u, v, lx, 36, lx + off, 50 - lift) <= 3.4
    M = body | hump | head | snout | ear | legs
    col = shade(FURW, 2.6 - 1.6 * ((v - 18) / 32) + 0.3 * (u / 60), yy, xx)
    col[legs & (v > 47)] = hexc('#9aa6ba')
    col[((u - 66.5) / 1.8) ** 2 + ((v - 27) / 1.5) ** 2 <= 1] = hexc('#14101a')
    col[ear & (((u - 51) / 1.2) ** 2 + ((v - 18) / 1.2) ** 2 <= 1)] = hexc('#9aa6ba')
    if eye == 'open': col[((u - 56.5) / 1.1) ** 2 + ((v - 23) / 1.2) ** 2 <= 1] = hexc('#14101a')
    elif eye == 'happy': col[(np.abs(v - 23.5 + 0.5 * (1 - ((u - 56.5) / 1.4) ** 2)) < 0.5) & (np.abs(u - 56.5) < 1.5)] = hexc('#14101a')
    elif eye == 'hungry':
        col[((u - 56.5) / 1.1) ** 2 + ((v - 23) / 1.2) ** 2 <= 1] = hexc('#14101a')
        col[(np.abs(v - 21 + 0.3 * (u - 54)) < 0.5) & (np.abs(u - 56.5) < 2)] = hexc('#14101a')
        col[((u - 61) / 2.2) ** 2 + ((v - 31) / 1.2) ** 2 <= 1] = hexc('#e8607a'); M |= ((u - 61) / 2.2) ** 2 + ((v - 31) / 1.2) ** 2 <= 1
    col, M = finish(col, M)
    if flip: col, M = col[:, ::-1], M[:, ::-1]
    out = (col, M, (n - 32 * scale if flip else 32 * scale, 50 * scale)); _bc[key] = out; return out
def draw_bear(F, x, y, **kw):
    col, M, (ox, oy) = bear(**kw); pv.blit_hr(F, col, M, x - ox, y - oy, 1)
def santa_sprite():
    n = 40; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    body = ((xx - 20) / 11) ** 2 + ((yy - 26) / 10) ** 2 <= 1
    face = ((xx - 20) / 6) ** 2 + ((yy - 11) / 5.5) ** 2 <= 1
    beard = ((xx - 20) / 7.5) ** 2 + ((yy - 16) / 5.5) ** 2 <= 1
    hat = ((yy >= 0) & (yy < 7) & (np.abs(xx - 20 - (7 - yy) * 0.6) <= 2 + yy * 0.9)) | (((xx - 26) / 2.2) ** 2 + ((yy - 1) / 2.2) ** 2 <= 1)
    brim = (yy >= 6) & (yy < 8.5) & (np.abs(xx - 20) <= 7.5)
    boots = (yy >= 35) & (yy < 39) & ((np.abs(xx - 14) < 3.5) | (np.abs(xx - 26) < 3.5))
    M = body | face | beard | hat | brim | boots
    col = np.zeros((n, n, 3), np.float32)
    col[body] = shade([hexc('#9a1424'), hexc('#c81e2e'), hexc('#e8404a')], 1.8 - (xx - 20) / 14, yy, xx)[body]
    col[body & (np.abs(yy - 28) < 1.3)] = hexc('#1b1418'); col[body & (np.abs(yy - 28) < 1.3) & (np.abs(xx - 20) < 2)] = hexc('#ffcc4a')
    col[body & (np.abs(xx - 20) < 1.2) & (yy < 27)] = hexc('#ffffff')
    col[face] = hexc('#f2c2a0'); col[beard & ~(face & (yy < 13))] = hexc('#ffffff')
    for ex in (17.5, 22.5): col[(np.abs(xx - ex) < 0.8) & (np.abs(yy - 10.5) < 0.8)] = hexc('#14101a')
    col[((xx - 20) / 1.4) ** 2 + ((yy - 13) / 1.1) ** 2 <= 1] = hexc('#e8907a')
    col[hat] = hexc('#c81e2e'); col[((xx - 26) / 2.2) ** 2 + ((yy - 1) / 2.2) ** 2 <= 1] = hexc('#ffffff'); col[brim] = hexc('#ffffff')
    col[boots] = hexc('#1b1418')
    return finish(col, M)
SANTA = santa_sprite()
def draw_santa(F, x, y, bob=0.0): pv.blit_hr(F, SANTA[0], SANTA[1], x - 20, y - 39 - bob, 1)
def auk_sprite(ghost=False):
    n = 64; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    body = ((xx - 30) / 11) ** 2 + ((yy - 40) / 16) ** 2 <= 1
    head = ((xx - 32) / 7.5) ** 2 + ((yy - 18) / 7) ** 2 <= 1
    neck = sd(xx, yy, 31, 22, 30, 30) <= 6
    beak = (yy >= 14) & (yy <= 24) & (xx >= 37) & (xx <= 37 + 11 * (1 - np.abs(yy - 19) / 6)) & ~(((xx - 48) / 2.5) ** 2 + ((yy - 23) / 2) ** 2 <= 1)
    beak |= ((xx - 47) / 2.4) ** 2 + ((yy - 15.5) / 2.2) ** 2 <= 1
    wing = ((xx - 24) / 4) ** 2 + ((yy - 40) / 10) ** 2 <= 1
    feet = (yy >= 55) & (yy < 58) & ((np.abs(xx - 26) < 4) | (np.abs(xx - 34) < 4))
    M = body | head | neck | beak | wing | feet
    col = np.zeros((n, n, 3), np.float32)
    black = shade([hexc('#14141c'), hexc('#262634'), hexc('#3a3a4c')], 1.6 - (xx - 30) / 16, yy, xx)
    col[M] = black[M]
    belly = body & (xx > 29) & (yy > 30); col[belly] = shade([hexc('#d8dce6'), hexc('#f4f6fa'), hexc('#ffffff')], 1.8 - (yy - 30) / 30, yy, xx)[belly]
    col[((xx - 34) / 2.6) ** 2 + ((yy - 15.5) / 2.0) ** 2 <= 1] = hexc('#ffffff')       # white spot in front of the eye
    col[((xx - 30) / 1.0) ** 2 + ((yy - 17) / 1.1) ** 2 <= 1] = hexc('#ffffff')
    col[beak & ((np.abs(xx - 41) < 0.6) | (np.abs(xx - 43.5) < 0.6))] = hexc('#cfd2da')  # grooves on the bill
    col[wing] = hexc('#1b1b26'); col[feet] = hexc('#1b1418')
    col, M = finish(col, M)
    if ghost:
        g = col.mean(-1, keepdims=True); col = np.where(M[..., None], g * 0.5 + hexc('#6fa6dd') * 0.5, col)
    return col, M
AUK, AUK_GHOST = auk_sprite(), auk_sprite(True)
def draw_auk(F, x, y, ghost=False, alpha=1.0):
    col, M = AUK_GHOST if ghost else AUK
    if alpha < 1: M = M & (pv.HR_BAYER[:M.shape[0], :M.shape[1]] if False else (BAY[np.arange(M.shape[0])[:, None] % 4, np.arange(M.shape[1])[None, :] % 4] < alpha))
    pv.blit_hr(F, col, M, x - 30, y - 58, 1)

# ---------------- globe ----------------
_ly, _lx = np.mgrid[0:64, 0:128]
LAT = (0.5 - (_ly + 0.5) / 64) * math.pi; LON = (_lx + 0.5) / 128 * TAU
LAND = (np.sin(LON * 2 + 0.5) * np.cos(LAT * 3) + 0.6 * np.sin(LON * 5 + LAT * 4) + 0.35 * np.cos(LON * 3 - LAT * 6)) > 0.55
GC, GR = (90, 112), 50
def globe(F, t, hi_top=0.0, hi_bot=0.0, equator=False):
    R = GR; yy, xx = np.mgrid[-R - 1:R + 2, -R - 1:R + 2]
    nx, ny = (xx + 0.5) / R, (yy + 0.5) / R; d2 = nx ** 2 + ny ** 2; M = d2 <= 1
    nz = np.sqrt(np.clip(1 - d2, 0, 1)); lat = np.arcsin(np.clip(-ny, -1, 1)); lon = (np.arctan2(nx, nz + 1e-6) + t * 0.2) % TAU
    land = LAND[np.clip(((0.5 - lat / math.pi) * 64).astype(int), 0, 63), (lon / TAU * 128).astype(int) % 128]
    light = np.clip(nx * -0.5 + ny * -0.45 + nz * 0.7, 0, 1); lvl = np.clip(np.floor(light * 3.2 + BAY[yy % 4, xx % 4] * 0.9), 0, 3).astype(int)
    OCE = np.stack([hexc('#123f8a'), hexc('#1d5bb8'), hexc('#2f7ddf'), hexc('#5ea6f2')])
    LND = np.stack([hexc('#1d6a3a'), hexc('#2f8f4a'), hexc('#4fb860'), hexc('#8fe08a')])
    ICE_ = np.stack([hexc('#8fb3dd'), hexc('#c4dcf4'), hexc('#eaf4ff'), hexc('#ffffff')])
    col = np.where(land[..., None], LND[lvl], OCE[lvl]); col = np.where((np.abs(lat) > 1.15)[..., None], ICE_[lvl], col)
    glow_top = (lat > 1.0) & (hi_top > 0); glow_bot = (lat < -1.0) & (hi_bot > 0)
    col[glow_top] = col[glow_top] * (1 - 0.35 * hi_top) + hexc('#ffe27a') * 0.35 * hi_top
    col[glow_bot] = col[glow_bot] * (1 - 0.35 * hi_bot) + hexc('#ffe27a') * 0.35 * hi_bot
    if equator: col[(np.abs(lat) < 0.03) & ((xx // 2) % 2 == 0)] = hexc('#ffcc4a')
    col, M2 = bk.outline(col.astype(np.float32), M)
    pv.blit_hr(F, col, M2, GC[0] - R - 1, GC[1] - R - 1, 1)

# ---------------- props ----------------
def card(F, t):
    x0, y0, x1, y1 = 22, 62, 158, 170
    col = np.zeros((y1 - y0, x1 - x0, 3), np.float32); M = np.ones((y1 - y0, x1 - x0), bool)
    yy, xx = np.mgrid[0:y1 - y0, 0:x1 - x0]
    col[:] = hexc('#fdf6e8'); border = (xx < 5) | (xx >= x1 - x0 - 5) | (yy < 5) | (yy >= y1 - y0 - 5)
    col[border] = hexc('#c81e2e'); col[border & (((xx + yy) // 3) % 2 == 0)] = hexc('#1f7a3e')
    col[(yy > 80) & ~border] = hexc('#eaf3fd')
    col, M = bk.outline(col, M); pv.blit_hr(F, col, M, x0, y0, 1)
    draw_bear(F, 60, 152, scale=0.62, flip=False, eye='happy')
    draw_santa(F, 92, 152, bob=abs(math.sin(t * 3)))
    draw_penguin(F, 128, 152, scale=0.3, eyes='happy', hat=True, flipR=1.6)
    for k in range(10):
        sx, sy = 30 + (k * 37) % 120, 70 + ((k * 23 + int(t * 20)) % 70); put(F, sx, sy, hexc('#c4dcf4'))
def speech_bubble(F, x, y, text):
    w_ = len(text) * 6 * 5 + 30; X, Y = int(x * S - w_ / 2), int(y * S)
    F[Y:Y + 70, X:X + w_] = 1.0
    for k in range(4): F[Y + k, X:X + w_] = F[Y + 69 - k, X:X + w_] = NAVY; F[Y:Y + 70, X + k] = F[Y:Y + 70, X + w_ - 1 - k] = NAVY
    bk.pixel_text(F, text, X + 15, Y + 18, px=5, colr=(20, 24, 40))
WATER = [hexc('#1d5bb8'), hexc('#2f7ddf'), hexc('#5ea6f2')]
def water(F, t, x0=0, x1=W, y0=GROUND + 2, y1=GROUND + 22):
    yy, xx = np.mgrid[y0:y1, x0:x1]
    v = 2.0 - (yy - y0) / 30 + 0.3 * np.sin(xx / 6 + t * 3)
    col = np.stack(WATER)[np.clip(np.floor(v + BAY[yy % 4, xx % 4] - 0.5), 0, 2).astype(int)]
    col[(yy == y0) & ((xx + int(t * 8)) % 6 < 3)] = hexc('#ffffff')
    pv.blit_hr(F, col.astype(np.float32), np.ones(col.shape[:2], bool), x0, y0, 1)

# ---------------- scenes ----------------
def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def loc(t, i):
    a, b = SEG[i]; nxt = SEG[i + 1][0] if i + 1 < len(SEG) else END
    return t - a, min(1.0, max(0.0, (t - a) / max(0.3, nxt - a)))
def small_island(F, cx, w_=66):
    if ('isl', w_) not in rv.ISL_CACHE: rv.ISL_CACHE[('isl', w_)] = bk.diorama(w_, 26, 7, rv.SNOWP, rv.SIDEP, seed=w_)
    c, M = rv.ISL_CACHE[('isl', w_)]; pv.blit_hr(F, c, M, cx - w_ / 2, GROUND - 12, 1)

def scene(F, t):
    i = seg_of(t); a, p = loc(t, i)
    if i in (L_HOOK, L_WHAT):                                # two islands, never met
        small_island(F, 44); small_island(F, 136)
        shock = i == L_WHAT
        draw_penguin(F, 44, GROUND + 2 - (4 * abs(math.sin(a * 14)) if shock else 0), scale=0.42, hat=True,
                     eyes='wide' if shock else 'open', look=1, flipL=2.0 if shock else 0.3, flipR=2.0 if shock else 0.3)
        draw_bear(F, 148, GROUND + 2, scale=0.62, flip=True, eye='open')
        bk.label(F, 'PENGUIN', 60, 520, int(44 * S), int((GROUND - 48) * S), px=6)
        bk.label(F, 'POLAR BEAR', 640, 520, int(136 * S), int((GROUND - 32) * S), px=6)
        rv.counter(F, 'TIMES MET: 0', y=330, colr=(255, 200, 58) if shock else (225, 235, 255))
    elif i == L_CARD:                                        # the Christmas card lie
        card(F, t); bk.tag(F, 'CHRISTMAS CARD', 290, 300, px=6)
    elif i in (L_ARCTIC, L_SOUTH, L_PLANET):                 # where they really live
        globe(F, t, hi_top=1.0 if i in (L_ARCTIC, L_PLANET) else 0.0, hi_bot=1.0 if i in (L_SOUTH, L_PLANET) else 0.0, equator=i >= L_SOUTH)
        if i in (L_ARCTIC, L_PLANET): draw_bear(F, 90, GC[1] - GR + 6, scale=0.32, flip=True); bk.label(F, 'ARCTIC', 700, 300, int(104 * S), int((GC[1] - GR + 2) * S), px=6)
        if i in (L_SOUTH, L_PLANET): draw_penguin(F, 90, GC[1] + GR + 4, scale=0.24, hat=True); bk.label(F, 'ANTARCTICA', 640, 1020, int(96 * S), int((GC[1] + GR - 2) * S), px=6)
        if i == L_SOUTH and t > chunk_start(L_SOUTH, 3) - 0.1: bk.label(F, 'EQUATOR', 40, 900, int(44 * S), int(GC[1] * S), px=6)
        if i == L_PLANET:
            for k in range(0, 100, 4):
                yy_ = GC[1] - GR + 12 + (2 * GR - 24) * k / 100; put(F, 34, yy_, hexc('#ffcc4a'))
            rv.counter(F, '20,000 KM APART', y=150, colr=(255, 200, 58))
    elif i == L_MOVE:                                        # a penguin travels north to Santa
        globe(F, t, equator=True)
        s_ = smooth(p); yy_ = lerp(GC[1] + GR + 2, GC[1] - GR - 6, s_)
        for k in range(0, int(30 * s_)):
            put(F, 90 + 4 * math.sin(k * 0.6), lerp(GC[1] + GR, GC[1] - GR, k / 30), hexc('#ffcc4a'))
        draw_penguin(F, 90 + 4 * math.sin(s_ * 18), yy_, scale=0.26, hat=True, eyes='happy')
        draw_santa(F, 128, GC[1] - GR + 4); bk.label(F, 'SANTA', 820, 300, int(128 * S), int((GC[1] - GR - 30) * S), px=6)
    elif i in (L_NOFEAR, L_EVEN, L_SPEED):                   # no fear... even of a polar bear
        rv.island(F); draw_santa(F, 28, GROUND)
        bx = lerp(200, 132, smooth((t - SEG[L_EVEN][0] + 0.3) / 2.0)) if i >= L_EVEN else 220
        draw_penguin(F, 72, GROUND + 2, scale=0.42, hat=True, eyes='happy', look=1, flipR=1.5 + 0.4 * math.sin(t * 8) if i == L_EVEN else 0.4)
        if i >= L_EVEN: draw_bear(F, bx, GROUND + 2, scale=0.75, flip=True, step=(t * 1.4) % 1 if bx > 133 else 0, eye='hungry')
        if i == L_NOFEAR: bk.tag(F, 'NO LAND PREDATORS', 270, 300, px=6)
        if i == L_EVEN and t > SEG[L_EVEN][0] + 0.6: speech_bubble(F, 72, 60, 'HI!')
        if i == L_SPEED:
            rv.bar_meter(F, 'PENGUIN 2 KM/H', 0.05, 60, 300); rv.bar_meter(F, 'BEAR 40 KM/H', 1.0, 600, 300, good=False)
    elif i == L_RUN:                                         # RUN, BUDDY!
        rv.island(F)
        k_ = smooth(a / max(0.4, SEG[L_RUN][1] - SEG[L_RUN][0] + 0.4))
        px_ = lerp(72, 30, k_); bx = lerp(132, 92, k_)
        for k in range(0, 40, 3): put(F, px_ + 10 + k, GROUND + 1, hexc('#eaf3ff'), 0.8 - k / 50)
        draw_penguin(F, px_, GROUND - 6, scale=0.42, hat=True, eyes='wide', tilt=-1.45, flipL=0.3, flipR=0.3)
        draw_bear(F, bx, GROUND + 2, scale=0.75, flip=True, step=(t * 2.4) % 1, eye='hungry')
    elif i == L_WATER:                                       # into the water: penguins are rockets
        rv.island(F); water(F, t, 0, 18) if t < SEG[L_WATER][0] + 0.6 else None
        dive = SEG[L_WATER][0] + 0.6
        if t < dive: draw_penguin(F, lerp(30, 12, smooth((t - SEG[L_WATER][0]) / 0.6)), GROUND - 6, scale=0.42, hat=True, eyes='wide', tilt=-1.45)
        draw_bear(F, 50, GROUND + 2, scale=0.75, flip=True, eye='open')
        if t >= dive:
            a2 = t - dive; k_ = min(1.0, a2 / 0.25)
            x0, x1, y0, y1 = 14, 166, 66, 168
            yy, xx = np.mgrid[y0:y1, x0:x1]
            v = 2.4 - (yy - y0) / 40 + 0.25 * np.sin(xx / 7 + t * 3)
            col = np.stack([hexc('#123f8a'), hexc('#1d5bb8'), hexc('#2f7ddf'), hexc('#5ea6f2')])[np.clip(np.floor(v + BAY[yy % 4, xx % 4] - 0.5), 0, 3).astype(int)].astype(np.float32)
            col[(yy == y0) & ((xx + int(t * 8)) % 6 < 3)] = hexc('#ffffff')
            M = BAY[yy % 4, xx % 4] < k_ * 1.01
            col, M = bk.outline(col, M); pv.blit_hr(F, col, M, x0, y0, 1)
            px_ = 20 + 150 * min(1.0, (a2 % 2.2) / 1.6)
            for k in range(1, 9): put(F, px_ - 10 - k * 5, 122 + 2 * (k % 2), hexc('#cfe9ff'), 0.9 - k * 0.1)
            for k in range(6): put(F, (px_ - 8 - k * 9) % 160 + 14, 100 + 18 * math.sin(k * 2.3 + t), hexc('#9fd8ff'))
            if px_ < 172: draw_penguin(F, px_, 132, scale=0.34, hat=True, eyes='happy', tilt=-1.5, flipL=0.2, flipR=0.2)
            if t > chunk_start(L_WATER, 2) - 0.1: rv.counter(F, 'ROCKET MODE', y=300, colr=(255, 200, 58))
    elif i == L_TWIST:                                       # plot twist: a mystery northern bird
        rv.island(F)
        col, M = AUK; sil = np.where(M[..., None], hexc('#0b1430'), col); pv.blit_hr(F, sil, M, 90 - 30, GROUND + 2 - 58, 1)
        bk.tag(F, 'PLOT TWIST', 380, 230, px=7)
        bk.pixel_text(F, '?', 520, 560, px=12, colr=(255, 200, 58))
    elif i == L_AUK:                                         # the great auk
        rv.island(F); draw_auk(F, 90, GROUND + 2)
        bk.label(F, 'GREAT AUK', 640, 300, int(110 * S), int((GROUND - 50) * S), px=6)
        facts = [(chunk_start(L_AUK, 1), 'BLACK + WHITE'), (chunk_start(L_AUK, 2), "CAN'T FLY"), (chunk_start(L_AUK, 3), 'SWIMS FAST')]
        for k, (ts, txt) in enumerate(facts):
            if t >= ts - 0.05: bk.pixel_text(F, txt, 60, 420 + k * 60, px=6, colr=(225, 235, 255))
        if t >= chunk_start(L_AUK, 4) - 0.05: bk.tag(F, 'SAILORS: "PENGUIN"', 250, 190, px=6)
    elif i == L_EXTINCT:                                     # wiped out, 1844
        rv.island(F)
        last = chunk_start(L_EXTINCT, 2)
        if t < last:
            for k, x in enumerate((50, 90, 130)): draw_auk(F, x, GROUND + 2, alpha=1.0 - smooth((t - SEG[L_EXTINCT][0]) / 1.4) * (k != 1))
        else:
            fade = smooth((t - chunk_start(L_EXTINCT, 3)) / 1.2) if t > chunk_start(L_EXTINCT, 3) else 0
            draw_auk(F, 72, GROUND + 2, ghost=fade > 0.5); draw_auk(F, 108, GROUND + 2, ghost=fade > 0.5)
            rv.calendar(F, '1844')
            if fade > 0.5: bk.tag(F, 'EXTINCT', 400, 380, px=7)
    elif i == L_NAME:                                        # the name moved south
        rv.island(F); draw_auk(F, 46, GROUND + 2, ghost=True)
        draw_penguin(F, 132, GROUND + 2, scale=0.42, hat=True, eyes='happy')
        k_ = smooth((t - SEG[L_NAME][0]) / max(0.5, SEG[L_NAME][1] - SEG[L_NAME][0]))
        x = int(lerp(46, 132, k_) * S) - 120; bk.tag(F, 'PENGUIN', max(30, min(x, WF - 300)), 360 + int(-60 * math.sin(math.pi * k_)), px=7)
    else:                                                    # Santa never met one... Merry Christmas
        rv.island(F); draw_santa(F, 90, GROUND, bob=abs(math.sin(t * 3)) * 1.5)
        draw_bear(F, 150, GROUND + 2, scale=0.6, flip=True, eye='happy')
        if t >= chunk_start(L_END, 2) - 0.05: draw_auk(F, 34, GROUND + 2, ghost=True); bk.label(F, 'GREAT AUK', 40, 520, int(34 * S), int((GROUND - 58) * S), px=6)
        if t >= chunk_start(L_END, 4) - 0.05:
            for k in range(14):
                th = TAU * k / 14 + t; put(F, 90 + 50 * math.cos(th), 70 + 18 * math.sin(th), hexc('#ffd84a'))

# ---------------- captions, snow, frame ----------------
CAPS = [(c['t0'], c['t1'], rv.caption_sprite(c['text'], set(c['hl']))) for c in CAPJ]
def captions(F, t):
    for a, b, spr in CAPS:
        if a <= t < b:
            dy = int(6 * (1 - min(1.0, (t - a) / 0.06))); h_ = spr.shape[0]; A = spr[..., 3:4]
            F[rv.CAP_Y + dy:rv.CAP_Y + dy + h_] = F[rv.CAP_Y + dy:rv.CAP_Y + dy + h_] * (1 - A) + spr[..., :3] * A
    if t < SEG[1][1] + 0.4:
        y0 = rv.CAP_Y + 140; x0 = WF // 2 - 35
        for r_, row in enumerate(rv.HEADPHONES):
            for c_, bb in enumerate(row):
                if bb == '1': F[y0 + r_ * 7:y0 + r_ * 7 + 7, x0 + c_ * 7:x0 + c_ * 7 + 7] = 1.0
SHOUTS = [SEG[L_WHAT][0], SEG[L_RUN][0], chunk_start(L_TWIST, 1)]
def frame(t):
    F = rv.BG.copy()
    scene(F, t); rv.snow(F, t)
    i = seg_of(t)
    if i >= 1 and 0 <= t - SEG[i][0] < 0.12 and i in (L_CARD, L_ARCTIC, L_MOVE, L_NOFEAR, L_SPEED, L_WATER, L_TWIST, L_AUK, L_EXTINCT, L_NAME, L_END):
        m = rv.HR_BAYER < (1 - (t - SEG[i][0]) / 0.12) * 0.7; F[m] = F[m] * 0.4 + hexc('#f4fbff') * 0.6
    for st in SHOUTS:                                       # screen shake on every shout
        if 0 <= t - st < 0.35:
            A = 14 * math.exp(-(t - st) / 0.1); dx, dy = int(A * math.sin(t * 90)), int(A * math.cos(t * 70))
            F = np.roll(np.roll(F, dx, 1), dy, 0)
    captions(F, t)
    return (np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == '__main__':
    if sys.argv[1] == '--stills':
        for ts in sys.argv[3:]: Image.fromarray(frame(float(ts))).save(f'{sys.argv[2]}/still_{float(ts):06.2f}.png')
        sys.exit()
    out, wav = sys.argv[1], sys.argv[2]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WF}x{HF}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(int(round(END * FPS))):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 600 == 0: print('frame', f, flush=True)
    p.stdin.close(); p.wait(); print('done', out)
