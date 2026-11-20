"""Clean UI pieces for the shorts (approved redesign):
callout(): pixel tag box with drop shadow + chunky outlined leader line with an elbow and a glowing target dot.
thought_bubble(): puffy cloud with navy outline, drop shadow, 3-shade bottom shading, shine, shrinking trail bubbles.
All coordinates are GRID pixels (1 grid px = 6 screen px)."""
import math
import numpy as np
import blueprint_kit as bk
from characters import Layers
from blueprint_kit import hexc, OUTLINE as NAVY
S, W, H = 6, 180, 320
def put(F, x, y, c, a=1.0):
    X, Y = int(round(x * S)), int(round(y * S))
    if 0 <= X < W * S - S and 0 <= Y < H * S - S: F[Y:Y + S, X:X + S] = F[Y:Y + S, X:X + S] * (1 - a) + c * a
def blit_mask(F, M, col, x0, y0, alpha=1.0):
    """paint a grid-pixel mask (with colour array or single colour) onto the screen frame"""
    h_, w_ = M.shape; C = col if col.ndim == 3 else np.broadcast_to(col, (h_, w_, 3))
    for yy in range(h_):
        for xx in range(w_):
            if M[yy, xx]:
                X, Y = int((x0 + xx) * S), int((y0 + yy) * S)
                if 0 <= X < W * S - S and 0 <= Y < H * S - S:
                    F[Y:Y + S, X:X + S] = F[Y:Y + S, X:X + S] * (1 - alpha) + C[yy, xx] * alpha
