"""Renders 'What If the Planets Played Christmas Music?' - 1080x1920 / 60 fps pixel art.

Planets circle the Sun on golden garland orbits hung with bells; each bell a planet passes
rings on the beat (closer to the Sun = faster). A comet plays Deck the Halls and every note
lights a star; the stars turn out to be a Christmas tree. Curved edges get soft in-between
pixels; nothing drifts - pixels twinkle in place and react to the Sun's light.

usage: python3 video.py out.mp4 audio.wav
       python3 video.py --stills DIR t1 t2 ...
"""
import sys, subprocess, math
import numpy as np
from score import *

W, H, S = 270, 480, 4
TAU = 2 * math.pi
def w(k): return TAU * k / LOOP  # loop-safe angular frequency

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
def pal(*c): return np.stack([hexc(x) for x in c])

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16
YY, XX = np.mgrid[0:H, 0:W]

def dith(v, p, bay):
    return p[np.clip(np.floor(v + bay), 0, len(p) - 1).astype(int)]

def smooth(s): s = min(1.0, max(0.0, s)); return s * s * (3 - 2 * s)

# ---- organic, tileable noise (blurred white noise on a torus: no straight lines anywhere)
def torus_noise(n, sigma, seed):
    r = np.random.default_rng(seed)
    f = np.fft.fftfreq(n)
    g = np.exp(-(f[:, None] ** 2 + f[None, :] ** 2) * (TAU * sigma) ** 2 / 2)
    z = np.real(np.fft.ifft2(np.fft.fft2(r.standard_normal((n, n))) * g))
    return ((z - z.min()) / (z.max() - z.min())).astype(np.float32)
NZ = torus_noise(256, 3.0, 99)      # fine grain
NZB = torus_noise(256, 14.0, 7)     # big soft blobs (cloud shadows)


# ---- primitives
def put(F, x, y, col, a=1.0):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        F[y, x] = F[y, x] * (1 - a) + col * a

def glow(F, x, y, col, a):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        F[y, x] = np.minimum(1, F[y, x] + col * a)

def blend(F, x, y, rgba, alpha=1.0):
    h, w_ = rgba.shape[:2]
    x0, y0 = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x0), max(0, -y0)
    ex, ey = min(w_, W - x0), min(h, H - y0)
    if ex <= sx0 or ey <= sy0: return
    src = rgba[sy0:ey, sx0:ex]
    a = src[..., 3:4] * alpha
    dst = F[y0 + sy0:y0 + ey, x0 + sx0:x0 + ex]
    dst[:] = dst * (1 - a) + src[..., :3] * a


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




# ================================================================== world layout
SUN = (135.0, 336.0)
TILT = 0.38                                                      # orbit ellipses seen from slightly above
ORB = {'mercury': 30, 'venus': 48, 'earth': 68, 'mars': 90, 'jupiter': 112}
PR = {'mercury': 6.0, 'venus': 8.0, 'earth': 9.5, 'mars': 7.0, 'jupiter': 16.0}
SPIN = {'mercury': 2, 'venus': 1, 'earth': 6, 'mars': 5, 'jupiter': 9, 'sun': 2}   # whole turns per loop

def theta(name, t):
    p = PLANETS[name]
    return math.pi / 2 + TAU * (t - p['first']) / p['period']
def pos(name, t):
    th = theta(name, t); r = ORB[name]
    return SUN[0] + r * math.cos(th), SUN[1] + r * TILT * math.sin(th), math.sin(th)

def present(name, t):
    """(mode, s): ('form', s) / ('on', 0) / ('burst', s) / None"""
    if name == 'earth': return ('on', 0)
    p = PLANETS[name]
    if t < p['first'] - FORM or t >= BURST[name] + 0.8: return None
    if t < p['first']: return ('form', (t - (p['first'] - FORM)) / FORM)
    if t >= BURST[name]: return ('burst', (t - BURST[name]) / 0.8)
    return ('on', 0)

def last_age(hits, t):
    i = int(np.searchsorted(hits, t, side='right') - 1)
    return t - hits[i] if i >= 0 else 99.0

