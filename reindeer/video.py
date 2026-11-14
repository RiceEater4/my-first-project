"""'What If Santa's Reindeer Were Boys?' - blueprint pixel short with Ethan's narration (1080x1920, 60 fps).

Layout rule: the visual sits in the middle of the screen or a bit higher; one-line captions sit
right below it. Hook: a blunt statement on the very first frame, no rewind.
Timing comes from timing.json (start/end of every narration line, measured from the voice track).

usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study')); sys.path.insert(0, os.path.join(ROOT_, 'penguin_gift')); sys.path.insert(0, HERE)
import importlib.util
_s = importlib.util.spec_from_file_location('penguin_model', os.path.join(ROOT_, 'penguin_gift', 'video.py'))
pv = importlib.util.module_from_spec(_s); _s.loader.exec_module(pv)
import blueprint_kit as bk
from script import LINES

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc = pv.hexc; NAVY = bk.OUTLINE; pv.INK = NAVY
smooth, put, up, BAY = pv.smooth, pv.put, pv.up, pv.BAYER
def lerp(a, b, s): return a + (b - a) * s
TIMING = json.load(open(os.path.join(HERE, 'timing.json')))
SEG = TIMING['lines']                      # [[start, end], ...] per narration line (seconds)
END = TIMING['total']

# ---------------- background ----------------
def build_bg():
    yy, xx = np.mgrid[0:HF, 0:WF].astype(np.float32)
    top, mid, low = hexc('#0f2a55'), hexc('#1f4782'), hexc('#162f5c')
    f = yy / HF
    base = np.where((f < 0.42)[..., None], top + (mid - top) * (f / 0.42)[..., None], mid + (low - mid) * ((f - 0.42) / 0.58)[..., None])
    glow = np.exp(-(((xx - 540) / 560) ** 2 + ((yy - 760) / 600) ** 2)); base = base + glow[..., None] * hexc('#123a70') * 0.55
    vig = np.clip(1 - 0.35 * ((np.abs(xx - WF / 2) / (WF / 2)) ** 2 + (np.abs(yy - HF / 2) / (HF / 2)) ** 2) / 2, 0, 1)
    base = base * vig[..., None]
    grid = ((yy.astype(int) % 60) == 0) | ((xx.astype(int) % 60) == 0)
    base[grid] = base[grid] * 1.12 + 0.012
    return np.clip(base, 0, 1).astype(np.float32)
BG = build_bg()
HR_BAYER = up(BAY[np.arange(H)[:, None] % 4, np.arange(W)[None, :] % 4][..., None])[..., 0]

# ---------------- the island (visual centred a bit above the middle) ----------------
SNOWP = [hexc('#a9c8ea'), hexc('#cfe2f6'), hexc('#eaf3fd'), hexc('#ffffff')]
SIDEP = [hexc('#2c5d96'), hexc('#4a86c5'), hexc('#6fa6dd')]
ISLAND = bk.diorama(150, 30, 8, SNOWP, SIDEP, seed=7)
ISL_X, ISL_Y = 15, 140
GROUND = 152                                  # feet line (grid)
CAP_Y = 1090                                  # caption top (screen px), right below the island
def island(F):
    yy, xx = np.mgrid[0:HF, 0:WF]
    d = ((xx - 540) / 470.0) ** 2 + ((yy - (ISL_Y + 46) * S) / 70.0) ** 2
    m = np.clip(1.1 - d, 0, 1) * 0.45; F[:] = F * (1 - m[..., None]) + F * 0.3 * m[..., None]
    pv.blit_hr(F, ISLAND[0], ISLAND[1], ISL_X, ISL_Y, 1)
ISL_CACHE = {}
def base_frame():
    if 'f' not in ISL_CACHE:
        F = BG.copy(); island(F); ISL_CACHE['f'] = F
    return ISL_CACHE['f'].copy()

# ---------------- reindeer sprite ----------------
FUR = [hexc('#5a3820'), hexc('#7a4e2e'), hexc('#9a6640'), hexc('#b8835a')]
MANE, BELLY = hexc('#efe0c4'), hexc('#dcc4a0')
ANT = [hexc('#8a6a42'), hexc('#bfa070'), hexc('#e2cc9c')]
HOOF = hexc('#2a1a12')
def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; t = np.clip(((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy + 1e-9), 0, 1)
    return np.hypot(px - (ax + t * dx), py - (ay + t * dy))
ANTLER_SEGS = [((41, 9), (38, 1)), ((38, 1), (33, -6)), ((38, 1), (43, -4)), ((35, -3), (30, -2)), ((40, 5), (45, 3)),
               ((44, 9), (47, 2)), ((47, 2), (46, -5)), ((47, 2), (51, -1))]
_cache = {}
def reindeer(scale=1.0, antlers=1.0, nose='black', step=0.0, eye='open', thin=0.0, tilt=0.0, young=False):
    key = (round(scale, 2), round(antlers, 2), nose, round(step, 1), eye, round(thin, 2), round(tilt, 2), young)
    if key in _cache: return _cache[key]
    n = int(64 * scale) + 4
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    ox, oy = 26 * scale, 54 * scale                       # feet centre
    u, v = (xx + 0.5 - ox) / scale + 26, (yy + 0.5 - oy) / scale + 54
    if tilt:
        c_, s_ = math.cos(tilt), math.sin(tilt); cx, cy = 26, 54
        u, v = (u - cx) * c_ + (v - cy) * s_ + cx, -(u - cx) * s_ + (v - cy) * c_ + cy
    ry = 8.5 * (1 - 0.22 * thin); rx = 14.5 * (1 - 0.1 * thin)
    body = ((u - 25) / rx) ** 2 + ((v - 34) / ry) ** 2 <= 1
    neck = seg_dist(u, v, 34, 32, 40, 21) <= 4.2
    head = ((u - 43) / 5.6) ** 2 + ((v - 18) / 4.8) ** 2 <= 1
    snout = ((u - 48.5) / 4.0) ** 2 + ((v - 20) / 2.9) ** 2 <= 1
    ear = ((u - 38.5) / 2.8) ** 2 + ((v - 13.5) / 1.4) ** 2 <= 1
    tail = ((u - 10.5) / 2.2) ** 2 + ((v - 30) / 2.6) ** 2 <= 1
    sw = math.sin(step * TAU)
    legs = np.zeros_like(body); hooves = np.zeros_like(body)
    for lx, ph in ((15, 0), (19, math.pi), (31, math.pi), (35, 0)):
        off = 2.6 * math.sin(step * TAU + ph)
        lift = max(0, 1.8 * math.sin(step * TAU + ph)) if step else 0
        leg = seg_dist(u, v, lx, 38, lx + off, 52 - lift) <= 1.5
        legs |= leg; hooves |= leg & (v > 50 - lift)
    M = body | neck | head | snout | ear | tail | legs
    col = np.zeros((n, n, 3), np.float32)
    shade = 2.2 - 1.4 * ((v - 26) / 18) + 0.4 * ((u - 25) / 25)
    col[:] = np.stack(FUR)[np.clip(np.floor(shade + BAY[yy.astype(int) % 4, xx.astype(int) % 4] - 0.5), 0, 3).astype(int)]
    col[legs] = FUR[0]; col[hooves] = HOOF
    col[body & (v > 37)] = BELLY
    col[(neck | (body & (u > 33) & (v < 34))) & (u > 33)] = MANE
    col[tail] = MANE
    col[snout] = FUR[3]
    nr = 1.7 if nose == 'black' else 2.3
    nm = ((u - 52) / nr) ** 2 + ((v - 19.4) / nr) ** 2 <= 1
    M |= nm; col[nm] = hexc('#1b1418') if nose == 'black' else hexc('#ff2a3c')
    if nose == 'red': col[nm & (u < 51.6) & (v < 19)] = hexc('#ffb0b8')
    if eye == 'open':
        e = ((u - 44) / 1.3) ** 2 + ((v - 16.6) / 1.5) ** 2 <= 1; col[e] = hexc('#14101a')
        col[e & (u < 43.8) & (v < 16.2)] = hexc('#ffffff')
    elif eye == 'happy':
        col[(np.abs(v - 17.2 + 0.6 * (1 - ((u - 44) / 1.6) ** 2)) < 0.55) & (np.abs(u - 44) < 1.7)] = hexc('#14101a')
    elif eye == 'tired':
        col[(np.abs(v - 17.0) < 0.6) & (np.abs(u - 44) < 1.6)] = hexc('#14101a')
        col[head & (v < 16.3) & (np.abs(u - 44) < 1.9) & (v > 15.0)] = FUR[0]
    elif eye == 'shock':
        e = ((u - 44) / 1.9) ** 2 + ((v - 16.6) / 2.1) ** 2 <= 1; col[e] = hexc('#ffffff')
        col[((u - 44.3) / 0.8) ** 2 + ((v - 16.8) / 0.9) ** 2 <= 1] = hexc('#14101a')
    cheek = ((u - 46) / 1.2) ** 2 + ((v - 19.8) / 0.8) ** 2 <= 1; col[cheek & head] = hexc('#e89a8a')
    if antlers > 0:
        A = np.zeros_like(body)
        segs = ANTLER_SEGS[:4] if young else ANTLER_SEGS
        for (a, b) in segs:
            ax, ay = a; bx, by = b
            bx, by = ax + (bx - ax) * antlers, ay + (by - ay) * antlers
            if young: bx, by = ax + (bx - ax) * 0.6, ay + (by - ay) * 0.6
            A |= seg_dist(u, v, ax, ay, bx, by) <= 1.15
        A &= ~head
        col[A] = np.stack(ANT)[np.clip(np.floor(1 + (u[A] - 38) / 8 + BAY[yy.astype(int)[A] % 4, xx.astype(int)[A] % 4] - 0.5), 0, 2).astype(int)]
        M |= A
    col = bk.dither_seams(col, M)
    col, M = bk.outline(col, M)
    _cache[key] = (col, M, (ox, oy))
    return _cache[key]
def draw_deer(F, x, y, **kw):
    col, M, (ox, oy) = reindeer(**kw)
    pv.blit_hr(F, col, M, x - ox, y - oy, 1)
def loose_antler(F, x, y, ang):
    n = 26; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    c_, s_ = math.cos(ang), math.sin(ang); u = (xx - 13) * c_ + (yy - 13) * s_ + 41; v = -(xx - 13) * s_ + (yy - 13) * c_ + 2
    A = np.zeros((n, n), bool)
    for (a, b) in ANTLER_SEGS[:5]: A |= seg_dist(u, v, a[0], a[1], b[0], b[1]) <= 1.15
    col = np.zeros((n, n, 3), np.float32); col[A] = ANT[1]; col[A & (u > 39)] = ANT[2]
    col, A = bk.outline(col, A); pv.blit_hr(F, col, A, x - 13, y - 13, 1)

# ---------------- sleigh with Santa ----------------
def sleigh():
    w_, h_ = 40, 30; yy, xx = np.mgrid[0:h_, 0:w_].astype(np.float32)
    bodym = (yy >= 12) & (yy < 24) & (xx >= 4) & (xx < 34 - (24 - yy) * 0.15) | (((xx - 34) / 5) ** 2 + ((yy - 14) / 6) ** 2 <= 1) & (xx > 30)
    run = (np.abs(yy - 27) < 1.2) & (xx > 2) & (xx < 38) | ((((xx - 37) / 2.5) ** 2 + ((yy - 25) / 2.5) ** 2 <= 1) & (xx > 37))
    struts = ((np.abs(xx - 10) < 1) | (np.abs(xx - 26) < 1)) & (yy >= 24) & (yy < 27)
    santa_body = ((xx - 14) / 6) ** 2 + ((yy - 10) / 5) ** 2 <= 1
    face = ((xx - 14.5) / 2.6) ** 2 + ((yy - 3.5) / 2.5) ** 2 <= 1
    beard = ((xx - 14.5) / 3.2) ** 2 + ((yy - 6.2) / 2.6) ** 2 <= 1
    hat = (yy >= -1) & (yy < 2) & (np.abs(xx - 14) <= 3.2 - (1 - yy) * 0.6) | (((xx - 18.5) / 1.4) ** 2 + ((yy - 0.6) / 1.4) ** 2 <= 1)
    sack = ((xx - 26) / 5) ** 2 + ((yy - 9) / 5) ** 2 <= 1
    M = bodym | run | struts | santa_body | face | beard | hat | sack
    col = np.zeros((h_, w_, 3), np.float32)
    col[sack] = hexc('#8a5a36'); col[sack & (xx < 25)] = hexc('#a8744a')
    col[santa_body] = hexc('#d22a34'); col[face] = hexc('#f2c2a0'); col[beard] = hexc('#ffffff'); col[hat] = hexc('#d22a34')
    col[hat & (yy >= 1)] = hexc('#ffffff'); col[((xx - 18.5) / 1.4) ** 2 + ((yy - 0.6) / 1.4) ** 2 <= 1] = hexc('#ffffff')
    col[(np.abs(xx - 15.4) < 0.6) & (np.abs(yy - 3) < 0.6)] = hexc('#14101a')
    col[bodym] = hexc('#c01e2c'); col[bodym & (yy < 15)] = hexc('#e23a44'); col[bodym & (np.abs(yy - 18) < 0.8)] = hexc('#ffcc4a')
    col[run | struts] = hexc('#ffcc4a'); col[run & (yy > 27.4)] = hexc('#c9963a')
    col = bk.dither_seams(col, M); return bk.outline(col, M)
SLEIGH = sleigh()

# ---------------- little props ----------------
def calendar(F, month, x=310, y=200):
    w_, h_ = 460, 120
    F[y:y + h_, x:x + w_] = hexc('#f4f6fb'); F[y:y + 34, x:x + w_] = hexc('#d22a34')
    for t in range(4):
        F[y + t, x:x + w_] = F[y + h_ - 1 - t, x:x + w_] = NAVY; F[y:y + h_, x + t] = F[y:y + h_, x + w_ - 1 - t] = NAVY
    for rx in (x + 70, x + w_ - 80): F[y - 16:y + 12, rx:rx + 10] = hexc('#3a4664')
    tw = len(month) * 6 * 7 - 7; bk.pixel_text(F, month, x + (w_ - tw) // 2, y + 52, px=7, colr=(30, 36, 60))
def counter(F, text, y=230, colr=(225, 235, 255)):
    tw = len(text) * 6 * 7 - 7; bk.pixel_text(F, text, (WF - tw) // 2, y, px=7, colr=colr)
def sparkle(F, x, y, a, colr='#fff6c0'):
    if a <= 0: return
    for k in range(1, 4):
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)): put(F, x + dx, y + dy, hexc(colr), a * (1 - k / 4))
    put(F, x, y, hexc('#ffffff'), a)
def sweat(F, x, y, a):
    for k in range(3): put(F, x, y + k, hexc('#9fd8ff'), a)
    put(F, x - 1, y + 2, hexc('#9fd8ff'), a)

# ---------------- scenes ----------------
def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a: i = k
    return i
def loc(t, i):
    a, b = SEG[i]; nxt = SEG[i + 1][0] if i + 1 < len(SEG) else END
    return t - a, (t - a) / max(0.3, nxt - a)
TEAM = [(62, 0), (100, 0), (138, 0), (70, -8), (108, -8), (146, -8), (78, -16), (116, -16), (154, -16)]   # x, y offset
def team(F, t, antlers, eye='open', thin=0.0, bob=True, sink=0.0, wobble=0.0, rud_glow=0.0, pop_times=None):
    order = sorted(range(9), key=lambda k: TEAM[k][1])
    pv.blit_hr(F, SLEIGH[0], SLEIGH[1], 2, GROUND - 30 - 14 + sink, 1)
    for k in order:
        x, dy = TEAM[k]
        b = 0.8 * abs(math.sin(t * 6 + k)) if bob else 0
        a_ = antlers if pop_times is None else (1.0 if t < pop_times[k] else 0.0)
        nose = 'red' if k == 2 else 'black'
        draw_deer(F, x, GROUND + dy - b + sink * (0.3 if k % 3 else 0), scale=0.74, antlers=a_, nose=nose, step=(t * 1.6 + k * 0.3) % 1 if bob else 0,
                  eye=eye, thin=thin, tilt=wobble * math.sin(t * 9 + k))
        if pop_times is not None and 0 <= t - pop_times[k] < 0.9:
            a2 = t - pop_times[k]
            loose_antler(F, x + 14 + 18 * a2, GROUND + dy - 48 - 30 * a2 + 90 * a2 * a2, a2 * 7)
        if k == 2 and rud_glow > 0:
            nx, ny = x + 19, GROUND + dy - 26
            for r in range(1, 5):
                for q in range(16):
                    th = TAU * q / 16; put(F, nx + r * math.cos(th), ny + r * math.sin(th), hexc('#ff4a5a'), rud_glow * 0.5 * (1 - r / 5))

def scene(F, t):
    i = seg_of(t); a, p = loc(t, i)
    big_x, big_y = 74, GROUND + 4
    if i <= 1:                                          # hook: Rudolph, big, right away
        step = 0
        draw_deer(F, big_x, big_y, scale=1.55, antlers=1.0, nose='red', eye='happy' if (t % 3.1) > 0.15 else 'tired')
        sparkle(F, 136, 92, 0.7 + 0.3 * math.sin(t * 6))
        if i == 0 and t > 0.4: bk.label(F, 'GIRL', 720, 330, int(118 * S), int(100 * S), px=6)
        if i == 1:
            fl = 0.5 + 0.5 * math.sin(t * 10)
            for sx, sy in ((128, 66), (140, 72), (118, 74)): sparkle(F, sx, sy, fl)
            bk.label(F, 'ANTLERS', 640, 230, int(130 * S), int(70 * S), px=6)
            bk.arrow(F, int(96 * S), int(52 * S))
    elif i in (2, 3):                                   # boy vs girl through the winter
        months = ['NOVEMBER', 'DECEMBER'] if i == 2 else ['DECEMBER', 'JANUARY', 'FEBRUARY', 'MARCH']
        mi = min(len(months) - 1, int(p * len(months)))
        calendar(F, months[mi])
        drop_t = SEG[2][0] + (SEG[2][1] - SEG[2][0]) * 0.55
        boy_ant = 1.0 if t < drop_t else 0.0
        boy_eye = 'shock' if 0 <= t - drop_t < 1.2 else 'open'
        draw_deer(F, 54, GROUND, scale=0.95, antlers=boy_ant, eye=boy_eye)
        draw_deer(F, 122, GROUND, scale=0.95, antlers=1.0, eye='happy' if i == 3 else 'open')
        if t >= drop_t:
            a2 = t - drop_t
            fall = min(1.0, a2 / 0.5); bounce = 4 * abs(math.sin(min(a2, 1.2) * 8)) * math.exp(-a2 * 4) if a2 > 0.5 else 0
            loose_antler(F, 62 + 10 * fall, lerp(GROUND - 52, GROUND - 6, fall ** 2) - bounce, fall * 2.6)
        bk.label(F, 'BOY', 140, 560, int(48 * S), int((GROUND - 46) * S), px=6)
        bk.label(F, 'GIRL', 800, 560, int(124 * S), int((GROUND - 46) * S), px=6)
        if i == 3:
            for sx, sy in ((132, 100), (140, 106)): sparkle(F, sx, sy, 0.5 + 0.5 * math.sin(t * 7 + sx))
    elif i in (4, 5):                                   # the sleigh team: count the girls
        team(F, t, 1.0, rud_glow=0.7 if i == 5 else 0)
        n = 9 if i == 5 else min(9, int(p * 10))
        counter(F, f'GIRLS: {n} / 9', colr=(255, 200, 58) if n == 9 else (225, 235, 255))
        if i == 5 and a > 0.8: bk.label(F, 'RUDOLPH', 720, 470, int(152 * S), int((GROUND - 24) * S), px=6)
    elif i == 6:                                        # what if... they were boys: antlers pop off
        base = SEG[6][0] + 0.6; span = max(1.0, (SEG[6][1] - SEG[6][0]) - 0.6)
        pops = [base + span * k / 9 for k in (0, 4, 8, 2, 6, 1, 5, 3, 7)]
        team(F, t, 1.0, pop_times=pops, eye='shock')
        bk.tag(F, 'WHAT IF?', 410, 230, px=7)
    elif i == 7:                                        # nine reindeer, zero antlers
        team(F, t, 0.0, eye='open')
        counter(F, 'ANTLERS: 0', colr=(255, 200, 58))
    elif i == 8:                                        # exhausted: the fight, then the weight drop
        if p < 0.45:
            k_ = p / 0.45; gap = 18 - 14 * abs(math.sin(k_ * math.pi * 3))
            draw_deer(F, 90 - gap - 26, GROUND, scale=0.95, antlers=1.0, eye='shock')
            col, M, (ox, oy) = reindeer(scale=0.95, antlers=1.0, eye='shock'); col, M = col[:, ::-1], M[:, ::-1]
            pv.blit_hr(F, col, M, 90 + gap + 26 - (M.shape[1] - ox), GROUND - oy, 1)
            if gap < 7:
                for q in range(8): put(F, 90 + 6 * math.cos(q), GROUND - 46 + 6 * math.sin(q), hexc('#ffe27a'))
            bk.tag(F, 'FIGHTING SEASON', 300, 230, px=6)
        else:
            k_ = smooth((p - 0.45) / 0.4)
            draw_deer(F, 90, GROUND, scale=1.15, antlers=0.0, eye='tired', thin=k_)
            sweat(F, 118, 70, 1.0)
            pct = int(round(100 - 25 * k_)); bar_w = int(500 * pct / 100)
            F[240:290, 290:790] = hexc('#0a1430'); F[244:286, 294:294 + bar_w - 8] = hexc('#ff6a5a') if k_ > 0.5 else hexc('#7ed37a')
            bk.pixel_text(F, f'WEIGHT: {pct}%', 330, 180, px=7, colr=(225, 235, 255))
            if k_ > 0.9: bk.pixel_text(F, '-25%', 820, 245, px=7, colr=(255, 106, 90))
    elif i == 9:                                        # Santa would never make it
        team(F, t, 0.0, eye='tired', thin=1.0, bob=False, sink=6 * smooth(p), wobble=0.06)
        for k in range(3): sweat(F, TEAM[k][0] + 14, GROUND + TEAM[k][1] - 30, 0.8)
        counter(F, 'SPEED: 0 MPH', colr=(255, 106, 90))
    elif i == 10:                                       # unless... teenage boys
        draw_deer(F, 58, GROUND, scale=0.95, antlers=0.0, eye='tired', thin=1.0)
        draw_deer(F, 124, GROUND, scale=0.8, antlers=1.0, young=True, eye='happy', step=(t * 1.5) % 1 if p < 0.3 else 0)
        bk.label(F, 'ADULT BOY', 60, 560, int(48 * S), int((GROUND - 40) * S), px=6)
        bk.label(F, 'TEEN BOY', 700, 560, int(128 * S), int((GROUND - 38) * S), px=6)
    else:                                               # Rudolph, definitely a girl
        draw_deer(F, big_x, big_y, scale=1.55, antlers=1.0, nose='red', eye='happy')
        nx, ny = big_x + 40, big_y - 54
        g = 0.6 + 0.4 * math.sin(t * 5)
        for r in range(2, 9):
            for q in range(24):
                th = TAU * q / 24; put(F, nx + r * math.cos(th), ny + r * math.sin(th), hexc('#ff4a5a'), g * 0.35 * (1 - r / 9))
        bk.label(F, 'GIRL', 720, 330, int(118 * S), int(100 * S), px=6)
        for hx, ph in ((40, 0), (150, 1.3), (60, 2.1)):
            hy = 60 - ((t * 14 + ph * 20) % 50)
            put(F, hx, hy, hexc('#ff4f7a')); put(F, hx + 1, hy, hexc('#ff4f7a')); put(F, hx, hy + 1, hexc('#ff4f7a')); put(F, hx + 1, hy + 1, hexc('#ff4f7a'))

# ---------------- snow + captions ----------------
rng = np.random.default_rng(3)
FLAKES = [(rng.uniform(0, W), rng.uniform(0, 1), rng.uniform(10, 22), rng.uniform(0, 6.28)) for _ in range(46)]
def snow(F, t):
    for x0, ph0, sp, ph in FLAKES:
        y = ((t * sp / H + ph0) % 1.0) * (H + 10) - 5
        put(F, (x0 + 4 * math.sin(t * 0.8 + ph)) % W, y, np.array([0.9, 0.95, 1.0]), 0.45)
HEADPHONES = ["0011111100", "0100000010", "1000000001", "1000000001", "1110000111", "1110000111", "1110000111", "0110000110"]
def caption_sprite(line, hl):
    size = 82
    while True:
        font = ImageFont.truetype(bk.FONT_BOLD, size); d = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
        words = line.split(' '); sp = int(size * 0.27); wd = [d.textlength(w_, font=font) for w_ in words]
        if sum(wd) + sp * (len(words) - 1) < WF - 90 or size < 50: break
        size -= 4
    img = Image.new('RGBA', (WF, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    x = (WF - (sum(wd) + sp * (len(words) - 1))) / 2
    for w_, ww in zip(words, wd):
        colr = bk.YELLOW if w_.strip(".,!?:-'…").upper() in hl or w_.strip(".,!?:-'…").upper().replace("'S", '') in hl else bk.WHITE
        d.text((x + 5, 18), w_, font=font, fill=(6, 10, 24, 255), stroke_width=7, stroke_fill=(6, 10, 24, 255))
        d.text((x, 11), w_, font=font, fill=colr + (255,), stroke_width=7, stroke_fill=(8, 14, 30, 255))
        x += ww + sp
    return np.asarray(img).astype(np.float32) / 255
CAPS = []
for (txt, chunks, hl), (a, b) in zip(LINES, SEG):
    words = [len(c.split()) for c in chunks]; tot = sum(words); t0 = a
    for c, nw in zip(chunks, words):
        t1 = t0 + (b - a) * nw / tot
        CAPS.append((t0, t1, caption_sprite(c, set(hl))))
        t0 = t1
def captions(F, t):
    for a, b, spr in CAPS:
        if a <= t < b:
            dy = int(10 * (1 - min(1.0, (t - a) / 0.08)))
            h_ = spr.shape[0]; A = spr[..., 3:4]
            F[CAP_Y + dy:CAP_Y + dy + h_] = F[CAP_Y + dy:CAP_Y + dy + h_] * (1 - A) + spr[..., :3] * A
    if t < SEG[0][1] + 0.4:                                     # headphones icon under the first caption
        y0 = CAP_Y + 140; x0 = WF // 2 - 35
        for r_, row in enumerate(HEADPHONES):
            for c_, bb in enumerate(row):
                if bb == '1': F[y0 + r_ * 7:y0 + r_ * 7 + 7, x0 + c_ * 7:x0 + c_ * 7 + 7] = 1.0

def frame(t):
    F = base_frame()
    scene(F, t); snow(F, t)
    i = seg_of(t)
    if i >= 1 and 0 <= t - SEG[i][0] < 0.12 and i in (2, 4, 6, 8, 10, 11):        # quick pixel wipe on scene changes
        m = HR_BAYER < (1 - (t - SEG[i][0]) / 0.12) * 0.7; F[m] = F[m] * 0.4 + hexc('#f4fbff') * 0.6
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
