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

# ================================================================ page background (style study recipe)
PAGE = curved_bands(pal('#182a48', '#13223b', '#0e1a2e', '#091221'), 0, H, 3, 1).astype(np.float32)

# ================================================================ the four world panels
PANELS = {'earth': (6, 96, 88, 204), 'moon': (92, 96, 174, 204), 'mars': (6, 210, 88, 312), 'jupiter': (92, 210, 174, 312)}
GROUND = {'earth': 194, 'moon': 194, 'mars': 300, 'jupiter': 300}
PX_PER_M = 90
LOOK = {
    'earth':   dict(sky=pal('#2b3f6e', '#22345e', '#1a2a4e', '#132040'), gnd=pal('#eef5ff', '#cfe0f4', '#a9c3e4', '#86a5d0'), name='EARTH'),
    'moon':    dict(sky=pal('#1d1c2a', '#171622', '#11111a', '#0b0b12'), gnd=pal('#c9c6c0', '#a6a29c', '#85827d', '#64625e'), name='MOON'),
    'mars':    dict(sky=pal('#e0a070', '#cc8a5c', '#b4744c', '#9a5e3e'), gnd=pal('#e0784a', '#c45e36', '#a24a2a', '#7e3820'), name='MARS'),
    'jupiter': dict(sky=pal('#f0c890', '#e2ae74', '#d0945c', '#b87a48'), gnd=pal('#8a5a3a', '#76492e', '#613a24', '#4c2c1a'), name='JUPITER'),
}
FONT_SC = 1
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

def build_panel(name):
    x0, y0, x1, y1 = PANELS[name]; g = GROUND[name]; L = LOOK[name]
    P = np.zeros((H, W, 3), np.float32)
    sky = curved_bands(L['sky'], y0, g, 3, hash(name) % 97)
    P[:] = sky
    gy = YY - g
    gv = np.clip(gy / (y1 - g) * 3.2, 0, 3) + 0.35 * np.sin(XX / 7 + hash(name) % 5) * (gy < 3)
    gmask = YY >= g + np.round(0.8 * np.sin(XX / 6 + len(name)))
    P[gmask] = L['gnd'][np.clip(np.floor(gv + BAYER[YY % 4, XX % 4] - 0.5), 0, 3).astype(int)][gmask]
    r = np.random.default_rng(len(name) * 7)
    if name == 'moon':                     # craters, Earth in the black sky
        for _ in range(6):
            cx, cw = r.uniform(x0 + 6, x1 - 6), r.uniform(3, 6)
            for xx in range(int(cx - cw), int(cx + cw) + 1):
                P[g + 2, xx] = L['gnd'][3]; P[g + 3, xx] = L['gnd'][1]
        ex, ey = x1 - 16, y0 + 18
        d = np.hypot(XX + 0.5 - ex, YY + 0.5 - ey)
        P[d <= 6] = hexc('#2f7dff'); P[(d <= 6) & (np.sin(XX * 0.9) + np.cos(YY * 0.8) > 0.6)] = hexc('#3fcf6a')
        P[(d <= 6) & (XX < ex - 2)] = P[(d <= 6) & (XX < ex - 2)] * 0.55
        P[(d > 6) & (d <= 7)] = INK
    if name == 'mars':                     # small pale sun, rocks
        d = np.hypot(XX + 0.5 - (x0 + 18), YY + 0.5 - (y0 + 20)); P[d <= 3] = hexc('#fff0d8')
        for _ in range(4):
            rx = int(r.uniform(x0 + 6, x1 - 8)); P[g - 2:g, rx:rx + 3] = L['gnd'][3]; P[g - 2, rx:rx + 3] = INK
    if name == 'jupiter':                  # cloud bands + the great red spot in the sky
        for k, yy in enumerate(range(y0 + 10, g - 6, 12)):
            band = (YY >= yy + 2 * np.sin(XX / 11 + k)) & (YY < yy + 4 + 2 * np.sin(XX / 11 + k)) & (YY < g)
            P[band] = (L['sky'][3] if k % 2 else hexc('#f6dcb4'))
        d = ((XX + 0.5 - (x1 - 20)) / 7) ** 2 + ((YY + 0.5 - (y0 + 24)) / 4) ** 2
        P[d <= 1] = hexc('#c8452e'); P[(d > 1) & (d <= 1.4)] = hexc('#9a3020')
        P[(YY >= g) & (YY < g + 1)] = hexc('#ffe6b0')                       # the pretend floor's glossy edge
    if name == 'earth':                    # a little snowy pine
        for k in range(14):
            hw = 1 + k * 0.45
            for xx in range(int(x0 + 16 - hw), int(x0 + 16 + hw) + 1):
                P[g - 16 + k, xx] = hexc('#1f6a3a') if (xx + k) % 5 else hexc('#eef5ff')
        P[g - 2:g, x0 + 15:x0 + 17] = hexc('#4a2c1c'); P[g - 17, x0 + 16] = hexc('#ffd84a')
    m = np.zeros((H, W), bool); m[y0:y1, x0:x1] = True
    for cy, cx in ((y0, x0), (y0, x1 - 1), (y1 - 1, x0), (y1 - 1, x1 - 1)): m[cy, cx] = False
    return P, m