# ================================================================== background (static values, no drift)
SPACE = pal('#080a22', '#0c0f2c', '#111436', '#171840', '#1f1b49', '#2a1f52', '#36225a')
def build_space():
    """4 shades, light at the top -> dark at the bottom, split by 3 smooth curves,
    each blended through a wide ordered-dither ramp (same recipe as the style study)."""
    shades = pal('#25204f', '#1d1a42', '#151434', '#0d0d25')
    curves = [128 + 15 * np.sin(XX / 50 + 0.7) + 6 * np.sin(XX / 27 + 2.1),
              250 + 18 * np.sin(XX / 55 + 2.4) + 7 * np.sin(XX / 31 + 0.3),
              372 + 16 * np.sin(XX / 52 + 4.0) + 6 * np.sin(XX / 25 + 1.2)]
    v = sum(np.clip((YY - cv) / 21.0 + 0.5, 0, 1) for cv in curves)
    return shades[np.clip(np.floor(v + BAYER[YY % 4, XX % 4]), 0, 3).astype(int)].astype(np.float32)
SPACEBG = build_space()
rng = np.random.default_rng(21)
BGSTARS = [(rng.uniform(0, W), rng.uniform(0, H), int(rng.integers(1, 9)), rng.uniform(0, 6.28), rng.random()) for _ in range(70)]

def draw_bgstars(F, t):
    for x, y, k, ph, br in BGSTARS:
        b = 0.5 + 0.5 * math.sin(w(k) * t + ph)
        c = np.array([0.85, 0.9, 1.0]) if br < 0.7 else (hexc('#ffd8a0') if br < 0.85 else hexc('#a8c8ff'))
        put(F, x, y, c, 0.25 + 0.6 * b * (0.5 + br * 0.5))
        if br > 0.93 and b > 0.7:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): glow(F, x + dx, y + dy, c, 0.25 * b)

