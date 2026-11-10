"""Renders 'What If You Dropped a Candy Cane on Every World?' - 1080x1920 / 60 fps pixel art.

Four world panels (Earth, Moon, Mars, Jupiter). Each candy cane bounces with its world's real
gravity, and each landing is a beat; the Jingle Bells chorus lights a string of Christmas lights.
Style: chunky 6x pixels, flat shades, black outlines, 4-shade curved backgrounds.

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

# ================================================================ helpers
def dilate(m):
    p = np.pad(m, 1)
    return m | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
INK = hexc('#06070e')
def smooth(s): s = min(1.0, max(0.0, s)); return s * s * (3 - 2 * s)
def last_age(hits, t):
    i = int(np.searchsorted(hits, t, side='right') - 1)
    return t - hits[i] if i >= 0 else 99.0
def put(F, x, y, col, a=1.0):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H: F[y, x] = F[y, x] * (1 - a) + col * a

def curved_bands(shades, y0, y1, n_curves, seed):
    """4-shade recipe: light top -> dark bottom, smooth curves, wide dithered blends"""
    r = np.random.default_rng(seed)
    span = y1 - y0
    v = np.zeros((H, W))
    for k in range(n_curves):
        cy = y0 + span * (k + 1) / (n_curves + 1)
        cv = cy + span * 0.07 * np.sin(XX / r.uniform(26, 34) + r.uniform(0, 6)) + span * 0.03 * np.sin(XX / r.uniform(13, 19) + r.uniform(0, 6))
        v = v + np.clip((YY - cv) / (span * 0.09) + 0.5, 0, 1)
    return shades[np.clip(np.floor(v + BAYER[YY % 4, XX % 4]), 0, len(shades) - 1).astype(int)]

# ================================================================ full-screen worlds (one at a time)
GY = 268                                  # ground line
PX_PER_M = 180
LOOK = {
    'earth':   dict(sky=pal('#2b3f6e', '#22345e', '#1a2a4e', '#132040'), gnd=pal('#eef5ff', '#cfe0f4', '#a9c3e4', '#86a5d0'), name='EARTH'),
    'moon':    dict(sky=pal('#1d1c2a', '#171622', '#11111a', '#0b0b12'), gnd=pal('#c9c6c0', '#a6a29c', '#85827d', '#64625e'), name='MOON'),
    'mars':    dict(sky=pal('#e0a070', '#cc8a5c', '#b4744c', '#9a5e3e'), gnd=pal('#e0784a', '#c45e36', '#a24a2a', '#7e3820'), name='MARS'),
    'jupiter': dict(sky=pal('#f0c890', '#e2ae74', '#d0945c', '#b87a48'), gnd=pal('#8a5a3a', '#76492e', '#613a24', '#4c2c1a'), name='JUPITER'),
}
CX = 90
def text_sprite(text, sc=1, pad=2):
    tm = text_mask(text, sc); th, tw = tm.shape
    out = np.zeros((th + 2 * pad, tw + 2 * pad, 4), np.float32); out[..., 3] = 1
    bh, bw = out.shape[:2]
    for cy, cx in ((0, 0), (0, bw - 1), (bh - 1, 0), (bh - 1, bw - 1)): out[cy, cx, 3] = 0
    out[pad:pad + th, pad:pad + tw][tm] = [1, 1, 1, 1]
    return out
def blit(F, spr, x, y, alpha=1.0):
    h, w_ = spr.shape[:2]; a = spr[..., 3:4] * alpha
    F[y:y + h, x:x + w_] = F[y:y + h, x:x + w_] * (1 - a) + spr[..., :3] * a

def curved_bands(shades, y0, y1, n_curves, seed):
    r = np.random.default_rng(seed); span = y1 - y0; v = np.zeros((H, W))
    for k in range(n_curves):
        cy = y0 + span * (k + 1) / (n_curves + 1)
        cv = cy + span * 0.05 * np.sin(XX / r.uniform(30, 40) + r.uniform(0, 6)) + span * 0.02 * np.sin(XX / r.uniform(15, 21) + r.uniform(0, 6))
        v = v + np.clip((YY - cv) / (span * 0.07) + 0.5, 0, 1)
    return shades[np.clip(np.floor(v + BAYER[YY % 4, XX % 4]), 0, len(shades) - 1).astype(int)]

def build_world(name):
    L = LOOK[name]; P = curved_bands(L['sky'], 0, GY, 3, len(name) * 13).astype(np.float32)
    gy = YY - GY
    gv = np.clip(gy / (H - GY) * 3.2, 0, 3)
    gmask = YY >= GY + np.round(1.2 * np.sin(XX / 9 + len(name)))
    P[gmask] = L['gnd'][np.clip(np.floor(gv + BAYER[YY % 4, XX % 4] - 0.5), 0, 3).astype(int)][gmask]
    P[gmask & ~np.roll(gmask, 1, 0)] = np.minimum(1, L['gnd'][0] * 1.05)          # lit rim on the ground edge
    r = np.random.default_rng(len(name) * 7)
    if name == 'moon':
        for _ in range(7):
            cx, cw = r.uniform(8, 172), r.uniform(5, 11)
            for xx in range(int(cx - cw), int(cx + cw) + 1):
                if 0 <= xx < W: P[GY + 4, xx] = L['gnd'][3]; P[GY + 5, xx] = L['gnd'][1]
        ex, ey = 140, 104
        d = np.hypot(XX + 0.5 - ex, YY + 0.5 - ey)
        e = d <= 12
        P[e] = hexc('#2f7dff'); P[e & (np.sin(XX * 0.45) + np.cos(YY * 0.4) > 0.6)] = hexc('#3fcf6a')
        P[e & (XX < ex - 4)] = P[e & (XX < ex - 4)] * 0.55
        P[(d > 12) & (d <= 13)] = INK
    if name == 'mars':
        d = np.hypot(XX + 0.5 - 40, YY + 0.5 - 110); P[d <= 6] = hexc('#fff0d8'); P[(d > 6) & (d <= 7)] = hexc('#f0c8a0')
        for _ in range(5):
            rx = int(r.uniform(6, 168)); P[GY - 4:GY, rx:rx + 6] = L['gnd'][3]; P[GY - 4, rx:rx + 6] = INK
            P[GY - 4:GY, rx] = INK; P[GY - 4:GY, rx + 5] = INK
    if name == 'jupiter':
        for k, yy in enumerate(range(96, GY - 10, 22)):
            band = (YY >= yy + 3 * np.sin(XX / 17 + k)) & (YY < yy + 7 + 3 * np.sin(XX / 17 + k)) & (YY < GY)
            P[band] = (L['sky'][3] if k % 2 else hexc('#f6dcb4'))
        d = ((XX + 0.5 - 130) / 15) ** 2 + ((YY + 0.5 - 118) / 8) ** 2
        P[d <= 1] = hexc('#c8452e'); P[(d > 1) & (d <= 1.25)] = hexc('#9a3020')
        P[(YY >= GY) & (YY < GY + 1)] = hexc('#ffe6b0')
    if name == 'earth':
        for (tx, th_) in ((26, 34), (160, 26)):
            for k in range(th_):
                hw = 1 + k * 0.42
                for xx in range(int(tx - hw), int(tx + hw) + 1):
                    if 0 <= xx < W: P[GY - th_ + k, xx] = hexc('#1f6a3a') if (xx + k) % 6 else hexc('#eef5ff')
            P[GY - 3:GY, tx - 1:tx + 2] = hexc('#4a2c1c'); P[GY - th_ - 1, tx] = hexc('#ffd84a')
    return P
WORLD_IMG = {n: build_world(n) for n in WORLDS}

# which world the camera looks at. 'fall': a new cane falls from the sky and the camera follows it
# down onto the next world (ends exactly at that cane's release). 'fade': a soft pixel fade.
ORDER = ['earth', 'moon', 'mars', 'jupiter']
def release(n): return WORLDS[n]['first'] - WORLDS[n]['period'] / 2
SCENES = [(0.0, 'earth', None), (4.2, 'moon', 'fall'), (9.2, 'mars', 'fall'), (13.1, 'jupiter', 'fall'),
          (17.75, 'earth', 'fade'), (21.75, 'moon', 'fade'), (25.75, 'mars', 'fade'), (29.75, 'jupiter', 'fade'), (33.75, 'earth', 'fade')]
FADE = 0.5
def view(t):
    k = max(i for i, sc in enumerate(SCENES) if t >= sc[0])
    ts, name, kind = SCENES[k]
    if kind is None: return name, None, 0.0, None
    dur = (release(name) - ts) if kind == 'fall' else FADE
    s_ = (t - ts) / dur
    if s_ >= 1: return name, None, 0.0, None
    return SCENES[k - 1][1], name, s_, kind

# ================================================================ candy cane (distance-field sprite, rotatable)
def cane_path():
    pts = [(0.0, -k * 0.25) for k in range(0, 65)]                       # straight stick, 16 px
    cx, cy, r = 3.6, -16.0, 3.6
    for k in range(1, 50):
        a = math.pi - k * (math.pi + 0.6) / 49
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    pts = np.array(pts)
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    tan = np.gradient(pts, axis=0); tan /= np.linalg.norm(tan, axis=1, keepdims=True)
    return pts, s, tan
CP, CS, CT = cane_path()
RED, RED_D, RED_L = hexc('#e8283c'), hexc('#a0142a'), hexc('#ff6a78')
WHT, WHT_D = hexc('#fff6f2'), hexc('#d6cbd6')
LDIR = np.array([-0.7, -0.7])

CSC = 2.0
def draw_cane(F, bx, by, ang, sq=1.0, mode=('on',), seed=0):
    """bx,by = bottom tip on screen; ang = tilt (rad) around the tip; sq = vertical squash"""
    ca, sa = math.cos(ang), math.sin(ang)
    P = CP.copy() * CSC; P[:, 1] *= sq
    PX = bx + P[:, 0] * ca - P[:, 1] * sa; PY = by + P[:, 0] * sa + P[:, 1] * ca
    T = np.stack([CT[:, 0] * ca - CT[:, 1] * sa, CT[:, 0] * sa + CT[:, 1] * ca], 1)
    x0, x1 = int(PX.min()) - 4, int(PX.max()) + 5; y0, y1 = int(PY.min()) - 4, int(PY.max()) + 5
    yy, xx = np.mgrid[y0:y1, x0:x1]
    dx = xx[..., None] + 0.5 - PX; dy = yy[..., None] + 0.5 - PY
    d2 = dx * dx + dy * dy; i = np.argmin(d2, axis=-1); d = np.sqrt(np.take_along_axis(d2, i[..., None], -1)[..., 0])
    R = 1.9 * CSC
    inside = d <= R
    side = (T[i, 0] * np.take_along_axis(dy, i[..., None], -1)[..., 0] - T[i, 1] * np.take_along_axis(dx, i[..., None], -1)[..., 0])
    nrm_x, nrm_y = -T[i, 1], T[i, 0]
    lit = (nrm_x * LDIR[0] + nrm_y * LDIR[1]) * np.sign(side + 1e-6)
    stripe = (np.floor((CS[i] * CSC + side * 1.3) / (2.6 * CSC)) % 2) == 0
    col = np.where(stripe[..., None], np.where((lit > 0.3)[..., None] & (np.abs(side) > 0.7 * CSC)[..., None], RED_L, np.where((lit < -0.3)[..., None] & (np.abs(side) > 0.7 * CSC)[..., None], RED_D, RED)),
                   np.where((lit < -0.3)[..., None] & (np.abs(side) > 0.7 * CSC)[..., None], WHT_D, WHT))
    ring = dilate(inside) & ~inside
    if mode[0] != 'on':
        ys, xs = np.nonzero(inside); cc = col[ys, xs]; ys = ys + y0; xs = xs + x0
        rr = np.random.default_rng(seed); n = len(ys)
        ang_ = rr.uniform(0, TAU, n); dist = rr.uniform(8, 30, n); lag = rr.uniform(0, 0.35, n)
        if mode[0] == 'form':
            s_ = np.clip((mode[1] - lag) / (1 - lag), 0, 1); e = (1 - s_) ** 2
            px, py = xs + np.cos(ang_) * dist * e, ys + np.sin(ang_) * dist * e
            cc = cc * s_[:, None] + np.array([1.0, 0.95, 0.9]) * (1 - s_[:, None])
        else:
            s_ = np.clip((mode[1] - lag * 0.5) / (1 - lag * 0.5), 0, 1); e = s_ ** 0.7
            px, py = xs + np.cos(ang_) * dist * e * 1.5, ys + np.sin(ang_) * dist * e * 1.5 - 6 * s_
            cc = cc * (1 - s_[:, None]) + np.array([1.0, 0.95, 0.85]) * s_[:, None]
            keep = np.random.default_rng(seed + 1).random(n) > s_; px, py, cc = px[keep], py[keep], cc[keep]
        xi, yi = np.round(px).astype(int), np.round(py).astype(int)
        ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H); F[yi[ok], xi[ok]] = cc[ok]; return
    for m, cv in ((ring, INK), (inside, None)):
        ys, xs = np.nonzero(m); Y, X = ys + y0, xs + x0
        ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
        F[Y[ok], X[ok]] = INK if cv is not None else col[ys[ok], xs[ok]]

def cane_state(name, t):
    w_ = WORLDS[name]; hits, T = w_['hits'], w_['period']
    g = GY; hpx = w_['h'] * PX_PER_M
    release = hits[0] - T / 2
    pop = POP[name]
    if name == 'earth':
        if t >= REFORM: return g - hpx, 0, 1, ('form', min(1, (t - REFORM) / 0.5))
        if t < release: return g - hpx + 1.0 * math.sin(t * 5), 0, 1, ('on',)
    else:
        if t < release: return None                       # still falling in with the camera (see frame)
    if t >= pop + 0.8: return None
    if t >= hits[-1]:
        hov = g - hpx * min(1, (t - hits[-1]) / (T / 2)) ** 0.5
        return (hov, 0, 1, ('on',)) if t < pop else (hov, 0, 1, ('pop', (t - pop) / 0.8))
    u = (t - hits[0]) / T; f = u - math.floor(u)
    y = g - hpx * 4 * f * (1 - f)
    age = f * T
    k = max(0.0, 1 - min(f, 1 - f) * T / 0.05)
    tilt = 0.22 * math.sin(age * 28) * math.exp(-age / 0.12) * (1 if (int(u) % 2) else -1)
    return y, tilt, 1 - 0.18 * k, ('on',)

def draw_impact(F, name, t):
    w_ = WORLDS[name]; age = last_age(w_['hits'], t); g = GY
    if age > 0.5 or t > w_['hits'][-1] + 0.5 or t < w_['first']: return
    gl = LOOK[name]['gnd']; a = math.exp(-age / 0.12)
    for yy in range(g, g + 10):                     # the ground lights up under the impact
        for xx in range(CX - 30, CX + 31):
            fall = a * (1 - abs(xx - CX) / 31) * (1 - (yy - g) / 10)
            if fall > BAYER[yy % 4, xx % 4]: F[yy, xx] = np.minimum(1, F[yy, xx] * 0.6 + gl[0] * 0.5 + 0.12)
    r = np.random.default_rng(int(t / max(w_['period'], 0.25)) + len(name))
    n, spd = {'earth': (10, 40), 'moon': (14, 22), 'mars': (10, 32), 'jupiter': (8, 18)}[name]
    grav = {'earth': 160, 'moon': 30, 'mars': 70, 'jupiter': 400}[name]   # dust falls back with each world's gravity
    for k in range(n):
        vx = (r.random() - 0.5) * spd * 2; vy = -r.random() * spd - 6
        px = CX + vx * age; py = g - 1 + vy * age + grav * age * age
        if py <= g:
            put(F, px, py, gl[0], 1 - age / 0.5); put(F, px + 1, py, gl[1], 0.7 * (1 - age / 0.5))

# ================================================================ Christmas lights across the top (one bulb per melody note)
MEL_T = [m[0] for m in MELODY]; NB = len(MEL_T)
BULB_X = [10 + i * (160 / (NB - 1)) for i in range(NB)]
def wire_y(x): return 10 + 6 * (1 - ((x - 90) / 84) ** 2)
BCOL = [hexc(c) for c in ('#ff3b4e', '#3fe07a', '#ffd23a', '#4aa8ff')]
def draw_lights(F, t):
    for x in range(8, 173):
        put(F, x, wire_y(x), hexc('#1d4a2c'))
    flash = math.exp(-(t - LIGHTS_FLASH) / 0.35) if t >= LIGHTS_FLASH else 0
    off = t >= LIGHTS_FLASH + 0.9
    for i, (x, mt) in enumerate(zip(BULB_X, MEL_T)):
        y = int(round(wire_y(x))) + 1; c = BCOL[i % 4]
        on = (mt <= t) and not off
        a = t - mt
        b = (1.0 + 1.2 * math.exp(-a / 0.15) if on else 0.28) + flash
        put(F, x, y, hexc('#2a2f3a'))                                  # cap
        for dy in (1, 2, 3):
            put(F, x, y + dy, np.minimum(1, c * min(1.0, b) + (0.35 * (b - 1) if b > 1 else 0)))
        put(F, x - 1, y + 2, INK); put(F, x + 1, y + 2, INK); put(F, x, y + 4, INK)
        if on or flash > 0.05:
            gb = min(1.0, (0.35 + 0.65 * math.exp(-max(a, 0) / 0.2)) if on else 0) + flash
            for dx, dy in ((-2, 2), (2, 2), (0, 5), (-1, 4), (1, 4), (-2, 1), (2, 1)):
                if gb * 0.6 > BAYER[(y + dy) % 4, int(x + dx) % 4]: put(F, x + dx, y + dy, c, 0.55)
            if on and a < 0.35:                                         # sparkle when the note hits
                for k in range(2, 2 + int(5 * (1 - a / 0.35)) + 1):
                    for ddx, ddy in ((k, 2), (-k, 2), (0, 2 + k + 1)):
                        put(F, x + ddx, y + ddy, np.array([1, 1, 0.9]), 0.8 * (1 - a / 0.35))

# ================================================================ captions (plain, near the top) + headphones on the title
HEADPHONES = ["0011111100", "0100000010", "1000000001", "1000000001", "1110000111", "1110000111", "1110000111", "0110000110"]
def caption_sprite(text, icon=False, sc=1, pad=3):
    out = text_sprite(text, sc, pad)
    if icon:
        g = np.array([[c_ == '1' for c_ in r] for r in HEADPHONES])
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
        self.s = caption_sprite(text, icon); h, w_ = self.s.shape[:2]
        self.x, self.y, self.t_in, self.t_out = (W - w_) // 2, y, t_in, t_out
        r = np.random.default_rng(seed); self.yy, self.xx = np.mgrid[0:h, 0:w_]
        self.vis = self.s[..., 3] > 0
        self.t_app = 0.07 * r.random((h, w_))
        self.t_dis = 0.06 + 0.5 * (0.55 * r.random((h, w_)) + 0.45 * (self.xx / w_))
        self.dx = (r.random((h, w_)) - 0.25) * 12; self.dy = -(5 + r.random((h, w_)) * 10)
    def draw(self, F, t):
        for tt in (t, t + LOOP, t - LOOP):
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
cap("WHAT IF YOU DROPPED A\nCANDY CANE ON\nEVERY WORLD?", 37.4, 39.75, icon=True)
cap("ON EARTH, IT BOUNCES\nTO THE BEAT", 2.2, 3.9)
cap("ON THE MOON, GRAVITY\nIS WEAK... IT FLOATS", 5.0, 8.7)
cap("MARS PULLS HARDER\nTHAN THE MOON", 10.0, 12.5)
cap("IF JUPITER HAD A FLOOR,\nIT WOULD SLAM DOWN!", 14.0, 17.2)
cap("AND THE LIGHTS\nSING ALONG", 18.4, 21.5)
cap("STRONGER GRAVITY,\nFASTER BOUNCE", 26.4, 29.4)
cap("SO THE STRONGER THE\nGRAVITY, THE FASTER\nIT BOUNCES", 34.4, 36.85)

# ================================================================ living pixels
rng = np.random.default_rng(21)
SNOW = [(rng.uniform(0, W), rng.uniform(0, 1), int(rng.integers(3, 7)), rng.uniform(0, 6.28)) for _ in range(40)]
MSTARS = [(rng.uniform(0, W), rng.uniform(4, 240), int(rng.integers(2, 9)), rng.uniform(0, 6.28)) for _ in range(40)]
DUST = [(rng.uniform(0, W), rng.uniform(60, 260), int(rng.integers(1, 4)), rng.uniform(0, 6.28)) for _ in range(18)]
ESTARS = [(rng.uniform(0, W), rng.uniform(4, 200), int(rng.integers(2, 9)), rng.uniform(0, 6.28)) for _ in range(22)]
def w(k): return TAU * k / LOOP
def ambient(F, name, t):
    if name == 'earth':
        for x, y, k, ph in ESTARS: put(F, x, y, hexc('#c8d8ff'), 0.15 + 0.5 * (0.5 + 0.5 * math.sin(w(k) * t + ph)))
        for x0, ph0, n, ph in SNOW:                   # snow falls in from the top and settles on the ground
            cyc = LOOP / n; tau = ((t / cyc + ph0) % 1.0) * cyc; fall = (GY + 6) / 30.0
            if tau < fall:
                x, y = x0 + 3 * math.sin(tau * 1.6 + ph), -6 + 30 * tau
                put(F, x, y, np.array([0.95, 0.97, 1.0])); put(F, x + 1, y, np.array([0.9, 0.94, 1.0]), 0.6)
            elif tau < fall + 1.4: put(F, x0 + 3 * math.sin(fall * 1.6 + ph), GY, np.array([1, 1, 1]), 0.9 * (1 - (tau - fall) / 1.4))
    if name == 'moon':
        for x, y, k, ph in MSTARS: put(F, x, y, np.array([0.92, 0.92, 1.0]), 0.2 + 0.7 * (0.5 + 0.5 * math.sin(w(k) * t + ph)))
    if name == 'mars':
        for x, y, k, ph in DUST: put(F, x + 3 * math.sin(w(k * 3) * t + ph), y + 3 * math.cos(w(k * 2) * t + ph), hexc('#ffd8b0'), 0.7)
    tick = int(t * 20) % int(LOOP * 20)              # a few background pixels swap with a neighbour, in place
    r = np.random.default_rng(tick + 1000); n = 220
    ys = r.integers(40, GY - 2, n); xs = r.integers(1, W - 1, n); d = r.integers(0, 4, n)
    ys2 = ys + np.array([0, 0, 1, -1])[d]; xs2 = xs + np.array([1, -1, 0, 0])[d]
    a_, b_ = F[ys, xs].copy(), F[ys2, xs2].copy(); F[ys, xs] = b_; F[ys2, xs2] = a_

def world_frame(name, t, cane=True):
    F = WORLD_IMG[name].copy()
    ambient(F, name, t)
    draw_impact(F, name, t)
    st = cane_state(name, t) if cane else None
    if st is not None:
        y, tilt, sq, mode = st
        if mode[0] == 'on':                                       # shadow shrinks as the cane rises
            hgt = GY - y; sw = max(1, int(8 - hgt / 22))
            for xx in range(CX - sw, CX + sw + 1):
                put(F, xx, GY + 1, INK, 0.35); put(F, xx, GY + 2, INK, 0.2)
        draw_cane(F, CX - 4, y, tilt, sq, mode, 7 + ORDER.index(name))
    return F

FULL_BAYER = BAYER[YY % 4, XX % 4]
def frame(t):
    cur, nxt, s_, kind = view(t)
    F = world_frame(cur, t, cane=(kind != 'fall'))
    if kind == 'fade':                                            # soft ordered-dither pixel fade
        G2 = world_frame(nxt, t); m = FULL_BAYER < smooth(s_)
        F[m] = G2[m]
    elif kind == 'fall':                                          # the cane drops out of this world; the camera follows it down
        e = smooth(s_); off = int(round(e * H))
        G2 = world_frame(nxt, t)
        if off > 0:
            # stack the two worlds and blend them across a soft, wavy, dithered band (no straight seam)
            stack = np.concatenate([F, G2], axis=0)           # world A above world B
            A_rows = np.clip(YY + off, 0, H - 1); B_rows = np.clip(YY + off - H, 0, H - 1)
            seam = (H - off) + 5 * np.sin(XX / 23 + 0.8) + 3 * np.sin(XX / 11 + 2.0)
            wgt = np.clip((YY - seam) / 40.0 + 0.5, 0, 1)
            wgt = np.where(YY + off >= H, np.maximum(wgt, (YY + off >= H + 20).astype(float)), wgt)
            wgt = np.where(YY + off < H - 20, np.minimum(wgt, 0.0), wgt)
            useB = FULL_BAYER < wgt
            F = np.where(useB[..., None], G2[B_rows, XX], F[A_rows, XX])
        drop = GY - WORLDS[nxt]['h'] * PX_PER_M
        ts = max(sc[0] for sc in SCENES if sc[0] <= t)
        y0 = cane_state(cur, ts)[0]                                 # where the cane was when it left
        y = y0 + (drop - y0) * s_ ** 1.6                            # speeds up as it falls
        draw_cane(F, CX - 4, y, 0.12 * math.sin(s_ * 9) * (1 - s_), 1, ('on',), 7 + ORDER.index(nxt))
    draw_lights(F, t)
    for c_ in CAPTIONS: c_.draw(F, t)
    return np.repeat(np.repeat((np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8), S, 0), S, 1)

if __name__ == '__main__':
    if sys.argv[1] == '--stills':
        from PIL import Image
        for ts in sys.argv[3:]: Image.fromarray(frame(float(ts))).save(f'{sys.argv[2]}/still_{float(ts):06.2f}.png')
        sys.exit()
    out, wav = sys.argv[1], sys.argv[2]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W*S}x{H*S}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(int(LOOP * FPS)):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 300 == 0: print('frame', f, flush=True)
    p.stdin.close(); p.wait(); print('done', out)
