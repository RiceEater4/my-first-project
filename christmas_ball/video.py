"""Renders 'What If You Dropped a Ball?' as 1080x1920 / 60 fps pixel art.

Everything is drawn on a 270x480 canvas and scaled up 4x (nearest neighbour),
so every 'pixel' is a crisp 4x4 block. All motion is driven by score.py, so each
landing happens on exactly the frame its sound plays.

usage: python3 video.py out.mp4 audio.wav      (full render)
       python3 video.py --stills DIR t1 t2 ... (preview frames as PNG)
"""
import sys, subprocess, math
import numpy as np
from score import *

W, H, S = 270, 480, 4
GROUND = 440

def hexc(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16
YY, XX = np.mgrid[0:H, 0:W]
BAY = BAYER[YY % 4, XX % 4]

def dither_palette(v, pal):
    """v: float index map into pal -> ordered-dithered RGB (smooth pixel-art gradients)."""
    idx = np.clip(np.floor(v + BAY - 0.5 + 0.5), 0, len(pal) - 1).astype(int)
    return np.stack(pal)[idx]

# ------------------------------------------------------------------ static background
SKY = [hexc(c) for c in ['#070b24', '#0c1438', '#121f4f', '#1a2d68', '#223f82', '#2c559c', '#3a6fb4', '#4f8cc8', '#6eaad8']]
FAR = [hexc(c) for c in ['#2b4775', '#355688', '#41679b', '#5079ad', '#628cbe']]
NEAR = [hexc(c) for c in ['#6d8fc2', '#7f9fcd', '#93b1da', '#a8c3e6', '#bfd4ef']]
SNOW = [hexc(c) for c in ['#9db6dc', '#b1c7e6', '#c6d7ef', '#dbe6f7', '#eef4fd']]
TREE = [hexc(c) for c in ['#071f1a', '#0b2d23', '#10402e', '#17573b', '#206f4a', '#2d8858']]
TRUNK = [hexc(c) for c in ['#2a170e', '#4a2c1a', '#6b4227']]
MOON = (222, 108, 13)
CX = 135
TIERS = [(118, 192, 30), (160, 252, 46), (214, 322, 60), (276, 414, 72)]

def tree_half(y, yt, yb, hw):
    f = (y - yt) / (yb - yt)
    return hw * f + 3 * (((y - yt) % 9) / 9) * f

def build_bg():
    bg = np.zeros((H, W, 3), np.float32)
    # sky: dithered vertical gradient + moon glow so the blues melt into each other
    v = (np.clip(YY / 360, 0, 1) ** 1.25) * (len(SKY) - 1)
    d = np.hypot(XX - MOON[0], YY - MOON[1])
    v = v + 2.6 * np.exp(-(d / 46) ** 2) + 1.2 * np.exp(-(d / 110) ** 2)
    bg[:] = dither_palette(v, SKY)
    moon = d <= MOON[2]
    bg[moon] = hexc('#f4f1dc')
    crater = moon & ((np.hypot(XX - 218, YY - 104) < 3) | (np.hypot(XX - 226, YY - 112) < 2) | (np.hypot(XX - 216, YY - 113) < 1.6))
    bg[crater] = hexc('#d8d3b5')
    # far hills
    yh = 300 + 12 * np.sin(XX / 37 + 1) + 7 * np.sin(XX / 15)
    m = YY >= yh
    vv = (len(FAR) - 1) - np.clip((YY - yh) / 26, 0, 1) * 2.5 + 0.8 * np.exp(-((XX - MOON[0]) / 90) ** 2)
    bg[m] = dither_palette(vv, FAR)[m]
    # far pine silhouettes
    rng = np.random.default_rng(3)
    for px in rng.integers(0, W, 26):
        if 55 < px < 215: continue
        base = 300 + 12 * math.sin(px / 37 + 1) + 7 * math.sin(px / 15) + 4
        hgt = rng.integers(14, 26)
        for yy in range(int(base - hgt), int(base)):
            hw = (yy - (base - hgt)) / hgt * 5 + ((yy % 3) == 0)
            x0, x1 = int(px - hw), int(px + hw) + 1
            bg[yy, max(0, x0):min(W, x1)] = hexc('#1f3660')
    # near hills
    yn = 352 + 10 * np.sin(XX / 29 + 2) + 6 * np.sin(XX / 11)
    m = YY >= yn
    vv = (len(NEAR) - 1) - np.clip((YY - yn) / 40, 0, 1) * 3.2
    bg[m] = dither_palette(vv, NEAR)[m]
    # ground
    m = YY >= GROUND - 2 + (np.sin(XX / 5) > 0.6)
    vv = (len(SNOW) - 1) - np.clip((YY - GROUND) / 40, 0, 1) * 3.6
    bg[m] = dither_palette(vv, SNOW)[m]
    # tree
    for yt, yb, hw in TIERS:
        for y in range(yt, yb + 1):
            half = tree_half(y, yt, yb, hw)
            x0, x1 = int(round(CX - half)), int(round(CX + half)) + 1
            xs = np.arange(x0, x1)
            f = (y - yt) / (yb - yt)
            val = 2.6 + 2.2 * (xs - CX) / max(half, 1) - 1.6 * f ** 2 + 0.6 * (y < yt + 10)
            row = dither_palette(np.broadcast_to(val, (H, len(xs)))[y:y + 1], TREE)[0] if False else None
            idx = np.clip(np.floor(val + BAYER[y % 4, xs % 4]), 0, len(TREE) - 1).astype(int)
            bg[y, x0:x1] = np.stack(TREE)[idx]
            # snow resting on the branch tips along each tier's lower rim
            sn = (y >= yb - 3 + 1.6 * np.sin(xs * 0.9 + yt)) & (np.abs(xs - CX) > half * 0.15)
            sv = 2.2 + 1.5 * (xs - CX) / max(half, 1)
            sidx = np.clip(np.floor(sv + BAYER[y % 4, xs % 4]), 0, len(SNOW) - 1).astype(int)
            bg[y, xs[sn]] = np.stack(SNOW)[sidx[sn]]
    for y in range(414, GROUND):
        for x in range(CX - 6, CX + 7):
            bg[y, x] = TRUNK[min(2, max(0, int((x - CX + 6) / 13 * 2.9 + BAYER[y % 4, x % 4] - 0.5)))]
    return bg

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
}
HEADPHONES = ["0011111100", "0100000010", "1000000001", "1000000001", "1110000111", "1110000111", "1110000111", "0110000110"]
NOTE = ["00110", "00101", "00100", "00100", "01100", "11100", "11000"]