# ================================================================== spheres with soft (anti-aliased) curved edges
SUB = np.array([0.25, 0.75])
def sphere(F, cx, cy, r, tex, L, spin, night=None, alpha=1.0, ret=False):
    x0, x1 = int(math.floor(cx - r - 1)), int(math.ceil(cx + r + 1))
    y0, y1 = int(math.floor(cy - r - 1)), int(math.ceil(cy + r + 1))
    yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    cov = np.zeros(yy.shape, np.float32)                         # 2x2 supersampled coverage
    for sy in SUB:
        for sx in SUB:
            cov += (((xx + sx - cx) ** 2 + (yy + sy - cy) ** 2) <= r * r) / 4
    m = cov > 0
    nx = np.clip((xx + 0.5 - cx) / r, -1, 1); ny = np.clip((yy + 0.5 - cy) / r, -1, 1)
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    lat = np.arcsin(np.clip(-ny, -1, 1)); lon = np.arctan2(nx, nz + 1e-6) + spin
    col = tex(lat, lon)
    shade = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1) if L is not None else np.ones_like(nx)
    lit = col * (0.30 + 0.95 * shade[..., None])
    if night is not None: lit = np.maximum(lit, night(lat, lon, shade))
    rim = np.clip(1 - nz, 0, 1) ** 3 * 0.25                       # thin atmosphere rim light
    lit = lit + rim[..., None] * shade[..., None] * np.array([0.6, 0.75, 1.0])
    q = np.floor(np.clip(lit, 0, 1) * 7 + (BAYER[yy % 4, xx % 4] - 0.5)[..., None]) / 7      # dithered to a pixel palette
    q = np.clip(q, 0, 1)
    if ret: return yy[m], xx[m], q[m], cov[m]
    ok = m & (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
    a = (cov[ok] * alpha)[:, None]                                # partial pixels on the curve = soft edge
    F[yy[ok], xx[ok]] = F[yy[ok], xx[ok]] * (1 - a) + q[ok] * a


# ---- clean pixel-art planets: a few flat shades per material, crisp light bands,
#      1px dark outline with a light rim on the sunlit side, simple solid features.
MW, MH = 96, 48
_ly, _lx = np.mgrid[0:MH, 0:MW]
LAT = (0.5 - (_ly + 0.5) / MH) * math.pi; LON = (_lx + 0.5) / MW * TAU

def smooth_mask(m, it=2):
    for _ in range(it):
        p = np.pad(m.astype(int), 1, mode='wrap')
        n = sum(p[1 + dy:1 + dy + MH, 1 + dx:1 + dx + MW] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
        m = n >= 5
    return m

def blobs(seed, thr, scale=2):
    z = NZB[(_ly * scale + seed) % 256, (_lx * scale + seed * 3) % 256]
    return smooth_mask(z > thr, 3)

def shades(*c): return pal(*c)
MAT = {   # material: 4 shades, dark -> light
    'ocean': shades('#0b2a6b', '#1650b8', '#2378ff', '#5aa8ff'),
    'land':  shades('#14532a', '#23863f', '#3fd46a', '#8ef0a0'),
    'ice':   shades('#6f8fbe', '#b4cdee', '#e6f0ff', '#ffffff'),
    'cloud': shades('#7f98c0', '#c4d6f0', '#eef4ff', '#ffffff'),
    'rock':  shades('#3a3634', '#6e6660', '#a89e94', '#ddd4c8'),
    'crat':  shades('#24201e', '#48423e', '#756c66', '#a49a90'),
    'vena':  shades('#7a4a14', '#c07a22', '#ffb84a', '#ffe0a0'),
    'venb':  shades('#8a5a1c', '#d8a040', '#ffd88a', '#fff4d4'),
    'mars':  shades('#5a1a0c', '#a8381c', '#ff6a32', '#ffa478'),
    'marsd': shades('#3e1208', '#7a2814', '#c0461e', '#e8703c'),
    'jupl':  shades('#7a4a2a', '#c8885a', '#ffd6a8', '#fff0dc'),
    'jupd':  shades('#4a2412', '#8a4a2a', '#d07a48', '#f0a070'),
    'spot':  shades('#5a120c', '#a8261a', '#ff4a32', '#ff8a6a'),
}
MATS = list(MAT); MI = {k: i for i, k in enumerate(MATS)}
MATP = np.stack([MAT[k] for k in MATS])            # (n_mat, 4, 3)

def map_earth():
    m = np.full((MH, MW), MI['ocean'])
    m[blobs(17, 0.55)] = MI['land']
    m[np.abs(LAT) > 1.12] = MI['ice']
    cl = smooth_mask((NZB[(_ly * 3 + 90) % 256, (_lx + 40) % 256] > 0.66) & (np.abs(LAT) < 1.0), 2)
    m[cl] = MI['cloud']
    return m
def map_mercury():
    m = np.full((MH, MW), MI['rock'])
    r = np.random.default_rng(3)
    for _ in range(9):
        cy, cx, rr = r.uniform(8, 40), r.uniform(0, MW), r.uniform(2.5, 5.5)
        d = np.hypot((_ly - cy), np.minimum(np.abs(_lx - cx), MW - np.abs(_lx - cx)) * 0.6)
        m[(d < rr) & (d > rr - 1.6)] = MI['crat']
    return m
def map_venus():
    b = np.sin(LAT * 6 + 0.5 * np.sin(LON * 2)) > 0.1
    return np.where(b, MI['venb'], MI['vena'])
def map_mars():
    m = np.full((MH, MW), MI['mars'])
    m[blobs(41, 0.6)] = MI['marsd']
    m[LAT > 1.2] = MI['ice']
    return m
def map_jupiter():
    edges = [-1.3, -0.95, -0.6, -0.3, -0.05, 0.25, 0.55, 0.9, 1.25]
    m = np.full((MH, MW), MI['jupl'])
    for k in range(0, len(edges) - 1, 2):
        wob = 0.03 * np.sin(LON * 3 + k)
        m[(LAT > edges[k] + wob) & (LAT < edges[k + 1] + wob)] = MI['jupd']
    sp = ((LAT + 0.42) / 0.14) ** 2 + ((np.angle(np.exp(1j * (LON - 2.0)))) / 0.42) ** 2 < 1
    m[sp] = MI['spot']
    return m
MAPS = {'earth': map_earth(), 'mercury': map_mercury(), 'venus': map_venus(), 'mars': map_mars(), 'jupiter': map_jupiter()}

def clean_planet(F, name, cx, cy, r, L, spin, ret=False):
    cx, cy = round(cx * 2) / 2, round(cy * 2) / 2
    R = int(math.ceil(r)) + 1
    yy, xx = np.mgrid[int(cy) - R:int(cy) + R + 1, int(cx) - R:int(cx) + R + 1]
    dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
    inside = dx * dx + dy * dy <= r * r
    nx, ny = dx / r, dy / r
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    lat = np.arcsin(np.clip(-ny, -1, 1)); lon = (np.arctan2(nx, nz + 1e-6) + spin) % TAU
    mat = MAPS[name][np.clip(((0.5 - lat / math.pi) * MH).astype(int), 0, MH - 1), (lon / TAU * MW).astype(int) % MW]
    d = nx * L[0] + ny * L[1] + nz * L[2]
    lvl = np.clip(np.floor((d * 0.9 + 0.55) * 3.2), 0, 3).astype(int)    # crisp light bands
    col = MATP[mat, lvl]
    # outline: inside pixels touching the outside
    p = np.pad(inside, 1)
    edge = inside & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    lit_edge = edge & ((nx * L[0] + ny * L[1]) > 0.35)
    col[lit_edge] = np.minimum(1, MATP[mat[lit_edge], 3] * 1.05)
    if name == 'earth':                              # Christmas-light cities on the night side
        h = (np.sin(lat * 91.7 + np.floor(lon * 15.3) * 12.9) * 43758.5) % 1.0
        city = (mat == MI['land']) & (d < -0.3) & (h > 0.86) & ~edge
        col[city] = hexc('#ffd36a')
    if ret: return yy[inside], xx[inside], col[inside], np.ones(inside.sum())
    ring = ~inside & (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
    rk = ring & (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
    F[yy[rk], xx[rk]] = hexc('#06070e')
    ok = inside & (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
    F[yy[ok], xx[ok]] = col[ok]

def clean_sun(F, cx, cy, r, pulse):
    yy, xx = np.mgrid[int(cy - r - 12):int(cy + r + 13), int(cx - r - 12):int(cx + r + 13)]
    d = np.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
    ring1 = (d > r) & (d <= r + 3 + 2 * pulse)
    ring2 = (d > r + 3 + 2 * pulse) & (d <= r + 7 + 3 * pulse) & (((xx + yy) % 2) == 0)
    ring3 = (d > r + 7 + 3 * pulse) & (d <= r + 11 + 3 * pulse) & ((xx % 2 == 0) & (yy % 2 == 0))
    for m, c in ((ring3, '#c8501a'), (ring2, '#ff8a2a'), (ring1, '#ffb43a')):
        ok = m & (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
        F[yy[ok], xx[ok]] = hexc(c)
    lv = np.where(d <= r * 0.45, 3, np.where(d <= r * 0.75, 2, np.where(d <= r - 1, 1, 0)))
    sp = hexc('#fff6c8'), hexc('#ffe27a'), hexc('#ffc43a'), hexc('#ff9a2a')
    for k, c in enumerate([sp[3], sp[2], sp[1], sp[0]]):
        m = (d <= r) & (lv == k)
        F[yy[m], xx[m]] = c

def light_dir(name, t):
    th = theta(name, t)
    v = np.array([-math.cos(th), -0.4 * math.sin(th), -math.sin(th)])
    v = v / np.linalg.norm(v) + np.array([0.0, -0.2, 0.5])
    return v / np.linalg.norm(v)

# ================================================================== orbits: golden garlands hung with bells
GOLD, GOLD_D = hexc('#e9c25a'), hexc('#8a6a24')
def ring_points(name, back):
    r = ORB[name]; n = int(TAU * r / 3.2)
    out = []
    for k in range(n):
        th = TAU * k / n
        if (math.sin(th) < 0) == back:
            out.append((SUN[0] + r * math.cos(th), SUN[1] + r * TILT * math.sin(th), th))
    return out
RINGPTS = {(n, b): ring_points(n, b) for n in ORB for b in (True, False)}

def splat(F, x, y, col, a):
    """soft 2x2 splat: sub-pixel position spread over neighbours (smooth curves, no jaggies)"""
    x0, y0 = int(math.floor(x)), int(math.floor(y)); fx, fy = x - x0, y - y0
    for dx, dy, wgt in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        put(F, x0 + dx, y0 + dy, col, a * wgt)

BELL = ["010", "111", "111", "202"]
def draw_ring(F, name, t, back, vis):
    if vis <= 0: return
    a = (0.30 if back else 0.55) * vis
    for x, y, th in RINGPTS[(name, back)]:
        put(F, x, y, GOLD * (0.55 if back else 0.8), vis)
    p = PLANETS[name]; r = ORB[name]
    age = last_age(p['hits'], t) if p['first'] <= t < p['last'] + 1 else 9
    i_last = int(np.searchsorted(p['hits'], t, side='right') - 1)
    for k in range(p['bells']):
        th = math.pi / 2 + TAU * k / p['bells']
        if (math.sin(th) < 0) != back: continue
        bx, by = SUN[0] + r * math.cos(th), SUN[1] + r * TILT * math.sin(th)
        hit = (i_last >= 0 and i_last % p['bells'] == k and age < 0.35)
        sw = int(round(math.sin(age * 40) * 1.2 * math.exp(-age / 0.12))) if hit else 0
        fl = math.exp(-age / 0.1) if hit else 0
        for yy, row in enumerate(BELL):
            for xx, c in enumerate(row):
                if c == '0': continue
                col = GOLD if c == '1' else GOLD_D
                col = col * (0.75 + 0.25 * (xx == 2)) * (0.7 if back else 1.0)
                put(F, bx - 1 + xx + sw * (yy > 0), by - 3 + yy, np.minimum(1, col + fl * 0.8), vis)
        if fl > 0.05:
            for rr in range(2, 6):
                for q in range(12):
                    ang = TAU * q / 12
                    glow(F, bx + math.cos(ang) * rr * (1 + 3 * (1 - fl)), by - 1 + math.sin(ang) * rr * (1 + 3 * (1 - fl)) * 0.7, GOLD, 0.25 * fl)

# ================================================================== the sun
def draw_sun(F, t):
    kick = math.exp(-last_age(PLANETS['earth']['hits'], t) / 0.15) if 2 <= t < 38.3 else 0
    hk = [h for h, _ in HOOK] + [h for h, _ in ECHO]
    kick = max(kick, 1.3 * math.exp(-last_age(sorted(hk), t) / 0.12))
    r = 14
    clean_sun(F, SUN[0], SUN[1], r, min(1.0, kick))

# ================================================================== planets (form from sparkles / burst into sparkles)
def draw_planet(F, name, t, seed):
    st = present(name, t)
    if st is None: return
    x, y, z = pos(name, t)
    r = PR[name] * (1 + 0.06 * z)
    L = light_dir(name, t); spin = TAU * SPIN[name] * t / LOOP
    if st[0] == 'on':
        clean_planet(F, name, x, y, r, L, spin); return
    ys, xs, col, cov = clean_planet(F, name, x, y, r, L, spin, ret=True)
    rr = np.random.default_rng(seed); n = len(ys)
    ang = rr.uniform(0, TAU, n); dist = rr.uniform(6, 22, n); lag = rr.uniform(0, 0.35, n)
    if st[0] == 'form':
        s = np.clip((st[1] - lag) / (1 - lag), 0, 1); e = (1 - s) ** 2
        px, py = xs + np.cos(ang) * dist * e, ys + np.sin(ang) * dist * e
        c = col * s[:, None] + np.array([1.0, 0.95, 0.8]) * (1 - s[:, None]); a = np.clip(s * 1.4, 0, 1) * cov
    else:
        s = np.clip((st[1] - lag * 0.5) / (1 - lag * 0.5), 0, 1); e = s ** 0.7
        px, py = xs + np.cos(ang) * dist * e * 1.6, ys + np.sin(ang) * dist * e * 1.6
        c = col * (1 - s[:, None]) + np.array([1.0, 0.95, 0.75]) * s[:, None]; a = (1 - s) * cov
    xi, yi = np.round(px).astype(int), np.round(py).astype(int)
    ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
    F[yi[ok], xi[ok]] = F[yi[ok], xi[ok]] * (1 - a[ok, None]) + c[ok] * a[ok, None]

def ring_vis(name, t):
    st = present(name, t)
    if st is None: return 0
    return {'form': min(1, st[1] * 1.3), 'on': 1, 'burst': 1 - st[1]}[st[0]]

# ================================================================== the comet and the star tree
def tree_points():
    rows = [(232, 2), (214, 7), (194, 6), (174, 5), (154, 5), (134, 4), (114, 3), (95, 1)]
    pts = []
    for ri, (y, n) in enumerate(rows):
        hw = 6 if ri == 0 else (y - 78) / 150 * 68
        xs = [135] if n == 1 else [135 - hw + 2 * hw * i / (n - 1) for i in range(n)]
        if ri % 2: xs = xs[::-1]
        pts += [(x, y) for x in xs]
    return pts + [(135, 72)]                       # top star (last note)
TREE = [(x, y + 42) for x, y in tree_points()]
assert len(TREE) == len(MELODY)
MEL_T = [m[0] for m in MELODY]
COMET_IN = (300.0, 20.0)

def comet_pos(t):
    if t < MEL_T[0] - 0.9 or t > MEL_T[-1]: return None
    if t < MEL_T[0]:
        s = smooth((t - (MEL_T[0] - 0.9)) / 0.9); x0, y0 = COMET_IN; x1, y1 = TREE[0]
        return x0 + (x1 - x0) * s, y0 + (y1 - y0) * s - 30 * math.sin(s * math.pi)
    i = int(np.searchsorted(MEL_T, t, side='right') - 1)
    if i + 1 >= len(MEL_T): return TREE[-1]
    s = (t - MEL_T[i]) / (MEL_T[i + 1] - MEL_T[i]); (x0, y0), (x1, y1) = TREE[i], TREE[i + 1]
    e = smooth(s)
    return x0 + (x1 - x0) * e, y0 + (y1 - y0) * e - 10 * math.sin(s * math.pi)

def draw_comet(F, t):
    p = comet_pos(t)
    if p is None: return
    for k in range(30, 0, -1):                       # glittering tail along its recent path
        q = comet_pos(t - k * 0.018)
        if q is None: continue
        f = 1 - k / 30
        col = hexc('#7fd8ff') * f + hexc('#b07cff') * (1 - f)
        if k % 2 == 0: put(F, q[0], q[1], col, 0.9 * f)
    for dx, dy, a in ((0, 0, 1), (1, 0, .6), (-1, 0, .6), (0, 1, .6), (0, -1, .6), (1, 1, .3), (-1, -1, .3), (1, -1, .3), (-1, 1, .3)):
        glow(F, p[0] + dx, p[1] + dy, np.array([0.9, 0.97, 1.0]), a)

STARSHAPE = ["0000100000", "0000100000", "0001110000", "1111111111", "0111111110", "0011111100", "0011011100", "0110001110", "0100000010"]
STARSHAPE = np.array([[c == '1' for c in r] for r in STARSHAPE])
TREE_FADE = np.random.default_rng(5).uniform(0, 0.8, len(TREE))
def draw_tree(F, t):
    glowk = math.exp(-(t - TREE_GLOW) / 0.4) if t >= TREE_GLOW else 0
    for i, ((x, y), mt) in enumerate(zip(TREE, MEL_T)):
        a = t - mt
        if a < 0: continue
        fade = 1.0
        if t > TREE_GLOW + 0.2:
            fade = max(0.0, 1 - (t - TREE_GLOW - 0.2 - TREE_FADE[i]) / 0.3) if t - TREE_GLOW - 0.2 > TREE_FADE[i] else 1.0
        if fade <= 0: continue
        tw = 0.75 + 0.25 * math.sin(w(9 + i % 5) * t + i)
        b = (tw + 1.2 * math.exp(-a / 0.15) + glowk) * fade
        col = [hexc('#fff6c8'), hexc('#ff6a6a'), hexc('#7dff9a'), hexc('#8ad0ff')][i % 4] if i < len(TREE) - 1 else hexc('#ffd84a')
        if i == len(TREE) - 1:
            ys, xs = np.nonzero(STARSHAPE)
            for yy, xx in zip(ys, xs): put(F, x - 5 + xx, y - 4 + yy, np.minimum(1, col * min(1, b) + 0.2 * glowk), fade)
            for k in range(1, 7):
                for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)): glow(F, x + dx - 0.5, y + dy, hexc('#ffe9a0'), 0.35 * b / k)
            continue
        put(F, x, y, np.minimum(1, col * 0.6 + 0.4 * min(1, b)))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): put(F, x + dx, y + dy, np.minimum(1, col * min(1, b)), fade)
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)): glow(F, x + dx, y + dy, col, 0.35 * min(1.5, b))
        burst = math.exp(-a / 0.12) if a < 0.4 else 0
        if burst > 0.05:
            for k in range(2, int(3 + 6 * (1 - burst))):
                for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)): glow(F, x + dx, y + dy, col, 0.6 * burst)

