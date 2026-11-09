"""Pixel-art study in the clean style of the reference: flat shades, crisp bands,
dark outlines with a lit rim, calm dark-navy water. Drawn on 180x320, scaled 6x."""
import numpy as np, math
from PIL import Image

W, H, S = 180, 320, 6
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16
YY, XX = np.mgrid[0:H, 0:W]
def c(h): h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)

F = np.zeros((H, W, 3), np.uint8)
# ---- water: dark navy, a soft dithered band of lighter water behind the action
WATER = [c('#060c1a'), c('#0a1426'), c('#0e1b32'), c('#13233e')]
v = 1.2 + 1.6 * np.exp(-((YY - 150) / 70) ** 2) - 0.9 * (YY / H)
v = v + 0.5 * np.exp(-((YY - 175) / 18) ** 2)
F[:] = np.stack(WATER)[np.clip(np.floor(v + BAYER[YY % 4, XX % 4] - 0.5), 0, 3).astype(int)]
rng = np.random.default_rng(4)
for _ in range(55):                                          # floating specks
    x, y = rng.integers(0, W), rng.integers(0, H)
    F[y, x] = c('#2e6f80') if rng.random() < 0.6 else c('#1f4a5a')

# ---- hagfish: a pink tube along a curve, lit from above
def bez(p0, p1, p2, p3, n=400):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3
CURVE = np.vstack([bez(np.array([12, 166]), np.array([40, 146]), np.array([75, 134]), np.array([100, 138])),
                   bez(np.array([100, 138]), np.array([125, 142]), np.array([138, 150]), np.array([137, 166]))])
PINK = [c('#5a2440'), c('#9a4c68'), c('#c87a90'), c('#e9a6b6')]
def draw_hagfish(region):
    for y in range(H):
        for x in range(W):
            if not region(x, y): continue
            d = np.hypot(CURVE[:, 0] - x, CURVE[:, 1] - y); i = int(np.argmin(d))
            s = i / len(CURVE)
            r = 3.2 + 2.0 * math.sin(min(1, s * 1.4) * math.pi / 2) - (2.4 * (s - 0.8) / 0.2 if s > 0.8 else 0)
            if d[i] > r or s < 0.003: continue
            off = (y - CURVE[i, 1]) / r                          # -1 top .. +1 bottom
            if d[i] > r - 1: col = PINK[3] if off < -0.4 else PINK[0]       # lit rim / dark outline
            else: col = PINK[3] if off < -0.45 else PINK[2] if off < 0.2 else PINK[1]
            if s > 0.86 and off > -0.3 and (x + y) % 3 == 0: col = PINK[0]   # tail fin rays
            F[y, x] = col
    for dx, dy in ((-1, 0), (-2, -1), (-2, 1), (-3, 0)):        # barbels on the head
        F[166 + dy, 11 + dx] = PINK[2]

draw_hagfish(lambda x, y: x > 104)                             # back half (behind the shark)

# ---- shark: torpedo pointing left, crisp grey bands, belly, dark outline
GREY = {'out': c('#141a22'), 'dark': c('#4a545e'), 'mid': c('#76838c'), 'light': c('#a5b2b6'), 'belly': c('#d8e2e0')}
X0, YC = 80, 130
def prof(x):
    u = x - X0
    top = YC - 1 - 15 * min(1, math.sqrt(max(u, 0) / 48))
    bot = YC + 3 + 13 * min(1, math.sqrt(max(u, 0) / 40))
    return top, bot
SH = np.zeros((H, W), bool)
for x in range(X0, W):
    top, bot = prof(x)
    SH[int(math.ceil(top)):int(bot) + 1, x] = True
    for y in range(int(math.ceil(top)), int(bot) + 1):
        f = (y - top) / (bot - top)
        col = GREY['dark'] if f < 0.32 else GREY['mid'] if f < 0.55 else GREY['light'] if f < 0.7 else GREY['belly']
        if y == int(math.ceil(top)): col = GREY['out'] if x < X0 + 6 else GREY['light']   # lit back line
        if y == int(bot): col = GREY['out']
        F[y, x] = col
    if x == X0: F[YC - 1:YC + 4, x] = GREY['out']
for k in range(22):                                             # dorsal fin
    base = int(prof(136 + k)[0])
    h = int(20 * k / 9) if k < 9 else int(20 * (22 - k) / 13)
    for y in range(base - h, base):
        F[y, 136 + k] = GREY['light'] if (k < 9 and y == base - h) else (GREY['out'] if y == base - h else GREY['dark'])
for k in range(14):                                             # pectoral fin under the belly
    for j in range(int(k * 0.6)):
        F[prof(126 + k)[1] + j, 120 + k] = GREY['dark']