def text_mask(text, sc):
    lines = text.split('\n')
    w = max(len(l) for l in lines) * 6 * sc - sc
    h = len(lines) * 9 * sc - 2 * sc
    m = np.zeros((h, w), bool)
    for li, line in enumerate(lines):
        off = (w - (len(line) * 6 * sc - sc)) // 2
        for ci, ch in enumerate(line):
            g = np.array([[c == '1' for c in r] for r in FONT[ch]])
            g = np.kron(g, np.ones((sc, sc), bool))
            y0, x0 = li * 9 * sc, off + ci * 6 * sc
            m[y0:y0 + 7 * sc, x0:x0 + 5 * sc] |= g
    return m

def caption_sprite(text, sc=2, icon=False, pad=4):
    tm = text_mask(text, sc)
    h, w = tm.shape
    bw, bh = w + 2 * pad, h + 2 * pad
    rgba = np.zeros((bh, bw, 4), np.float32)
    rgba[..., :3] = hexc('#04050b'); rgba[..., 3] = 1
    rgba[pad:pad + h, pad:pad + w][tm] = [0.96, 0.97, 1.0, 1]
    if icon:   # headphones badge under the box, like the reference shorts
        g = np.array([[c == '1' for c in r] for r in HEADPHONES])
        ih, iw = g.shape[0] + 6, g.shape[1] + 6
        out = np.zeros((bh + 3 + ih, bw, 4), np.float32)
        out[:bh] = rgba
        x0 = (bw - iw) // 2
        out[bh + 3:bh + 3 + ih, x0:x0 + iw, :3] = hexc('#04050b'); out[bh + 3:bh + 3 + ih, x0:x0 + iw, 3] = 1
        sub = out[bh + 6:bh + 6 + g.shape[0], x0 + 3:x0 + 3 + g.shape[1]]
        sub[g] = [0.96, 0.97, 1.0, 1]
        rgba = out
    return rgba