PANEL_IMG = {n: build_panel(n) for n in PANELS}
PANEL_SEED = {n: np.random.default_rng(i + 3).random((H, W)) for i, n in enumerate(PANELS)}
NAMES = {n: text_sprite(LOOK[n]['name']) for n in PANELS}

def panel_reveal(name, t):
    w_ = WORLDS[name]
    if name == 'earth': return 1.0
    t_in = w_['first'] - w_['period'] / 2 - FORM - 0.5
    t_out = POP[name] + 0.8                       # dissolve away after its cane pops, so the loop matches
    return min(1.0, max(0.0, (t - t_in) / 0.5), max(0.0, 1 - (t - t_out) / 0.5))

def draw_panel(F, name, t):
    a = panel_reveal(name, t)
    if a <= 0: return
    P, m = PANEL_IMG[name]
    show = m & (PANEL_SEED[name] < a)                 # pixel-dissolve in
    F[dilate(show) & ~show & ~dilate(dilate(m) & ~m) | (dilate(m) & ~m & (a >= 1))] = INK
    F[show] = P[show]
    x0, y0, x1, y1 = PANELS[name]
    if a >= 1: blit(F, NAMES[name], x0 + 3, y0 + 3)

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

def draw_cane(F, bx, by, ang, sq=1.0, mode=('on',), seed=0):
    """bx,by = bottom tip on screen; ang = tilt (rad) around the tip; sq = vertical squash"""
    ca, sa = math.cos(ang), math.sin(ang)
    P = CP.copy(); P[:, 1] *= sq
    PX = bx + P[:, 0] * ca - P[:, 1] * sa; PY = by + P[:, 0] * sa + P[:, 1] * ca
    T = np.stack([CT[:, 0] * ca - CT[:, 1] * sa, CT[:, 0] * sa + CT[:, 1] * ca], 1)
    x0, x1 = int(PX.min()) - 4, int(PX.max()) + 5; y0, y1 = int(PY.min()) - 4, int(PY.max()) + 5
    yy, xx = np.mgrid[y0:y1, x0:x1]
    dx = xx[..., None] + 0.5 - PX; dy = yy[..., None] + 0.5 - PY
    d2 = dx * dx + dy * dy; i = np.argmin(d2, axis=-1); d = np.sqrt(np.take_along_axis(d2, i[..., None], -1)[..., 0])
    R = 1.9
    inside = d <= R
    side = (T[i, 0] * np.take_along_axis(dy, i[..., None], -1)[..., 0] - T[i, 1] * np.take_along_axis(dx, i[..., None], -1)[..., 0])
    nrm_x, nrm_y = -T[i, 1], T[i, 0]
    lit = (nrm_x * LDIR[0] + nrm_y * LDIR[1]) * np.sign(side + 1e-6)
    stripe = (np.floor((CS[i] + side * 1.3) / 2.6) % 2) == 0
    col = np.where(stripe[..., None], np.where((lit > 0.3)[..., None] & (np.abs(side) > 0.7)[..., None], RED_L, np.where((lit < -0.3)[..., None] & (np.abs(side) > 0.7)[..., None], RED_D, RED)),
                   np.where((lit < -0.3)[..., None] & (np.abs(side) > 0.7)[..., None], WHT_D, WHT))
    ring = dilate(inside) & ~inside
    if mode[0] != 'on':
        ys, xs = np.nonzero(inside); cc = col[ys, xs]; ys = ys + y0; xs = xs + x0
        rr = np.random.default_rng(seed); n = len(ys)
        ang_ = rr.uniform(0, TAU, n); dist = rr.uniform(5, 18, n); lag = rr.uniform(0, 0.35, n)
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
    g = GROUND[name]; hpx = w_['h'] * PX_PER_M
    release = hits[0] - T / 2
    pop = POP[name]
    if name == 'earth':
        if t >= REFORM: return g - hpx, 0, 1, ('form', min(1, (t - REFORM) / 0.5))
        if t < release: return g - hpx + 1.0 * math.sin(t * 5), 0, 1, ('on',)
    else:
        if t < release - FORM: return None
        if t < release: return g - hpx, 0, 1, ('form', (t - (release - FORM)) / FORM)
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
    w_ = WORLDS[name]; age = last_age(w_['hits'], t); g = GROUND[name]
    x0, y0, x1, y1 = PANELS[name]; cx = (x0 + x1) / 2
    if age > 0.45 or panel_reveal(name, t) < 1 or t > w_['hits'][-1] + 0.45: return
    gl = LOOK[name]['gnd']
    # light reacts: ground under the cane brightens one shade, dithered, fading out
    a = math.exp(-age / 0.12)
    for yy in range(g, g + 6):
        for xx in range(int(cx - 14), int(cx + 15)):
            fall = a * (1 - abs(xx - cx) / 15) * (1 - (yy - g) / 6)
            if fall > BAYER[yy % 4, xx % 4]: F[yy, xx] = np.minimum(1, F[yy, xx] * 0.6 + gl[0] * 0.5 + 0.12)
    r = np.random.default_rng(int(t / max(w_['period'], 0.25)) + len(name))
    n, spd = {'earth': (6, 22), 'moon': (8, 12), 'mars': (6, 18), 'jupiter': (4, 10)}[name]
    grav = {'earth': 90, 'moon': 18, 'mars': 40, 'jupiter': 220}[name]          # dust falls back with each world's gravity
    for k in range(n):
        vx = (r.random() - 0.5) * spd * 2; vy = -r.random() * spd - 4
        px = cx + vx * age; py = g - 1 + vy * age + grav * age * age
        if py <= g: put(F, px, py, gl[0], 1 - age / 0.45)

