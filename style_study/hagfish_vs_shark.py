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
# four close shades of the same navy (light at the top -> dark at the bottom),
# split by three smooth curves with a short ordered-dither blend across each
WATER = [c('#15253f'), c('#111f36'), c('#0d192d'), c('#0a1324')]
curves = [92 + 10 * np.sin(XX / 33 + 0.7) + 4 * np.sin(XX / 18 + 2.1),
          176 + 12 * np.sin(XX / 37 + 2.4) + 5 * np.sin(XX / 21 + 0.3),
          256 + 11 * np.sin(XX / 35 + 4.0) + 4 * np.sin(XX / 17 + 1.2)]
RAMP = 6.0
v = sum(np.clip((YY - cv) / RAMP + 0.5, 0, 1) for cv in curves)
F = np.stack(WATER)[np.clip(np.floor(v + BAYER[YY % 4, XX % 4]), 0, 3).astype(int)].astype(np.uint8)
rng = np.random.default_rng(4)
for _ in range(60):
    x, y = rng.integers(0, W), rng.integers(0, H)
    F[y, x] = c('#2e6f80') if rng.random() < 0.5 else c('#1c4554')

# ================================================================ shark: long, thin, friendly (proportions measured from the reference)
X0, TIPY = 93, 153                        # snout tip
CORNER = (113, 160)                       # back corner of the open mouth
def top_y(x):
    u = x - X0
    return TIPY - 9.5 * math.sqrt(min(u, 26) / 26) - 0.03 * max(0, u - 26)
def jaw_y(x):                             # underside of the upper jaw (snout -> mouth corner)
    s_ = (x - X0) / (CORNER[0] - X0)
    return TIPY + 1 + (CORNER[1] - TIPY - 1) * s_ ** 1.2
def bot_y(x):
    if x < CORNER[0]: return jaw_y(x)
    return CORNER[1] + 7 * math.sqrt(min(x - CORNER[0], 22) / 22)

G = {'dk': c('#4f5963'), 'md': c('#7a868e'), 'lt': c('#a9b4b8'), 'bl': c('#dfe7e4'), 'fin': c('#454e57'), 'jaw': c('#c3cdcc')}
body = np.zeros((H, W), bool); col = np.zeros((H, W, 3), np.uint8)
for x in range(X0, W):
    t, b = top_y(x), bot_y(x)
    for y in range(int(math.ceil(t)), int(math.floor(b)) + 1):
        body[y, x] = True
        f = (y - t) / max(1.0, (bot_y(max(x, CORNER[0] + 8)) - t))
        col[y, x] = G['dk'] if f < 0.3 else G['md'] if f < 0.5 else G['lt'] if f < 0.66 else G['bl']

dorsal = np.zeros((H, W), bool); dcol = np.zeros((H, W, 3), np.uint8); dcol[:] = G['fin']
DB0, DPK, DB1 = (150, 142), (167, 121), (179, 141)                 # big swept dorsal fin
for x in range(DB0[0], DB1[0] + 1):
    base = top_y(x) + 1
    if x <= DPK[0]: ytop = DB0[1] + (DPK[1] - DB0[1]) * ((x - DB0[0]) / (DPK[0] - DB0[0])) ** 0.9
    else: ytop = DPK[1] + (DB1[1] - DPK[1]) * ((x - DPK[0]) / (DB1[0] - DPK[0])) ** 2.2
    if ytop < base: dorsal[int(round(ytop)):int(base) + 1, x] = True
for k in range(2, 13):                                           # thin light leading edge
    x = DB0[0] + k; y = DB0[1] + (DPK[1] - DB0[1]) * (k / (DPK[0] - DB0[0])) ** 0.9
    dcol[int(round(y)) + 1, x] = c('#d6dfe0')

pect = np.zeros((H, W), bool)                                     # pectoral fin: long, swept back and down
PF0, PTIP, PF1 = (128, 166), (156, 184), (150, 167)
for x in range(PF0[0], PTIP[0] + 1):
    base = bot_y(x) - 1
    ylow = PF0[1] + (PTIP[1] - PF0[1]) * ((x - PF0[0]) / (PTIP[0] - PF0[0])) ** 1.25
    if x > PF1[0]:                                                # trailing edge curls back up to the body
        yhigh = PF1[1] + (PTIP[1] - PF1[1]) * ((x - PF1[0]) / (PTIP[0] - PF1[0])) ** 0.6
        pect[int(round(yhigh)):int(round(ylow)) + 1, x] = True
    else:
        pect[int(base):int(round(ylow)) + 1, x] = True
pcol = np.zeros((H, W, 3), np.uint8); pcol[:] = G['fin']
for y, x in zip(*np.nonzero(pect)):
    if pect[y - 1, x] and not pect[min(H - 1, y + 1), x]: pcol[y, x] = c('#2f363d')    # shade along the lower edge

mouth = np.zeros((H, W), bool); jaw = np.zeros((H, W), bool)
JAW_TIP = (103, 174)
for k in range(80):                                              # lower jaw: a light wedge, thick at the hinge
    s_ = k / 79
    x = CORNER[0] - (CORNER[0] - JAW_TIP[0]) * s_; y = CORNER[1] + 1 + (JAW_TIP[1] - CORNER[1] - 1) * s_
    th = 4 - 2.5 * s_
    jaw[int(round(y)):int(round(y + th)), int(round(x))] = True
    jaw[int(round(y)):int(round(y + th)), int(round(x)) + 1] = True