def label_sprite(text, sc=1, pad=2):
    return caption_sprite(text, sc, False, pad)

# ------------------------------------------------------------------ drawing helpers
def blend(F, x, y, rgba, alpha=1.0):
    h, w = rgba.shape[:2]
    x0, y0 = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x0), max(0, -y0)
    ex, ey = min(w, W - x0), min(h, H - y0)
    if ex <= sx0 or ey <= sy0: return
    src = rgba[sy0:ey, sx0:ex]
    a = src[..., 3:4] * alpha
    dst = F[y0 + sy0:y0 + ey, x0 + sx0:x0 + ex]
    dst[:] = dst * (1 - a) + src[..., :3] * a

def put(F, x, y, col, a=1.0):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        F[y, x] = F[y, x] * (1 - a) + col * a

def add_light(F, x, y, col, a):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        F[y, x] = np.minimum(1, F[y, x] + col * a)

def rect(F, x0, y0, x1, y1, col, a=1.0):
    x0, y0, x1, y1 = max(0, int(x0)), max(0, int(y0)), min(W, int(x1)), min(H, int(y1))
    if x1 > x0 and y1 > y0:
        F[y0:y1, x0:x1] = F[y0:y1, x0:x1] * (1 - a) + col * a

# ------------------------------------------------------------------ dissolving captions
class Caption:
    """Pops in by pixel, holds, then each pixel breaks off and drifts up as mist."""
    def __init__(self, sprite, x, y, t_in, t_out, seed):
        self.s, self.x, self.y, self.t_in, self.t_out = sprite, x, y, t_in, t_out
        h, w = sprite.shape[:2]
        r = np.random.default_rng(seed)
        u = r.random((h, w))
        yy, xx = np.mgrid[0:h, 0:w]
        self.t_dis = 0.08 + 0.42 * (0.6 * u + 0.4 * (xx / w))       # sweeps left->right with noise
        self.t_app = 0.22 * (0.7 * r.random((h, w)) + 0.3 * (yy / h))
        self.dx = (r.random((h, w)) - 0.3) * 16
        self.dy = -(6 + r.random((h, w)) * 14)
        self.yy, self.xx = yy, xx
        self.vis = sprite[..., 3] > 0

    def draw(self, F, t):
        for tt in (t, t + LOOP, t - LOOP):
            if self.t_in <= tt <= self.t_out + 1.0:
                self._draw(F, tt)

    def _draw(self, F, t):
        a_in = t - self.t_in
        a_out = t - self.t_out
        solid = self.vis & (a_in >= self.t_app)
        if a_out > 0:
            age = a_out - self.t_dis
            solid &= age < -0.12
            # halftone flicker just before a pixel lets go
            fading = self.vis & (age >= -0.12) & (age < 0)
            fading &= BAYER[self.yy % 4, self.xx % 4] < (-age / 0.12)
            solid |= fading & (a_in >= self.t_app)
            mist = self.vis & (age >= 0) & (age < 0.55)
            if mist.any():
                ag = age[mist]
                k = ag / 0.55
                px = self.x + self.xx[mist] + self.dx[mist] * k + 3 * np.sin(ag * 9 + self.yy[mist])
                py = self.y + self.yy[mist] + self.dy[mist] * k
                col = self.s[..., :3][mist] * 0.4 + np.array([0.75, 0.85, 1.0]) * 0.6
                al = (1 - k) ** 1.5 * 0.65
                for i in range(len(px)):
                    put(F, px[i], py[i], col[i], al[i])
        h, w = self.s.shape[:2]
        x0, y0 = int(self.x), int(self.y)
        ys, xs = np.nonzero(solid)
        ok = (x0 + xs >= 0) & (x0 + xs < W) & (y0 + ys >= 0) & (y0 + ys < H)
        F[y0 + ys[ok], x0 + xs[ok]] = self.s[ys[ok], xs[ok], :3]

def centered(sprite, y):
    return (W - sprite.shape[1]) // 2, y

CAPTIONS = []
def cap(text, t_in, t_out, icon=False, y=30, sc=2):
    s = caption_sprite(text, sc, icon)
    x, y = centered(s, y)
    CAPTIONS.append(Caption(s, x, y, t_in, t_out, len(CAPTIONS) + 11))

