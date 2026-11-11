"""Renders 'The Christmas Star Is Coming Back... in 2080' - 1080x1920 / 60 fps pixel art.

A snowy village under two bright dots: Jupiter and Saturn. Through the telescope, Jupiter's moons
(Io, Europa, Ganymede, really orbiting 1:2:4) play kick, clap and bass; Saturn's rings sparkle on the
hi-hats. Then the two planets slide together and become one Christmas star on Silent Night's high note.

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
def put(F, x, y, col, a=1.0):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H: F[y, x] = F[y, x] * (1 - a) + col * a
def last_age(hits, t):
    i = int(np.searchsorted(hits, t, side='right') - 1)
    return t - hits[i] if i >= 0 else 99.0
def w(k): return TAU * k / LOOP
FULL_BAYER = BAYER[YY % 4, XX % 4]

def curved_bands(shades, y0, y1, n_curves, seed):
    """the approved recipe: light at the top -> dark at the bottom, smooth curves, wide dithered blends"""
    r = np.random.default_rng(seed); span = y1 - y0; v = np.zeros((H, W))
    for k in range(n_curves):
        cy = y0 + span * (k + 1) / (n_curves + 1)
        cv = cy + span * 0.05 * np.sin(XX / r.uniform(30, 40) + r.uniform(0, 6)) + span * 0.02 * np.sin(XX / r.uniform(15, 21) + r.uniform(0, 6))
        v = v + np.clip((YY - cv) / (span * 0.07) + 0.5, 0, 1)
    return shades[np.clip(np.floor(v + FULL_BAYER), 0, len(shades) - 1).astype(int)]

# ================================================================ WIDE: snowy village under the night sky
HILL_FAR = 236 + 9 * np.sin(XX / 23 + 0.5) + 4 * np.sin(XX / 9 + 1.3)
HILL_NEAR = 262 + 7 * np.sin(XX / 17 + 2.0) + 3 * np.sin(XX / 7)
HOUSES = [(22, 14, 11), (44, 12, 9), (136, 13, 10), (160, 14, 12)]          # x, width, wall height
TREE_X, TREE_H = 96, 30
def build_wide():
    P = curved_bands(pal('#22345a', '#1b2b4f', '#152243', '#101a36'), 0, 250, 3, 5).astype(np.float32)
    far = YY >= HILL_FAR
    P[far] = hexc('#1a2a4c'); P[far & (YY < HILL_FAR + 1.5)] = hexc('#6b86b4')        # snow rim catching the starlight
    near = YY >= HILL_NEAR
    P[near] = curved_bands(pal('#2c4068', '#24375c', '#1d2e50', '#172645'), 262, H, 2, 9)[near]
    P[near & (YY < HILL_NEAR + 1.5)] = hexc('#a9bfe0')
    for hx, hw, hh in HOUSES:                                                       # little houses on the hill
        base = int(HILL_NEAR[0, hx]) + 2
        wall = (XX >= hx - hw // 2) & (XX < hx + hw // 2) & (YY >= base - hh) & (YY < base)
        roof = (YY >= base - hh - hw // 2) & (YY < base - hh) & (np.abs(XX - hx + 0.5) <= (YY - (base - hh - hw // 2)) + 0.5)
        m = wall | roof
        P[dilate(m) & ~m] = INK
        P[wall] = hexc('#3a2a3e'); P[roof] = hexc('#e8f0fb'); P[roof & (YY == base - hh - 1)] = hexc('#b8c8e0')
        P[base - hh + 3:base - hh + 5, hx - 2:hx] = hexc('#ffd27a')                 # warm window
    return P
WIDE = build_wide()
TREE_LIGHTS = []
for k in range(TREE_H):                                                            # the village Christmas tree
    hw = 1 + k * 0.42
    if k > 4 and k % 4 == 1:
        for s_ in (-1, 1): TREE_LIGHTS.append((TREE_X + s_ * int(hw - 1), int(HILL_NEAR[0, TREE_X]) - TREE_H + k, len(TREE_LIGHTS)))
def draw_tree(F, t, glow):
    base = int(HILL_NEAR[0, TREE_X]) + 1
    m = np.zeros((H, W), bool)
    for k in range(TREE_H):
        hw = 1 + k * 0.42; y = base - TREE_H + k
        m[y, int(TREE_X - hw):int(TREE_X + hw) + 1] = True
    m[base:base + 3, TREE_X - 1:TREE_X + 2] = True
    F[dilate(m) & ~m] = INK
    F[m] = hexc('#1d5a36'); F[m & (XX < TREE_X)] = hexc('#2a7a4a')
    F[base:base + 3, TREE_X - 1:TREE_X + 2] = hexc('#4a2c1c')
    cols = [hexc(c) for c in ('#ff4d5e', '#ffd35a', '#59e1ff', '#7dff8a')]
    for x, y, i in TREE_LIGHTS:
        b = min(1.0, 0.45 + 0.35 * math.sin(w(13 + i % 5) * t + i) + glow)
        put(F, x, y, cols[i % 4] * (0.5 + 0.5 * b) + 0.25 * b)
    star_on = glow > 0.05
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        put(F, TREE_X + dx, base - TREE_H - 1 + dy, hexc('#ffd84a') if star_on or dx == dy == 0 else hexc('#8a7a3a'))

rng = np.random.default_rng(21)
STARS = [(rng.uniform(0, W), rng.uniform(4, 225), int(rng.integers(2, 9)), rng.uniform(0, 6.28), rng.random()) for _ in range(60)]
SNOW = [(rng.uniform(0, W), rng.uniform(0, 1), int(rng.integers(3, 7)), rng.uniform(0, 6.28)) for _ in range(30)]
MID = np.array([96.0, 132.0]); DIRV = np.array([-0.8, -0.6]); SEP0 = 76
def separation(t):
    if t < 16.7: return SEP0
    if t < MERGE: return SEP0 * (1 - ((t - 16.7) / (MERGE - 16.7)) ** 1.7)
    if t < REWIND[0]: return 0
    if t < REWIND[1]: return SEP0 * smooth((t - REWIND[0]) / (REWIND[1] - REWIND[0]))
    return SEP0

def draw_dot(F, x, y, core, glow, arm, size):
    for dy in range(-(size // 2), size - size // 2):
        for dx in range(-(size // 2), size - size // 2): put(F, x + dx, y + dy, core)
    for k in range(1, arm + 1):
        a = (1 - k / (arm + 1)) * 0.8
        for dx, dy in ((k + size // 2, 0), (-k - size // 2, 0), (0, k + size // 2), (0, -k - size // 2)):
            if a > FULL_BAYER[int(y + dy) % H, int(x + dx) % W] * 0.9: put(F, x + dx, y + dy, glow)

def draw_star(F, x, y, t):
    kick = math.exp(-last_age(MOONS['io']['hits'], t) / 0.15) if t < END + 0.2 else 0
    born = t - MERGE
    grow = smooth(born / 0.35)
    ln = lambda base: int(round(base * grow + 2 * kick))
    gold, white = hexc('#ffd86a'), hexc('#fffaf0')
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if abs(dx) + abs(dy) < 4: put(F, x + dx, y + dy, white if abs(dx) + abs(dy) < 2 else gold)
    for k in range(2, ln(26) + 1):                      # long Bethlehem-style rays
        a = 1 - k / (ln(26) + 2)
        put(F, x, y + k, white if k < 5 else gold, a + 0.2)
    for k in range(2, ln(17) + 1):
        a = 1 - k / (ln(17) + 2); put(F, x, y - k, white if k < 4 else gold, a + 0.2)
    for k in range(2, ln(15) + 1):
        a = 1 - k / (ln(15) + 2); put(F, x + k, y, white if k < 4 else gold, a + 0.2); put(F, x - k, y, white if k < 4 else gold, a + 0.2)
    for k in range(2, ln(7) + 1):
        for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)): put(F, x + sx * k, y + sy * k, gold, 0.7)
    if 0 <= born < 0.9:                                  # crisp burst ring + a dithered flash of light across the sky
        r_ = 4 + 90 * smooth(born / 0.9)
        for q in range(140):
            th = TAU * q / 140
            put(F, x + r_ * math.cos(th), y + r_ * math.sin(th) * 0.9, gold, 1 - born / 0.9)
        r2 = 2 + 55 * smooth(born / 0.9)
        for q in range(100):
            th = TAU * q / 100 + 0.03
            put(F, x + r2 * math.cos(th), y + r2 * math.sin(th) * 0.9, hexc('#fffaf0'), 1 - born / 0.9)

def wide_frame(t):
    F = WIDE.copy()
    for x, y, k, ph, br in STARS:
        b = 0.5 + 0.5 * math.sin(w(k) * t + ph)
        put(F, x, y, hexc('#dce6ff') if br < 0.8 else hexc('#ffe9c0'), 0.2 + 0.65 * b)
    for mt, n, d in MELODY:                               # a star in the sky twinkles on every melody note
        a = t - mt
        if 0 <= a < 0.5:
            x, y, *_ = STARS[int(mt * 7) % len(STARS)]
            for k in range(1, 4):
                for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)): put(F, x + dx, y + dy, hexc('#ffffff'), (1 - a / 0.5) * (1 - k / 4))
    sep = separation(t)
    if t >= MERGE and t < REWIND[0]:
        draw_star(F, MID[0], MID[1], t)
        glow = 0.6
    else:
        jx, jy = MID - DIRV * sep / 2; sx, sy = MID + DIRV * sep / 2
        tension = smooth((t - 22.5) / 4.5) if 22.5 < t < MERGE else 0
        io = math.exp(-last_age(MOONS['io']['hits'], t) / 0.12) if 3 <= t < END + 0.2 else 0
        ring = math.exp(-last_age(RING_HITS, t) / 0.08) if 13.5 <= t < END else 0
        draw_dot(F, sx, sy, hexc('#ffe3a0'), hexc('#d8b060'), 3 + int(ring * 2 + tension * 3), 4)
        for dx in range(-5, 6):
            if abs(dx) > 2: put(F, sx + dx, sy + (1 if dx > 0 else 0), hexc('#e8c880'))
        draw_dot(F, jx, jy, hexc('#fff4dc'), hexc('#e8d0a0'), 4 + int(io * 3 + tension * 4), 5)
        if REWIND[0] <= t < REWIND[1]:                    # rewind streaks
            for k in range(1, 6):
                put(F, jx + DIRV[0] * k * 2, jy + DIRV[1] * k * 2, hexc('#e8d0a0'), 0.5 - k * 0.08)
                put(F, sx - DIRV[0] * k * 2, sy - DIRV[1] * k * 2, hexc('#d8b060'), 0.5 - k * 0.08)
        glow = 0.0
    if t >= MERGE and t < REWIND[0]: glow = 0.6 + 0.4 * math.exp(-(t - MERGE) / 0.6)
    draw_tree(F, t, glow)
    for x0, ph0, n, ph in SNOW:                           # snow falls and settles on the hill
        cyc = LOOP / n; tau = ((t / cyc + ph0) % 1.0) * cyc; land = HILL_NEAR[0, int(x0) % W]; fall = (land + 6) / 28.0
        if tau < fall: put(F, x0 + 3 * math.sin(tau * 1.6 + ph), -6 + 28 * tau, np.array([0.95, 0.97, 1.0]), 0.9)
        elif tau < fall + 1.4: put(F, x0 + 3 * math.sin(fall * 1.6 + ph), land, np.array([1, 1, 1]), 0.9 * (1 - (tau - fall) / 1.4))
    return F

# ================================================================ CLOSE-UPS (through the telescope)
SPACE = curved_bands(pal('#161d3a', '#121831', '#0e1328', '#0a0e1f'), 0, H, 3, 17).astype(np.float32)
SPACE_STARS = [(rng.uniform(0, W), rng.uniform(0, H), int(rng.integers(2, 9)), rng.uniform(0, 6.28)) for _ in range(45)]
LDIR = np.array([-0.65, -0.35, 0.68]); LDIR /= np.linalg.norm(LDIR)

def sphere(F, cx, cy, r, colour_fn, outline=True):
    """clean flat-shaded ball: 4 light bands, black outline, lit rim (no blur)"""
    R = int(r) + 2
    yy, xx = np.mgrid[int(cy) - R:int(cy) + R + 1, int(cx) - R:int(cx) + R + 1]
    nx, ny = (xx + 0.5 - cx) / r, (yy + 0.5 - cy) / r
    inside = nx * nx + ny * ny <= 1
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    d = nx * LDIR[0] + ny * LDIR[1] + nz * LDIR[2]
    lvl = np.clip(np.floor((d * 0.9 + 0.5) * 3.3), 0, 3).astype(int)
    col = colour_fn(nx, ny, nz, lvl)
    p = np.pad(inside, 1)
    edge = inside & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    col[edge & ((nx * LDIR[0] + ny * LDIR[1]) > 0.3)] = np.minimum(1, col[edge & ((nx * LDIR[0] + ny * LDIR[1]) > 0.3)] * 1.25 + 0.08)
    ring = ~inside & (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
    ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
    if outline: F[yy[ring & ok], xx[ring & ok]] = INK
    F[yy[inside & ok], xx[inside & ok]] = col[inside & ok]
    return inside, yy, xx

JUP = (90.0, 176.0, 34.0)
J_ZONE = pal('#7a5434', '#c4946a', '#ecd2ac', '#fff2dc'); J_BELT = pal('#4e2c18', '#8a5432', '#c07a4a', '#e6a070')
J_SPOT = pal('#5a1a10', '#a4321e', '#e0503a', '#ff8a6a')
J_EDGES = [-0.62, -0.38, -0.12, 0.12, 0.34, 0.58]
def jupiter_col(t):
    spin = TAU * 2 * t / LOOP
    def f(nx, ny, nz, lvl):
        lat = np.arcsin(np.clip(-ny, -1, 1)); lon = np.arctan2(nx, nz + 1e-6) + spin
        wob = 0.025 * np.sin(lon * 3)
        belt = np.zeros_like(lat, bool)
        for k in range(0, len(J_EDGES) - 1, 2): belt |= (lat > J_EDGES[k] + wob) & (lat < J_EDGES[k + 1] + wob)
        col = np.where(belt[..., None], J_BELT[lvl], J_ZONE[lvl])
        spot = ((lat + 0.42) / 0.11) ** 2 + (np.angle(np.exp(1j * (lon - 1.2))) / 0.36) ** 2 < 1
        return np.where(spot[..., None], J_SPOT[lvl], col)
    return f

MOON_LOOK = {'io': (48, 3.2, pal('#6a4a10', '#c4902a', '#f0c84a', '#fff09a')),
             'europa': (62, 2.8, pal('#5a5048', '#a89a88', '#e0d6c4', '#fffaf0')),
             'ganymede': (78, 4.0, pal('#3a3430', '#6e645a', '#a2968a', '#d4cabe'))}
TILT = 0.3
MOON_JOIN = {'io': 0.0, 'europa': 5.6, 'ganymede': 7.8}
def moon_pos(name, t):
    m = MOONS[name]; R = MOON_LOOK[name][0]
    th = math.pi / 2 + TAU * (t - m['first']) / m['period']
    return JUP[0] + R * math.cos(th), JUP[1] + R * TILT * math.sin(th), math.sin(th)

def draw_orbit(F, name, back):
    R = MOON_LOOK[name][0]
    for q in range(0, 360, 4):
        th = math.radians(q)
        if (math.sin(th) < 0) == back: put(F, JUP[0] + R * math.cos(th), JUP[1] + R * TILT * math.sin(th), hexc('#2e3a66'), 0.9)

def draw_moon(F, name, t):
    if t < MOON_JOIN[name]: return
    x, y, z = moon_pos(name, t); r = MOON_LOOK[name][1]; P = MOON_LOOK[name][2]
    j = t - MOON_JOIN[name]
    if name != 'io' and j < 0.4:                                   # pops in with a sparkle
        r = r * smooth(j / 0.4)
        for k in range(2, 6): put(F, x + k, y - k, hexc('#ffffff'), 1 - j / 0.4); put(F, x - k, y + k, hexc('#ffffff'), 1 - j / 0.4)
        if r < 0.8: return
    hit = math.exp(-last_age(MOONS[name]['hits'], t) / 0.12) if t >= MOONS[name]['first'] else 0
    sphere(F, x, y, r, lambda nx, ny, nz, lvl: np.minimum(1, P[lvl] + hit * 0.45))
    if hit > 0.1:                                                  # little flash ring on its beat
        for q in range(16):
            th = TAU * q / 16; rr = r + 2 + 4 * (1 - hit)
            put(F, x + rr * math.cos(th), y + rr * math.sin(th), hexc('#fff6d8'), hit)

def jupiter_frame(t):
    F = SPACE.copy()
    for x, y, k, ph in SPACE_STARS: put(F, x, y, hexc('#dce6ff'), 0.2 + 0.6 * (0.5 + 0.5 * math.sin(w(k) * t + ph)))
    for n in MOONS: draw_orbit(F, n, True)
    for n in MOONS:
        if moon_pos(n, t)[2] < 0: draw_moon(F, n, t)
    inside, yy, xx = sphere(F, JUP[0], JUP[1], JUP[2], jupiter_col(t))
    for n in MOONS:                                                # each moon casts a tiny shadow when it is in front
        if t < MOON_JOIN[n]: continue
        x, y, z = moon_pos(n, t)
        if z > 0 and abs(x + 4 - JUP[0]) < JUP[2] - 3:
            sx, sy = x + 4, JUP[1] + (y - JUP[1]) * 0.4 + 6
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if abs(dx) + abs(dy) < 2 and (sx + dx - JUP[0]) ** 2 + (sy + dy - JUP[1]) ** 2 < (JUP[2] - 1) ** 2: put(F, sx + dx, sy + dy, INK)
    for n in MOONS: draw_orbit(F, n, False)
    for n in MOONS:
        if moon_pos(n, t)[2] >= 0: draw_moon(F, n, t)
    return F

SAT = (90.0, 180.0, 25.0)
S_PAL = pal('#7a6038', '#c8a46a', '#ecd4a0', '#fff4d8'); S_PAL2 = pal('#6a5030', '#b08c58', '#d8b884', '#f0dcb4')
RING_BANDS = [(0.62, 0.74, '#b89c70'), (0.74, 0.86, '#e8d4a8'), (0.86, 0.89, None), (0.89, 1.0, '#cdb486')]
RX, RY = 64.0, 15.0
def saturn_col(nx, ny, nz, lvl):
    lat = np.arcsin(np.clip(-ny, -1, 1))
    band = (np.floor(lat / 0.22) % 2) == 0
    return np.where(band[..., None], S_PAL[lvl], S_PAL2[lvl])
def draw_rings(F, front, t):
    d = np.hypot((XX + 0.5 - SAT[0]) / RX, (YY + 0.5 - SAT[1]) / RY)
    half = (YY + 0.5 > SAT[1]) if front else (YY + 0.5 <= SAT[1])
    allr = (d >= 0.62) & (d <= 1.0)
    for a, b, c in RING_BANDS:
        m = (d >= a) & (d < b) & half
        if c is None: F[m] = INK
        else: F[m] = hexc(c); F[m & (FULL_BAYER < 0.25) & (d < (a + b) / 2)] = hexc(c) * 0.85
    edge = dilate(allr) & ~allr & half
    F[edge] = INK
def saturn_frame(t):
    F = SPACE.copy()
    for x, y, k, ph in SPACE_STARS: put(F, x, y, hexc('#dce6ff'), 0.2 + 0.6 * (0.5 + 0.5 * math.sin(w(k) * t + ph)))
    draw_rings(F, False, t)
    sphere(F, SAT[0], SAT[1], SAT[2], saturn_col)
    draw_rings(F, True, t)
    for i, h in enumerate(RING_HITS):                              # ring sparkles on the hi-hats
        a = t - h
        if 0 <= a < 0.2:
            th = i * 2.4; x, y = SAT[0] + RX * 0.8 * math.cos(th), SAT[1] + RY * 0.8 * math.sin(th)
            if math.sin(th) > 0 or abs(x - SAT[0]) > SAT[2] + 1:
                k_ = 1 - a / 0.2
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): put(F, x + dx, y + dy, hexc('#ffffff'), k_ * (1 if dx == dy == 0 else 0.6))
    return F

# ================================================================ captions: plain, casual, near the top
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
cap("SEE THESE TWO DOTS?", 37.4, 39.75, icon=True)
cap("OK SO THIS ONE'S\nJUPITER", 3.6, 6.3)
cap("AND THOSE LITTLE GUYS\nARE ITS MOONS", 6.6, 9.3)
cap("THEY ORBIT 1, 2, 4...\nLIKE A DRUM BEAT LOL", 9.6, 12.9)
cap("AND THIS ONE'S\nSATURN", 13.8, 16.0)
cap("NOW WATCH THEM...", 17.0, 19.8)
cap("THEY'RE GETTING\nCLOSER...", 20.3, 22.8)
cap("CLOSER...", 23.4, 26.0)
cap("BOOM. THEY LOOK\nLIKE ONE STAR", 27.1, 29.4)
cap("THIS HAPPENED IN 2020.\nPEOPLE CALLED IT THE\nCHRISTMAS STAR", 29.7, 32.3)
cap("NEXT TIME? 2080.\nSET A REMINDER LOL", 32.6, 35.4)

# ================================================================ scenes: wide sky <-> telescope close-ups (pixel fades)
SCENE_FN = {'wide': wide_frame, 'jupiter': jupiter_frame, 'saturn': saturn_frame}
def view(t):
    k = max(i for i, sc in enumerate(SCENES) if t >= sc[0])
    ts, name = SCENES[k]
    if k == 0 or t - ts >= FADE: return name, None, 0.0
    return SCENES[k - 1][1], name, (t - ts) / FADE

def living_pixels(F, t):
    tick = int(t * 20) % int(LOOP * 20)
    r = np.random.default_rng(tick + 1000); n = 200
    ys = r.integers(76, 228, n); xs = r.integers(1, W - 1, n); d = r.integers(0, 4, n)
    ys2 = ys + np.array([0, 0, 1, -1])[d]; xs2 = xs + np.array([1, -1, 0, 0])[d]
    a_, b_ = F[ys, xs].copy(), F[ys2, xs2].copy(); F[ys, xs] = b_; F[ys2, xs2] = a_

def frame(t):
    cur, nxt, s_ = view(t)
    F = SCENE_FN[cur](t)
    if nxt is not None:
        G = SCENE_FN[nxt](t); m = FULL_BAYER < smooth(s_); F[m] = G[m]
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