def ring(M):
    p = np.pad(M, 1); return (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~M

# ---------- NEW: callout label ----------
def callout(F, text, tx, ty, ax, ay, px=5, accent='#ffcc4a'):
    """pixel tag box (with drop shadow) + chunky outlined leader line with an elbow and a target dot.
    tx, ty: tag top-left in GRID px; ax, ay: what it points at (grid px)."""
    tw = len(text) * 6 * px - px                     # text width in screen px
    bw, bh = int(math.ceil((tw + 4 * S) / S)), int(math.ceil((7 * px + 3 * S) / S))
    # leader path: from tag bottom-centre straight down/up, then diagonal to the anchor
    sx, sy = tx + bw // 2, (ty + bh) if ay > ty else ty - 1
    x0, y0 = min(sx, ax) - 3, min(sy, ay) - 3; x1, y1 = max(sx, ax) + 4, max(sy, ay) + 4
    M = np.zeros((y1 - y0, x1 - x0), bool)
    ex, ey = sx, sy + (ay - sy) * 0.45                 # elbow point
    for (a_, b_) in (((sx, sy), (ex, ey)), ((ex, ey), (ax, ay))):
        n = int(max(abs(b_[0] - a_[0]), abs(b_[1] - a_[1]))) + 1
        for k in range(n + 1):
            x = a_[0] + (b_[0] - a_[0]) * k / n; y = a_[1] + (b_[1] - a_[1]) * k / n
            M[int(round(y)) - y0, int(round(x)) - x0] = True
    dot = np.zeros_like(M); yy, xx = np.mgrid[0:M.shape[0], 0:M.shape[1]]
    dot |= (xx + x0 - ax) ** 2 + (yy + y0 - ay) ** 2 <= 2.3
    blit_mask(F, ring(M | dot), NAVY, x0, y0)
    blit_mask(F, M, hexc('#f4f8ff'), x0, y0); blit_mask(F, dot, hexc(accent), x0, y0)
    halo = ((xx + x0 - ax) ** 2 + (yy + y0 - ay) ** 2 <= 9) & ~((xx + x0 - ax) ** 2 + (yy + y0 - ay) ** 2 <= 5.5)
    blit_mask(F, halo, hexc(accent), x0, y0, alpha=0.45)
    # tag: shadow, outline, fill, top highlight, text
    box = np.ones((bh, bw), bool); box[0, 0] = box[0, -1] = box[-1, 0] = box[-1, -1] = False
    blit_mask(F, np.pad(box, 1), hexc('#050a18'), tx - 1 + 1, ty - 1 + 1, alpha=0.6)
    blit_mask(F, ring(np.pad(box, 1))[1:-1, 1:-1] | False, NAVY, tx, ty)
    fill = np.zeros((bh, bw, 3), np.float32) + hexc('#14234a'); fill[0] = hexc('#2a3f78'); fill[-1] = hexc('#0b1530')
    blit_mask(F, box, fill, tx, ty)
    edge = ring(np.pad(box, 1))[1:-1, 1:-1]
    bk.pixel_text(F, text, int(tx * S + (bw * S - tw) / 2), int(ty * S + (bh * S - 7 * px) / 2), px=px, colr=(255, 255, 255))
    for xx_ in range(1, bw - 1): put(F, tx + xx_, ty + bh - 1, hexc(accent))          # accent underline

# ---------- NEW: thought bubble ----------
def cloud_mask(w_, h_):
    """smooth pixel cloud: a rounded core plus evenly spaced puffs all the way around"""
    yy, xx = np.mgrid[0:h_, 0:w_].astype(np.float32); cx, cy = w_ / 2 - 0.5, h_ / 2 - 0.5
    rx, ry = w_ * 0.36, h_ * 0.30
    M = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    n = 11
    for k in range(n):
        th = 2 * math.pi * k / n + 0.2
        r = h_ * (0.20 + 0.035 * ((k * 7) % 3))
        px_, py_ = cx + rx * 0.98 * math.cos(th), cy + ry * 0.92 * math.sin(th)
        M |= (xx - px_) ** 2 + (yy - py_) ** 2 <= r * r
    return M
def thought_bubble(F, cx, cy, w_, h_, tail_to, t=0.0):
    M = cloud_mask(w_, h_); x0, y0 = int(cx - w_ / 2), int(cy - h_ / 2) + int(round(math.sin(t * 2.2)))
    yy, xx = np.mgrid[0:h_, 0:w_]
    col = np.zeros((h_, w_, 3), np.float32) + 1.0
    col[yy > h_ * 0.62] = hexc('#d9e8fb'); col[yy > h_ * 0.78] = hexc('#bcd3f2')     # soft bottom shading (3 shades)
    hl = ((xx - w_ * 0.28) / (w_ * 0.12)) ** 2 + ((yy - h_ * 0.22) / (h_ * 0.07)) ** 2 <= 1
    blit_mask(F, np.pad(M, 1), hexc('#050a18'), x0 - 1 + 2, y0 - 1 + 3, alpha=0.55)  # drop shadow
    blit_mask(F, ring(np.pad(M, 1))[1:-1, 1:-1] | False, NAVY, x0, y0)
    R = ring(M); blit_mask(F, R, NAVY, x0, y0)
    blit_mask(F, M & ~R, col, x0, y0); blit_mask(F, M & hl & ~R, hexc('#ffffff'), x0, y0)
    # trail: three shrinking bubbles towards the thinker
    bx, by = cx - w_ * 0.18, cy + h_ * 0.5
    for k, r in enumerate((3.2, 2.3, 1.5)):
        f = (k + 1) / 3.6; qx, qy = bx + (tail_to[0] - bx) * f, by + (tail_to[1] - by) * f
        n = int(r * 2 + 3); yy2, xx2 = np.mgrid[0:n, 0:n]; m = (xx2 - n / 2 + 0.5) ** 2 + (yy2 - n / 2 + 0.5) ** 2 <= r * r
        c2 = np.zeros((n, n, 3), np.float32) + 1.0; c2[yy2 > n * 0.6] = hexc('#bcd3f2')
        blit_mask(F, m, hexc('#050a18'), qx - n / 2 + 1, qy - n / 2 + 2, alpha=0.5)
        blit_mask(F, ring(m), NAVY, qx - n / 2, qy - n / 2); blit_mask(F, m & ~ring(m), c2, qx - n / 2, qy - n / 2)
    return x0, y0

def fish_icon(F, x, y, t=0.0):
    L = Layers(22, 14); yy, xx = np.mgrid[0:14, 0:22].astype(np.float32)
    body = ((xx - 9) / 8) ** 2 + ((yy - 7) / 5) ** 2 <= 1
    tail = (xx >= 15) & (xx < 21) & (np.abs(yy - 7) <= (xx - 15) * 0.9)
    L.add(tail, hexc('#e8782a'))
    def bf(c, m):
        c[m] = hexc('#ff9a3a'); c[m & (yy > 8)] = hexc('#ffb86a'); c[m & (np.abs(xx - 10) < 0.7)] = hexc('#e8782a')
        c[(xx >= 4) & (xx < 6) & (yy >= 5) & (yy < 7)] = hexc('#1b1428'); c[(xx >= 4) & (xx < 5) & (yy >= 5) & (yy < 6)] = hexc('#ffffff')
        c[(xx >= 1) & (xx < 3) & (yy >= 8) & (yy < 9)] = hexc('#8a3a3a')
    L.add(body, bf)
    c, M = L.out(); blit_mask(F, M, c, x, int(round(y + math.sin(t * 3))))