# ================================================================== captions (plain, smaller, lower)
HEADPHONES = ["0011111100", "0100000010", "1000000001", "1000000001", "1110000111", "1110000111", "1110000111", "0110000110"]
def caption_sprite(text, sc=2, pad=4, icon=False):
    tm = text_mask(text, sc); th, tw = tm.shape
    bw, bh = tw + 2 * pad, th + 2 * pad
    out = np.zeros((bh, bw, 4), np.float32); out[..., 3] = 1
    for cy, cx in ((0, 0), (0, bw - 1), (bh - 1, 0), (bh - 1, bw - 1)): out[cy, cx, 3] = 0
    out[pad:pad + th, pad:pad + tw][tm] = [1, 1, 1, 1]
    if icon:   # headphones badge under the title box: small black box, rounded corners, white icon
        g = np.kron(np.array([[c == '1' for c in r] for r in HEADPHONES]), np.ones((sc, sc), bool))
        ih, iw = g.shape[0] + 8, g.shape[1] + 8
        full = np.zeros((bh + 3 + ih, bw, 4), np.float32); full[:bh] = out
        x0 = (bw - iw) // 2; y0 = bh + 3
        full[y0:y0 + ih, x0:x0 + iw] = [0, 0, 0, 1]
        for cy, cx in ((y0, x0), (y0, x0 + iw - 1), (y0 + ih - 1, x0), (y0 + ih - 1, x0 + iw - 1)): full[cy, cx, 3] = 0
        full[y0 + 4:y0 + 4 + g.shape[0], x0 + 4:x0 + 4 + g.shape[1]][g] = [1, 1, 1, 1]
        out = full
    return out

