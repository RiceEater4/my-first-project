"""Pixel-art study in the clean style of the reference: flat shades, black outlines,
contour-following shading, curved water bands. Drawn on 180x320, scaled 6x to 1080x1920."""
import numpy as np, math
from PIL import Image

W, H, S = 180, 320, 6
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16
YY, XX = np.mgrid[0:H, 0:W]
def c(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)
INK = c('#06080e')                      # the black outline colour

def dilate(m):
    p = np.pad(m, 1)
    return m | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]

def layer(F, mask, colours):
    """outline then fill: 1px black ring around every visible edge"""
    F[dilate(mask) & ~mask] = INK
    F[mask] = colours[mask]

# ================================================================ water: bands with curved, unique edges
WATER = [c('#050a16'), c('#08101f'), c('#0c172b'), c('#112038'), c('#162a46')]
wave1 = 132 + 14 * np.sin(XX / 21 + 0.7) + 6 * np.sin(XX / 8.5 + 2.1) + 3 * np.sin(XX / 4.1)
wave2 = 232 + 16 * np.sin(XX / 26 + 2.4) + 7 * np.sin(XX / 10 + 0.3) + 3 * np.sin(XX / 5.3 + 1)
v = np.where(YY < wave1, 2.2 - 0.9 * np.clip((wave1 - YY) / 130, 0, 1),
     np.where(YY < wave2, 3.3 - 0.6 * np.abs((YY - (wave1 + wave2) / 2) / ((wave2 - wave1) / 2)) ** 3,
              1.6 - 1.3 * np.clip((YY - wave2) / 90, 0, 1)))
edge = np.minimum(np.abs(YY - wave1), np.abs(YY - wave2)) < 3          # dither only along the curved edges
F = np.stack(WATER)[np.clip(np.floor(v + np.where(edge, BAYER[YY % 4, XX % 4] - 0.5, 0)), 0, 4).astype(int)].astype(np.uint8)
rng = np.random.default_rng(4)
for _ in range(60):
    x, y = rng.integers(0, W), rng.integers(0, H)
    F[y, x] = c('#2e6f80') if rng.random() < 0.5 else c('#1c4554')

# ================================================================ shark geometry
X0, YC = 74, 186                          # snout tip, body centre line at the head
def top_y(x):
    u = x - X0
    return YC - 2 - 20 * (1 - math.exp(-u / 20)) - 0.04 * max(0, u - 60)
def bot_y(x):
    u = x - X0
    return YC + 3 + 17 * (1 - math.exp(-u / 24))
CORNER = (X0 + 30, YC + 9)                # back corner of the mouth
def upper_jaw_y(x):                       # underside of the upper jaw, snout -> corner
    s = (x - X0) / (CORNER[0] - X0)
    return YC + 2 + (CORNER[1] - YC - 2) * s ** 1.4
def lower_jaw_top(x):                     # the open lower jaw hangs down and forward
    s = (CORNER[0] - x) / (CORNER[0] - X0 - 6)
    return CORNER[1] + 13 * s

body = np.zeros((H, W), bool)
for x in range(X0, W):
    t, b = top_y(x), bot_y(x)
    body[int(math.ceil(t)):int(b) + 1, x] = True
    if x < CORNER[0]:                     # carve the open mouth out of the head
        body[int(upper_jaw_y(x)) + 1:, x] = False
mouth = np.zeros((H, W), bool); jaw = np.zeros((H, W), bool)
for x in range(X0 + 6, CORNER[0] + 1):
    uj, lj = upper_jaw_y(x), lower_jaw_top(x)
    mouth[int(uj) + 1:int(lj), x] = True
    jaw[int(lj):int(lj) + 5, x] = True

# contour-following countershading: dark back / mid / light line / white belly along a curved split
G = {'dk': c('#3e4852'), 'md': c('#6c7983'), 'lt': c('#9eabb1'), 'rim': c('#c9d4d6'), 'bl': c('#e4ece9'), 'sh': c('#b8c4c2')}
col = np.zeros((H, W, 3), np.uint8)
for x in range(X0, W):
    t, b = top_y(x), bot_y(x); u = x - X0
    split = t + (b - t) * (0.56 + 0.05 * math.sin(u / 11)) + (2 if x < CORNER[0] else 0)
    for y in range(int(math.ceil(t)), int(b) + 1):
        if y < t + 1.5: k = G['rim'] if u < 70 else G['lt']          # lit edge along the back
        elif y < t + (split - t) * 0.45: k = G['dk']
        elif y < split - 1: k = G['md']
        elif y < split: k = G['lt']
        elif y > b - 2.5: k = G['sh']                                 # belly shadow
        else: k = G['bl']
        col[y, x] = k

