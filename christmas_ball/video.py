"""Renders 'What If You Drop a Ball 4x Higher?' - 1080x1920 / 60 fps pixel art.

Only balls, snow, mountains, trees and sky. The world is drawn on a 270x480 canvas;
a camera picks one ball at a time and scales the view up with nearest-neighbour
sampling. Every surface - sky, ground, trees and the balls themselves - is re-dithered
each frame with drifting noise and lit by the balls' glow, so no pixel is ever frozen.
All motion is driven by score.py, so each landing hits the exact frame of its sound.

usage: python3 video.py out.mp4 audio.wav
       python3 video.py --stills DIR t1 t2 ...
"""
import sys, subprocess, math
import numpy as np
from score import *

W, H, S = 270, 480, 4
GROUND = 440
LANE = 458                       # where the melody ball lands (a little closer to camera)
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

CUR = {}                            # per-frame dither crawl shared by everything
def live_fields(t):
    ox, oy = int(t / LOOP * 256 * 7) % 256, int(t / LOOP * 256 * 4) % 256
    sx, sy = int(t / LOOP * 256 * 2) % 256, int(t / LOOP * 256 * 1) % 256
    b = int(t / LOOP * 4 * 240)
    CUR['b'] = b; CUR['o'] = (ox, oy)
    return dict(noise=NZ[(YY + oy) % 256, (XX + ox) % 256] - 0.5,
                noise2=NZ[(YY * 2 + 37 - oy * 3) % 256, (XX * 2 + 91 + ox * 2) % 256] - 0.5,
                shadow=1.1 * (NZB[(YY // 2 + sy) % 256, (XX // 2 + sx) % 256] - 0.5),
                bay=BAYER[(YY + b // 4) % 4, (XX + b) % 4] - 0.5)

def paint_live(F, L, fld, extra=None):
    m = L['mask']
    v = L['v'] + 1.7 * L.get('n', 0.6) * fld['noise'] + 1.9 * L.get('n2', 0.5) * fld['noise2'] + L.get('s', 1.0) * fld['shadow']
    if extra is not None: v = v + extra
    F[m] = dith(v, L['p'], fld['bay'])[m]

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

LIGHT = np.array([-0.55, -0.55, 0.63]); LIGHT /= np.linalg.norm(LIGHT)

def ball_pixels(cx, cy, rx, ry, p):
    """shaded sphere whose dither crawls and shimmers every frame -> (ys, xs, colours)"""
    x0, x1 = int(math.floor(cx - rx - 1)), int(math.ceil(cx + rx + 1))
    y0, y1 = int(math.floor(cy - ry - 1)), int(math.ceil(cy + ry + 1))
    yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
    nx = (xx + 0.5 - cx) / rx; ny = (yy + 0.5 - cy) / ry
    d2 = nx * nx + ny * ny
    inside = d2 <= 1.0
    nz = np.sqrt(np.clip(1 - d2, 0, 1))
    shade = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
    b = CUR.get('b', 0); ox, oy = CUR.get('o', (0, 0))
    v = 0.3 + shade * (len(p) - 1.2) + 0.9 * (NZ[(yy * 3 + oy * 2) % 256, (xx * 3 + ox * 2) % 256] - 0.5)
    idx = np.clip(np.floor(v + BAYER[(yy + b // 4) % 4, (xx + b) % 4] - 0.5), 0, len(p) - 1).astype(int)
    idx[d2 > (1 - 1.4 / min(rx, ry)) ** 2] = 0
    col = p[idx]
    hx, hy = int(round(cx - rx * 0.4)), int(round(cy - ry * 0.45))
    spec = (yy == hy) & (np.abs(xx - hx) <= (1 if rx > 5 else 0))
    col[spec & inside] = [1, 1, 1]
    return yy[inside], xx[inside], col[inside]

def draw_pixels(F, ys, xs, col, alpha=1.0):
    ok = (xs >= 0) & (xs < W) & (ys >= 0) & (ys < H)
    F[ys[ok], xs[ok]] = F[ys[ok], xs[ok]] * (1 - alpha) + col[ok] * alpha

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


# ------------------------------------------------------------------ palettes & layers
SKY = pal('#050822', '#081032', '#0c1842', '#112352', '#163063', '#1c3f76', '#244f88', '#2f6298', '#3d76a6', '#5089b0')
MTN = pal('#1a2a52', '#22375f', '#2c466f', '#3a5a84', '#4d7199', '#6a8db0', '#9ab6d0', '#cfe0ef')
SNOW = pal('#5f7ea8', '#7493bb', '#89a7cc', '#a2bedc', '#bcd2ea', '#d6e5f5', '#eef5fd')
PINE = pal('#04140f', '#071f17', '#0b2c20', '#103b2a', '#174d35', '#1f6142', '#2a7650')
PINE_FAR = pal('#0d2236', '#11293f', '#163249', '#1c3c54')
MOON = (52, 120, 12)

def build_sky():
    v = (np.clip(YY / 330, 0, 1) ** 1.15) * (len(SKY) - 1)
    d = np.hypot(XX - MOON[0], YY - MOON[1])
    v = v + 2.2 * np.exp(-(d / 34) ** 2) + 1.0 * np.exp(-(d / 95) ** 2)
    return dict(mask=np.ones((H, W), bool), v=v, p=SKY, n=0.45, n2=0.3, s=0.2)

def build_mountains():
    ym = 268 - 26 * np.abs(np.sin(XX / 41 + 0.4)) + 14 * np.sin(XX / 19 + 1) + 6 * np.sin(XX / 7)
    depth = np.clip((YY - ym) / 45, 0, 1)
    lit = np.clip(-(np.cos(XX / 41 + 0.4)) * 0.6 + 0.5, 0, 1)
    mtn = dict(mask=YY >= ym, v=(len(MTN) - 1) * (1 - depth) * (0.55 + 0.45 * lit) + 0.3, p=MTN, n=0.5, n2=0.4, s=0.3)
    yh = 330 + 8 * np.sin(XX / 33 + 2) + 5 * np.sin(XX / 13)
    v = (len(SNOW) - 1.5) - np.clip((YY - yh) / 60, 0, 1) * 3.2 + 0.8 * np.exp(-((XX - 50) / 80) ** 2) - 1.3
    hill = dict(mask=YY >= yh, v=v, p=SNOW, n=0.45, n2=0.35, s=0.0)
    return [mtn, hill]

def build_ground():
    top = GROUND - 1 + np.round(np.sin(XX / 6) * 0.6)
    m = YY >= top
    v = (len(SNOW) - 1.2) - np.clip((YY - GROUND) / 34, 0, 1) * 3.4 + 1.2 * (YY - top < 1.5) - 1.1
    return dict(mask=m, v=v, p=SNOW, n=0.45, n2=0.35, s=0.0)

def draw_moon(F, fld):
    d = np.hypot(XX - MOON[0], YY - MOON[1])
    m = d <= MOON[2]
    sh = np.clip(0.75 + 0.35 * ((XX - MOON[0]) * -0.6 + (YY - MOON[1]) * -0.6) / MOON[2], 0, 1)
    F[m] = dith(sh * 3.2 + 0.9 * fld['noise2'], pal('#b9b39a', '#dcd6bb', '#f2eed8', '#fffdf0'), fld['bay'])[m]

SKYL, MOUNTL, GROUNDL = build_sky(), build_mountains(), build_ground()
PINES = [(make_pine(120, 52, PINE_FAR, 1), -16, 352, 1.0, 5), (make_pine(96, 44, PINE_FAR, 2), 150, 350, 0.8, 6),
         (make_pine(84, 40, PINE_FAR, 5), 236, 354, 0.9, 7),
         (make_pine(150, 70, PINE, 3), -34, GROUND + 2, 1.6, 4), (make_pine(126, 60, PINE, 4), 232, GROUND + 2, 1.4, 5)]

# ------------------------------------------------------------------ captions (plain: black box, white text, 1px round corners)
def caption_sprite(text, sc=3, pad=6):
    tm = text_mask(text, sc)
    th, tw = tm.shape
    bw, bh = tw + 2 * pad, th + 2 * pad
    out = np.zeros((bh, bw, 4), np.float32); out[..., 3] = 1
    for cy, cx in ((0, 0), (0, bw - 1), (bh - 1, 0), (bh - 1, bw - 1)): out[cy, cx, 3] = 0
    out[pad:pad + th, pad:pad + tw][tm] = [1, 1, 1, 1]
    return out

class Caption:
    """pops in, holds, then each pixel breaks off and drifts up as mist."""
    def __init__(self, text, t_in, t_out, seed):
        self.s = caption_sprite(text)
        h, w_ = self.s.shape[:2]
        self.x, self.y, self.t_in, self.t_out = (W - w_) // 2, 12, t_in, t_out
        r = np.random.default_rng(seed)
        self.yy, self.xx = np.mgrid[0:h, 0:w_]
        self.vis = self.s[..., 3] > 0
        self.t_app = 0.07 * r.random((h, w_))
        self.t_dis = 0.06 + 0.5 * (0.55 * r.random((h, w_)) + 0.45 * (self.xx / w_))
        self.dx = (r.random((h, w_)) - 0.25) * 18
        self.dy = -(8 + r.random((h, w_)) * 16)

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
                pxs = self.x + self.xx[mist] + self.dx[mist] * k + 2.5 * np.sin(ag * 8 + self.yy[mist] * 0.7)
                pys = self.y + self.yy[mist] + self.dy[mist] * k
                col = self.s[..., :3][mist] * 0.35 + np.array([0.78, 0.88, 1.0]) * 0.65
                al = (1 - k) ** 1.6 * 0.6
                ok = (pxs >= 0) & (pxs < W - 0.5) & (pys >= 0) & (pys < H - 0.5)
                xi, yi = np.round(pxs[ok]).astype(int), np.round(pys[ok]).astype(int)
                F[yi, xi] = F[yi, xi] * (1 - al[ok, None]) + col[ok] * al[ok, None]
        ys, xs = np.nonzero(solid)
        X, Y = self.x + xs, self.y + ys
        ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
        F[Y[ok], X[ok]] = self.s[ys[ok], xs[ok], :3]

CAPTIONS = []
def cap(text, t_in, t_out): CAPTIONS.append(Caption(text, t_in, t_out, 40 + len(CAPTIONS)))
cap("WHAT IF YOU\nDROP A BALL\n4X HIGHER?", 37.4, 39.75)
cap("31 CM DROP:\nA BOUNCE\nEVERY BEAT", 2.3, 5.3)
cap("8 CM DROP:\n4X LOWER\n= 2X FASTER", 6.3, 9.3)
cap("1.2 M DROP:\n4X HIGHER\n= 2X SLOWER", 10.6, 13.2)
cap("4.9 M DROP:\nONE BOUNCE\nPER BAR", 14.3, 17.0)
cap("ADD ONE MORE\nAND IT SINGS", 17.6, 20.8)
cap("HEIGHT SETS\nTHE RHYTHM", 23.0, 26.4)
cap("4X HIGHER\nIS ALWAYS\n2X SLOWER", 34.7, 36.85)

# ------------------------------------------------------------------ balls
BALLS = {   # name: x, radius, palette (dark->light), glow colour, hits, period, finale key
    'cat':   dict(x=84, r=6, p=pal('#3d0a12', '#8a1824', '#d22f3c', '#ff6d6d', '#ffc2c2'), g=hexc('#ff5a5a'), hits=KICK_HITS, period=0.5, fin='kick'),
    'mouse': dict(x=50, r=4, p=pal('#5a3a08', '#a8700f', '#e8b52a', '#ffe68a', '#fff6d0'), g=hexc('#ffd04a'), hits=BELL_HITS, period=0.25, fin='bell'),
    'kid':   dict(x=136, r=7, p=pal('#0b3520', '#18663a', '#2db35f', '#7ee39b', '#d8ffe2'), g=hexc('#4dff8a'), hits=SNARE_HITS, period=1.0, fin='snare'),
    'santa': dict(x=196, r=10, p=pal('#0b1a52', '#1c41a3', '#3b80f2', '#86b9ff', '#e0efff'), g=hexc('#5aa0ff'), hits=BASS_HITS, period=2.0, fin='bass'),
}
for b in BALLS.values(): b['hpx'] = height_for(b['period']) * PX_PER_M
FORM = 0.5   # seconds a ball takes to gather out of the snow
REFORM = 37.0
BALLS['cat']['opener'] = True

def rhythm_state(b, t):
    """centre y, squash k, alpha-mode: ('form', s) / ('ball',) / ('burst', s) / None"""
    hits, T = b['hits'], b['period']
    release, peak_end = hits[0] - T / 2, hits[-1] + T / 2
    top = GROUND - b['hpx'] - b['r']
    pop = RETURN[b['fin']]
    if b.get('opener'):                      # this ball is on screen from the very first frame
        if t >= REFORM: return top, 0.0, ('form', min(1.0, (t - REFORM) / FORM))
        if t < release: return top + 1.2 * math.sin(t * 5), 0.0, ('ball',)
    if t < release - FORM or t >= pop + 0.7: return None
    if t < release: return top, 0.0, ('form', (t - (release - FORM)) / FORM)
    if t >= peak_end:
        hover = top + 1.5 * math.sin((t - peak_end) * 5)
        return (hover, 0.0, ('ball',)) if t < pop else (hover, 0.0, ('burst', (t - pop) / 0.7))
    u = (t - hits[0]) / T; f = u - math.floor(u)
    y = GROUND - b['hpx'] * 4 * f * (1 - f) - b['r']
    k = max(0.0, 1 - min(f, 1 - f) * T / 0.045)
    return y + b['r'] * 0.3 * k, k, ('ball',)

SPOT_X = [58, 98, 138, 178, 218]                   # glowing spots in the snow: G A B C D
SPOT_C = [hexc(c) for c in ('#ff5a6a', '#ffa64a', '#ffe066', '#6dff95', '#62c0ff')]
MEL = dict(r=5, p=pal('#3b4252', '#79849a', '#c6cedc', '#eef2f8', '#ffffff'), g=hexc('#dfe8ff'))
MEL_HITS = [m[0] for m in MELODY]
MEL_X = [SPOT_X[PRESENT_INDEX[n]] for _, n, _ in MELODY]

def melody_state(t):
    r = MEL['r']; pop = RETURN['melody']
    if t < 17.6 - FORM or t >= pop + 0.7: return None
    if t < 17.6: return MEL_X[0], LANE - 48 - r, 0, ('form', (t - (17.6 - FORM)) / FORM)
    if t < MEL_HITS[0]:
        s = (t - 17.6) / 0.4; return MEL_X[0], LANE - 48 * (1 - s * s) - r, 0, ('ball',)
    i = int(np.searchsorted(MEL_HITS, t, side='right') - 1)
    dn = min(abs(t - MEL_HITS[i]), abs(MEL_HITS[i + 1] - t) if i + 1 < len(MEL_HITS) else 9)
    k = max(0.0, 1 - dn / 0.045)
    if i + 1 >= len(MEL_HITS):     # final note: one last little hop up, hover, then burst on the last chime
        a = t - MEL_HITS[-1]
        y = LANE - r - 30 * min(1, a / 0.5) ** 0.5 + 1.5 * math.sin(a * 5) * (a > 0.5)
        return MEL_X[-1], y + r * 0.3 * k, k, ('ball',) if t < pop else ('burst', (t - pop) / 0.7)
    T = MEL_HITS[i + 1] - MEL_HITS[i]; s = (t - MEL_HITS[i]) / T
    hgt = min(50, 12 + 34 * T)
    x = MEL_X[i] + (MEL_X[i + 1] - MEL_X[i]) * smooth(s)
    return x, LANE - r - 4 * hgt * s * (1 - s) + r * 0.3 * k, k, ('ball',)

def draw_ball(F, x, cy, r, k, p, mode, seed):
    rx, ry = r * (1 + 0.35 * k), r * (1 - 0.3 * k)
    ys, xs, col = ball_pixels(x, cy, rx, ry, p)
    if mode[0] == 'ball':
        draw_pixels(F, ys, xs, col); return
    rr = np.random.default_rng(seed)
    n = len(ys)
    ang = rr.uniform(0, TAU, n); dist = rr.uniform(8, 26, n); lag = rr.uniform(0, 0.35, n)
    if mode[0] == 'form':      # snow drifts in and packs into a ball
        s = np.clip((mode[1] - lag) / (1 - lag), 0, 1); e = (1 - s) ** 2
        px = xs + np.cos(ang) * dist * e; py = ys + np.sin(ang) * dist * e - 6 * e
        c = col * s[:, None] + np.array([0.9, 0.95, 1.0]) * (1 - s[:, None])
        a = np.clip(s * 1.4, 0, 1)
    else:                      # bursts back into glittering snow
        s = np.clip((mode[1] - lag * 0.5) / (1 - lag * 0.5), 0, 1); e = s ** 0.7
        px = xs + np.cos(ang) * dist * e * 1.4; py = ys + np.sin(ang) * dist * e * 1.4 - 10 * s + 30 * s * s
        c = col * (1 - s[:, None]) + np.array([1.0, 1.0, 1.0]) * s[:, None]
        a = 1 - s
    xi, yi = np.round(px).astype(int), np.round(py).astype(int)
    ok = (xi >= 0) & (xi < W) & (yi >= 0) & (yi < H)
    F[yi[ok], xi[ok]] = F[yi[ok], xi[ok]] * (1 - a[ok, None]) + c[ok] * a[ok, None]

# ------------------------------------------------------------------ light: balls glow and light the snow
GY, GX = np.mgrid[GROUND - 12:H, 0:W]
def ground_light(t, states):
    """returns value boost and colour tint for the ground rows"""
    boost = np.zeros(GY.shape, np.float32); tint = np.zeros(GY.shape + (3,), np.float32)
    def pool(x, y, rad, inten, col):
        d2 = ((GX - x) / rad) ** 2 + ((GY - y) / (rad * 0.35)) ** 2
        g = inten * np.exp(-d2)
        boost[:] += g; tint[:] += g[..., None] * col
    for name, st in states.items():
        if st is None: continue
        b = BALLS[name]; cy = st[0]
        hgt = GROUND - (cy + b['r'])
        age = last_age(b['hits'], t)
        flash = 1.6 * math.exp(-age / 0.12) if age < 0.6 else 0
        pool(b['x'], GROUND + 2, 10 + b['r'] * 2.2, 0.9 * math.exp(-hgt / 60) + flash, b['g'])
    for i, x in enumerate(SPOT_X):           # the five note spots glow softly, flare when hit
        if not (17.0 <= t < 36.0): continue
        on = smooth((t - 17.0) / 0.8) * (1 - smooth((t - 35.2) / 0.8))
        a = min([t - mt for mt, n, _ in MELODY if PRESENT_INDEX[n] == i and t >= mt] + [9])
        pool(x, LANE, 14, on * (1.3 + 2.6 * math.exp(-a / 0.18)), SPOT_C[i])
    m = melody_state(t)
    if m: pool(m[0], LANE + 1, 12, 0.8 * math.exp(-(LANE - m[1]) / 40), MEL['g'])
    return boost, tint

def last_age(hits, t):
    i = int(np.searchsorted(hits, t, side='right') - 1)
    return t - hits[i] if i >= 0 else 99.0

def ball_halo(F, x, cy, r, col, inten):
    """soft light around a glowing ball, dithered so it shimmers"""
    rad = r * 3.2
    x0, x1, y0, y1 = int(x - rad), int(x + rad) + 1, int(cy - rad), int(cy + rad) + 1
    x0c, x1c, y0c, y1c = max(0, x0), min(W, x1), max(0, y0), min(H, y1)
    if x1c <= x0c or y1c <= y0c: return
    yy, xx = np.mgrid[y0c:y1c, x0c:x1c]
    d = np.hypot(xx - x, yy - cy) / rad
    g = np.clip(1 - d, 0, 1) ** 2 * inten
    b = CUR.get('b', 0)
    q = np.floor(g * 4 + BAYER[(yy + b // 4) % 4, (xx + b) % 4] - 0.5) / 4
    F[y0c:y1c, x0c:x1c] = np.minimum(1, F[y0c:y1c, x0c:x1c] + col * np.clip(q, 0, 1)[..., None] * 0.5)

# ------------------------------------------------------------------ ambient life
rng = np.random.default_rng(11)
STARS = [(rng.uniform(0, W), rng.uniform(80, 250), int(rng.integers(2, 9)), rng.uniform(0, 6.28)) for _ in range(90)]
SNOWFALL = [(rng.uniform(-20, W + 20), rng.uniform(GROUND + 1, 476), int(rng.integers(2, 5)), rng.random(), rng.uniform(0, 6.28), rng.random() < 0.2)
            for _ in range(200)]
AUR_Y = np.arange(70, 300)[:, None]; AUR_X = np.arange(W)[None, :]
AURP = pal('#0f3a4a', '#13625a', '#1c8f6c', '#3fc08a', '#8af0b8')

def draw_sky_life(F, t):
    pulse = 0.35 * math.exp(-last_age(BASS_HITS, t) / 0.5) if 14 <= t < 34 else 0
    pulse += 0.5 * math.exp(-(t - 35.0) / 0.8) if t >= 35.0 else 0
    ox, oy = CUR['o']
    c = 170 + 22 * np.sin(AUR_X / 46 + w(3) * t) + 10 * np.sin(AUR_X / 17 - w(5) * t)
    band = np.exp(-((AUR_Y - c) / 32) ** 2)
    soft = 0.45 + 0.9 * NZB[(AUR_Y // 2 + oy // 2) % 256, (AUR_X + ox) % 256]
    I = band * soft * (0.45 + pulse)
    b = CUR['b']
    lvl = np.clip(np.floor(I * 5 + BAYER[(AUR_Y + b // 4) % 4, (AUR_X + b) % 4] - 0.5), 0, 4).astype(int)
    F[70:300] = np.minimum(1, F[70:300] + AURP[lvl] * (lvl > 0)[..., None] * 0.3)
    for x, y, k, ph in STARS:
        if math.hypot(x - MOON[0], y - MOON[1]) < 22: continue
        bb = 0.5 + 0.5 * math.sin(w(k) * t + ph)
        put(F, x, y, np.array([0.9, 0.94, 1.0]), 0.2 + 0.7 * bb)

def draw_snowfall(F, t):
    for x0, yland, n, ph0, ph, big in SNOWFALL:
        cyc = LOOP / n
        tau = ((t / cyc + ph0) % 1.0) * cyc
        fall = (yland + 12) / 34.0
        c = np.array([0.94, 0.97, 1.0])
        if tau < fall:
            y = -12 + 34.0 * tau; x = x0 + 5 * math.sin(tau * 1.7 + ph) + 6 * tau
            put(F, x, y, c, 0.95 if big else 0.6)
            if big: put(F, x + 1, y, c, 0.8); put(F, x, y + 1, c, 0.8); put(F, x + 1, y + 1, c, 0.5)
        else:
            a = tau - fall; x = x0 + 5 * math.sin(fall * 1.7 + ph) + 6 * fall
            k = max(0.0, 1 - a / 1.6)
            if k > 0:
                put(F, x, yland, np.array([1, 1, 1]), 0.9 * k)
                if big: put(F, x + 1, yland, c, 0.7 * k)

def draw_impacts(F, t):
    for name, b in BALLS.items():
        life, n, spd = {'cat': (0.35, 7, 26), 'mouse': (0.22, 4, 12), 'kid': (0.4, 9, 34), 'santa': (0.6, 14, 46)}[name]
        for hi, h in enumerate(b['hits']):
            a = t - h
            if not 0 <= a < life: continue
            r = np.random.default_rng(hi * 31 + len(name))
            for k in range(n):
                vx = (r.random() - 0.5) * spd * 2; vy = -r.random() * spd - 6
                px = b['x'] + vx * a; py = GROUND - 1 + vy * a + 70 * a * a
                if py <= GROUND + 1: put(F, px, min(py, GROUND - 1), np.array([0.96, 0.98, 1.0]), 1 - a / life)
    for mi, (mt, n, d) in enumerate(MELODY):
        a = t - mt
        if not 0 <= a < 0.5: continue
        i = PRESENT_INDEX[n]; r = np.random.default_rng(900 + mi)
        for k in range(8):
            vx = (r.random() - 0.5) * 60; vy = -22 - r.random() * 30
            glow(F, SPOT_X[i] + vx * a, LANE - 2 + vy * a + 70 * a * a, SPOT_C[i], 0.9 * (1 - a / 0.5))

# ------------------------------------------------------------------ camera: one ball at a time
def mel_x_smooth(t):
    xs = [melody_state(t + d) for d in np.linspace(-0.7, 0.7, 9)]
    xs = [m[0] for m in xs if m]
    return sum(xs) / len(xs) if xs else 140

CAM = [(0.0, 84, 400, 3), (5.3, 84, 400, 3), (5.95, 56, 410, 3), (9.4, 56, 410, 3),
       (10.05, 136, 372, 2), (12.2, 136, 372, 2), (12.85, 196, 160, 2), (13.05, 196, 160, 2),
       (14.0, 135, 240, 1), (16.4, 135, 240, 1), (17.3, 'mel', 410, 2), (29.6, 'mel', 410, 2),
       (30.6, 135, 240, 1), (36.9, 135, 240, 1), (37.85, 84, 400, 3), (38.0, 84, 400, 3)]

def camera(t):
    for (t0, x0, y0, z0), (t1, x1, y1, z1) in zip(CAM, CAM[1:]):
        if t0 <= t <= t1:
            x0 = mel_x_smooth(t) if x0 == 'mel' else x0
            x1 = mel_x_smooth(t) if x1 == 'mel' else x1
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

# ------------------------------------------------------------------ frame
def frame(t):
    fld = live_fields(t)
    F = np.zeros((H, W, 3), np.float32)
    paint_live(F, SKYL, fld)
    draw_sky_life(F, t)
    draw_moon(F, fld)
    for L in MOUNTL: paint_live(F, L, fld)
    for i, (pn, x, base, amp, k) in enumerate(PINES):
        sway_blit(F, pine_sprite(pn, t, i * 53), x, base - pn['V'].shape[0], amp, w(k) * t + x)
    states = {n: rhythm_state(b, t) for n, b in BALLS.items()}
    boost, tint = ground_light(t, states)
    extra = np.zeros((H, W), np.float32); extra[GROUND - 12:] = boost * 0.35
    paint_live(F, GROUNDL, fld, extra)
    gm = GROUNDL['mask'][GROUND - 12:]
    tq = np.floor(np.clip(tint[gm], 0, 2) * 3 + (BAYER[(GY[gm] + CUR['b'] // 4) % 4, (GX[gm] + CUR['b']) % 4] - 0.5)[:, None]) / 3
    F[GROUND - 12:][gm] = np.clip(F[GROUND - 12:][gm] * (1 - 0.25 * np.clip(tq, 0, 1).max(1, keepdims=True)) + np.clip(tq, 0, 1.5) * 0.45, 0, 1)
    if 17.0 <= t < 36.0:
        on = smooth((t - 17.0) / 0.8) * (1 - smooth((t - 35.2) / 0.8))
        bb = CUR['b']
        for i, x in enumerate(SPOT_X):
            a_ = min([t - mt for mt, n, _ in MELODY if PRESENT_INDEX[n] == i and t >= mt] + [9])
            fl = math.exp(-a_ / 0.18)
            for yy in range(LANE - 3, LANE + 4):
                for xx in range(x - 11, x + 12):
                    d = math.hypot((xx - x) / 11, (yy - LANE) / 3.4)
                    if d > 1: continue
                    lv = (1 - d) * (0.8 + 1.4 * fl) * on
                    if lv + BAYER[(yy + bb // 4) % 4, (xx + bb) % 4] - 0.5 > 0.35:
                        c = SPOT_C[i] * (0.75 + 0.25 * fl) + (0.5 * fl if d < 0.35 else 0)
                        put(F, xx, yy, np.clip(c, 0, 1))
    draw_impacts(F, t)
    for i, (name, st) in enumerate(states.items()):
        if st is None: continue
        b = BALLS[name]; cy, k, mode = st
        draw_ball(F, b['x'], cy, b['r'], k, b['p'], mode, 5 + i)
    m = melody_state(t)
    if m:
        draw_ball(F, m[0], m[1], MEL['r'], m[2], MEL['p'], m[3], 77)
    draw_snowfall(F, t)
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