class Caption:
    def __init__(self, text, t_in, t_out, seed, y=60, icon=False):
        self.s = caption_sprite(text, icon=icon); h, w_ = self.s.shape[:2]
        self.x, self.y, self.t_in, self.t_out = (W - w_) // 2, y, t_in, t_out
        r = np.random.default_rng(seed)
        self.yy, self.xx = np.mgrid[0:h, 0:w_]
        self.vis = self.s[..., 3] > 0
        self.t_app = 0.07 * r.random((h, w_))
        self.t_dis = 0.06 + 0.5 * (0.55 * r.random((h, w_)) + 0.45 * (self.xx / w_))
        self.dx = (r.random((h, w_)) - 0.25) * 16; self.dy = -(6 + r.random((h, w_)) * 14)
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
                pxs = self.x + self.xx[mist] + self.dx[mist] * k + 2 * np.sin(ag * 8 + self.yy[mist] * 0.7)
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
def cap(text, a, b, icon=False): CAPTIONS.append(Caption(text, a, b, 40 + len(CAPTIONS), icon=icon))
cap("WHAT IF THE PLANETS\nPLAYED CHRISTMAS\nMUSIC?", 41.3, 43.7, icon=True)
cap("EARTH RINGS EVERY\nBELL IT PASSES", 2.3, 5.3)
cap("MERCURY IS CLOSER TO\nTHE SUN, SO IT GOES\nFASTER", 6.3, 9.3)
cap("VENUS PLAYS\nIN BETWEEN", 10.4, 13.3)
cap("MARS IS FARTHER OUT,\nSO IT TAKES ITS TIME", 14.4, 17.3)
cap("GIANT JUPITER IS\nTHE SLOWEST OF ALL", 18.3, 21.0)
cap("AND A COMET\nBRINGS THE SONG", 21.6, 24.8)
cap("EVERY NOTE\nLIGHTS A STAR", 27.0, 30.5)
cap("THE STARS MADE A\nCHRISTMAS TREE!", 37.5, 40.6)