cap("WHAT IF YOU\nDROPPED A BALL?", 37.45, 39.6, icon=True)
cap("IT KEEPS\nTHE BEAT", 2.35, 5.3)
cap("HALF THE SIZE,\nTWICE THE SPEED", 6.3, 9.4)
cap("THIS ONE ONLY\nHITS 2 AND 4", 10.6, 13.4)
cap("THE BIG ONE\nTAKES A WHOLE BAR", 14.3, 17.2)
cap("NOW DROP ONE\nON THE PRESENTS", 17.6, 20.8)
cap("EVERY BOUNCE\nIS A NOTE", 22.0, 25.4)
cap("5 BALLS,\n1 SONG", 28.0, 31.2)
cap("THIS SONG WAS\n5 DROPPED BALLS", 35.2, 36.75)

# ------------------------------------------------------------------ balls
def pal(*c): return [hexc(x) for x in c]
BALLS = {
    #        colour palette (dark->light)                             r   x    hang slot   period hits        height label
    'kick':  dict(p=pal('#3d0a12', '#8a1824', '#d22f3c', '#ff7a7a'), r=9, x=24, slot=(104, 300), hits=KICK_HITS, hgt=34, bpm='120'),
    'bell':  dict(p=pal('#0b3520', '#18663a', '#2db35f', '#8cf0a8'), r=6, x=51, slot=(166, 244), hits=BELL_HITS, hgt=12, bpm='240'),
    'snare': dict(p=pal('#4f3307', '#a26b0e', '#eab52c', '#fff0a0'), r=7, x=221, slot=(118, 206), hits=SNARE_HITS, hgt=72, bpm='60'),
    'bass':  dict(p=pal('#0b1a52', '#1c41a3', '#3b80f2', '#a6d0ff'), r=10, x=248, slot=(160, 362), hits=BASS_HITS, hgt=118, bpm='30'),
    'melody': dict(p=pal('#363c4c', '#79849a', '#c6cedc', '#ffffff'), r=7, x=None, slot=(135, 158), hits=[m[0] for m in MELODY], hgt=0, bpm=None),
}
DROP = 0.8
PRESENTS = [  # x centre, height, body, dark, light, ribbon
    (83, 34, '#c4302b', '#80181a', '#ef5a4c', '#f5c542'),
    (109, 30, '#239a52', '#125c31', '#45c879', '#e8394a'),
    (135, 26, '#2f6fd8', '#1a3f8f', '#62a0ff', '#f4f6ff'),
    (161, 22, '#8d45b5', '#552275', '#b878df', '#f5c542'),
    (187, 19, '#e2a32b', '#9b6514', '#ffd166', '#e8394a'),
]
PRESENTS = [(x, h, hexc(a), hexc(b), hexc(c), hexc(d)) for x, h, a, b, c, d in PRESENTS]

def present_top(i): return GROUND - PRESENTS[i][1]

_sprite_cache = {}
def ball_sprite(name, sx=1.0, sy=1.0):
    b = BALLS[name]
    key = (name, round(sx, 2), round(sy, 2))
    if key in _sprite_cache: return _sprite_cache[key]
    r = b['r']; rx, ry = r * sx, r * sy
    w, h = int(math.ceil(rx * 2)) + 2, int(math.ceil(ry * 2)) + 2
    yy, xx = np.mgrid[0:h, 0:w]
    nx = (xx + 0.5 - w / 2) / rx; ny = (yy + 0.5 - h / 2) / ry
    d2 = nx ** 2 + ny ** 2
    inside = d2 <= 1
    nz = np.sqrt(np.clip(1 - d2, 0, 1))
    L = np.array([0.45, -0.55, 0.70]); L /= np.linalg.norm(L)
    shade = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    v = 0.3 + shade * 3.0
    idx = np.clip(np.floor(v + BAYER[yy % 4, xx % 4] - 0.5), 0, 3).astype(int)
    idx[d2 > 0.78] = np.minimum(idx[d2 > 0.78], 1)
    idx[d2 > 0.9] = 0
    rgba = np.zeros((h, w, 4), np.float32)
    rgba[..., :3] = np.stack(b['p'])[idx]; rgba[..., 3] = inside
    hx, hy = int(w / 2 + 0.38 * rx), int(h / 2 - 0.45 * ry)
    rgba[hy, hx] = [1, 1, 1, 1]
    if r >= 8: rgba[hy, hx + 1] = rgba[hy + 1, hx] = [1, 1, 1, 1]
    _sprite_cache[key] = rgba
    return rgba

