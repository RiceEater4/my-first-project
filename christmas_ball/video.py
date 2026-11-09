"""Renders 'What If You Drop a Ball 4x Higher?' - 1080x1920 / 60 fps pixel art.

Drawn on a 270x480 canvas, scaled 4x nearest-neighbour. Every motion is driven by
score.py so each landing happens on the exact frame its sound plays. Every ambient
animation uses a whole number of cycles per LOOP, so the video loops seamlessly.

usage: python3 video.py out.mp4 audio.wav
       python3 video.py --stills DIR t1 t2 ...
"""
import sys, subprocess, math
import numpy as np
from score import *

W, H, S = 270, 480, 4
GROUND = 440
TAU = 2 * math.pi
def w(k): return TAU * k / LOOP          # loop-safe angular frequency (k whole cycles per loop)

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
def pal(*c): return np.stack([hexc(x) for x in c])

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16
YY, XX = np.mgrid[0:H, 0:W]
BAY = BAYER[YY % 4, XX % 4]

def dith(v, p, bay):
    return p[np.clip(np.floor(v + bay), 0, len(p) - 1).astype(int)]

# ---- "living pixels": every surface is re-dithered each frame with a drifting noise field,
# sweeping cloud shadows and a crawling dither pattern, so no pixel is ever frozen.
_r = np.random.default_rng(99)
_ny, _nx = np.mgrid[0:256, 0:256]
NZ = np.zeros((256, 256), np.float32)
for _k in range(6):
    fx, fy = _r.integers(1, 9, 2)
    NZ += np.sin(TAU * (fx * _nx + fy * _ny) / 256 + _r.uniform(0, TAU)) / (1 + _k * 0.5)
NZ = (NZ - NZ.min()) / (NZ.max() - NZ.min())