# ================================================================== living pixels: swap with a neighbour, in place
def alive(F, t, rate=0.015):
    tick = int(t * 20) % int(LOOP * 20)
    r = np.random.default_rng(tick + 1000); n = int(W * H * rate)
    ys = r.integers(1, H - 1, n); xs = r.integers(1, W - 1, n); d = r.integers(0, 4, n)
    ys2 = ys + np.array([0, 0, 1, -1])[d]; xs2 = xs + np.array([1, -1, 0, 0])[d]
    a, b = F[ys, xs].copy(), F[ys2, xs2].copy(); F[ys, xs] = b; F[ys2, xs2] = a

# ================================================================== camera: one subject at a time
def target(name, t):
    if name == 'sun': return SUN[0], SUN[1]
    if name == 'sunup': return SUN[0], SUN[1] - 40
    if name == 'wide': return W / 2, H / 2
    if name == 'comet':
        ps = [comet_pos(t + d) for d in np.linspace(-0.9, 0.9, 13)]
        ps = [p for p in ps if p]
        return (sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps)) if ps else TREE[-1]
    ps = [pos(name, t + d) for d in np.linspace(-0.5, 0.5, 9)]
    return sum(p[0] for p in ps) / 9, sum(p[1] for p in ps) / 9

# Start framed on the inner planets (the whole of their orbits fit), ease out to the full
# view when Jupiter's huge orbit arrives, stay wide for the comet and the star tree.
CAM = [(0.0, 'sunup', 1.25), (16.6, 'sunup', 1.25), (17.9, 'wide', 1.0), (41.0, 'wide', 1.0), (42.0, 'sunup', 1.25)]
def camera(t):
    for (t0, a, z0), (t1, b, z1) in zip(CAM, CAM[1:]):
        if t0 <= t <= t1:
            s = smooth((t - t0) / max(1e-6, t1 - t0))
            (x0, y0), (x1, y1) = target(a, t), target(b, t)
            z = math.exp(math.log(z0) + (math.log(z1) - math.log(z0)) * s)
            return x0 + (x1 - x0) * s, y0 + (y1 - y0) * s, z
    x, y = target('sunup', t); return x, y, 1.25