def draw_ball(F, name, x, y, sx=1.0, sy=1.0, string=False):
    s = ball_sprite(name, sx, sy)
    h, w = s.shape[:2]
    if string:
        for k in range(1, 7): put(F, x, y - BALLS[name]['r'] - 1 - k, hexc('#d9c48a'), 0.8)
    blend(F, x - w / 2, y - h / 2, s)
    cw = 3 if BALLS[name]['r'] < 8 else 5           # little cap on top, it is an ornament
    rect(F, x - cw / 2, y - h / 2 - 1, x + cw / 2, y - h / 2 + 1, hexc('#cdb36a'))
    put(F, x, y - h / 2 - 2, hexc('#8a7740'))

def smooth(s): s = min(1, max(0, s)); return s * s * (3 - 2 * s)

def ball_state(name, t):
    """returns (x, y, sx, sy, mode) mode in hang/air/ground"""
    b = BALLS[name]; hits = b['hits']; r = b['r']
    sx0, sy0 = b['slot']
    t_first = hits[0]; t_ret = RETURN[name]
    if name == 'melody':
        land = [(present_top(PRESENT_INDEX[n]) - r, PRESENTS[PRESENT_INDEX[n]][0]) for _, n, _ in MELODY]
    else:
        land = [(GROUND - r, b['x'])] * len(hits)
    if t < t_first - DROP:                              # hanging (with a wobble before it lets go)
        wob = 0
        if t > t_first - DROP - 0.45:
            k = (t - (t_first - DROP - 0.45)) / 0.45
            wob = math.sin(k * 22) * 1.3 * k
        return sx0 + wob, sy0, 1, 1, 'hang'
    if t < t_first:                                     # falling off the tree
        s = (t - (t_first - DROP)) / DROP
        y = sy0 + (land[0][0] - sy0) * s * s
        x = sx0 + (land[0][1] - sx0) * smooth(s)
        st = min(1.25, 1 + 0.3 * s)
        return x, y, 1 / math.sqrt(st), st, 'air'
    depart = t_ret - 0.55
    if t >= t_ret:                                      # back on the tree, swinging to rest
        a = t - t_ret
        return sx0 + 2.2 * math.sin(a * 11) * math.exp(-a * 3), sy0, 1, 1, 'hang'
    if t >= depart:                                     # hopping back up to its branch
        s = (t - depart) / 0.55
        y0, x0 = land[-1]
        yc = min(y0, sy0) - 45
        y = (1 - s) ** 2 * y0 + 2 * s * (1 - s) * yc + s * s * sy0
        x = x0 + (sx0 - x0) * smooth(s)
        return x, y, 1, 1, 'air'
    i = int(np.searchsorted(hits, t, side='right') - 1)
    yl, xl = land[i]
    # squash at contact
    dn = min(abs(t - hits[i]), abs(hits[i + 1] - t) if i + 1 < len(hits) else 9)
    k = max(0, 1 - dn / 0.055)
    sq = (1 + 0.32 * k, 1 - 0.28 * k)
    if i + 1 >= len(hits) or (name == 'snare' and hits[i] >= hits[-1]):
        return xl, yl + 0.28 * k * r, sq[0], sq[1], 'ground'
    T = hits[i + 1] - hits[i]
    s = (t - hits[i]) / T
    yn, xn = land[i + 1]
    if name == 'melody':
        hgt = min(70, 12 + 34 * T)
        y = yl + (yn - yl) * s - 4 * hgt * s * (1 - s)
        x = xl + (xn - xl) * smooth(s)
    else:
        y = yl - b['hgt'] * 4 * s * (1 - s); x = xl
    return x, y + 0.28 * k * r, sq[0], sq[1], 'ground' if k > 0 else 'air'

def last_hit(hits, t):
    i = int(np.searchsorted(hits, t, side='right') - 1)
    return (i, hits[i]) if i >= 0 else (-1, None)