# ================================================================ Christmas lights across the top (one bulb per melody note)
MEL_T = [m[0] for m in MELODY]; NB = len(MEL_T)
BULB_X = [10 + i * (160 / (NB - 1)) for i in range(NB)]
def wire_y(x): return 84 + 6 * (1 - ((x - 90) / 84) ** 2)
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
    def __init__(self, text, t_in, t_out, seed, icon=False, y=32):
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
cap("ON EARTH, IT BOUNCES\nTO THE BEAT", 2.3, 5.3)
cap("ON THE MOON, GRAVITY\nIS WEAK... IT FLOATS", 6.3, 9.3)
cap("MARS PULLS HARDER\nTHAN THE MOON", 10.4, 13.3)
cap("IF JUPITER HAD A FLOOR,\nIT WOULD SLAM DOWN!", 14.3, 17.3)
cap("AND THE LIGHTS\nSING ALONG", 18.4, 21.5)
cap("STRONGER GRAVITY,\nFASTER BOUNCE", 25.0, 28.5)
cap("SO THE STRONGER THE\nGRAVITY, THE FASTER\nIT BOUNCES", 34.4, 36.85)

# ================================================================ living pixels (background only)
rng = np.random.default_rng(21)
STARS = [(rng.uniform(0, W), rng.uniform(0, H), int(rng.integers(2, 9)), rng.uniform(0, 6.28)) for _ in range(45)]
SNOW = [(rng.uniform(8, 86), rng.uniform(0, 1), int(rng.integers(2, 5)), rng.uniform(0, 6.28)) for _ in range(22)]
MSTARS = [(rng.uniform(94, 172), rng.uniform(98, 190), int(rng.integers(2, 9)), rng.uniform(0, 6.28)) for _ in range(14)]
DUST = [(rng.uniform(8, 86), rng.uniform(214, 296), int(rng.integers(1, 4)), rng.uniform(0, 6.28)) for _ in range(12)]
def w(k): return TAU * k / LOOP
def ambient(F, t):
    for x, y, k, ph in STARS:
        b = 0.5 + 0.5 * math.sin(w(k) * t + ph)
        if not any(px0 <= x < px1 and py0 <= y < py1 for px0, py0, px1, py1 in PANELS.values()):
            put(F, x, y, hexc('#9fb6e0'), 0.15 + 0.6 * b)
    if panel_reveal('moon', t) >= 1:
        for x, y, k, ph in MSTARS:
            put(F, x, y, np.array([0.9, 0.9, 1.0]), 0.2 + 0.7 * (0.5 + 0.5 * math.sin(w(k) * t + ph)))
    for x0, ph0, n, ph in SNOW:                                         # snow falls into the Earth panel and settles
        cyc = LOOP / n; tau = ((t / cyc + ph0) % 1.0) * cyc; fall = 96 / 20.0
        if tau < fall: put(F, x0 + 2 * math.sin(tau * 2 + ph), 98 + 20 * tau, np.array([0.95, 0.97, 1.0]), 0.9)
        elif tau < fall + 1.2: put(F, x0 + 2 * math.sin(fall * 2 + ph), GROUND['earth'], np.array([1, 1, 1]), 0.9 * (1 - (tau - fall) / 1.2))
    if panel_reveal('mars', t) >= 1:
        for x, y, k, ph in DUST:
            put(F, x + 2 * math.sin(w(k * 3) * t + ph), y + 2 * math.cos(w(k * 2) * t + ph), hexc('#ffd0a0'), 0.6)
    tick = int(t * 20) % int(LOOP * 20)                                 # pixel swaps on the page background only
    r = np.random.default_rng(tick + 1000); n = 260
    ys = r.integers(1, H - 1, n); xs = r.integers(1, W - 1, n); d = r.integers(0, 4, n)
    ys2 = ys + np.array([0, 0, 1, -1])[d]; xs2 = xs + np.array([1, -1, 0, 0])[d]
    okm = ~(PAGE_MASK[ys, xs] | PAGE_MASK[ys2, xs2])
    ys, xs, ys2, xs2 = ys[okm], xs[okm], ys2[okm], xs2[okm]
    a_, b_ = F[ys, xs].copy(), F[ys2, xs2].copy(); F[ys, xs] = b_; F[ys2, xs2] = a_
PAGE_MASK = np.zeros((H, W), bool)
for px0, py0, px1, py1 in PANELS.values(): PAGE_MASK[py0 - 2:py1 + 2, px0 - 2:px1 + 2] = True
PAGE_MASK[24:100] = True

# ================================================================ frame
def frame(t):
    F = PAGE.copy()
    for n in PANELS: draw_panel(F, n, t)
    ambient(F, t)
    for i, n in enumerate(PANELS):
        if panel_reveal(n, t) < 1 and n != 'earth': continue
        draw_impact(F, n, t)
        st = cane_state(n, t)
        if st is None: continue
        y, tilt, sq, mode = st
        x0, y0, x1, y1 = PANELS[n]
        if mode[0] == 'on':                                             # soft shadow under the cane
            hgt = GROUND[n] - y; sw = max(1, int(4 - hgt / 25))
            for xx in range(int((x0 + x1) / 2 - sw), int((x0 + x1) / 2 + sw) + 1):
                put(F, xx, GROUND[n] + 1, INK, 0.35)
        draw_cane(F, (x0 + x1) / 2 - 1, y, tilt, sq, mode, 7 + i)
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