OX = (np.arange(W * S) + 0.5) / S; OY = (np.arange(H * S) + 0.5) / S
def shoot(F, t):
    cx, cy, z = camera(t); vw, vh = W / z, H / z
    cx = min(max(cx, vw / 2), W - vw / 2); cy = min(max(cy, vh / 2), H - vh / 2)
    xi = np.clip(np.floor(cx - vw / 2 + OX / z).astype(int), 0, W - 1)
    yi = np.clip(np.floor(cy - vh / 2 + OY / z).astype(int), 0, H - 1)
    return F[yi][:, xi]

# ================================================================== frame
ORDER = ['mercury', 'venus', 'earth', 'mars', 'jupiter']
def frame(t):
    F = SPACEBG.copy()
    draw_bgstars(F, t)
    alive(F, t)
    draw_tree(F, t)
    for n in ORDER: draw_ring(F, n, t, True, ring_vis(n, t))
    back = [n for n in ORDER if pos(n, t)[2] < 0]; front = [n for n in ORDER if n not in back]
    for n in sorted(back, key=lambda n: pos(n, t)[2]): draw_planet(F, n, t, ORDER.index(n) + 3)
    draw_sun(F, t)
    for n in ORDER: draw_ring(F, n, t, False, ring_vis(n, t))
    for n in sorted(front, key=lambda n: pos(n, t)[2]): draw_planet(F, n, t, ORDER.index(n) + 3)
    draw_comet(F, t)
    out = shoot(F, t)
    scr = out[::S, ::S].copy(); before = scr.copy()
    for c in CAPTIONS: c.draw(scr, t)
    ch = np.any(np.abs(scr - before) > 1e-6, axis=2)
    if ch.any():
        big = np.repeat(np.repeat(ch, S, 0), S, 1)
        out[big] = np.repeat(np.repeat(scr, S, 0), S, 1)[big]
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)

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