for gx in (114, 117, 120, 123, 126):                            # gill slits
    for y in range(YC - 2, YC + 5): F[y, gx] = GREY['out']
ex, ey = 99, YC - 5                                             # teal eye
for y in range(ey - 3, ey + 4):
    for x in range(ex - 3, ex + 4):
        d = math.hypot(x - ex, y - ey)
        if d <= 3.3: F[y, x] = GREY['out'] if d > 2.4 else c('#5ee0d4')
F[ey, ex] = F[ey, ex + 1] = F[ey + 1, ex] = F[ey + 1, ex + 1] = GREY['out']
F[ey - 2, ex - 1] = c('#ffffff')
for x in range(X0 + 1, X0 + 22):                                # mouth line + teeth
    y = YC + 3 + (x - X0) // 7
    F[y, x] = GREY['out']
    if x % 3 == 0: F[y - 1, x] = c('#f4f6f8')

draw_hagfish(lambda x, y: x <= 104 and (not SH[y, x] or y > YC + 3 + (x - X0) // 7))   # front half, into the open mouth
for x in range(X0 + 4, X0 + 24):                                # lower jaw over the hagfish
    y = YC + 9 + (x - X0) // 3
    for j in range(2): F[y + j, x] = GREY['belly'] if j == 0 else GREY['out']
    if x % 4 == 0: F[y - 1, x] = c('#f4f6f8')

# ---- bubbles: clean cyan rings rising from the bite
placed = []
while len(placed) < 22:
    bx, by, r = rng.uniform(30, 100), rng.uniform(98, 122), float(rng.choice([1.5, 2.2, 2.8]))
    if any(math.hypot(bx - px, by - py) < r + pr + 2 for px, py, pr in placed): continue
    placed.append((bx, by, r))
    for y in range(int(by - r - 1), int(by + r + 2)):
        for x in range(int(bx - r - 1), int(bx + r + 2)):
            if abs(math.hypot(x - bx, y - by) - r) < 0.55 and not SH[y, x]: F[y, x] = c('#3f9aa8')
    if not SH[int(round(by - r * 0.5)), int(round(bx - r * 0.5))]: F[int(round(by - r * 0.5)), int(round(bx - r * 0.5))] = c('#9ee6ee')

# ---- caption: plain black box, white pixel text, 1px rounded corners
FONT = {'A': ["01110","10001","10001","11111","10001","10001","10001"], 'F': ["11111","10000","10000","11110","10000","10000","10000"],
 'G': ["01110","10001","10000","10111","10001","10001","01111"], 'H': ["10001","10001","10001","11111","10001","10001","10001"],
 'I': ["01110","00100","00100","00100","00100","00100","01110"], 'K': ["10001","10010","10100","11000","10100","10010","10001"],
 'L': ["10000","10000","10000","10000","10000","10000","11111"], 'M': ["10001","11011","10101","10101","10001","10001","10001"],
 'R': ["11110","10001","10001","11110","10100","10010","10001"], 'S': ["01111","10000","10000","01110","00001","00001","11110"],
 'V': ["10001","10001","10001","10001","10001","01010","00100"], 'E': ["11111","10000","10000","11110","10000","10000","11111"], ' ': ["00000"] * 7}
lines, sc, pad = ["HAGFISH", "SLIME", "VS A SHARK"], 2, 3
tw = max(len(l) for l in lines) * 6 * sc - sc; th = len(lines) * 9 * sc - 2 * sc
bx0, by0 = (W - tw) // 2 - pad, 36
F[by0:by0 + th + 2 * pad, bx0:bx0 + tw + 2 * pad] = 0
for yy_, xx_ in ((by0, bx0), (by0, bx0 + tw + 2 * pad - 1), (by0 + th + 2 * pad - 1, bx0), (by0 + th + 2 * pad - 1, bx0 + tw + 2 * pad - 1)):
    F[yy_, xx_] = F[yy_ - 1, xx_]
for li, ln in enumerate(lines):
    off = (tw - (len(ln) * 6 * sc - sc)) // 2
    for ci, ch in enumerate(ln):
        g = np.kron(np.array([[q == '1' for q in r] for r in FONT[ch]]), np.ones((sc, sc), bool))
        y0, x0 = by0 + pad + li * 9 * sc, bx0 + pad + off + ci * 6 * sc
        F[y0:y0 + 7 * sc, x0:x0 + 5 * sc][g] = 255

Image.fromarray(np.repeat(np.repeat(F, S, 0), S, 1)).save('hagfish_vs_shark.png')
print('saved')