def live_fields(t):
    ox = int(t / LOOP * 256 * 7) % 256
    oy = int(t / LOOP * 256 * 4) % 256
    noise = NZ[(YY + oy) % 256, (XX + ox) % 256] - 0.5
    noise2 = NZ[(YY * 2 + 37 - oy * 3) % 256, (XX * 2 + 91 + ox * 2) % 256] - 0.5
    shadow = 0.32 * (np.sin((XX * 0.8 + YY * 0.5) / 26 - w(4) * t) + np.sin((XX - YY * 0.6) / 41 + w(3) * t))
    ripple = np.sin(XX / 7.5 + YY / 2.6 - w(24) * t + 1.5 * np.sin(YY / 9 + w(2) * t))
    b = int(t / LOOP * 4 * 240)
    bay = BAYER[(YY + b // 4) % 4, (XX + b) % 4] - 0.5
    return dict(noise=noise, noise2=noise2, shadow=shadow, ripple=ripple, bay=bay)

def paint_live(F, L, fld):
    """L: dict(mask, v, p, n=noise amp, s=shadow amp, r=ripple amp)"""
    m = L['mask']
    v = L['v'] + 1.7 * L.get('n', 0.6) * fld['noise'] + 1.9 * L.get('n2', 0.5) * fld['noise2'] + L.get('s', 1.0) * fld['shadow'] + L.get('r', 0) * fld['ripple']
    F[m] = dith(v, L['p'], fld['bay'])[m]

def smooth(s): s = min(1.0, max(0.0, s)); return s * s * (3 - 2 * s)

# ------------------------------------------------------------------ primitive drawing
def put(F, x, y, col, a=1.0):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        F[y, x] = F[y, x] * (1 - a) + col * a

def glow(F, x, y, col, a):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        F[y, x] = np.minimum(1, F[y, x] + col * a)

def rect(F, x0, y0, x1, y1, col, a=1.0):
    x0, y0, x1, y1 = max(0, int(round(x0))), max(0, int(round(y0))), min(W, int(round(x1))), min(H, int(round(y1)))
    if x1 > x0 and y1 > y0:
        F[y0:y1, x0:x1] = F[y0:y1, x0:x1] * (1 - a) + col * a

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

LIGHT = np.array([-0.55, -0.55, 0.63]); LIGHT /= np.linalg.norm(LIGHT)     # moonlight from upper left

def blob(F, cx, cy, rx, ry, p, outline=True, lift=0.0):
    """dithered, shaded ellipse with a dark outline (bodies, heads, balls)."""
    x0, x1 = int(math.floor(cx - rx - 1)), int(math.ceil(cx + rx + 1))
    y0, y1 = int(math.floor(cy - ry - 1)), int(math.ceil(cy + ry + 1))
    x0c, x1c, y0c, y1c = max(0, x0), min(W, x1 + 1), max(0, y0), min(H, y1 + 1)
    if x1c <= x0c or y1c <= y0c: return
    yy, xx = np.mgrid[y0c:y1c, x0c:x1c]
    nx = (xx + 0.5 - cx) / max(rx, 0.5); ny = (yy + 0.5 - cy) / max(ry, 0.5)
    d2 = nx * nx + ny * ny
    inside = d2 <= 1.0
    if not inside.any(): return
    nz = np.sqrt(np.clip(1 - d2, 0, 1))
    shade = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
    v = 0.25 + shade * (len(p) - 1.0) + lift
    idx = np.clip(np.floor(v + BAYER[yy % 4, xx % 4] - 0.5), 0, len(p) - 1).astype(int)
    if outline and min(rx, ry) >= 2:
        edge = d2 > (1 - 1.6 / min(rx, ry)) ** 2
        idx[edge] = 0
    sub = F[y0c:y1c, x0c:x1c]
    sub[inside] = p[idx[inside]]

def line(F, x0, y0, x1, y1, col, thick=1.0, p=None):
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(n + 1):
        s = i / n
        x, y = x0 + (x1 - x0) * s, y0 + (y1 - y0) * s
        if thick <= 1: put(F, x, y, col)
        else:
            r = thick / 2
            for dy in range(-int(r), int(r) + 1):
                for dx in range(-int(r), int(r) + 1):
                    if dx * dx + dy * dy <= r * r + 0.3: put(F, x + dx, y + dy, col)

# ------------------------------------------------------------------ palettes
SKY = pal('#050822', '#081032', '#0c1842', '#112352', '#163063', '#1c3f76', '#244f88', '#2f6298', '#3d76a6', '#5089b0')
MTN = pal('#1a2a52', '#22375f', '#2c466f', '#3a5a84', '#4d7199', '#6a8db0', '#9ab6d0', '#cfe0ef')
SNOW = pal('#5f7ea8', '#7493bb', '#89a7cc', '#a2bedc', '#bcd2ea', '#d6e5f5', '#eef5fd')
PINE = pal('#04140f', '#071f17', '#0b2c20', '#103b2a', '#174d35', '#1f6142', '#2a7650')
PINE_FAR = pal('#0d2236', '#11293f', '#163249', '#1c3c54')
WOOD = pal('#2a120c', '#3e1c12', '#55281a', '#6c3422', '#84432b')
ROOF = pal('#2a1418', '#3d1d22', '#542a2e')
WARM = pal('#7a3a10', '#c2661a', '#f0a43a', '#ffd877', '#fff3c4')
MOON = (40, 138, 12)

# ------------------------------------------------------------------ static layers
def build_sky():
    v = (np.clip(YY / 330, 0, 1) ** 1.15) * (len(SKY) - 1)
    d = np.hypot(XX - MOON[0], YY - MOON[1])
    v = v + 2.2 * np.exp(-(d / 34) ** 2) + 1.0 * np.exp(-(d / 95) ** 2)
    return dict(mask=np.ones((H, W), bool), v=v, p=SKY, n=0.7, n2=0.4, s=0.5)

def draw_moon(F, fld):
    d = np.hypot(XX - MOON[0], YY - MOON[1])
    m = d <= MOON[2]
    sh = np.clip(0.75 + 0.35 * ((XX - MOON[0]) * -0.6 + (YY - MOON[1]) * -0.6) / MOON[2], 0, 1)
    F[m] = dith(sh * 3.2 + 0.5 * fld['noise2'], pal('#b9b39a', '#dcd6bb', '#f2eed8', '#fffdf0'), fld['bay'])[m]

def build_mountains():
    ym = 268 - 26 * np.abs(np.sin(XX / 41 + 0.4)) + 14 * np.sin(XX / 19 + 1) + 6 * np.sin(XX / 7)
    depth = np.clip((YY - ym) / 45, 0, 1)
    lit = np.clip(-(np.cos(XX / 41 + 0.4)) * 0.6 + 0.5, 0, 1)
    mtn = dict(mask=YY >= ym, v=(len(MTN) - 1) * (1 - depth) * (0.55 + 0.45 * lit) + 0.3, p=MTN, n=0.9, n2=0.6, s=1.1)
    yh = 330 + 8 * np.sin(XX / 33 + 2) + 5 * np.sin(XX / 13)
    v = (len(SNOW) - 1.5) - np.clip((YY - yh) / 60, 0, 1) * 3.2 + 0.8 * np.exp(-((XX - 40) / 80) ** 2)
    hill = dict(mask=YY >= yh, v=v - 1.3, p=SNOW, n=0.8, n2=0.6, s=1.2, r=0.35)
    return [mtn, hill]

def build_ground():
    top = GROUND - 1 + np.round(np.sin(XX / 6) * 0.6) - 8 * np.exp(-((XX - 275) / 22) ** 2)
    m = YY >= top
    v = (len(SNOW) - 1.2) - np.clip((YY - GROUND) / 34, 0, 1) * 3.4 + 1.2 * (YY - top < 1.5)
    return [dict(mask=m, v=v - 1.1, p=SNOW, n=0.9, n2=0.7, s=1.2, r=0.6)]

EAVE_X0, EAVE_Y0 = 150, 160
def roof_y(x): return EAVE_Y0 - (x - EAVE_X0) * 0.52

def build_house():
    L = np.zeros((H, W, 4), np.float32)
    lives = []
    wall = (XX >= 156) & (YY >= 166) & (YY < GROUND + 1)
    plank = ((YY - 166) % 7 == 0)
    detail = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in WINDOWS:
        detail |= (XX >= x0 - 2) & (XX < x1 + 2) & (YY >= y0 - 2) & (YY < y1 + 3)
    detail |= (XX >= 172) & (XX < 202) & (YY >= 369)
    detail |= (XX >= 156) & (XX < 159) & (YY >= 164)
    wglow = np.zeros((H, W))
    for x0, y0, x1, y1 in WINDOWS:
        wglow += np.exp(-(np.hypot(XX - (x0 + x1) / 2, YY - (y0 + y1) / 2) / 30) ** 2)
    v = 2.0 + 1.4 * np.clip(1 - (XX - 156) / 60, 0, 1) - 0.8 * plank - 0.4 * ((XX * 13 + (YY // 7) * 29) % 37 < 2) + 0.9 * wglow
    lives.append(dict(mask=wall & ~detail, v=v, p=WOOD, n=0.7, n2=0.5, s=0.9, glow=wglow))
    trim = (XX >= 156) & (XX < 159) & (YY >= 164)
    L[trim, :3] = hexc('#d9cdb8'); L[trim & (XX == 158), :3] = hexc('#a99b84'); L[trim, 3] = 1
    ry = EAVE_Y0 - (XX - EAVE_X0) * 0.52
    roof = (XX >= EAVE_X0) & (YY >= ry) & (YY < 167)
    sh = ((YY + (XX // 5)) % 4 == 0)
    lives.append(dict(mask=roof, v=1.5 - sh * 0.9 + 0 * XX, p=ROOF, n=0.6, n2=0.4, s=0.6))
    sn = (XX >= EAVE_X0 - 2) & (YY >= ry - 5 - 1.2 * np.sin(XX / 4)) & (YY < ry + 3)
    v = 5.2 - np.clip((YY - (ry - 5)) / 8, 0, 1) * 2.5 + 0.8 * np.clip((EAVE_X0 + 40 - XX) / 40, 0, 1)
    lip = (XX >= EAVE_X0 - 3) & (XX < 270) & (YY >= 164) & (YY < 168 + (np.sin(XX * 0.9) > 0.3))
    v = np.where(lip, 4.5, v)
    lives.append(dict(mask=sn | lip, v=v, p=SNOW, n=0.8, n2=0.6, s=1.0, r=0.3))
    ch = (XX >= 226) & (XX < 240) & (YY >= 100) & (YY < ry + 2)
    brick = ((YY % 4 == 0) | (((XX + (YY // 4) * 3) % 7) == 0))
    lives.append(dict(mask=ch, v=np.where(brick, 0.3, 2.0) + (XX < 229) * 1.0, p=pal('#3b1a14', '#6a2c20', '#7a3324', '#a2493a'), n=0.5, n2=0.4, s=0.6))
    cap = (XX >= 224) & (XX < 242) & (YY >= 97) & (YY < 101)
    lives.append(dict(mask=cap, v=np.full((H, W), 5.0), p=SNOW, n=0.8, s=0.8))
    for x0, y0, x1, y1 in WINDOWS:
        fr = (XX >= x0 - 2) & (XX < x1 + 2) & (YY >= y0 - 2) & (YY < y1 + 3)
        L[fr, :3] = hexc('#e8dcc4'); L[fr, 3] = 1
        sill = fr & (YY >= y1 + 1)
        L[sill, :3] = hexc('#eef5fd'); L[fr & (YY == y1 + 2), :3] = hexc('#c8d8ee')
    d = (XX >= 174) & (XX < 200) & (YY >= 372) & (YY < GROUND)
    lives.append(dict(mask=d, v=2.0 - 1.2 * ((XX - 174) < 4) - 0.3 * ((XX - 174) % 6 == 0), p=pal('#0f2a1c', '#173d29', '#205538', '#2b6b46'), n=0.6, s=0.5))
    fr = (XX >= 172) & (XX < 202) & (YY >= 369) & (YY < GROUND) & ~d
    L[fr, :3] = hexc('#e8dcc4'); L[fr, 3] = 1
    L[(XX >= 200) & (XX < 202) & (YY >= 369) & (YY < GROUND), :3] = hexc('#c9bca2')
    L[(YY == 408) & (XX == 195), :3] = hexc('#ffd877')
    return L, lives

WINDOWS = [(176, 192, 200, 220), (226, 192, 250, 220), (222, 296, 254, 332)]

def make_pine(height, width, p, seed, snow=True):
    """layered drooping-branch pine: returns value map, palette-id map (0 none, 1 pine, 2 snow, 3 trunk)."""
    r = np.random.default_rng(seed)
    h, w_ = height + 4, width + 8
    yy, xx = np.mgrid[0:h, 0:w_]
    cx = w_ / 2
    V = np.zeros((h, w_), np.float32); ID = np.zeros((h, w_), np.int8)
    trunk = (np.abs(xx - cx) < max(1.5, width / 18)) & (yy > height - 6)
    ID[trunk] = 3; V[trunk] = 1.0
    tiers = max(4, height // 14)
    noise = r.random((h, w_))
    for k in range(tiers):
        f0 = k / tiers
        top = 2 + f0 * (height - 10) * 0.92
        bot = top + (height - 6) / tiers * 1.9
        hw = (width / 2) * (0.25 + 0.75 * ((k + 1) / tiers))
        s_ = (yy - top) / (bot - top)
        half = hw * np.clip(s_, 0, 1) ** 0.8
        scal = 2.2 * np.abs(np.sin((xx - cx) / max(2.5, hw / 3.2) * math.pi / 2 + k))
        droop = bot - scal - 2 * ((np.abs(xx - cx) / max(hw, 1)) ** 2)
        m = (yy >= top) & (yy <= droop) & (np.abs(xx - cx) <= half + 0.5)
        side = (xx - cx) / max(hw, 1)
        V[m] = (2.6 - 2.0 * side - 1.4 * np.clip(s_, 0, 1) ** 2 + (noise - 0.5) * 1.6 + 0.8 * (1 - np.clip(s_ * 3, 0, 1)))[m]
        ID[m] = 1
        if snow:
            sm = m & (yy <= top + 2 + 2.5 * np.clip(s_ * 4, 0, 1) * np.abs(side)) & (side < 0.75) & (noise > 0.15)
            tip = m & (yy >= droop - 1.4) & (side < 0.6) & (noise > 0.45)
            V[sm | tip] = (4.6 - 1.6 * np.clip(side, 0, 1) + noise)[sm | tip]
            ID[sm | tip] = 2
    return dict(V=V, ID=ID, p=p)

def pine_sprite(pn, t, seed):
    V, ID = pn['V'], pn['ID']
    h, w_ = V.shape
    yy, xx = np.mgrid[0:h, 0:w_]
    o = int(t / LOOP * 256 * 9) % 256
    nz = NZ[(yy * 3 + seed + o) % 256, (xx * 3 + seed * 7) % 256] - 0.5
    b = int(t / LOOP * 4 * 240)
    bay = BAYER[(yy + b // 4) % 4, (xx + b) % 4] - 0.5
    spr = np.zeros((h, w_, 4), np.float32)
    for i, pp in ((1, pn['p']), (2, SNOW), (3, pal('#1a0e08', '#2b1a12', '#3e2618'))):
        m = ID == i
        spr[m, :3] = dith(V + nz * 1.4, pp, bay)[m]; spr[m, 3] = 1
    return spr

def sway_blit(F, spr, x, y, amp, phase):
    """blit a sprite with rows sheared by wind: the top moves, the base stays put."""
    h = spr.shape[0]
    for r in range(h):
        k = 1 - r / h
        dx = int(round(amp * k * k * math.sin(phase + r * 0.05)))
        blend(F, x + dx, y + r, spr[r:r + 1])

SKYL = build_sky()
MOUNTL = build_mountains()
GROUNDL = build_ground()
HOUSE, HOUSEL = build_house()
PINES = [  # (pine, x, y-base, sway amp, sway cycles per loop)
    (make_pine(120, 52, PINE_FAR, 1), -14, 352, 1.0, 5),
    (make_pine(96, 44, PINE_FAR, 2), 54, 350, 0.8, 6),
    (make_pine(150, 70, PINE, 3), -30, GROUND + 2, 1.6, 4),
    (make_pine(108, 52, PINE, 4), 112, GROUND - 40, 1.2, 5),
]

# ------------------------------------------------------------------ pixel font
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

def caption_sprite(text, sc=3, pad=6):
    """plain black box, white text, one pixel trimmed off each corner."""
    tm = text_mask(text, sc)
    th, tw = tm.shape
    bw, bh = tw + 2 * pad, th + 2 * pad
    out = np.zeros((bh, bw, 4), np.float32)
    out[..., 3] = 1
    for cy, cx in ((0, 0), (0, bw - 1), (bh - 1, 0), (bh - 1, bw - 1)):
        out[cy, cx, 3] = 0
    out[pad:pad + th, pad:pad + tw][tm] = [1, 1, 1, 1]
    return out, (pad, pad, tw)

class Caption:
    """slides open from the centre, letters pop in left->right, then dissolves into drifting mist."""
    def __init__(self, text, t_in, t_out, y, seed, sc=3):
        self.s, (px, py, tw) = caption_sprite(text, sc)
        h, w_ = self.s.shape[:2]
        self.x, self.y, self.t_in, self.t_out = (W - w_) // 2, y, t_in, t_out
        r = np.random.default_rng(seed)
        yy, xx = np.mgrid[0:h, 0:w_]
        self.yy, self.xx = yy, xx
        self.vis = self.s[..., 3] > 0
        txt = np.zeros((h, w_), bool)
        txt[py:py + h, px:px + tw] = True
        self.t_app = 0.07 * r.random((h, w_))
        self.t_dis = 0.06 + 0.5 * (0.55 * r.random((h, w_)) + 0.45 * (xx / w_))
        self.dx = (r.random((h, w_)) - 0.25) * 18
        self.dy = -(8 + r.random((h, w_)) * 16)

    def draw(self, F, t):
        for tt in (t, t + LOOP, t - LOOP):
            if self.t_in <= tt <= self.t_out + 1.2:
                self._draw(F, tt)

    def _draw(self, F, t):
        a_in, a_out = t - self.t_in, t - self.t_out
        yoff = 0
        solid = self.vis & (a_in >= self.t_app)
        alpha = self.s[..., 3].copy()
        if a_out > 0:
            age = a_out - self.t_dis
            solid &= age < 0
            flick = self.vis & (age >= -0.14) & (age < 0) & (BAYER[self.yy % 4, self.xx % 4] < (age + 0.14) / 0.14)
            solid &= ~flick
            mist = self.vis & (age >= 0) & (age < 0.6)
            if mist.any():
                ag = age[mist]; k = ag / 0.6
                pxs = self.x + self.xx[mist] + self.dx[mist] * k + 2.5 * np.sin(ag * 8 + self.yy[mist] * 0.7)
                pys = self.y + yoff + self.yy[mist] + self.dy[mist] * k
                col = self.s[..., :3][mist] * 0.35 + np.array([0.78, 0.88, 1.0]) * 0.65
                al = (1 - k) ** 1.6 * 0.6
                ok = (pxs >= 0) & (pxs < W - 0.5) & (pys >= 0) & (pys < H - 0.5)
                xi, yi = np.round(pxs[ok]).astype(int), np.round(pys[ok]).astype(int)
                F[yi, xi] = F[yi, xi] * (1 - al[ok, None]) + col[ok] * al[ok, None]
        ys, xs = np.nonzero(solid)
        X, Y = self.x + xs, int(round(self.y + yoff)) + ys
        ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
        a = alpha[ys[ok], xs[ok]][:, None]
        F[Y[ok], X[ok]] = F[Y[ok], X[ok]] * (1 - a) + self.s[ys[ok], xs[ok], :3] * a

CAPTIONS = []
def cap(text, t_in, t_out):
    CAPTIONS.append(Caption(text, t_in, t_out, 12, 40 + len(CAPTIONS)))

cap("WHAT IF YOU\nDROP A BALL\n4X HIGHER?", 37.4, 39.75)
cap("31 CM DROP:\nA BOUNCE\nEVERY BEAT", 2.3, 5.3)
cap("4X LOWER\n= 2X FASTER", 6.3, 9.3)
cap("4X HIGHER\n= 2X SLOWER", 10.6, 13.4)
cap("FROM THE ROOF\n4.9 M = 1 BAR", 14.3, 17.0)
cap("NOW BOUNCE\nONE ON A\nXYLOPHONE", 17.4, 20.7)
cap("HEIGHT SETS\nTHE RHYTHM", 22.0, 25.3)
cap("THE KEYS\nSET THE NOTES", 26.3, 29.6)
cap("4X HIGHER\nIS ALWAYS\n2X SLOWER", 34.7, 36.85)

# ------------------------------------------------------------------ the droppers and their balls
# ball x, radius, palette, sound hits, release height (m). Hand holds the ball at that height.
BALLS = {
    'cat':   dict(x=77, r=4, p=pal('#3d0a12', '#8a1824', '#d22f3c', '#ff6d6d', '#ffc2c2'), hits=KICK_HITS, period=0.5),
    'mouse': dict(x=40, r=2.5, p=pal('#5a3a08', '#a8700f', '#e8b52a', '#ffe68a'), hits=BELL_HITS, period=0.25),
    'kid':   dict(x=128, r=5, p=pal('#0b3520', '#18663a', '#2db35f', '#7ee39b', '#d8ffe2'), hits=SNARE_HITS, period=1.0),
    'santa': dict(x=141, r=6, p=pal('#0b1a52', '#1c41a3', '#3b80f2', '#86b9ff', '#e0efff'), hits=BASS_HITS, period=2.0),
}
for b in BALLS.values():
    b['hpx'] = height_for(b['period']) * PX_PER_M     # drop height in canvas pixels (ball bottom)

def ball_y(name, t):
    """returns (bottom_y, squash k, state) for a perfectly elastic ball on the beat grid"""
    b = BALLS[name]; hits = b['hits']; T = b['period']
    release, catch = hits[0] - T / 2, hits[-1] + T / 2
    if t < release or t >= catch:
        return GROUND - b['hpx'], 0.0, 'held'
    u = (t - hits[0]) / T
    f = u - math.floor(u)
    y = GROUND - b['hpx'] * 4 * f * (1 - f)
    dn = min(f, 1 - f) * T
    k = max(0.0, 1 - dn / 0.045)
    return y, k, 'air'

def draw_ball(F, name, x, bottom, k=0.0, p=None, r=None):
    b = BALLS.get(name, {})
    p = b['p'] if p is None else p
    r = b['r'] if r is None else r
    rx, ry = r * (1 + 0.35 * k), r * (1 - 0.3 * k)
    blob(F, x, bottom - ry, rx, ry, p)
    hx, hy = x - rx * 0.38, bottom - ry - ry * 0.45
    put(F, hx, hy, np.array([1, 1, 1]))
    if r >= 4.5: put(F, hx + 1, hy, np.array([1, 1, 1]), 0.7)
    if name == 'mouse':  # jingle bell slit
        put(F, x, bottom - 1, hexc('#3a2504')); put(F, x - 1, bottom - 1, hexc('#3a2504'))

def last_hit_age(hits, t):
    i = int(np.searchsorted(hits, t, side='right') - 1)
    return t - hits[i] if i >= 0 else 99.0

def bob(t):
    if 2.0 <= t < 32.3:
        return 1 if last_hit_age(KICK_HITS, t) < 0.13 else 0
    return 0

# ---- characters (procedural pixel art)
GRAY = pal('#2a2c38', '#4c4f60', '#7a7e92', '#a9adbf', '#d4d7e4')
GINGER = pal('#3b1a08', '#7a3a12', '#c2661f', '#ec9442', '#ffc27a')
SKIN = pal('#5a2e22', '#a35d44', '#e3a07c', '#f8cfae')
COAT = pal('#3a0b10', '#6e1420', '#b0222f', '#e2434a', '#ff8a86')
JEANS = pal('#141d3d', '#22305e', '#33467f', '#4c64a3')
SUIT = pal('#3a0b10', '#711420', '#b51d2b', '#e2363f', '#ff7b72')
FUR = pal('#8fa3c4', '#c7d3e6', '#edf2fb', '#ffffff')

def draw_mouse(F, t):
    b = bob(t); x, g = 31, GROUND - b
    tail = [(26, 438), (24, 437), (23, 435), (23, 433), (24, 431)]
    for i, (tx, ty) in enumerate(tail):
        put(F, tx + (1 if i > 2 and math.sin(w(19) * t) > 0 else 0), ty - b, hexc('#d98c9a'))
    blob(F, x, g - 5, 4, 5.5, GRAY)
    blob(F, x + 1, g - 12, 3.6, 3.4, GRAY)
    for ex in (x - 2, x + 3):
        blob(F, ex, g - 16, 1.8, 1.8, GRAY, outline=False); put(F, ex, g - 16, hexc('#e8a0b0'))
    put(F, x + 3, g - 12, hexc('#0a0a12')); put(F, x + 5, g - 11, hexc('#ff8fa6'))
    put(F, x + 1, g - 10, hexc('#d4d7e4'))
    line(F, x + 2, g - 7, x + 7, g - 9 + b, hexc('#7a7e92'))        # arm out to the ball
    put(F, x + 8, g - 9 + b, hexc('#ffb3c1'))
    put(F, x - 1, g, hexc('#ffb3c1')); put(F, x + 2, g, hexc('#ffb3c1'))

def draw_cat(F, t):
    b = bob(t); g = GROUND - b; x = 60
    sw = math.sin(w(38) * t)   # tail swishes on the beat (76 swishes/loop = every beat)
    for i in range(12):
        s = i / 11
        tx = x - 7 - 5 * math.sin(s * 2.2) - sw * 2 * s
        ty = g - 2 - s * 14 + 3 * s * s
        blob(F, tx, ty, 1.6, 1.6, GINGER, outline=False)
    blob(F, x, g - 9, 8, 9.5, GINGER)
    blob(F, x - 3, g - 4, 5, 4, GINGER)
    for i in range(3):
        put(F, x - 5 + i * 2, g - 12 + i, hexc('#7a3a12')); put(F, x - 4 + i * 2, g - 12 + i, hexc('#7a3a12'))
    blob(F, x + 4, g - 22, 6.5, 5.8, GINGER)
    for ex, sgn in ((x, -1), (x + 7, 1)):            # ears
        for k in range(4):
            for j in range(-(3 - k) // 2, (3 - k) // 2 + 1):
                put(F, ex + j + sgn * 0, g - 27 - k, hexc('#c2661f') if k < 3 else hexc('#7a3a12'))
        put(F, ex, g - 27, hexc('#ff9eb0'))
    lk = -1 if (5.3 < t < 7.2 or 16.5 < t < 18.6) else 0       # glance at the mouse / the robin
    put(F, x + 6, g - 23, hexc('#9cff6a')); put(F, x + 6 + lk, g - 22 + (lk != 0) * -1, hexc('#0a0a12'))
    put(F, x + 2, g - 23, hexc('#9cff6a')); put(F, x + 2 + lk, g - 22 + (lk != 0) * -1, hexc('#0a0a12'))
    put(F, x + 9, g - 20, hexc('#ff8fa6'))
    for k in (-1, 1):
        line(F, x + 10, g - 20 + k, x + 13, g - 21 + 2 * k, hexc('#ffe8d0'))
    blob(F, x + 3, g - 15, 3, 2.5, pal('#d8c8b0', '#f0e6d8', '#ffffff'), outline=False)   # chest
    line(F, x + 5, g - 13, x + 15, g - 26 + b, hexc('#c2661f'), thick=2.6)               # raised paw
    blob(F, x + 17, g - 28 + b, 2.4, 2.0, GINGER, outline=False)
    put(F, x - 2, g, hexc('#ffc27a')); put(F, x + 4, g, hexc('#ffc27a'))

def draw_kid(F, t):
    b = bob(t); g = GROUND - b; x = 104
    for bx in (x - 5, x + 3):                                   # boots
        rect(F, bx - 1, g - 7, bx + 6, g, hexc('#2a1610')); rect(F, bx - 1, g - 7, bx + 6, g - 6, hexc('#e7eef9'))
        rect(F, bx, g - 6, bx + 2, g - 1, hexc('#4a2c1c'))
    for lx in (x - 5, x + 3):                                   # legs
        for yy in range(int(g - 31), int(g - 7)):
            for xx in range(lx, lx + 5):
                put(F, xx, yy, JEANS[min(3, max(0, int(1 + (xx - lx) * -0.4 + 2 + BAYER[yy % 4, xx % 4] - 0.5)))])
    blob(F, x, g - 46, 11, 17, COAT)                           # puffer coat
    for k in range(3):
        line(F, x - 9, g - 52 + k * 8, x + 9, g - 52 + k * 8, hexc('#6e1420'))
    rect(F, x - 1, g - 62, x + 1, g - 31, hexc('#e7c35a'), 0.9)  # zipper
    line(F, x - 8, g - 50, x - 10, g - 34, hexc('#b0222f'), thick=4)   # far arm down
    blob(F, x - 10, g - 33, 2.6, 2.6, pal('#1c4a2a', '#2d7a44', '#4aa864'))
    ph = math.sin(w(19) * t) * 1.2                                # scarf flaps in the wind
    rect(F, x - 7, g - 64, x + 8, g - 60, hexc('#2db35f'))
    for k in range(9):
        put(F, x - 7 - k * 0.6 + ph * k / 8, g - 60 + k, hexc('#2db35f')); put(F, x - 6 - k * 0.6 + ph * k / 8, g - 60 + k, hexc('#18663a'))
    blob(F, x + 1, g - 71, 7, 7, SKIN, lift=0.9)                # head
    rect(F, x - 6, g - 76, x - 2, g - 66, hexc('#3b2416'))     # hair (back of head)
    put(F, x - 3, g - 66, hexc('#3b2416')); put(F, x - 2, g - 76, hexc('#3b2416'))
    up = 2 if 12.2 < t < 14.4 else 0                         # looks up at Santa
    dn = 16.5 < t < 18.6                                       # then down at the robin
    put(F, x + 4 - dn, g - 72 - up + dn, hexc('#14141c')); put(F, x + 4 - dn, g - 73 - up + dn, hexc('#14141c'))
    put(F, x + 5, g - 69, hexc('#ff8f8f'), 0.8); put(F, x + 6, g - 69, hexc('#ff8f8f'), 0.6)
    put(F, x + 7, g - 68, hexc('#a35d44'))
    blob(F, x, g - 78, 8, 4.5, COAT)                            # beanie
    rect(F, x - 8, g - 77, x + 9, g - 74, hexc('#f2f5fb'))
    blob(F, x - 3, g - 85, 3, 3, FUR)                           # pom-pom
    line(F, x + 6, g - 58, x + 22, g - 83 + b, hexc('#b0222f'), thick=4.2)   # raised arm
    blob(F, x + 24, g - 86 + b, 3.2, 3, pal('#1c4a2a', '#2d7a44', '#4aa864', '#7ccf8f'))

def draw_santa(F, t):
    b = bob(t); x = 168; base = roof_y(x) + 2 - b
    for bx in (150, 157):                                       # legs over the eave, boots dangling
        line(F, x - 6, base - 5, bx + 3, base - 4, hexc('#b51d2b'), thick=5)
        sway = math.sin(w(19) * t + bx) * 0.8
        rect(F, bx + sway, base - 4, bx + 5 + sway, base + 10, hexc('#14141c'))
        rect(F, bx - 1 + sway, base + 8, bx + 6 + sway, base + 11, hexc('#2a2a36'))
        rect(F, bx + sway, base - 4, bx + 5 + sway, base - 2, hexc('#edf2fb'))
    blob(F, x, base - 15, 11, 13, SUIT)
    rect(F, x - 10, base - 12, x + 10, base - 9, hexc('#14141c'))
    rect(F, x - 2, base - 13, x + 3, base - 8, hexc('#ffd24a')); rect(F, x - 1, base - 12, x + 2, base - 9, hexc('#14141c'))
    rect(F, x - 1, base - 27, x + 1, base - 13, hexc('#edf2fb'))
    blob(F, x + 1, base - 33, 6.5, 6.5, SKIN)
    blob(F, x, base - 27, 7.5, 6.5, FUR)                        # beard
    blob(F, x - 3, base - 31, 3, 1.6, FUR, outline=False); blob(F, x + 3, base - 31, 3, 1.6, FUR, outline=False)
    put(F, x - 2, base - 35, hexc('#14141c')); put(F, x + 3, base - 35, hexc('#14141c'))
    put(F, x, base - 32, hexc('#e8907a'))
    rect(F, x - 7, base - 40, x + 9, base - 37, hexc('#edf2fb'))       # hat trim
    for k in range(12):                                         # floppy hat
        s = k / 11
        hx = x - 5 + s * 15 + 3 * s * s
        hy = base - 41 - 7 * math.sin(s * 2.3) + 4 * s * s
        blob(F, hx, hy, 4.5 - s * 3, 3.6 - s * 2.4, SUIT, outline=False)
    blob(F, x + 13, base - 41 + math.sin(w(19) * t) * 0.6, 2.4, 2.4, FUR)
    line(F, x - 7, base - 20, x - 23, base - 20 + b, hexc('#b51d2b'), thick=4.4)    # arm reaching out
    rect(F, x - 23, base - 23 + b, x - 20, base - 17 + b, hexc('#edf2fb'))
    blob(F, x - 27, base - 21 + b, 3.2, 3, pal('#101016', '#24242e', '#3a3a48'))

# ------------------------------------------------------------------ xylophone + robin
KEY_X = [34, 52, 70, 88, 106]
KEY_TOP = 452
KEYS = [(hexc(c), hexc(d), h) for c, d, h in
        [('#ff4d5e', '#a3202e', 17), ('#ff9a3c', '#a8531a', 15), ('#ffd84a', '#a8861a', 13),
         ('#5fe07a', '#21803a', 12), ('#4fb0ff', '#1d5ea8', 11)]]

def key_age(i, t):
    ages = [t - mt for mt, n, _ in MELODY if PRESENT_INDEX[n] == i and 0 <= t - mt < 0.5]
    return min(ages) if ages else 9.0

def draw_xylophone(F, t):
    rect(F, 22, 459, 120, 462, hexc('#5a3220')); rect(F, 22, 466, 120, 469, hexc('#5a3220'))
    rect(F, 22, 459, 120, 460, hexc('#8a5636')); rect(F, 22, 466, 120, 467, hexc('#8a5636'))
    for lx in (24, 116):
        rect(F, lx, 459, lx + 3, 474, hexc('#3e2114'))
    for i, (col, dark, h) in enumerate(KEYS):
        a = key_age(i, t)
        dip = 1 if a < 0.06 else 0
        x0 = KEY_X[i] - 7
        for yy in range(KEY_TOP + dip, KEY_TOP + h + dip):
            for xx in range(x0, x0 + 14):
                edge = xx == x0 or yy == KEY_TOP + h + dip - 1
                c = dark if edge else (col if (xx - x0) > 2 or BAYER[yy % 4, xx % 4] > 0.5 else dark)
                put(F, xx, yy, c)
        rect(F, x0 + 1, KEY_TOP + dip, x0 + 13, KEY_TOP + 1 + dip, np.minimum(1, col + 0.35))
        put(F, x0 + 7, KEY_TOP + 3 + dip, hexc('#e8e8f0')); put(F, x0 + 7, KEY_TOP + h - 4 + dip, hexc('#e8e8f0'))
        if a < 0.35:
            rect(F, x0, KEY_TOP + dip, x0 + 14, KEY_TOP + h + dip, np.array([1, 1, 0.95]), 0.65 * math.exp(-a / 0.08))

MEL_R = 4
MEL_P = pal('#3b4252', '#79849a', '#c6cedc', '#eef2f8', '#ffffff')
def melody_ball(t):
    hits = [m[0] for m in MELODY]
    land = [KEY_X[PRESENT_INDEX[n]] for _, n, _ in MELODY]
    if t < 17.6: return None
    if t < hits[0]:                                    # dropped by the robin
        s = (t - 17.6) / 0.4
        return 70, 425 + (KEY_TOP - 425) * s * s, 0.0
    if t >= 35.25: return None                         # carried away by the robin
    i = int(np.searchsorted(hits, t, side='right') - 1)
    dn = min(abs(t - hits[i]), abs(hits[i + 1] - t) if i + 1 < len(hits) else 9)
    k = max(0.0, 1 - dn / 0.045)
    if i + 1 >= len(hits):
        return land[-1], KEY_TOP, k
    T = hits[i + 1] - hits[i]; s = (t - hits[i]) / T
    hgt = min(46, 10 + 30 * T)
    return land[i] + (land[i + 1] - land[i]) * smooth(s), KEY_TOP - 4 * hgt * s * (1 - s), k

def robin_pos(t):
    if t < 16.6 or t >= 37.0: return None
    if t < 17.6:
        s = smooth((t - 16.6) / 1.0); return -10 + 80 * s, 370 + 50 * s - 22 * math.sin(s * math.pi), True
    if t < 18.4:
        s = smooth((t - 17.6) / 0.8); return 70 + 58 * s, 420 + 30 * s - 14 * math.sin(s * math.pi), True
    if t < 34.6:
        return 128, 450, False
    if t < 35.25:
        s = smooth((t - 34.6) / 0.65); return 128 - 94 * s, 450 - 4 - 16 * math.sin(s * math.pi), True
    s = smooth((t - 35.25) / 1.75); return 34 - 50 * s, 446 - 90 * s, True

def draw_robin(F, t):
    p = robin_pos(t)
    if p is None: return
    x, y, flying = p
    hop = 0 if flying else bob(t)
    y -= hop
    face = -1 if (34.6 <= t) else 1
    blob(F, x, y - 3, 4.2, 3.4, pal('#2a1a10', '#4e3220', '#7a5234', '#a3754c'))
    blob(F, x + 1.5 * face, y - 2, 2.4, 2.2, pal('#8a2a10', '#d8541e', '#ff8a3c'), outline=False)
    blob(F, x + 3 * face, y - 6, 2.4, 2.3, pal('#2a1a10', '#4e3220', '#7a5234'))
    put(F, x + 4 * face, y - 7, hexc('#0a0a12'))
    put(F, x + 5.5 * face, y - 6, hexc('#f2c14e')); put(F, x + 6.5 * face, y - 6, hexc('#c98e20'))
    for k in range(3): put(F, x - (5 + k) * face, y - 3 - k * 0.5, hexc('#4e3220'))
    if flying:
        up = math.sin(t * 60) > 0
        for k in range(4):
            put(F, x - 1 + k * 0.5 * face, y - 6 - (k if up else -k + 1), hexc('#6a4428'))
    else:
        put(F, x - 1, y + 1, hexc('#c98e20')); put(F, x + 1, y + 1, hexc('#c98e20'))
    if t >= 35.25:   # carrying the ball home
        draw_ball(F, 'melody', x, y + 4, 0, MEL_P, MEL_R)

# ------------------------------------------------------------------ living background
rng = np.random.default_rng(11)
STARS = [(rng.uniform(0, W), rng.uniform(100, 250), int(rng.integers(2, 9)), rng.uniform(0, 6.28)) for _ in range(80)]
FLAKES = [(rng.uniform(0, W), rng.uniform(0, H), int(rng.integers(3, 7)), int(rng.integers(1, 4)), rng.uniform(0, 6.28), rng.random()) for _ in range(170)]
GLINTS = [(rng.uniform(0, W), rng.uniform(GROUND + 1, 476), int(rng.integers(3, 12)), rng.uniform(0, 6.28)) for _ in range(60)]
VILLAGE = [(rng.uniform(0, 150), rng.uniform(300, 330), int(rng.integers(2, 7)), rng.uniform(0, 6.28)) for _ in range(14)]
DRIFT = [(rng.uniform(0, W), rng.uniform(GROUND - 6, GROUND + 26), int(rng.integers(5, 10)), rng.uniform(0, 6.28)) for _ in range(46)]
CLOUDS = [(rng.uniform(0, W + 120), rng.uniform(150, 240), rng.uniform(26, 44), int(rng.integers(1, 3))) for _ in range(5)]
AUR_Y = np.arange(80, 300)[:, None]; AUR_X = np.arange(W)[None, :]
AURP = pal('#0f3a4a', '#13625a', '#1c8f6c', '#3fc08a', '#8af0b8')

def draw_sky_life(F, t):
    # aurora: drifting curtains of light that swell with every bass bounce
    pulse = 0.35 * math.exp(-last_hit_age(BASS_HITS, t) / 0.5) if 14 <= t < 34 else 0
    pulse += 0.5 * math.exp(-(t - 35.0) / 0.8) if t >= 35.0 else 0
    c = 175 + 22 * np.sin(AUR_X / 46 + w(3) * t) + 10 * np.sin(AUR_X / 17 - w(5) * t)
    band = np.exp(-((AUR_Y - c) / 30) ** 2)
    rays = 0.72 + 0.28 * np.sin(AUR_X * 0.45 + w(7) * t + np.sin(AUR_X / 9) * 2)
    fade = np.clip(1 - np.abs(AUR_X - 70) / 200, 0, 1)
    I = band * rays * fade * (0.5 + pulse)
    lvl = np.clip(np.floor(I * 5 + BAYER[AUR_Y % 4, AUR_X % 4] - 0.5), 0, 4).astype(int)
    col = AURP[lvl] * (lvl > 0)[..., None]
    F[80:300] = np.minimum(1, F[80:300] + col * 0.45)
    for x, y, k, ph in STARS:
        if math.hypot(x - MOON[0], y - MOON[1]) < 22: continue
        b = 0.5 + 0.5 * math.sin(w(k) * t + ph)
        put(F, x, y, np.array([0.9, 0.94, 1.0]), 0.2 + 0.7 * b)
        if b > 0.92: glow(F, x + 1, y, np.array([0.5, 0.6, 0.8]), 0.3); glow(F, x - 1, y, np.array([0.5, 0.6, 0.8]), 0.3)
    for cx0, cy, rw, k in CLOUDS:   # thin clouds sliding past the moon
        cx = (cx0 + (W + 120) * k * t / LOOP) % (W + 120) - 60
        for dx in range(int(-rw), int(rw)):
            yy = int(cy + 2 * math.sin(dx * 0.3))
            th = (1 - (dx / rw) ** 2) * 5
            for dy in range(int(-th / 2), int(th / 2) + 1):
                if BAYER[(yy + dy) % 4, int(cx + dx) % 4] < 0.4:
                    put(F, cx + dx, yy + dy, hexc('#5b6f9a'), 0.55)

def draw_pines(F, t):
    for spr, x, base, amp, k in PINES:
        sway_blit(F, spr, x, base - spr.shape[0], amp, w(k) * t + x)

def draw_village(F, t):
    for x, y, k, ph in VILLAGE:
        b = 0.6 + 0.4 * math.sin(w(k) * t + ph)
        put(F, x, y, hexc('#ffd877'), b); glow(F, x, y - 1, hexc('#ffb347'), 0.2 * b)

def draw_house_life(F, t):
    # glass: warm dithered glow that flickers like firelight, brighter on snare hits
    sn = 0.25 * math.exp(-last_hit_age(SNARE_HITS, t) / 0.18) if 10 <= t < 32.5 else 0
    for wi, (x0, y0, x1, y1) in enumerate(WINDOWS):
        fl = 0.15 * math.sin(w(23 + wi * 4) * t) + 0.08 * math.sin(w(57 + wi) * t)
        chime = 0.5 * math.exp(-(t - RETURN[['bell', 'kick', 'snare'][wi]]) / 0.3) if t >= RETURN[['bell', 'kick', 'snare'][wi]] else 0
        yy, xx = np.mgrid[y0:y1, x0:x1]
        v = 2.4 + 1.3 * (1 - (yy - y0) / (y1 - y0)) + fl * 3 + sn * 4 + chime * 3
        F[y0:y1, x0:x1] = dith(v, WARM, BAYER[yy % 4, xx % 4] - 0.5)
        mx, my = (x0 + x1) // 2, (y0 + y1) // 2
        rect(F, mx - 1, y0, mx + 1, y1, hexc('#e8dcc4')); rect(F, x0, my - 1, x1, my, hexc('#e8dcc4'))
        if wi == 2:   # little tree inside
            for k in range(10):
                rect(F, mx + 7 - k * 0.6, y1 - 14 + k, mx + 8 + k * 0.6, y1 - 13 + k, hexc('#1f5a34'))
            put(F, mx + 7, y1 - 15, hexc('#ffe27a'))
        # light spilling onto the snow below
        for k in range(1, 7):
            for xx2 in range(x0 - k, x1 + k):
                if BAYER[(y1 + 3 + k) % 4, xx2 % 4] < 0.35 * (1 - k / 7) * (1 + fl + sn):
                    glow(F, xx2, y1 + 3 + k, hexc('#ffb347'), 0.25)
    # a few warm lights along the eave, gently twinkling (brighter at the finale)
    finale = math.exp(-(t - 35.0) / 0.6) if t >= 35.0 else 0
    for j, x in enumerate(range(154, 270, 9)):
        y = roof_y(x) + 9 + 1.2 * math.sin(j * 1.3)
        b = min(1, 0.6 + 0.25 * math.sin(w(11) * t + j * 2.1) + finale)
        c = hexc('#ffd877')
        put(F, x, y, c * (0.5 + 0.5 * b))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): glow(F, x + dx, y + dy, c, 0.35 * b)
    # icicles glint one after another
    for j, x in enumerate(range(153, 270, 5)):
        ln = 2 + (j * 7) % 4
        yb = 168
        for k in range(ln): put(F, x, yb + k, hexc('#cfe6ff'), 0.85 - k * 0.15)
        if 0.5 + 0.5 * math.sin(w(9) * t - j * 0.7) > 0.95: glow(F, x, yb + ln - 1, np.array([1, 1, 1]), 0.8)
    # wreath on the door, bow bounces on the bass
    bb = 1 if last_hit_age(BASS_HITS, t) < 0.12 and 14 <= t < 32.3 else 0
    for k in range(28):
        th = k / 28 * TAU
        put(F, 187 + 7 * math.cos(th), 388 + 7 * math.sin(th), hexc('#1f6a3a') if k % 3 else hexc('#2f8a4a'))
        put(F, 187 + 6 * math.cos(th), 388 + 6 * math.sin(th), hexc('#174d2c'))
        if k % 5 == 0: put(F, 187 + 6.5 * math.cos(th), 388 + 6.5 * math.sin(th), hexc('#ff4d5e'))
    for dx, dy in ((-2, 0), (-1, 1), (1, 1), (2, 0), (0, 1), (0, 2), (-1, 3), (1, 3)):
        put(F, 187 + dx, 394 + dy - bb, hexc('#d22f3c'))
    # chimney smoke: soft puffs drifting with the wind
    for k in range(14):
        ph = (t / LOOP * 9 + k / 14) % 1.0
        sx = 233 + ph * 26 + 4 * math.sin(ph * 7 + k)
        sy = 96 - ph * 70
        r = 2 + ph * 6
        a = 0.35 * (1 - ph) * min(1, ph * 8)
        for dy in range(int(-r), int(r) + 1):
            for dx in range(int(-r), int(r) + 1):
                if dx * dx + dy * dy <= r * r and BAYER[int(sy + dy) % 4, int(sx + dx) % 4] < 0.55:
                    put(F, sx + dx, sy + dy, hexc('#8a9ab8'), a)

def draw_ground_life(F, t):
    for x, y, k, ph in GLINTS:                       # snow crystals catching the moonlight
        b = 0.5 + 0.5 * math.sin(w(k) * t + ph)
        if b > 0.8:
            glow(F, x, y, np.array([1, 1, 1]), (b - 0.8) * 4)
            if b > 0.96:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): glow(F, x + dx, y + dy, np.array([0.7, 0.85, 1]), 0.4)

SNOWFALL = [(rng.uniform(-20, W + 20), rng.uniform(GROUND + 1, 472), int(rng.integers(2, 5)), rng.random(), rng.uniform(0, 6.28), rng.random() < 0.2)
            for _ in range(190)]
def draw_snowfall(F, t):
    for x0, yland, n, ph0, ph, big in SNOWFALL:
        cyc = LOOP / n                       # each flake: fall from above the sky, land, sit, melt
        tau = ((t / cyc + ph0) % 1.0) * cyc
        fall = (yland + 12) / 34.0
        c = np.array([0.94, 0.97, 1.0])
        if tau < fall:
            y = -12 + 34.0 * tau
            x = x0 + 5 * math.sin(tau * 1.7 + ph) + 6 * tau
            put(F, x, y, c, 0.95 if big else 0.6)
            if big: put(F, x + 1, y, c, 0.8); put(F, x, y + 1, c, 0.8); put(F, x + 1, y + 1, c, 0.5)
        else:
            a = tau - fall
            x = x0 + 5 * math.sin(fall * 1.7 + ph) + 6 * fall
            k = max(0.0, 1 - a / 1.6)
            if k > 0:
                put(F, x, yland, np.array([1, 1, 1]), 0.9 * k)
                if big: put(F, x + 1, yland, c, 0.7 * k)

def draw_impacts(F, t):
    for name, life, n, spd in (('cat', 0.35, 6, 26), ('mouse', 0.22, 3, 12), ('kid', 0.4, 8, 34), ('santa', 0.6, 12, 46)):
        b = BALLS[name]
        for hi, h in enumerate(b['hits']):
            a = t - h
            if not 0 <= a < life: continue
            r = np.random.default_rng(hi * 31 + len(name))
            for k in range(n):
                vx = (r.random() - 0.5) * spd * 2; vy = -r.random() * spd - 6
                px = b['x'] + vx * a; py = GROUND - 1 + vy * a + 70 * a * a
                if py <= GROUND + 1: put(F, px, min(py, GROUND - 1), np.array([0.96, 0.98, 1.0]), 1 - a / life)
            if name in ('kid', 'santa'):                 # ripple across the snow
                rr = 3 + (30 if name == 'santa' else 16) * a / life
                for k in range(56):
                    th = k / 56 * TAU
                    put(F, b['x'] + rr * math.cos(th), GROUND + 1.5 + rr * 0.16 * math.sin(th), np.array([1, 1, 1]), 0.6 * (1 - a / life))
            if name == 'kid' and a < 0.15:               # snare snap: star burst
                for dx, dy in ((1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1)):
                    for k in range(3, int(4 + a / 0.15 * 8)):
                        glow(F, b['x'] + dx * k, GROUND - 5 + dy * k, hexc('#c8ffd8'), 0.7 * (1 - a / 0.15))
    note = np.array([[c == '1' for c in r] for r in NOTE])
    ys, xs = np.nonzero(note)
    for mi, (mt, n, d) in enumerate(MELODY):
        a = t - mt
        if not 0 <= a < 0.8: continue
        i = PRESENT_INDEX[n]; x = KEY_X[i]
        col = KEYS[i][0]
        r = np.random.default_rng(900 + mi)
        for k in range(7):
            vx = (r.random() - 0.5) * 60; vy = -22 - r.random() * 30
            if a < 0.45: glow(F, x + vx * a, KEY_TOP - 2 + vy * a + 70 * a * a, col, 0.9 * (1 - a / 0.45))
        u = np.random.default_rng(mi).random(len(ys))
        for y, xx, uu in zip(ys, xs, u):
            if uu > (a / 0.8) ** 1.4:
                put(F, x - 2 + xx + 4 * math.sin(a * 6), KEY_TOP - 14 - 26 * a + y, col)

def draw_shadow(F, x, bottom, r):
    hgt = GROUND - bottom
    hw = r * (1.2 - 0.6 * min(1, hgt / 150))
    for xx in range(int(x - hw), int(x + hw) + 1):
        if BAYER[GROUND % 4, xx % 4] < 0.75 - 0.35 * min(1, hgt / 150): put(F, xx, GROUND, hexc('#6f8bb8'), 0.8)

# ------------------------------------------------------------------ frame
# camera keyframes (time, centre x, centre y, zoom). Zoom 1 = whole scene, 2 = close-up.
CAM = [(0.0, 62, 400, 3), (5.3, 62, 400, 3), (5.95, 44, 410, 3), (9.4, 44, 410, 3),
       (10.05, 106, 372, 2), (12.2, 106, 372, 2), (12.85, 160, 150, 2), (13.05, 160, 150, 2),
       (14.0, 135, 240, 1), (16.5, 135, 240, 1), (17.6, 72, 440, 3), (25.6, 72, 440, 3),
       (26.6, 90, 400, 1.5), (29.6, 90, 400, 1.5), (30.6, 135, 240, 1), (36.9, 135, 240, 1),
       (37.85, 62, 400, 3), (38.0, 62, 400, 3)]

def camera(t):
    for (t0, x0, y0, z0), (t1, x1, y1, z1) in zip(CAM, CAM[1:]):
        if t0 <= t <= t1:
            s = smooth((t - t0) / max(1e-6, t1 - t0))
            z = math.exp(math.log(z0) + (math.log(z1) - math.log(z0)) * s)
            return x0 + (x1 - x0) * s, y0 + (y1 - y0) * s, z
    return CAM[0][1:]

OX = (np.arange(W * S) + 0.5) / S
OY = (np.arange(H * S) + 0.5) / S
def shoot(F, t):
    cx, cy, z = camera(t)
    vw, vh = W / z, H / z
    cx = min(max(cx, vw / 2), W - vw / 2); cy = min(max(cy, vh / 2), H - vh / 2)
    xi = np.clip(np.floor(cx - vw / 2 + OX / z).astype(int), 0, W - 1)
    yi = np.clip(np.floor(cy - vh / 2 + OY / z).astype(int), 0, H - 1)
    return F[yi][:, xi]

def frame(t):
    fld = live_fields(t)
    F = np.zeros((H, W, 3), np.float32)
    paint_live(F, SKYL, fld)
    draw_sky_life(F, t)
    draw_moon(F, fld)
    for L in MOUNTL: paint_live(F, L, fld)
    for i, (pn, x, base, amp, k) in enumerate(PINES):
        sway_blit(F, pine_sprite(pn, t, i * 53), x, base - pn['V'].shape[0], amp, w(k) * t + x)
    blend(F, 0, 0, HOUSE)
    fl = 0.35 * math.sin(w(23) * t) + 0.2 * math.sin(w(57) * t)
    for L in HOUSEL:
        if 'glow' in L:
            L2 = dict(L); L2['v'] = L['v'] + fl * L['glow']; paint_live(F, L2, fld)
        else:
            paint_live(F, L, fld)
    draw_house_life(F, t)
    for L in GROUNDL: paint_live(F, L, fld)
    draw_ground_life(F, t)
    states = {n: ball_y(n, t) for n in BALLS}
    for n, (by, k, st) in states.items():
        if st == 'air': draw_shadow(F, BALLS[n]['x'], by, BALLS[n]['r'])
    draw_mouse(F, t); draw_cat(F, t); draw_kid(F, t); draw_santa(F, t)
    draw_impacts(F, t)
    for n, (by, k, st) in states.items():
        draw_ball(F, n, BALLS[n]['x'], by - (bob(t) if st == 'held' else 0), k)
    draw_xylophone(F, t)
    mb = melody_ball(t)
    if mb: draw_ball(F, 'melody', mb[0], mb[1], mb[2], MEL_P, MEL_R)
    draw_robin(F, t)
    draw_snowfall(F, t)
    out = shoot(F, t)
    # captions live in screen space (they do not zoom with the camera)
    scr = out[::S, ::S].copy(); before = scr.copy()
    for c in CAPTIONS: c.draw(scr, t)
    ch = np.any(np.abs(scr - before) > 1e-6, axis=2)
    if ch.any():
        big = np.repeat(np.repeat(ch, S, 0), S, 1)
        out[big] = np.repeat(np.repeat(scr, S, 0), S, 1)[big]
    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)

def upscale(img): return np.repeat(np.repeat(img, S, 0), S, 1)

if __name__ == '__main__':
    if sys.argv[1] == '--stills':
        from PIL import Image
        for ts in sys.argv[3:]:
            Image.fromarray(frame(float(ts))).save(f'{sys.argv[2]}/still_{float(ts):06.2f}.png')
        sys.exit()
    out, wav = sys.argv[1], sys.argv[2]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W*S}x{H*S}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    nfr = int(LOOP * FPS)
    for f in range(nfr):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 300 == 0: print('frame', f, '/', nfr, flush=True)
    p.stdin.close(); p.wait()
    print('done', out)