# fins
dorsal = np.zeros((H, W), bool); pect = np.zeros((H, W), bool)
for x in range(X0 + 58, X0 + 92):
    k = x - (X0 + 58); base = top_y(x) + 1
    h = 26 * (k / 13) if k < 13 else 26 * ((34 - k) / 21) ** 1.6
    dorsal[int(base - h):int(base) + 1, x] = True
for x in range(X0 + 40, X0 + 72):
    k = x - (X0 + 40); base = bot_y(x) - 2
    h = 6 + 16 * (k / 32) ** 1.3 if k < 26 else (6 + 16 * (26 / 32) ** 1.3) * (32 - k) / 6
    pect[int(base):int(base + h), x] = True
fincol = np.zeros((H, W, 3), np.uint8)
fincol[:] = G['dk']
for y, x in zip(*np.nonzero(dorsal)):
    if x - (X0 + 58) < 13 and not dorsal[y, x - 1]: fincol[y, x] = G['lt']     # lit leading edge
pcol = np.zeros((H, W, 3), np.uint8); pcol[:] = G['md']
for y, x in zip(*np.nonzero(pect)):
    if not pect[y - 1, x]: pcol[y, x] = G['dk']

# ================================================================ hagfish
def bez(p0, p1, p2, p3, n=500):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3
P = lambda a, b: np.array([a, b], float)
CURVE = np.vstack([bez(P(8, 226), P(30, 214), P(58, 200), P(X0 + 20, YC + 16)),
                   bez(P(X0 + 20, YC + 16), P(X0 + 44, YC + 24), P(X0 + 66, YC + 26), P(X0 + 70, YC + 50))])
