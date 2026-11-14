"""Blueprint pixel-art style kit (studied from the reference shorts).

- smooth navy blueprint background: vertical gradient, soft glow behind the subject, faint 60-px grid, dark corners
- chunky pixel subjects (6 screen-px pixels), dark NAVY outline, 3-5 shades per material, checker dither where shades meet
- floating diorama tile (top surface + thick front edge + soft shadow)
- captions: no box, heavy bold sans uppercase, dark outline, 1-3 words, key word in yellow/lime, ~2/3 down
- labels: tiny pixel text with a thin leader line, or a black boxed tag; pixel arrows
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WF, HF, PX = 1080, 1920, 6                      # full frame and pixel size
OUTLINE = np.array([11, 21, 48], np.float32) / 255
YELLOW = (255, 200, 58); LIME = (196, 245, 58); WHITE = (255, 255, 255)
FONT_BOLD = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'

def hexc(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)

def background(glow_xy=(540, 760), seed=0):
    yy, xx = np.mgrid[0:HF, 0:WF].astype(np.float32)
    top, mid, low = hexc('#0f2a55'), hexc('#1f4782'), hexc('#162f5c')
    f = yy / HF
    base = np.where((f < 0.45)[..., None], top + (mid - top) * (f / 0.45)[..., None], mid + (low - mid) * ((f - 0.45) / 0.55)[..., None])
    gx, gy = glow_xy
    glow = np.exp(-(((xx - gx) / 520) ** 2 + ((yy - gy) / 640) ** 2))
    base = base + glow[..., None] * hexc('#123a70') * 0.55
    vig = np.clip(1 - 0.35 * ((np.abs(xx - WF / 2) / (WF / 2)) ** 2 + (np.abs(yy - HF / 2) / (HF / 2)) ** 2) / 2, 0, 1)
    base = base * vig[..., None]
    grid = ((xx.astype(int) % 60) == 0) | ((yy.astype(int) % 60) == 0)
    base[grid] = base[grid] * 1.12 + 0.012
    r = np.random.default_rng(seed); base += (r.random((HF, WF, 1)) - 0.5) * 0.012
    return np.clip(base, 0, 1)

def dither_seams(col, M):
    """where two shades meet inside a sprite, checkerboard them together (the crunchy reference texture)"""
    out = col.copy(); h, w = M.shape
    yy, xx = np.mgrid[0:h, 0:w]
    for dy, dx in ((0, 1), (1, 0)):
        nb = np.roll(np.roll(col, -dy, 0), -dx, 1); nbm = np.roll(np.roll(M, -dy, 0), -dx, 1)
        diff = M & nbm & (np.abs(col - nb).sum(-1) > 0.02) & (np.abs(col - OUTLINE).sum(-1) > 0.05) & (np.abs(nb - OUTLINE).sum(-1) > 0.05)
        pick = diff & ((xx + yy) % 2 == 0)
        out[pick] = nb[pick]
    return out

def speckle(col, M, shades_from, shades_to, density, seed):
    """scatter single pixels of a neighbouring shade inside a material (grass / snow texture)"""
    r = np.random.default_rng(seed); m = M & (np.abs(col - shades_from).sum(-1) < 0.02) & (r.random(M.shape) < density)
    col[m] = shades_to
    return col

def outline(col, M):
    p = np.pad(M, 1); ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~M
    col = col.copy(); col[ring] = OUTLINE
    return col, M | ring

def blit(F, col, M, x, y, px=PX):
    """paste a pixel sprite (grid units) at full-res position x,y (top-left, screen px)"""
    C = np.repeat(np.repeat(col, px, 0), px, 1); K = np.repeat(np.repeat(M, px, 0), px, 1)
    x, y = int(round(x)), int(round(y)); h, w = K.shape
    x0, y0, x1, y1 = max(0, x), max(0, y), min(WF, x + w), min(HF, y + h)
    if x1 <= x0 or y1 <= y0: return
    k = K[y0 - y:y1 - y, x0 - x:x1 - x]
    F[y0:y1, x0:x1][k] = C[y0 - y:y1 - y, x0 - x:x1 - x][k]

def soft_shadow(F, cx, cy, rx, ry, a=0.45):
    yy, xx = np.mgrid[0:HF, 0:WF]
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    m = np.clip(1.15 - d, 0, 1) * a
    F[:] = F * (1 - m[..., None]) + (F * 0.35) * m[..., None]

def diorama(w, h, depth, top_shades, side_shades, seed=0):
    """rounded floating tile seen slightly from above: textured top + thick front edge (grid units)"""
    H_ = h + depth + 2; col = np.zeros((H_, w, 3), np.float32); M = np.zeros((H_, w), bool)
    yy, xx = np.mgrid[0:H_, 0:w]
    rad = min(w, h) * 0.18
    def rr(y0, y1):
        cx = np.clip(xx, rad, w - 1 - rad); cy = np.clip(yy, y0 + rad, y1 - rad)
        return ((xx - cx) ** 2 + (yy - cy) ** 2) <= rad ** 2
    top = rr(0, h - 1); side = rr(depth, h - 1 + depth) & ~top
    col[side] = side_shades[1]; col[side & (yy > h - 1 + depth * 0.55)] = side_shades[0]
    col[side & (xx < 3)] = side_shades[2]
    v = 1.2 + 1.8 * (1 - yy / h) - 0.6 * (xx / w)
    idx = np.clip(np.floor(v), 0, len(top_shades) - 1).astype(int)
    col[top] = np.stack(top_shades)[idx][top]
    M = top | side
    col = dither_seams(col, M)
    col = speckle(col, top, top_shades[2], top_shades[1], 0.06, seed)
    col = speckle(col, top, top_shades[1], top_shades[0], 0.05, seed + 1)
    col[top & ~np.roll(top, 1, 0)] = np.minimum(1, top_shades[-1] * 1.05)
    return outline(col, M)

def caption(F, words, y=1290, size=78, highlight=()):
    """bold uppercase caption, no box, dark outline + drop shadow; words in `highlight` turn yellow"""
    img = Image.fromarray((F * 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_BOLD, size)
    words = [w_.upper() for w_ in words]; space = size * 0.28
    widths = [d.textlength(w_, font=font) for w_ in words]; total = sum(widths) + space * (len(words) - 1)
    x = (WF - total) / 2
    for w_, wd in zip(words, widths):
        colr = YELLOW if w_.strip('.,!?') in [h.upper() for h in highlight] else WHITE
        d.text((x + 5, y + 7), w_, font=font, fill=(6, 10, 24), stroke_width=7, stroke_fill=(6, 10, 24))
        d.text((x, y), w_, font=font, fill=colr, stroke_width=7, stroke_fill=(8, 14, 30))
        x += wd + space
    F[:] = np.asarray(img).astype(np.float32) / 255

PIXFONT = {'A': ["01110","10001","10001","11111","10001","10001","10001"], 'B': ["11110","10001","10001","11110","10001","10001","11110"],
 'E': ["11111","10000","10000","11110","10000","10000","11111"], 'L': ["10000","10000","10000","10000","10000","10000","11111"],
 'P': ["11110","10001","10001","11110","10000","10000","10000"], 'G': ["01110","10001","10000","10111","10001","10001","01111"],
 'I': ["01110","00100","00100","00100","00100","00100","01110"], 'F': ["11111","10000","10000","11110","10000","10000","10000"],
 'T': ["11111","00100","00100","00100","00100","00100","00100"], 'S': ["01111","10000","10000","01110","00001","00001","11110"],
 'N': ["10001","10001","11001","10101","10011","10001","10001"], 'O': ["01110","10001","10001","10001","10001","10001","01110"],
 'U': ["10001","10001","10001","10001","10001","10001","01110"], 'R': ["11110","10001","10001","11110","10100","10010","10001"],
 'C': ["01110","10001","10000","10000","10000","10001","01110"], 'H': ["10001","10001","10001","11111","10001","10001","10001"],
 'Y': ["10001","10001","01010","00100","00100","00100","00100"], ' ': ["00000"] * 7, ':': ["00000","00100","00000","00000","00000","00100","00000"],
 '?': ["01110","10001","00001","00010","00100","00000","00100"],
 '2': ['01110', '10001', '00001', '00010', '00100', '01000', '11111'],
 '3': ['11110', '00001', '00001', '01110', '00001', '00001', '11110'],
 '4': ['00010', '00110', '01010', '10010', '11111', '00010', '00010'],
 '5': ['11111', '10000', '11110', '00001', '00001', '10001', '01110'],
 '6': ['00110', '01000', '10000', '11110', '10001', '10001', '01110'],
 '7': ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
 '8': ['01110', '10001', '10001', '01110', '10001', '10001', '01110'],
 '9': ['01110', '10001', '10001', '01111', '00001', '00010', '01100'],
 '/': ['00001', '00010', '00010', '00100', '01000', '01000', '10000'],
 'W': ['10001', '10001', '10001', '10101', '10101', '10101', '01010'],
 'K': ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
 'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
 'M': ['10001', '11011', '10101', '10101', '10001', '10001', '10001'],
 'V': ['10001', '10001', '10001', '10001', '10001', '01010', '00100'],
 ',': ['00000', '00000', '00000', '00000', '00110', '00100', '01000'],
 '-': ['00000', '00000', '00000', '11111', '00000', '00000', '00000'],
 '.': ['00000', '00000', '00000', '00000', '00000', '01100', '01100'],
 '+': ['00000', '00100', '00100', '11111', '00100', '00100', '00000'],
 'X': ['10001', '10001', '01010', '00100', '01010', '10001', '10001'],
 '0': ["01110","10001","10011","10101","11001","10001","01110"], '1': ["00100","01100","00100","00100","00100","00100","01110"]}
def pixel_text(F, text, x, y, px=4, colr=(235, 240, 255)):
    for i, ch in enumerate(text):
        for r, row in enumerate(PIXFONT.get(ch, PIXFONT[' '])):
            for c, b in enumerate(row):
                if b == '1': F[y + r * px:y + (r + 1) * px, x + (i * 6 + c) * px:x + (i * 6 + c + 1) * px] = np.array(colr) / 255
    return len(text) * 6 * px - px

def label(F, text, tx, ty, ax, ay, px=4):
    """thin pixel label at (tx,ty) with a leader line to (ax,ay)"""
    w_ = pixel_text(F, text, tx, ty, px)
    sx, sy = (tx + w_ // 2, ty + 9 * px) if ay > ty else (tx + w_ // 2, ty - 2 * px)
    n = int(max(abs(ax - sx), abs(ay - sy)))
    for k in range(n):
        x = int(sx + (ax - sx) * k / n); y = int(sy + (ay - sy) * k / n)
        F[y:y + 2, x:x + 2] = np.array([0.92, 0.95, 1.0])

def tag(F, text, x, y, px=5):
    """black boxed label with a thin light border (like 'MOAT')"""
    w_ = len(text) * 6 * px - px; h_ = 7 * px; pad = 3 * px
    F[y - pad:y + h_ + pad, x - pad:x + w_ + pad] = np.array([0.04, 0.06, 0.12])
    for t_ in range(2):
        F[y - pad + t_, x - pad:x + w_ + pad] = F[y + h_ + pad - 1 - t_, x - pad:x + w_ + pad] = 0.9
        F[y - pad:y + h_ + pad, x - pad + t_] = F[y - pad:y + h_ + pad, x + w_ + pad - 1 - t_] = 0.9
    pixel_text(F, text, x, y, px)

ARROW = ["1000000", "0110000", "0111000", "0011100", "0001111", "0000111", "0000111"]
def arrow(F, x, y, px=PX):
    col = np.zeros((7, 7, 3), np.float32); M = np.array([[c == '1' for c in r] for r in ARROW])
    col[M] = hexc('#f6e7c8'); col, M = outline(col, M); blit(F, col, M, x, y, px)