# ------------------------------------------------------------------ tree lights & star
rng = np.random.default_rng(5)
LIGHTS = []
LCOLS = [hexc(c) for c in ['#ff4d5e', '#ffd35a', '#59e1ff', '#7dff8a', '#ff7ae0']]
for k in range(30):
    while True:
        yt, yb, hw = TIERS[rng.integers(0, 4)]
        y = rng.uniform(yt + 8, yb - 4)
        half = tree_half(y, yt, yb, hw) - 4
        if half > 4: break
    LIGHTS.append((CX + rng.uniform(-half, half), y, LCOLS[k % 5], k % 2))
STAR = ["0000100000", "0000100000", "0001110000", "1111111111", "0111111110", "0011111100", "0011011100", "0110001110", "0100000010"]
STAR = np.array([[c == '1' for c in r] for r in STAR])

def draw_lights(F, t):
    groove = 2.0 <= t < 32.0
    for (x, y, col, grp) in LIGHTS:
        if groove:
            hits = KICK_HITS if grp == 0 or t < BELL_HITS[0] else BELL_HITS
            i, h = last_hit(hits, t)
            b = 0.3 + 0.7 * math.exp(-(t - h) / 0.13) if h is not None else 0.3
        else:
            b = 0.75 + 0.25 * math.sin(2 * math.pi * 4 * t / LOOP * 4 + x)
        put(F, x, y, col * (0.35 + 0.65 * b) + 0.25 * b)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            add_light(F, x + dx, y + dy, col, 0.5 * b)
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            add_light(F, x + dx, y + dy, col, 0.10 * b)

def draw_star(F, t):
    a = t - RETURN['melody']
    burst = math.exp(-a / 0.7) if 0 <= a < 3 else 0
    ys, xs = np.nonzero(STAR)
    x0, y0 = CX - 5, 106
    for y, x in zip(ys, xs):
        put(F, x0 + x, y0 + y, hexc('#ffd84a') * (0.85 + 0.15 * math.sin(t * 3)) + 0.3 * burst)
    for k in range(1, 6):
        g = (0.18 + 0.5 * burst) / k
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            add_light(F, CX + dx - 0.5, 110 + dy, hexc('#ffe9a0'), g)
    if burst > 0.02:   # rays
        for ang in range(8):
            th = ang * math.pi / 4 + a * 1.5
            for k in range(6, int(6 + 22 * (1 - burst) + 4)):
                add_light(F, CX + math.cos(th) * k, 110 + math.sin(th) * k, hexc('#fff4c4'), 0.5 * burst * (1 - k / 32))