for x in range(X0 + 2, CORNER[0] + 1):
    ytop = int(jaw_y(x)) + 1
    s_ = (CORNER[0] - x) / (CORNER[0] - JAW_TIP[0])
    ylow = int(CORNER[1] + 1 + (JAW_TIP[1] - CORNER[1] - 1) * min(1, s_)) if x >= JAW_TIP[0] else ytop
    mouth[ytop:ylow, x] = True

# ================================================================ hagfish
def bez(p0, p1, p2, p3, n=500):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3
P = lambda a, b: np.array([a, b], float)
CURVE = np.vstack([bez(P(14, 189), P(45, 172), P(80, 160), P(110, 162)),
                   bez(P(110, 162), P(132, 164), P(150, 168), P(156, 186))])
PK = [c('#7a3550'), c('#ab5b78'), c('#cf8199'), c('#eaa9b9')]
hag = np.zeros((H, W), bool); hcol = np.zeros((H, W, 3), np.uint8)
ys, xs = np.nonzero((YY > 145) & (YY < 200))
for y, x in zip(ys, xs):
    d = np.hypot(CURVE[:, 0] - x, CURVE[:, 1] - y); i = int(np.argmin(d)); s_ = i / len(CURVE)
    r = 1.5 + 3.3 * min(1, s_ / 0.12) + (1.2 * (s_ - 0.85) / 0.15 if s_ > 0.85 else 0)
    if d[i] > r: continue
    hag[y, x] = True
    seg = CURVE[min(i + 1, len(CURVE) - 1)] - CURVE[max(i - 1, 0)]
    nrm = np.array([-seg[1], seg[0]]); nrm /= np.linalg.norm(nrm) + 1e-9
    if nrm[1] > 0: nrm = -nrm
    off = -((x - CURVE[i, 0]) * nrm[0] + (y - CURVE[i, 1]) * nrm[1]) / r
    hcol[y, x] = PK[3] if off < -0.5 else PK[2] if off < 0.15 else PK[1] if off < 0.65 else PK[0]
    if s_ > 0.9 and off > -0.3 and (x + 2 * y) % 4 == 0: hcol[y, x] = PK[0]
for dx, dy in ((-2, 0), (-3, -1), (-3, 1)):                     # barbels
    hag[189 + dy, 14 + dx] = True; hcol[189 + dy, 14 + dx] = PK[2]

# ================================================================ compose (back to front)
behind = hag & (XX > CORNER[0])
layer(F, behind, hcol)
layer(F, dorsal, dcol)
layer(F, body, col)
layer(F, pect, pcol)
F[mouth] = c('#3a1220')
front = hag & (XX <= CORNER[0]) & ~body
F[dilate(front) & ~front & ~hag & ~body] = INK
F[front] = hcol[front]
layer(F, jaw, np.broadcast_to(G['jaw'], (H, W, 3)).copy())
for x in range(X0 + 3, CORNER[0], 2):                           # upper teeth
    F[int(jaw_y(x)) + 1, x] = c('#f6f8fa')
for k in range(2, 10, 2):                                        # lower teeth
    x = CORNER[0] - k; y = int(round(CORNER[1] + 1 + (JAW_TIP[1] - CORNER[1] - 1) * k / (CORNER[0] - JAW_TIP[0]))) - 1
    F[y, x] = c('#f6f8fa')
for gx in (126, 129, 132, 135, 138):                             # gill slits
    F[150:158, gx] = INK
ex, ey = 106.5, 150.5                                            # big friendly eye
for y in range(144, 158):
    for x in range(99, 115):
        d = math.hypot(x + 0.5 - ex, y + 0.5 - ey)
        if d <= 4.4: F[y, x] = INK if d > 3.4 else (INK if d < 1.7 else c('#43d0c4'))
F[148, 105] = c('#ffffff')

# ================================================================ bubbles: a loose trail rising from the bite
placed = []
tries = 0
while len(placed) < 13 and tries < 5000:
    tries += 1
    s = rng.random()
    by = 140 - s * 37
    bx = 103 + 3 * math.sin(s * 9) + rng.normal(0, 2 + 9 * s)      # rises straight up, spreading a little
    r = float(rng.choice([2.3, 2.6, 3.0, 3.6]))
    if any(math.hypot(bx - px, by - py) < r + pr + 4 for px, py, pr in placed): continue
    if body[int(by), int(bx)] or dorsal[int(by), int(bx)] or by < 103 or by > 138 or (bx > 140 and by > 118): continue
    placed.append((bx, by, r))
for bx, by, r in placed:
    for y in range(int(by - r - 1), int(by + r + 2)):
        for x in range(int(bx - r - 1), int(bx + r + 2)):
            if abs(math.hypot(x + 0.5 - bx, y + 0.5 - by) - r) < 0.62 and not body[y, x]: F[y, x] = c('#3fa0ae')
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
bx0, by0 = (W - bw) // 2, 38
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