PK = [c('#6a2a46'), c('#a2506e'), c('#cc7a92'), c('#eda8b8')]
hag = np.zeros((H, W), bool); hcol = np.zeros((H, W, 3), np.uint8); hs = np.zeros((H, W))
ys, xs = np.nonzero((YY > 170) & (YY < 250))
for y, x in zip(ys, xs):
    d = np.hypot(CURVE[:, 0] - x, CURVE[:, 1] - y); i = int(np.argmin(d)); s = i / len(CURVE)
    r = 4.0 + 2.2 * math.sin(min(1, s * 1.6) * math.pi / 2) - (3.8 * (s - 0.82) / 0.18 if s > 0.82 else 0)
    if d[i] > r or s < 0.004: continue
    hag[y, x] = True; hs[y, x] = s
    seg = CURVE[min(i + 1, len(CURVE) - 1)] - CURVE[max(i - 1, 0)]
    nrm = np.array([-seg[1], seg[0]]); nrm /= np.linalg.norm(nrm) + 1e-9
    if nrm[1] > 0: nrm = -nrm                                          # normal pointing up
    off = -((x - CURVE[i, 0]) * nrm[0] + (y - CURVE[i, 1]) * nrm[1]) / r   # -1 top .. +1 bottom
    k = PK[3] if off < -0.55 else PK[2] if off < 0.1 else PK[1] if off < 0.6 else PK[0]
    if 0.15 < off < 0.4 and (i // 9) % 2 == 0 and 0.05 < s < 0.8: k = PK[0]    # row of slime pores
    if s > 0.88 and off > -0.2 and (x + y) % 3 == 0: k = PK[0]           # tail fin rays
    hcol[y, x] = k
for dx, dy in ((-1, -1), (-2, -2), (-1, 1), (-2, 2)):                    # barbels
    hag[226 + dy, 8 + dx] = True; hcol[226 + dy, 8 + dx] = PK[2]

# ================================================================ compose (back to front)
behind = hag & (XX > CORNER[0])
layer(F, behind, hcol)
layer(F, pect, pcol)
layer(F, dorsal, fincol)
layer(F, body, col)
F[mouth] = c('#2a0c16'); F[mouth & (YY > YY.max())] = 0
front = hag & (XX <= CORNER[0])
F[dilate(front) & ~front & (XX <= CORNER[0]) & ~hag] = INK      # outline, but no seam where it enters the mouth
F[front] = hcol[front]
layer(F, jaw, np.broadcast_to(G['bl'], (H, W, 3)).copy())
for x in range(X0 + 7, CORNER[0] - 1, 3):                                # teeth
    uj, lj = int(upper_jaw_y(x)), int(lower_jaw_top(x))
    F[uj + 1, x] = F[uj + 2, x] = c('#f6f8fa'); F[uj + 1, x + 1] = c('#f6f8fa')
    F[lj - 1, x + 1] = F[lj - 2, x + 1] = c('#f6f8fa'); F[lj - 1, x] = c('#f6f8fa')
for k in range(5):                                                       # curved gill slits
    gx = X0 + 34 + k * 3
    for j in range(9):
        F[int(top_y(gx) + 10 + j), gx + (1 if 2 < j < 7 else 0)] = INK
F[YC - 1, X0 + 5] = INK; F[YC - 1, X0 + 6] = INK                       # nostril
ex, ey, er = X0 + 19, YC - 8, 5.2                                        # big eye
for y in range(int(ey - er - 1), int(ey + er + 2)):
    for x in range(int(ex - er - 1), int(ex + er + 2)):
        d = math.hypot(x + 0.5 - ex, y + 0.5 - ey)
        if d <= er:
            F[y, x] = INK if d > er - 1 else (c('#a8fff4') if (x < ex - 1 and y < ey - 1 and d > er - 2.5) else c('#45d2c6'))
for y in range(int(ey - 2), int(ey + 2)):
    for x in range(int(ex - 1), int(ex + 3)):
        if math.hypot(x + 0.5 - ex - 0.5, y + 0.5 - ey) <= 2.2: F[y, x] = INK
F[int(ey - 2), int(ex - 2)] = c('#ffffff')
SLIME = c('#bfe9ee')                                                      # slime strings at the bite
for k in range(6):
    sx = X0 + 4 + k * 4
    for j in range(4 + k % 3 * 2):
        y = int(upper_jaw_y(sx) + 3 + j * 1.6); x = sx - j // 2
        if 0 <= y < H and not front[y, x]: F[y, x] = SLIME

# ================================================================ bubbles: a loose trail rising from the bite
placed = []
tries = 0
while len(placed) < 13 and tries < 5000:
    tries += 1
    s = rng.random()
    by = 168 - s * 64 + rng.normal(0, 3)
    bx = X0 + 4 - s * 46 + rng.normal(0, 9)
    r = float(rng.choice([2.2, 2.7, 3.2, 3.8]))
    if any(math.hypot(bx - px, by - py) < r + pr + 4 for px, py, pr in placed): continue
    if body[int(by), int(bx)] or by < 102: continue
    placed.append((bx, by, r))
for bx, by, r in placed:
    for y in range(int(by - r - 1), int(by + r + 2)):
        for x in range(int(bx - r - 1), int(bx + r + 2)):
            if abs(math.hypot(x + 0.5 - bx, y + 0.5 - by) - r) < 0.55 and not body[y, x]: F[y, x] = c('#3fa0ae')
    F[int(by - r * 0.55), int(bx - r * 0.55)] = c('#a8f0f6')

# ================================================================ caption
FONT = {'A': ["01110","10001","10001","11111","10001","10001","10001"], 'F': ["11111","10000","10000","11110","10000","10000","10000"],
 'G': ["01110","10001","10000","10111","10001","10001","01111"], 'H': ["10001","10001","10001","11111","10001","10001","10001"],
 'I': ["01110","00100","00100","00100","00100","00100","01110"], 'K': ["10001","10010","10100","11000","10100","10010","10001"],
 'L': ["10000","10000","10000","10000","10000","10000","11111"], 'M': ["10001","11011","10101","10101","10001","10001","10001"],
 'R': ["11110","10001","10001","11110","10100","10010","10001"], 'S': ["01111","10000","10000","01110","00001","00001","11110"],
 'V': ["10001","10001","10001","10001","10001","01010","00100"], 'E': ["11111","10000","10000","11110","10000","10000","11111"], ' ': ["00000"] * 7}
lines, sc, pad = ["HAGFISH", "SLIME", "VS A SHARK"], 2, 3
tw = max(len(l) for l in lines) * 6 * sc - sc; th = len(lines) * 9 * sc - 2 * sc
bw, bh = tw + 2 * pad, th + 2 * pad
bx0, by0 = (W - bw) // 2, 34
box = np.ones((bh, bw), bool)
for cy, cx in ((0, 0), (0, bw - 1), (bh - 1, 0), (bh - 1, bw - 1)): box[cy, cx] = False
F[by0:by0 + bh, bx0:bx0 + bw][box] = 0
for li, ln in enumerate(lines):
    off = (tw - (len(ln) * 6 * sc - sc)) // 2
    for ci, ch in enumerate(ln):
        g = np.kron(np.array([[q == '1' for q in r] for r in FONT[ch]]), np.ones((sc, sc), bool))
        y0, x0 = by0 + pad + li * 9 * sc, bx0 + pad + off + ci * 6 * sc
        F[y0:y0 + 7 * sc, x0:x0 + 5 * sc][g] = 255

Image.fromarray(np.repeat(np.repeat(F, S, 0), S, 1)).save('hagfish_vs_shark.png')
print('saved')