# ------------------------------------------------------------------ presents
def draw_presents(F, t):
    for i, (x, hgt, body, dark, light, rib) in enumerate(PRESENTS):
        ages = [t - mt for mt, n, _ in MELODY if PRESENT_INDEX[n] == i and 0 <= t - mt < 0.4]
        a = min(ages) if ages else 9
        lift = round(3 * math.exp(-a / 0.07)) if a < 0.3 else 0
        sq = 1 if a < 0.05 else 0
        flash = 0.55 * math.exp(-a / 0.09) if a < 0.4 else 0
        top = GROUND - hgt + sq
        x0, x1 = x - 11, x + 11
        rect(F, x0, top + 3, x1, GROUND, body)
        rect(F, x0, top + 3, x0 + 4, GROUND, dark)
        for yy in range(int(top + 3), GROUND):                # dithered shade between dark side and body
            for xx in range(x0 + 4, x0 + 7):
                if BAYER[yy % 4, xx % 4] < (x0 + 7 - xx) / 4: put(F, xx, yy, dark)
        rect(F, x - 1, top + 3, x + 2, GROUND, rib)
        rect(F, x0, top + 3 + (hgt - 3) // 2, x1, top + 5 + (hgt - 3) // 2, rib)
        lt = top - lift
        rect(F, x0 - 1, lt, x1 + 1, lt + 4, light)
        rect(F, x0 - 1, lt + 3, x1 + 1, lt + 4, dark)
        rect(F, x - 1, lt, x + 2, lt + 4, rib)
        for dx, dy in ((-3, -1), (-2, -2), (-4, -2), (2, -1), (3, -2), (5, -2), (-1, -1), (1, -1)):  # bow
            put(F, x + dx, lt + dy, rib)
        if flash > 0:
            rect(F, x0 - 1, lt, x1 + 1, GROUND, np.array([1, 1, 0.92]), flash * 0.6)

# ------------------------------------------------------------------ effects
def fx_particles(F, t):
    specs = [('kick', 0.35, 5, '#f4f8ff', 26), ('bell', 0.25, 2, '#e8fff0', 14), ('snare', 0.3, 4, '#fff2b0', 22),
             ('bass', 0.45, 8, '#f4f8ff', 34)]
    for name, life, n, col, spd in specs:
        b = BALLS[name]
        for hi, h in enumerate(b['hits']):
            a = t - h
            if not 0 <= a < life: continue
            r = np.random.default_rng(hi * 31 + len(name))
            for k in range(n):
                vx = (r.random() - 0.5) * spd * 2; vy = -r.random() * spd - 8
                px = b['x'] + vx * a; py = GROUND - 1 + vy * a + 60 * a * a
                if py <= GROUND + 2:
                    put(F, px, min(py, GROUND - 1), hexc(col), 1 - a / life)
            if name == 'snare' and a < 0.16:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    for k in range(2, int(3 + a / 0.16 * 7)):
                        add_light(F, b['x'] + dx * k, GROUND - b['r'] + dy * k, hexc('#ffe27a'), 0.8 * (1 - a / 0.16))
            if name == 'bass' and a < 0.45:
                rr = 6 + 40 * a / 0.45
                for k in range(64):
                    th = k / 64 * 2 * math.pi
                    put(F, b['x'] + rr * math.cos(th), GROUND + 1 + rr * 0.18 * math.sin(th), hexc('#ffffff'), 0.55 * (1 - a / 0.45))
    # present hits: sparkles + a little music note that floats up and dissolves
    note = np.array([[c == '1' for c in r] for r in NOTE])
    for mi, (mt, n, d) in enumerate(MELODY):
        a = t - mt
        if not 0 <= a < 0.7: continue
        i = PRESENT_INDEX[n]; x = PRESENTS[i][0]; top = present_top(i)
        r = np.random.default_rng(900 + mi)
        for k in range(6):
            vx = (r.random() - 0.5) * 60; vy = -20 - r.random() * 30
            if a < 0.4:
                add_light(F, x + vx * a, top - 2 + vy * a + 70 * a * a, hexc('#fff3b0'), 0.9 * (1 - a / 0.4))
        ys, xs = np.nonzero(note)
        u = np.random.default_rng(mi).random(len(ys))
        keep = u > (a / 0.7) ** 1.3
        for y, xx, kk in zip(ys, xs, keep):
            if kk: put(F, x - 2 + xx + 4 * math.sin(a * 6), top - 18 - 22 * a + y, PRESENTS[i][5], 0.95)

def draw_shadow(F, name, x, y):
    b = BALLS[name]
    hgt = GROUND - b['r'] - y
    if hgt < -2 or hgt > 160: return
    hw = b['r'] * (1.15 - 0.6 * min(1, hgt / 120))
    col = hexc('#7d97c3')
    for xx in range(int(x - hw), int(x + hw) + 1):
        for yy in (GROUND, GROUND + 1):
            if BAYER[yy % 4, xx % 4] < 0.7 - 0.3 * min(1, hgt / 120): put(F, xx, yy, col, 0.75)

# ------------------------------------------------------------------ bpm labels (big pop -> small tag)
LABELS = {}
for name in ['kick', 'bell', 'snare', 'bass']:
    b = BALLS[name]
    LABELS[name] = dict(big=caption_sprite(b['bpm'], 2, pad=3), bpm=label_sprite('BPM', 1, 1),
                        small=caption_sprite(b['bpm'] + '\nBPM', 1, pad=2))
    sm = LABELS[name]['small']
    LABELS[name]['cap'] = Caption(sm, b['x'] - sm.shape[1] // 2, 449, 0, RETURN[name] + 0.1, 200 + len(name))

def draw_labels(F, t):
    for name, L in LABELS.items():
        b = BALLS[name]; t1 = b['hits'][0]
        a = t - t1
        if a < 0: continue
        big = L['big']
        bx_c = min(max(b['x'], big.shape[1] / 2 + 4), W - big.shape[1] / 2 - 4)
        by = 316
        sm = L['small']; sx, sy = b['x'] - sm.shape[1] / 2, 449
        if a < 0.9:
            pop = 1 + (0.25 * math.exp(-a / 0.08) if a < 0.3 else 0)
            blend(F, bx_c - big.shape[1] / 2, by - (pop - 1) * 6, big)
            blend(F, bx_c - L['bpm'].shape[1] / 2, by + big.shape[0] + 1, L['bpm'])
        elif a < 1.25:
            s = smooth((a - 0.9) / 0.35)
            blend(F, bx_c - big.shape[1] / 2 + (sx + sm.shape[1] / 2 - bx_c) * s, by + (sy - by) * s, big if s < 0.6 else sm)
        else:
            L['cap'].draw(F, t)

# ------------------------------------------------------------------ snow
rng = np.random.default_rng(11)
FLAKES = [(rng.uniform(0, W), rng.uniform(0, H), int(rng.integers(1, 4)), int(rng.integers(1, 3)), rng.uniform(0, 6.28), rng.random() < 0.18)
          for _ in range(150)]
STARS = [(rng.uniform(0, W), rng.uniform(0, 230), int(rng.integers(1, 6)), rng.uniform(0, 6.28)) for _ in range(70)]

def draw_snow(F, t):
    for x0, y0, vy, wm, ph, big in FLAKES:
        y = (y0 + vy * (H + 8) * t / LOOP * 4) % (H + 8) - 4
        x = (x0 + 5 * math.sin(2 * math.pi * wm * t / LOOP * 3 + ph)) % W
        c = np.array([0.93, 0.96, 1.0])
        put(F, x, y, c, 0.9 if big else 0.6)
        if big:
            put(F, x + 1, y, c, 0.9); put(F, x, y + 1, c, 0.9); put(F, x + 1, y + 1, c, 0.7)

def draw_stars(F, BG, t):
    for x, y, k, ph in STARS:
        if math.hypot(x - MOON[0], y - MOON[1]) < 30: continue
        b = 0.5 + 0.5 * math.sin(2 * math.pi * k * t / LOOP * 2 + ph)
        put(F, x, y, np.array([0.9, 0.93, 1.0]), 0.25 + 0.6 * b)

# ------------------------------------------------------------------ frame
BG = build_bg()
def frame(t):
    F = BG.copy()
    draw_stars(F, BG, t)
    draw_lights(F, t)
    draw_star(F, t)
    order = ['kick', 'bell', 'snare', 'bass', 'melody']
    states = {n: ball_state(n, t) for n in order}
    for n in order:
        x, y, sx, sy, mode = states[n]
        if mode == 'hang': draw_ball(F, n, x, y, string=True)
    draw_presents(F, t)
    for n in order[:4]:
        x, y, sx, sy, mode = states[n]
        if mode != 'hang' and t >= BALLS[n]['hits'][0] - 0.3: draw_shadow(F, n, x, y)
    fx_particles(F, t)
    for n in order:
        x, y, sx, sy, mode = states[n]
        if mode != 'hang':
            draw_ball(F, n, x, y + (BALLS[n]['r'] * (1 - sy)), sx, sy)
    draw_snow(F, t)
    draw_labels(F, t)
    for c in CAPTIONS: c.draw(F, t)
    return (np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8)

def upscale(img): return np.repeat(np.repeat(img, S, 0), S, 1)

if __name__ == '__main__':
    if sys.argv[1] == '--stills':
        from PIL import Image
        out = sys.argv[2]
        for ts in sys.argv[3:]:
            Image.fromarray(upscale(frame(float(ts)))).save(f'{out}/still_{float(ts):06.2f}.png')
        sys.exit()
    out, wav = sys.argv[1], sys.argv[2]
    nfr = int(LOOP * FPS)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W*S}x{H*S}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(nfr):
        p.stdin.write(upscale(frame(f / FPS)).tobytes())
        if f % 300 == 0: print('frame', f, '/', nfr, flush=True)
    p.stdin.close(); p.wait()
    print('done', out)
