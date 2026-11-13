"""'What If It Never Stopped Snowing?' - blueprint pixel-art short (1080x1920, 60 fps, 66.6 s).

Day 1 white Christmas -> day 7 cars buried -> day 30 houses buried -> 1 year: the bottom turns to ice
(cut-away) -> white snow reflects sunlight so Earth gets colder -> the whole planet becomes a snowball
-> plot twist: it really happened ~700 million years ago (Snowball Earth) -> volcanoes melted it.
Cold open on the buried house, then a rewind to day 1.

usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...  (video seconds)
"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'penguin_gift')); sys.path.insert(0, os.path.join(ROOT_, 'style_study')); sys.path.insert(0, HERE)
import importlib.util
_spec = importlib.util.spec_from_file_location('penguin_model', os.path.join(ROOT_, 'penguin_gift', 'video.py'))
pv = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(pv)   # penguin character model
import blueprint_kit as bk
from snow_score import *

W, H, S = 180, 320, 6
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc = pv.hexc; NAVY = bk.OUTLINE; pv.INK = NAVY
pv.BODY, pv.BODY_L = hexc('#1c2440'), hexc('#36446c')
smooth, put, up, BAY = pv.smooth, pv.put, pv.up, pv.BAYER
def last_age(h, t): return pv.last_age(h, t)
def lerp(a, b, s): return a + (b - a) * s
def blit(F, sp, x, y): pv.blit_hr(F, sp[0], sp[1], x, y, 1)

# ---------------- background ----------------
def build_bg():
    yy, xx = np.mgrid[0:HF, 0:WF].astype(np.float32)
    top, mid, low = hexc('#0f2a55'), hexc('#1f4782'), hexc('#162f5c')
    f = yy / HF
    base = np.where((f < 0.45)[..., None], top + (mid - top) * (f / 0.45)[..., None], mid + (low - mid) * ((f - 0.45) / 0.55)[..., None])
    glow = np.exp(-(((xx - 540) / 560) ** 2 + ((yy - 900) / 640) ** 2)); base = base + glow[..., None] * hexc('#123a70') * 0.55
    vig = np.clip(1 - 0.35 * ((np.abs(xx - WF / 2) / (WF / 2)) ** 2 + (np.abs(yy - HF / 2) / (HF / 2)) ** 2) / 2, 0, 1)
    base = base * vig[..., None]
    grid = ((yy.astype(int) % 60) == 0) | ((xx.astype(int) % 60) == 0)
    base[grid] = base[grid] * 1.12 + 0.012
    return np.clip(base, 0, 1).astype(np.float32)
BG = build_bg()
HR_BAYER = up(BAY[np.arange(H)[:, None] % 4, np.arange(W)[None, :] % 4][..., None])[..., 0]

# ---------------- sprites (grid units, navy outline, dithered) ----------------
def finish(col, M): return bk.outline(bk.dither_seams(col, M), M)
def shade(P, v, yy, xx): return np.stack(P)[np.clip(np.floor(v + BAY[yy % 4, xx % 4] - 0.5), 0, len(P) - 1).astype(int)]
SNOWP = [hexc('#a9c8ea'), hexc('#cfe2f6'), hexc('#eaf3fd'), hexc('#ffffff')]
SIDEP = [hexc('#2c5d96'), hexc('#4a86c5'), hexc('#6fa6dd')]
ISLAND = bk.diorama(144, 34, 8, SNOWP, SIDEP, seed=4)
ISLAND_X, ISLAND_Y = 18, 196
GROUND = 214
def house():
    w_, h_ = 38, 34; yy, xx = np.mgrid[0:h_, 0:w_]
    M = np.zeros((h_, w_), bool); col = np.zeros((h_, w_, 3), np.float32)
    wall = (yy >= 18) & (xx >= 3) & (xx < 35)
    roof = (yy >= 6) & (yy < 18) & (np.abs(xx - 19) <= 3 + (yy - 6) * 1.35)
    chim = (xx >= 27) & (xx < 31) & (yy >= 0) & (yy < 12)
    col[wall] = shade([hexc('#7a2a24'), hexc('#a8443a'), hexc('#c95a48')], 1.2 + 1.2 * (1 - xx / w_), yy, xx)[wall]
    col[wall & ((yy - 18) % 4 == 0)] = hexc('#6a2420')
    col[roof] = shade([hexc('#b9cde6'), hexc('#e2edf9'), hexc('#ffffff')], 0.6 + 2.0 * (1 - (yy - 6) / 12), yy, xx)[roof]
    col[chim] = hexc('#5a3a40'); col[chim & (yy < 2)] = hexc('#ffffff')
    win = (yy >= 22) & (yy < 28) & (((xx >= 7) & (xx < 13)) | ((xx >= 24) & (xx < 30))); col[win] = hexc('#ffd27a')
    col[win & ((xx == 10) | (xx == 27) | (yy == 25))] = hexc('#c9963a')
    door = (yy >= 24) & (xx >= 16) & (xx < 21); col[door] = hexc('#3a5a3a')
    M = wall | roof | chim
    return finish(col, M)
def car():
    w_, h_ = 26, 12; yy, xx = np.mgrid[0:h_, 0:w_]
    body = ((yy >= 4) & (yy < 10) & (xx >= 1) & (xx < 25)) | ((yy >= 0) & (yy < 4) & (xx >= 6) & (xx < 19))
    col = np.zeros((h_, w_, 3), np.float32); col[body] = shade([hexc('#a8202e'), hexc('#d8323f'), hexc('#ff6a6a')], 1 + 1.5 * (1 - yy / h_), yy, xx)[body]
    win = (yy >= 1) & (yy < 4) & (((xx >= 8) & (xx < 12)) | ((xx >= 13) & (xx < 17))); col[win] = hexc('#bfe6ff')
    wheel = ((xx - 6) ** 2 + (yy - 10) ** 2 <= 5) | ((xx - 19) ** 2 + (yy - 10) ** 2 <= 5); col[wheel] = hexc('#1b1f2a')
    M = body | wheel
    return finish(col, M)
def pine():
    w_, h_ = 22, 36; yy, xx = np.mgrid[0:h_, 0:w_]; M = np.zeros((h_, w_), bool)
    for k, (t0, b0, hw) in enumerate(((2, 14, 5), (9, 22, 8), (16, 31, 10.5))):
        s = (yy - t0) / (b0 - t0); M |= (yy >= t0) & (yy < b0) & (np.abs(xx - 10.5) <= hw * np.clip(s, 0, 1))
    trunk = (yy >= 31) & (np.abs(xx - 10.5) < 2); M |= trunk
    col = shade([hexc('#0f3d26'), hexc('#1d6a3d'), hexc('#2f8f52')], 1.3 + 1.3 * (1 - xx / w_), yy, xx)
    col[trunk] = hexc('#5a3a24')
    snow = M & ~trunk & ((yy % 7) < 2) & (xx < 14); col[snow] = hexc('#f4fbff')
    col[(yy == 1) & (np.abs(xx - 10.5) < 1)] = hexc('#ffd84a'); M[1, 10:12] = True
    return finish(col, M)
def snowman():
    w_, h_ = 18, 26; yy, xx = np.mgrid[0:h_, 0:w_]
    M = ((xx - 9) ** 2 + (yy - 19) ** 2 <= 42) | ((xx - 9) ** 2 + (yy - 11) ** 2 <= 20) | ((xx - 9) ** 2 + (yy - 5) ** 2 <= 12)
    col = shade(SNOWP, 1.2 + 2 * (1 - xx / w_), yy, xx)
    hat = (yy <= 2) & (np.abs(xx - 9) <= 3); hat |= (yy == 3) & (np.abs(xx - 9) <= 5); col[hat] = hexc('#1b1f2a'); M |= hat
    for ex in (7, 11): col[5, ex] = hexc('#1b1f2a')
    col[6, 10:13] = hexc('#ff8a2a'); M[6, 10:13] = True
    scarf = (yy >= 8) & (yy < 10) & (np.abs(xx - 9) <= 4); col[scarf & M] = hexc('#e3313f')
    col[(yy == 11) & (xx == 9)] = hexc('#1b1f2a'); col[(yy == 14) & (xx == 9)] = hexc('#1b1f2a')
    return finish(col, M)
HOUSE, CAR, PINE, SNOWMAN = house(), car(), pine(), snowman()

# ---------------- penguin (Pip) on the chunky grid ----------------
CHAR_SCALE = 0.11
def draw_char(F, wx, wy, pose):
    pose = dict(pose); pose['scale'] = pose.get('scale', 1.0) * CHAR_SCALE
    col, M, tips = pv.penguin(pose)
    ys, xs = np.nonzero(M); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    col, M = bk.dither_seams(col[y0:y1, x0:x1], M[y0:y1, x0:x1]), M[y0:y1, x0:x1]
    pv.blit_hr(F, col, M, wx - (pv.OX - x0), wy - (pv.OY - y0), 1)

# ---------------- scene: home (days 1 -> 30) ----------------
def depth(T):
    if T >= 58: return 2
    if T < 7.5: return 2
    if T < 12: return lerp(2, 15, smooth((T - 7.5) / 4.5))
    if T < 16.5: return 15
    if T < 21.5: return lerp(15, 31, smooth((T - 16.5) / 5.0))
    return 31
def day(T):
    if T >= 58: return 1
    d = 1
    for (t0, n0), (t1, n1) in zip(DAY_MARKS, DAY_MARKS[1:] + [(99, 365)]):
        if t0 <= T < t1: d = n0
    for t0, n in DAY_MARKS[1:]:
        if t0 <= T < t0 + 1.0:
            prev = [m for t_, m in DAY_MARKS if t_ < t0][-1]; d = int(lerp(prev, n, smooth(T - t0)))
    return d
SNOW_M = {1: '0.1', 7: '1', 30: '4', 365: '50+'}
rng = np.random.default_rng(5)
FLAKES = [(rng.uniform(0, W), rng.uniform(0, 1), rng.uniform(14, 30), rng.uniform(0, 6.28)) for _ in range(120)]
def snowfall(F, T, n):
    for x0, ph0, sp, ph in FLAKES[:n]:
        y = ((T * sp / H + ph0) % 1.0) * (H + 10) - 5
        put(F, (x0 + 5 * math.sin(T * 0.9 + ph)) % W, y, np.array([0.95, 0.97, 1.0]), 0.75)
SNOWBLOCK_X0, SNOWBLOCK_X1 = 22, 158
def snow_block(F, d):
    """the snow piling up on the island: a dithered white slab with a wavy top and navy outline"""
    if d <= 0.5: return
    top = GROUND - d
    h_ = int(232 - top) + 3; w_ = SNOWBLOCK_X1 - SNOWBLOCK_X0
    yy, xx = np.mgrid[0:h_, 0:w_]
    surf = 1.2 * np.sin(xx / 5.0) + 0.8 * np.sin(xx / 2.3 + 1)
    M = yy >= surf + 1.5
    rad = 6; M &= ~(((xx < rad) | (xx >= w_ - rad)) & (yy < rad) & (((np.minimum(xx, w_ - 1 - xx) - rad) ** 2 + (yy - rad) ** 2) > rad ** 2))
    v = 3.2 - 2.2 * np.clip(yy / max(10, h_), 0, 1)
    col = shade(SNOWP, v, yy, xx)
    rim = M & ~np.roll(M, 1, 0); col[rim] = hexc('#ffffff')
    col, M = finish(col, M)
    pv.blit_hr(F, col, M, SNOWBLOCK_X0, top - 1, 1)
def smoke(F, T, x, y):
    for i in range(5):
        ph = (T * 0.5 + i / 5) % 1.0
        r = 1 + ph * 3; a = 0.55 * (1 - ph) * min(1, ph * 6)
        cx, cy = x + 2 + ph * 8 + 1.5 * math.sin(ph * 6 + i), y - 2 - ph * 22
        for dy in range(-int(r), int(r) + 1):
            for dx in range(-int(r), int(r) + 1):
                if dx * dx + dy * dy <= r * r: put(F, cx + dx, cy + dy, hexc('#c9d6ea'), a)
def scene_home(F, T):
    blit(F, ISLAND, ISLAND_X, ISLAND_Y)
    blit(F, HOUSE, 28, GROUND - 34); blit(F, CAR, 74, GROUND - 12); blit(F, PINE, 136, GROUND - 36); blit(F, SNOWMAN, 116, GROUND - 26)
    d = depth(T)
    kid_y = GROUND - max(0, d - 2)
    pose = dict(hat=True, eyes='open', look=0.4, flop=1.2 * math.sin(T * 5), sq=1 + 0.02 * math.sin(T * 2.4))
    if T < 7.5 or T >= 58: pose['eyes'] = 'happy'; pose['flipR'] = 1.6 + 0.4 * math.sin(T * 8)          # waving, happy
    if 12.0 <= T < 15.6: pose['eyes'] = 'happy'; pose['flipL'] = pose['flipR'] = 1.8 + 0.5 * math.sin(T * 12); kid_y -= 4 * abs(math.sin(T * 6))   # no school!
    if 17.8 <= T < 24: pose['eyes'] = 'wide'; pose['look'] = -0.8; pose['tilt'] = 0.06 * math.sin(T * 3)    # where's the house?
    snow_block(F, d)
    if d < 31.5 or True: smoke(F, T, 56, GROUND - 34 - 0)
    draw_char(F, 98, kid_y, pose)
    snowfall(F, T, 30 if (T < 7.5 or T >= 58) else (70 if T < 16 else 120))
def counters(F, T, d_override=None):
    n = day(T) if d_override is None else d_override
    t1 = f'DAYS OF SNOW: {n}'; t2 = f'SNOW: {SNOW_M.get(n, "...")} M'
    bk.pixel_text(F, t1, (WF - (len(t1) * 30 - 5)) // 2, 360, px=5, colr=(225, 235, 255))
    bk.pixel_text(F, t2, (WF - (len(t2) * 30 - 5)) // 2, 420, px=5, colr=(170, 200, 240))

# ---------------- scene: cut-away (1 year) ----------------
def scene_cut(F, T):
    a = T - 24.0
    x0, x1, y0, y1 = 66, 154, 112, 236
    fill = smooth(a / 1.2); top = lerp(y1, y0, fill)
    ice_h = lerp(0, 46, smooth((a - 2.0) / 3.0)); packed_h = lerp(0, 34, smooth((a - 1.2) / 2.5))
    w_, h_ = x1 - x0, y1 - y0; yy, xx = np.mgrid[0:h_, 0:w_]
    yabs = yy + y0
    M = yabs >= top
    col = shade(SNOWP, 2.6 + 0.6 * (1 - xx / w_), yy, xx)
    packed = yabs >= y1 - ice_h - packed_h
    col[packed] = shade([hexc('#8eaacb'), hexc('#a9c1dd'), hexc('#c4d6ea')], 1.4 + 0.8 * (1 - xx / w_), yy, xx)[packed]
    icem = yabs >= y1 - ice_h
    col[icem] = shade([hexc('#2a6fb8'), hexc('#3f8fd6'), hexc('#6fb4ea')], 1.2 + 1.2 * (1 - xx / w_), yy, xx)[icem]
    col[icem & (((xx + 2 * yy) % 19) < 1)] = hexc('#cfe9ff')
    col, M = finish(col, M); pv.blit_hr(F, col, M, x0, y0, 1)
    if a > 1.6:                                                     # your house, way down at the bottom
        hc, hm = HOUSE; tint = hc * 0.55 + hexc('#2a6fb8') * 0.45
        pv.blit_hr(F, np.where(hm[..., None], tint, hc), hm, 91, y1 - 36, 1)
    draw_char(F, 110, top - 0.5, dict(hat=True, eyes='open' if a < 4 else 'wide', look=0, flop=1.2 * math.sin(T * 5), tilt=0.05 * math.sin(T * 2)))
    snowfall(F, T, 60)
    labels = [('FRESH SNOW', 24.8, 32, (x0 + 2, top + 8)), ('PACKED SNOW', 26.4, 32, (x0 + 2, y1 - ice_h - packed_h / 2)),
              ('ICE', 27.6, 32, (x0 + 2, y1 - ice_h / 2)), ('YOUR HOUSE', 25.8, 27.8, (98, y1 - 22))]
    for text, ta, tb, (ax, ay) in labels:
        if ta <= T < tb:
            ty = int(ay * S) - 80; bk.label(F, text, 24, ty, int(ax * S), int(ay * S), px=5)
    counters(F, T, 365)

# ---------------- scene: the trap (snow reflects sunlight) ----------------
SUN_C = (40, 92)
def scene_trap(F, T):
    a = T - 32.0
    blit(F, ISLAND, ISLAND_X, ISLAND_Y)
    snow_block(F, 6)
    for k in range(12):                                             # pixel sun with spinning rays
        th = TAU * k / 12 + T * 0.4
        for r in range(15, 19): put(F, SUN_C[0] + r * math.cos(th), SUN_C[1] + r * math.sin(th), hexc('#ffc83a'))
    yy, xx = np.mgrid[-12:13, -12:13]; m = xx ** 2 + yy ** 2 <= 144
    for y_, x_ in zip(*np.nonzero(m)):
        put(F, SUN_C[0] + x_ - 12, SUN_C[1] + y_ - 12, hexc('#ffe27a') if (x_ - 12) + (y_ - 12) < 0 else hexc('#ffb43a'))
    hit = (88, GROUND - 7)
    if a > 0.5:                                                     # sunlight comes in...
        s = min(1.0, (a - 0.5) / 0.8)
        for i in range(int(40 * s)):
            k = i / 40; put(F, lerp(SUN_C[0] + 10, hit[0], k), lerp(SUN_C[1] + 10, hit[1], k), hexc('#ffd84a'))
    if a > 1.8:                                                     # ...and bounces straight back out
        s = min(1.0, (a - 1.8) / 0.8)
        for i in range(0, int(40 * s), 2):
            k = i / 40; put(F, lerp(hit[0], 150, k), lerp(hit[1], 70, k), hexc('#fff6c0'))
    tx, ty0, ty1 = 150, 100, 180                                    # thermometer
    temp = lerp(-10, -50, smooth((a - 2.6) / 4.5))
    lvl = lerp(ty1 - 10, ty0 + 6, (temp + 60) / 80)
    for y in range(ty0, ty1):
        for x in range(tx - 3, tx + 4): put(F, x, y, NAVY if abs(x - tx) == 3 else (hexc('#e3313f') if y >= lvl else hexc('#eaf3fd')))
    for y in range(ty1 - 2, ty1 + 6):
        for x in range(tx - 5, tx + 6):
            if (x - tx) ** 2 + (y - ty1 - 2) ** 2 <= 22: put(F, x, y, hexc('#e3313f'))
    t_txt = f'{int(round(temp))} C'; bk.pixel_text(F, t_txt, int((tx - 8) * S), int((ty1 + 12) * S), px=5)
    shiver = 0.08 * math.sin(T * 40) if a > 3.5 else 0
    draw_char(F, 92, GROUND - 4, dict(hat=True, eyes='wide' if a > 3.5 else 'open', look=1 if a < 3 else 0, flop=1.2 * math.sin(T * 5), tilt=shiver, flipL=0.3, flipR=0.3))
    if a > 0.9 and a < 4.0: bk.label(F, 'SUNLIGHT', 330, 520, int(66 * S), int(118 * S), px=5)
    if a > 2.2 and a < 6.0: bk.label(F, 'BOUNCES BACK', 620, 300, int(128 * S), int(80 * S), px=5)
    snowfall(F, T, 90)

# ---------------- scene: the globe ----------------
GC, GR = (90, 140), 50
_ly, _lx = np.mgrid[0:64, 0:128]
LAT = (0.5 - (_ly + 0.5) / 64) * math.pi; LON = (_lx + 0.5) / 128 * TAU
LAND = (np.sin(LON * 2 + 0.5) * np.cos(LAT * 3) + 0.6 * np.sin(LON * 5 + LAT * 4) + 0.35 * np.cos(LON * 3 - LAT * 6)) > 0.55
def ice_line(T):
    if T < 40.6: return 1.25
    if T < 46.0: return lerp(1.25, -0.3, smooth((T - 40.6) / 5.0))
    if T < 53.0: return -0.3
    return lerp(-0.3, 1.25, smooth((T - 53.0) / 4.5))
VOLCS = [(-22, -8), (14, 18), (-4, 30), (26, -20)]
def scene_globe(F, T):
    R = GR; yy, xx = np.mgrid[-R - 1:R + 2, -R - 1:R + 2]
    nx, ny = (xx + 0.5) / R, (yy + 0.5) / R; d2 = nx ** 2 + ny ** 2; M = d2 <= 1
    nz = np.sqrt(np.clip(1 - d2, 0, 1)); lat = np.arcsin(np.clip(-ny, -1, 1)); lon = (np.arctan2(nx, nz + 1e-6) + T * 0.18) % TAU
    land = LAND[np.clip(((0.5 - lat / math.pi) * 64).astype(int), 0, 63), (lon / TAU * 128).astype(int) % 128]
    L = ice_line(T); wob = 0.08 * np.sin(lon * 5)
    ice = np.abs(lat) > L + wob
    light = np.clip(nx * -0.55 + ny * -0.5 + nz * 0.67, 0, 1); lvl = np.clip(np.floor(light * 3.2 + BAY[yy % 4, xx % 4] * 0.9), 0, 3).astype(int)
    OCE = np.stack([hexc('#123f8a'), hexc('#1d5bb8'), hexc('#2f7ddf'), hexc('#5ea6f2')])
    LND = np.stack([hexc('#1d6a3a'), hexc('#2f8f4a'), hexc('#4fb860'), hexc('#8fe08a')])
    ICE_ = np.stack([hexc('#8fb3dd'), hexc('#c4dcf4'), hexc('#eaf4ff'), hexc('#ffffff')])
    col = np.where(land[..., None], LND[lvl], OCE[lvl]); col = np.where(ice[..., None], ICE_[lvl], col)
    col, M2 = bk.outline(col.astype(np.float32), M)
    pv.blit_hr(F, col, M2, GC[0] - R - 1, GC[1] - R - 1, 1)
    if VOLCANO <= T < 58:                                           # volcanoes poke through and puff out warm gas
        for i, (vx, vy) in enumerate(VOLCS):
            a = T - VOLCANO - i * 0.6
            if a < 0: continue
            cx, cy = GC[0] + vx, GC[1] + vy
            for k in range(4):
                put(F, cx - k, cy + k, hexc('#4a3a34')); put(F, cx + k, cy + k, hexc('#4a3a34')); put(F, cx, cy + k, hexc('#6a4a3a'))
            put(F, cx, cy - 1, hexc('#ff6a2a'))
            for j in range(5):
                ph = (a * 0.6 + j / 5) % 1.0; r = 1 + ph * 3
                for dy in range(-int(r), int(r) + 1):
                    for dx in range(-int(r), int(r) + 1):
                        if dx * dx + dy * dy <= r * r: put(F, cx + dx + ph * 6, cy - 3 - ph * 20 + dy, hexc('#5a5a66'), 0.6 * (1 - ph))
    if 43.0 <= T < 52.0: bk.tag(F, 'SNOWBALL EARTH', 290, 1130, px=5)
    if 47.6 <= T < 52.0:                                            # the big number counts up
        n = int(700_000_000 * smooth((T - 47.6) / 1.4)); t_ = f'{n:,} YEARS AGO'
        bk.pixel_text(F, t_, (WF - (len(t_) * 30 - 5)) // 2, 300, px=5, colr=(255, 200, 58))
    if VOLCANO + 0.8 <= T < VOLCANO + 3.6: bk.label(F, 'VOLCANO', 160, 380, int((GC[0] + VOLCS[0][0]) * S), int((GC[1] + VOLCS[0][1] - 4) * S), px=5)

# ---------------- captions: unboxed bold, one line at a time ----------------
HEADPHONES = ["0011111100", "0100000010", "1000000001", "1000000001", "1110000111", "1110000111", "1110000111", "0110000110"]
def caption_sprite(line, hl, icon=False):
    size = 80
    while True:
        font = ImageFont.truetype(bk.FONT_BOLD, size); d = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
        words = line.split(' '); sp = int(size * 0.27); wd = [d.textlength(w_, font=font) for w_ in words]
        if sum(wd) + sp * (len(words) - 1) < WF - 90 or size < 50: break
        size -= 4
    img = Image.new('RGBA', (WF, 130 + (90 if icon else 0)), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    x = (WF - (sum(wd) + sp * (len(words) - 1))) / 2
    for w_, ww in zip(words, wd):
        colr = bk.YELLOW if w_.strip('.,!?:-\'…').upper() in hl else bk.WHITE
        d.text((x + 5, 18), w_, font=font, fill=(6, 10, 24, 255), stroke_width=7, stroke_fill=(6, 10, 24, 255))
        d.text((x, 11), w_, font=font, fill=colr + (255,), stroke_width=7, stroke_fill=(8, 14, 30, 255))
        x += ww + sp
    a = np.asarray(img).astype(np.float32) / 255
    if icon:
        y0 = 130; x0 = WF // 2 - 35
        for r_, row in enumerate(HEADPHONES):
            for c_, b in enumerate(row):
                if b == '1': a[y0 + r_ * 7:y0 + r_ * 7 + 7, x0 + c_ * 7:x0 + c_ * 7 + 7] = [1, 1, 1, 1]
    return a
CAP_Y, OFF = 1520, 2.6
CAPS = []
def cap(text, a, b, hl=(), icon=False, story=True):
    o = OFF if story else 0.0; lines = text.split('\n'); span = (b - a) / len(lines)
    for i, ln in enumerate(lines): CAPS.append((a + o + i * span, a + o + (i + 1) * span, caption_sprite(ln, set(hl), icon and i == 0)))
cap("IT NEVER STOPS SNOWING.", 0.0, 1.75, ('NEVER', 'SNOWING'), icon=True, story=False)
cap("LET'S GO BACK\nTO DAY 1.", 1.85, 3.25, ('DAY',), story=False)
for text, a, b, hl in [
    ("DAY 1.", 0.5, 1.9, ('1',)), ("A WHITE CHRISTMAS!", 2.0, 4.6, ('WHITE', 'CHRISTMAS')), ("PERFECT.", 4.8, 7.6, ('PERFECT',)),
    ("DAY 7.", 8.2, 9.6, ('7',)), ("THE CARS ARE GONE.", 9.8, 11.8, ('CARS',)), ("SCHOOL'S CANCELLED!", 12.0, 15.6, ('CANCELLED',)),
    ("DAY 30.", 16.2, 17.6, ('30',)), ("THE HOUSES ARE GONE.", 17.8, 19.9, ('HOUSES',)), ("OK...\nTHIS IS GETTING WEIRD.", 20.1, 23.6, ('WEIRD',)),
    ("1 YEAR.", 24.2, 25.6, ('YEAR',)), ("THE SNOW GETS\nSO HEAVY...", 25.8, 27.6, ('HEAVY',)), ("THE BOTTOM\nTURNS INTO ICE.", 27.8, 29.8, ('ICE',)),
    ("THAT'S HOW\nGLACIERS FORM.", 30.0, 31.8, ('GLACIERS',)),
    ("WHITE SNOW\nREFLECTS SUNLIGHT...", 32.3, 34.6, ('REFLECTS',)), ("SO EARTH\nGETS COLDER...", 34.8, 36.8, ('COLDER',)), ("SO EVEN MORE SNOW.", 37.0, 39.6, ('MORE',)),
    ("UNTIL THE WHOLE\nPLANET...", 40.3, 42.6, ('PLANET',)), ("IS ONE BIG SNOWBALL.", 42.8, 45.8, ('SNOWBALL',)),
    ("PLOT TWIST...", 46.1, 47.4, ('TWIST',)), ("THIS ACTUALLY\nHAPPENED.", 47.5, 49.6, ('ACTUALLY',)), ("ABOUT 700 MILLION\nYEARS AGO.", 49.7, 51.8, ('700', 'MILLION')),
    ("SO HOW DID IT END?", 52.0, 53.6, ('END',)), ("VOLCANOES.", 53.7, 54.9, ('VOLCANOES',)), ("THEIR GAS WARMED\nTHE PLANET...", 55.0, 56.6, ('WARMED',)),
    ("AND THE ICE MELTED.", 56.7, 57.9, ('MELTED',)), ("ANYWAY...", 58.3, 60.0, ()), ("MERRY CHRISTMAS.", 60.2, 63.8, ('CHRISTMAS',))]:
    cap(text, a, b, hl)
def draw_captions(F, v):
    for a, b, spr in CAPS:
        if a <= v < b:
            al = min(1.0, (v - a) / 0.08, (b - v) / 0.08); dy = int(8 * (1 - min(1.0, (v - a) / 0.1)))
            h_ = spr.shape[0]; y0 = CAP_Y + dy; A = spr[..., 3:4] * al
            F[y0:y0 + h_] = F[y0:y0 + h_] * (1 - A) + spr[..., :3] * A

# ---------------- labels in the home scene ----------------
def home_labels(F, T):
    if 9.8 <= T < 11.8: bk.label(F, 'YOUR CAR', 560, 820, int(86 * S), int((GROUND - depth(T)) * S), px=5)
    if 17.8 <= T < 22.0: bk.label(F, 'YOUR HOUSE', 200, 640, int(57 * S), int((GROUND - 34) * S), px=5)

# ---------------- compose ----------------
SCENE_FN = {'home': scene_home, 'cut': scene_cut, 'trap': scene_trap, 'globe': scene_globe}
def scene_at(T):
    k = max(i for i, (t0, _) in enumerate(SCENES) if T >= t0); return k
def draw_scene(name, T):
    F = BG.copy(); SCENE_FN[name](F, T)
    if name == 'home': counters(F, T); home_labels(F, T)
    return F
def render(T):
    k = scene_at(T); t0, name = SCENES[k]
    F = draw_scene(name, T)
    if k > 0 and T - t0 < 0.5:
        G = draw_scene(SCENES[k - 1][1], T); m = HR_BAYER >= smooth((T - t0) / 0.5); F[m] = G[m]
    if TWIST <= T < TWIST + 0.35:                                    # the plot-twist hit: a quick flash + shake
        a = (T - TWIST) / 0.35; k_ = (1 - a) * 0.6; m = HR_BAYER < k_; F[m] = F[m] * 0.3 + 0.7
        dx = int(10 * (1 - a) * math.sin(T * 90)); F = np.roll(F, dx, axis=1)
    return F

COLD0, COLD_LEN, REW = 19.0, 1.8, 0.8
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
