"""'What If Rudolph's Nose Was Real?' - blueprint pixel short narrated by Jett (1080x1920, 60 fps).
Layout: visual in the middle or a bit higher, one-line captions right below, the narration's exact words
timed to the voice (captions.json). Characters are clean layered sprites (style_study/characters.py) and
never overlap each other.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study')); sys.path.insert(0, os.path.join(ROOT_, 'penguin_gift'))
import importlib.util
_s = importlib.util.spec_from_file_location('reindeer_video', os.path.join(ROOT_, 'reindeer', 'video.py'))
rv = importlib.util.module_from_spec(_s); _s.loader.exec_module(rv)        # shared helpers (bg, island, captions, snow)
pv, bk = rv.pv, rv.bk
import characters as ch
sys.path.insert(0, HERE)

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
(L_HOOK, L_WHAT, L_CAM, L_LIT, L_WHY, L_COLD, L_BLOOD, L_WHATIF, L_EVERY, L_TWIST, L_EYES, L_DARK, L_UV,
 L_WOLF, L_SUM, L_END) = range(16)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))

# ---------------- characters (cached) ----------------
_cache = {}
def deer(**kw):
    key = ('d',) + tuple(sorted((k, round(v, 2) if isinstance(v, float) else v) for k, v in kw.items()))
    if key not in _cache: _cache[key] = ch.reindeer(**kw)
    return _cache[key]
def draw_deer(F, cx, feet=GROUND + 1, **kw):
    """draws a reindeer centred at cx with hooves on `feet`; returns the nose and eye positions (grid)"""
    col, M, (nx, ny), (ex, ey) = deer(**kw); x0, y0 = cx - 33, feet - 56
    pv.blit_hr(F, col, M, x0, y0, 1); return (x0 + nx, y0 + ny), (x0 + ex, y0 + ey)
def draw_wolf(F, cx, feet=GROUND + 1, uv=False, flip=True, step=0.0):
    key = ('w', uv, flip, round(step, 2))
    if key not in _cache: _cache[key] = ch.wolf(uv=uv, flip=flip, step=step)
    col, M = _cache[key]; pv.blit_hr(F, col, M, cx - 27, feet - 36, 1)
SANTA = ch.santa()
def draw_santa(F, cx, feet=GROUND + 1, bob=0.0): pv.blit_hr(F, SANTA[0], SANTA[1], cx - 23, feet - 50 - bob, 1)

# ---------------- light, night, thermal, UV ----------------
def glow(F, x, y, r, colr, a=1.0):
    """soft pixel halo: 4 dithered bands on the grid, blended at screen res"""
    if a <= 0: return
    x0, y0 = int(math.floor(x - r)), int(math.floor(y - r)); n = int(2 * r) + 2
    yy, xx = np.mgrid[y0:y0 + n, x0:x0 + n]
    d = np.hypot(xx + 0.5 - x, yy + 0.5 - y) / r
    lv = np.clip(1 - d, 0, 1) ** 1.4
    q = np.floor(lv * 4 + BAY[yy % 4, xx % 4] * 0.99) / 4 * a * 0.75
    ya, yb, xa, xb = max(0, y0), min(H, y0 + n), max(0, x0), min(W, x0 + n)
    if yb <= ya or xb <= xa: return
    A = np.repeat(np.repeat(q[ya - y0:yb - y0, xa - x0:xb - x0], S, 0), S, 1)[..., None]
    reg = F[ya * S:yb * S, xa * S:xb * S]; F[ya * S:yb * S, xa * S:xb * S] = reg * (1 - A) + hexc(colr) * A
def nose_glow(F, pos, t, a=1.0, big=1.0):
    pulse = 0.85 + 0.15 * math.sin(t * 5)
    glow(F, pos[0], pos[1], 16 * big * pulse, '#ff3a4a', 0.55 * a); glow(F, pos[0], pos[1], 6 * big, '#ff8a8a', 0.8 * a)
NIGHT = np.array([0.22, 0.26, 0.46], np.float32)
def night(F, light=None, amount=1.0):
    """darken everything; `light` (grid HxW, 0..1) keeps those places lit"""
    k = np.ones((H, W), np.float32) * amount
    if light is not None: k = k * (1 - light)
    f = 1 - k[..., None] * (1 - NIGHT)
    F *= np.repeat(np.repeat(f, S, 0), S, 1)
THERM = np.stack([hexc('#0c0828'), hexc('#1d1458'), hexc('#3a2a8a'), hexc('#6a3aa8')])
def thermal_bg(F, t):
    """the whole picture as a heat camera sees it: cold = deep purple"""
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1.3 + 0.9 * np.sin(yy / 40 + 0.4) * 0.3 - (yy / H) * 0.6
    g = THERM[np.clip(np.floor(v + BAY[yy % 4, xx % 4] * 0.9 - 0.4), 0, 3).astype(int)]
    F[:] = np.repeat(np.repeat(g, S, 0), S, 1)
    if 'ti' not in _cache:
        c, M = rv.ISLAND; lum = c.mean(-1)
        P = np.stack([hexc('#140c3a'), hexc('#24186a'), hexc('#34248a'), hexc('#4a32a0')])
        _cache['ti'] = (P[np.clip((lum * 4).astype(int) - 1, 0, 3)].astype(np.float32), M)
    c, M = _cache['ti']; pv.blit_hr(F, c, M, rv.ISL_X, rv.ISL_Y, 1)
def thermal_glow(F, pos, t):
    pulse = 0.9 + 0.1 * math.sin(t * 6)
    glow(F, pos[0], pos[1], 18 * pulse, '#ff3a2a', 0.6); glow(F, pos[0], pos[1], 9, '#ffb02a', 0.8); glow(F, pos[0], pos[1], 4, '#ffffa0', 0.9)
UVP = np.stack([hexc('#1a0f3a'), hexc('#3a2470'), hexc('#7a5ac8'), hexc('#c8b4ff'), hexc('#f4eeff')])
def uvify(F):
    lum = F.mean(-1); idx = np.clip((lum * 5.2).astype(int), 0, 4)
    F[:] = UVP[idx]

# ---------------- props ----------------
def viewfinder(F, t, k=1.0, rec=True, x0=10, y0=48, x1=170, y1=172):
    """camera brackets that close in (k 0->1), REC dot, temperature scale"""
    e = (1 - k) * 18; X0, Y0, X1, Y1 = int((x0 - e) * S), int((y0 - e) * S), int((x1 + e) * S), int((y1 + e) * S)
    L, th = 70, 8
    for (cx, cy, sx, sy) in ((X0, Y0, 1, 1), (X1, Y0, -1, 1), (X0, Y1, 1, -1), (X1, Y1, -1, -1)):
        xa, xb = sorted((cx, cx + sx * L)); ya, yb = sorted((cy, cy + sy * th)); F[max(0, ya):yb, max(0, xa):xb] = 1.0
        xa, xb = sorted((cx, cx + sx * th)); ya, yb = sorted((cy, cy + sy * L)); F[max(0, ya):yb, max(0, xa):xb] = 1.0
    if rec and k > 0.9:
        if int(t * 2) % 2 == 0:
            yy, xx = np.mgrid[0:36, 0:36]; m = (xx - 18) ** 2 + (yy - 18) ** 2 <= 15 ** 2
            F[Y0 + 30:Y0 + 66, X0 + 30:X0 + 66][m] = hexc('#ff3a3a')
        bk.pixel_text(F, 'REC', X0 + 80, Y0 + 34, px=5, colr=(255, 255, 255))
def heat_scale(F):
    x, y0, h_ = WF - 130, 420, 330
    for k in range(h_):
        f = 1 - k / h_; c = hexc('#ffffa0') if f > 0.85 else hexc('#ffb02a') if f > 0.65 else hexc('#ff3a2a') if f > 0.45 else hexc('#6a3aa8') if f > 0.25 else hexc('#1d1458')
        F[y0 + k, x:x + 30] = c
    F[y0 - 4:y0, x - 4:x + 34] = F[y0 + h_:y0 + h_ + 4, x - 4:x + 34] = 1.0
    F[y0:y0 + h_, x - 4:x] = F[y0:y0 + h_, x + 30:x + 34] = 1.0
    bk.pixel_text(F, 'HOT', x - 6, y0 - 50, px=4, colr=(255, 220, 120)); bk.pixel_text(F, 'COLD', x - 14, y0 + h_ + 20, px=4, colr=(150, 140, 230))
def ctag(F, text, y, px=6):
    w_ = len(text) * 6 * px - px; bk.tag(F, text, (WF - w_) // 2, y, px)
def ctext(F, text, y, px=7, colr=(255, 200, 58)):
    w_ = len(text) * 6 * px - px; bk.pixel_text(F, text, (WF - w_) // 2, y, px=px, colr=colr)
def thermometer(F, t, level):
    """level 1 = warm, 0 = minus forty"""
    x, y0, y1 = 150, 70, 128
    col = np.zeros((y1 - y0 + 12, 12, 3), np.float32); yy, xx = np.mgrid[0:y1 - y0 + 12, 0:12]
    tube = (np.abs(xx - 5.5) <= 2.5) & (yy < y1 - y0); bulb = (xx - 5.5) ** 2 + (yy - (y1 - y0 + 5)) ** 2 <= 5.5 ** 2
    M = tube | bulb; col[M] = hexc('#f4f6fb')
    top = (y1 - y0) * (1 - (0.15 + 0.75 * level))
    red = (bulb | (tube & (yy >= top))) & ((xx - 5.5) ** 2 + (yy - (y1 - y0 + 5)) ** 2 <= 3.5 ** 2) | ((np.abs(xx - 5.5) <= 1) & (yy >= top) & tube)
    col[red] = hexc('#e8303a') if level > 0.3 else hexc('#3a8aff')
    col, M = bk.outline(col, M); pv.blit_hr(F, col, M, x, y0, 1)
    for k in range(5): F[int((y0 + 6 + k * 11) * S):int((y0 + 6 + k * 11) * S) + 6, int((x + 9) * S):int((x + 11) * S)] = NAVY
def pine(F, cx, feet):
    if 'pine' not in _cache:
        L = ch.Layers(26, 34); yy, xx = np.mgrid[0:34, 0:26].astype(np.float32)
        L.add((np.abs(xx - 12.5) <= 2) & (yy >= 27) & (yy < 33), hexc('#6a4226'))
        for k, (ty, hgt, wd) in enumerate(((16, 12, 12), (8, 11, 9), (1, 10, 6))):
            m = (yy >= ty) & (yy < ty + hgt) & (np.abs(xx - 12.5) <= (yy - ty + 1) / hgt * wd)
            L.add(m, lambda c, m_: (c.__setitem__(m_, hexc('#2f8f4a')), c.__setitem__(m_ & (xx > 12.5), hexc('#1d6a3a')),
                                    c.__setitem__(m_ & (yy < ty + 2), hexc('#ffffff'))))
        _cache['pine'] = L.out()
    c, M = _cache['pine']; pv.blit_hr(F, c, M, cx - 13, feet - 33, 1)
LICHEN = [(-6, 0), (-3, -1), (0, 0), (3, -1), (6, 0), (-4, 1), (2, 1)]
def lichen(F, cx, y, uv=False, cover=0.0):
    for k, (dx, dy) in enumerate(LICHEN):
        for ox, oy in ((0, 0), (1, 0), (0, -1)):
            put(F, cx + dx + ox, y + dy + oy, hexc('#1a1030') if uv else (hexc('#c8d84a') if (k + ox) % 2 else hexc('#7a9a2a')))
    if cover > 0:
        for k in range(-8, 9):
            if BAY[k % 4, 1] < cover: put(F, cx + k, y - 1, hexc('#f4f8ff'))
def vessels(n_depth, seed, cx, cy, r):
    """branching blood vessels inside a circle: list of segments (x0,y0,x1,y1,order)"""
    rng = np.random.default_rng(seed); segs = []
    def grow(x, y, ang, ln, d, order):
        x2, y2 = x + ln * math.cos(ang), y + ln * math.sin(ang)
        if math.hypot(x2 - cx, y2 - cy) > r - 2: x2, y2 = x + 0.5 * ln * math.cos(ang), y + 0.5 * ln * math.sin(ang)
        segs.append((x, y, x2, y2, order))
        if d < n_depth:
            for s_ in (-1, 1): grow(x2, y2, ang + s_ * rng.uniform(0.35, 0.7), ln * 0.72, d + 1, order + 1)
    for k, a0 in enumerate(np.linspace(-math.pi * 0.85, -math.pi * 0.15, 3 if n_depth < 3 else 5)):
        grow(cx + (k - 1) * 3, cy + r - 3, a0, r * 0.45, 0, 0)
    return segs
def tissue(F, t, cx, cy, r, segs, grow, title):
    yy, xx = np.mgrid[0:2 * r + 2, 0:2 * r + 2].astype(np.float32); X, Y = xx + cx - r - 1, yy + cy - r - 1
    M = (X + 0.5 - cx) ** 2 + (Y + 0.5 - cy) ** 2 <= r * r
    col = np.zeros(M.shape + (3,), np.float32); col[M] = hexc('#f6c8b8')
    col[M & ((X + 0.5 - cx) ** 2 + (Y + 0.5 - cy) ** 2 > (r - 3) ** 2)] = hexc('#e8a898')
    maxo = max(s[4] for s in segs) + 1
    for (x0, y0, x1, y1, o) in segs:
        f = min(1.0, max(0.0, grow * maxo - o))
        if f <= 0: continue
        x1_, y1_ = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        m = ch.seg(X + 0.5, Y + 0.5, x0, y0, x1_, y1_) <= (1.1 if o < 2 else 0.7)
        col[m & M] = hexc('#c81e2e')
    col, M2 = bk.outline(col, M); pv.blit_hr(F, col, M2, cx - r - 1, cy - r - 1, 1)
    for k, (x0, y0, x1, y1, o) in enumerate(segs):                 # blood cells flowing
        if grow * maxo - o < 1: continue
        f = (t * 0.9 + k * 0.37) % 1; px_, py_ = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        if math.hypot(px_ - cx, py_ - cy) < r - 3: put(F, px_, py_, hexc('#ff6a7a'))
    w_ = len(title) * 6 * 6 - 6; bk.pixel_text(F, title, int(cx * S - w_ / 2), int((cy - r - 12) * S), px=6, colr=(235, 240, 255))
def check_row(F, text, y, done):
    x = 238; F[y:y + 60, x:x + 60] = hexc('#0a1020')
    for k in range(5): F[y + k, x:x + 60] = F[y + 59 - k, x:x + 60] = 0.92; F[y:y + 60, x + k] = F[y:y + 60, x + 55 + k] = 0.92
    if done > 0:
        for k in range(int(30 * done)):
            px_, py_ = (x + 12 + k, y + 28 + k) if k < 12 else (x + 24 + (k - 12) * 1.4, y + 40 - (k - 12) * 1.9)
            F[int(py_):int(py_) + 9, int(px_):int(px_) + 9] = hexc('#5ae07a')
    bk.pixel_text(F, text, x + 90, y + 6, px=7, colr=(255, 255, 255) if done > 0 else (150, 165, 200))
def star_burst(F, x, y, a, t0):
    if a <= 0: return
    for k in range(10):
        th = TAU * k / 10; rr = 8 + 26 * a
        rv.sparkle(F, x + rr * math.cos(th), y + rr * math.sin(th) * 0.8, 1 - a, '#ffe27a')

# ---------------- scenes ----------------
def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i

def scene(F, t):
    i = seg_of(t); a = t - SEG[i][0]
    if i in (L_HOOK, L_WHAT):                                    # Rudolph's red nose is real. WHAAAAT?!
        rv.island(F); shock = i == L_WHAT
        jump = 10 * abs(math.sin(a * 7)) * math.exp(-a * 1.5) if shock else 0
        nose, eye = draw_deer(F, 90, GROUND + 1 - jump, nose='red')
        nose_glow(F, nose, t, big=1.5 if shock else 1.0)
        if not shock: bk.label(F, 'RUDOLPH', 110, 420, int((nose[0] - 26) * S), int((nose[1] - 6) * S), px=6)
        if t >= cs(L_HOOK, 1) - 0.05 and not shock:
            ctag(F, 'REAL', 200, px=12)
        if shock:
            star_burst(F, nose[0], nose[1], ramp(t, SEG[L_WHAT][0], 0.5), 0)
            ctext(F, '!?', 330, px=14)
    elif i in (L_CAM, L_LIT):                                    # a heat camera on real reindeer
        Fn = rv.BG.copy(); rv.island(Fn)
        for cx in (46, 116): draw_deer(Fn, cx, nose='black', step=0.0)
        if i == L_LIT:
            Ft = F.copy(); thermal_bg(Ft, t); noses = [draw_deer(Ft, cx, thermal=True)[0] for cx in (46, 116)]
            for n_ in noses: thermal_glow(Ft, n_, t)
            Y0, Y1, X0, X1 = 48 * S, 172 * S, 10 * S, 170 * S
            wipe = Y0 + int(ramp(t, SEG[L_LIT][0], 0.6) * (Y1 - Y0))
            Fn[Y0:wipe, X0:X1] = Ft[Y0:wipe, X0:X1]
            if Y0 < wipe < Y1: Fn[wipe - 8:wipe, X0:X1] = 1.0
            heat_scale(Fn)
            if t >= cs(L_LIT, 1) - 0.05:
                for n_ in noses: bk.label(Fn, 'HOT', int(n_[0] * S) - 50, int((n_[1] - 32) * S), int(n_[0] * S), int((n_[1] - 6) * S), px=6)
        F[:] = Fn
        viewfinder(F, t, ramp(t, SEG[L_CAM][0], 0.5))
        ctag(F, 'HEAT CAMERA', 200, px=6)
    elif i == L_WHY:                                             # why: way more blood vessels
        segs_h = _cache.setdefault('vh', vessels(1, 3, 46, 112, 38)); segs_r = _cache.setdefault('vr', vessels(5, 5, 134, 112, 38))
        g_h = ramp(t, cs(L_WHY, 1), 1.2); g_r = ramp(t, cs(L_WHY, 2), 2.0)
        tissue(F, t, 46, 112, 38, segs_h, g_h, 'YOU'); tissue(F, t, 134, 112, 38, segs_r, g_r, 'REINDEER')
        bk.pixel_text(F, 'VS', 513, int(109 * S), px=5, colr=(255, 200, 58))
        ctag(F, 'INSIDE THE NOSE', 200, px=6)
        if t >= cs(L_WHY, 4) - 0.05: ctag(F, 'WAY MORE', 920, px=7)
    elif i in (L_COLD, L_BLOOD):                                 # minus forty, warm blood to the nose
        rv.island(F)
        if i == L_COLD:
            shiver = 0.6 * math.sin(t * 40) if t > cs(L_COLD, 2) else 0
            nose, eye = draw_deer(F, 70 + shiver, nose='black')
            lv = 1 - ramp(t, cs(L_COLD, 2) - 0.2, 0.8); thermometer(F, t, lv)
            if t >= cs(L_COLD, 2) - 0.05: bk.tag(F, '-40', 830, 330, px=7)
            for k in range(30):                                  # blizzard streaks
                x = (k * 53 + t * 140) % 200 - 10; y = 50 + (k * 37) % 110 + 6 * math.sin(t * 3 + k)
                put(F, x, y, hexc('#f4f8ff'), 0.8); put(F, x - 1, y, hexc('#f4f8ff'), 0.5); put(F, x - 2, y, hexc('#f4f8ff'), 0.3)
        else:
            hd = ramp(t, cs(L_BLOOD, 4) - 0.1, 0.7)
            lichen(F, 113, GROUND - 1, cover=1 - ramp(t, cs(L_BLOOD, 5), 0.8) * 0.8)
            nose, eye = draw_deer(F, 70, nose='black', head_down=hd)
            warm = ramp(t, SEG[L_BLOOD][0] + 0.2, 1.6)
            heart = (66, GROUND - 22)
            for k in range(7):                                   # blood dots racing from the heart to the nose
                f = ((t * 0.8 + k / 7) % 1)
                mx, my = lerp(heart[0], nose[0] - 6, f), lerp(heart[1], nose[1] + 1, f) - 6 * math.sin(math.pi * f)
                glow(F, mx, my, 3, '#ff3a4a', 0.9 * warm); put(F, mx, my, hexc('#ff6a7a'))
            glow(F, nose[0], nose[1], 10, '#ff6a3a', 0.6 * warm)
            if t >= cs(L_BLOOD, 0) - 0.05: bk.label(F, 'WARM BLOOD', 90, 330, int(heart[0] * S), int((heart[1] - 4) * S), px=6)
            if t >= cs(L_BLOOD, 3) - 0.05 and t < cs(L_BLOOD, 4): bk.tag(F, 'NO FREEZING', 600, 330, px=6)
            if t >= cs(L_BLOOD, 4) - 0.05: bk.label(F, 'FOOD', 760, 450, int(113 * S), int((GROUND - 4) * S), px=6)
    elif i == L_WHATIF:                                          # so what if it really glowed?
        rv.island(F); pine(F, 150, GROUND + 1)
        nose, eye = draw_deer(F, 72, nose='red')
        night(F, amount=ramp(t, SEG[L_WHATIF][0], 0.5))
        k = ramp(t, SEG[L_WHATIF][0] + 0.3, 0.6) * 0.5 + ramp(t, cs(L_WHATIF, 2) - 0.1, 0.6) * 0.5
        nose_glow(F, nose, t, a=0.6 + 0.4 * k, big=1.2 + 1.6 * k)
        glow(F, nose[0] + 10, GROUND - 2, 30 * k + 1, '#ff3a4a', 0.35 * k)
        ctag(F, 'WHAT IF', 300, px=7)
    elif i == L_EVERY:                                           # every reindeer is a Rudolph (herd through the camera)
        thermal_bg(F, t); t0 = SEG[L_EVERY][0]; count = 0
        for k in range(3):
            x = 64 + 55 * (t - t0) - 85 * k
            if -40 < x < 220:
                nose, _ = draw_deer(F, x, thermal=True, step=((t - t0) * 1.4) % 1); thermal_glow(F, nose, t)
            if x + 24 > 90: count += 1
        Fv = rv.BG.copy(); Fv[48 * S:172 * S, 10 * S:170 * S] = F[48 * S:172 * S, 10 * S:170 * S]; F[:] = Fv
        viewfinder(F, t); heat_scale(F)
        if t >= cs(L_EVERY, 2) - 0.05: ctext(F, f'RUDOLPHS: {count}', 230, px=7)
        else: ctag(F, 'HEAT CAMERA', 200, px=6)
    elif i == L_TWIST:                                           # plot twist: not even their best superpower
        rv.island(F)
        nose, eye = draw_deer(F, 90, nose='red'); nose_glow(F, nose, t, a=0.6)
        ctag(F, 'PLOT TWIST', 300, px=8)
        if t >= cs(L_TWIST, 1) - 0.05:
            star_burst(F, eye[0], eye[1], ramp(t, cs(L_TWIST, 1), 0.6), 0)
            if t >= cs(L_TWIST, 2) - 0.05: ctext(F, 'SUPERPOWER?', 440, px=7)
    elif i == L_EYES:                                            # eyes: gold in summer, blue in winter
        blue = ramp(t, cs(L_EYES, 3) - 0.1, 0.7)
        x0, y0, x1, y1 = 18, 62, 162, 160
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        fur = ((xx - 90) / 72) ** 4 + ((yy - 111) / 49) ** 4 <= 1
        col = np.zeros(fur.shape + (3,), np.float32); col[fur] = hexc('#8a5a36'); col[fur & (yy > 135)] = hexc('#a8744a')
        eyeM = ((xx + 0.5 - 90) / 46) ** 2 + ((yy + 0.5 - 110) / 25) ** 2 <= 1
        col[eyeM] = hexc('#f4ecdc')
        d = np.hypot(xx + 0.5 - 90, yy + 0.5 - 110)
        mix = (BAY[yy.astype(int) % 4, xx.astype(int) % 4] < blue)[..., None]
        iris_o = np.where(mix, hexc('#1d4aa8'), hexc('#a8761a')); iris_i = np.where(mix, hexc('#3a8aff'), hexc('#ffc83a'))
        iris = eyeM & (d <= 21); col[iris] = iris_o[iris]; inner = eyeM & (d <= 17); col[inner] = iris_i[inner]
        pupil = ((xx + 0.5 - 90) / 11) ** 2 + ((yy + 0.5 - 110) / 5) ** 2 <= 1; col[pupil] = hexc('#120c18')
        col[(xx >= 78) & (xx < 83) & (yy >= 99) & (yy < 104)] = hexc('#ffffff'); col[(xx >= 97) & (xx < 99) & (yy >= 115) & (yy < 117)] = hexc('#ffffff')
        rim = eyeM & ~(((xx + 0.5 - 90) / 44) ** 2 + ((yy + 0.5 - 110) / 23) ** 2 <= 1); col[rim] = NAVY
        col, M = bk.outline(col, fur); pv.blit_hr(F, col, M, x0, y0, 1)
        rv.calendar(F, 'WINTER' if t >= cs(L_EYES, 3) - 0.1 else 'SUMMER', x=310, y=200)
        if t < cs(L_EYES, 2) - 0.05: ctag(F, 'REINDEER EYE', 990, px=6)
        else: ctext(F, 'BLUE' if blue > 0.5 else 'GOLD', 990, px=8, colr=(90, 160, 255) if blue > 0.5 else (255, 200, 58))
    elif i == L_DARK:                                            # dark for weeks; blue eyes see in the dark
        rv.island(F); pine(F, 148, GROUND + 1); lichen(F, 120, GROUND - 1)
        nose, eye = draw_deer(F, 62, nose='black', eye_col='#3a8aff')
        light = None; see = ramp(t, cs(L_DARK, 4) - 0.1, 0.8)
        if see > 0:
            yy, xx = np.mgrid[0:H, 0:W]; dx, dy = xx - eye[0], yy - eye[1]
            ang = np.abs(np.arctan2(dy, np.maximum(dx, 1e-3)) - 0.25); light = ((dx > 0) & (ang < 0.45) & (dx < 120)).astype(np.float32) * 0.8 * see
            light *= np.clip(1 - dx / 130, 0, 1) ** 0.3 * (yy < GROUND + 6)
        night(F, light, amount=ramp(t, SEG[L_DARK][0], 0.5))
        glow(F, eye[0], eye[1], 5, '#5aa0ff', 0.9)
        weeks = 1 + int(7 * ramp(t, SEG[L_DARK][0], max(0.5, cs(L_DARK, 2) - SEG[L_DARK][0])))
        if t < cs(L_DARK, 2) - 0.05: ctext(F, f'DARK: WEEK {weeks}', 300, px=7, colr=(200, 215, 255))
        else:
            ctag(F, 'BLUE EYES', 300, px=7)
            for k in range(10):                                  # light pulled into the eye
                f = (t * 0.9 + k / 10) % 1; sx, sy = 175 - 20 * (k % 3), 50 + 9 * k
                put(F, lerp(sx, eye[0], f), lerp(sy, eye[1], f), hexc('#fff6c0'), 1 - f * 0.5)
    elif i == L_UV:                                              # ultraviolet: snow glows, food and wolves go dark
        rv.island(F); Y0, Y1, X0, X1 = 48 * S, 172 * S, 10 * S, 170 * S
        U = rv.BG.copy(); pv.blit_hr(U, rv.ISLAND[0], rv.ISLAND[1], rv.ISL_X, rv.ISL_Y, 1); nose, eye = draw_deer(U, 46, nose='black')
        R_ = U[Y0:Y1, X0:X1].copy(); bgm = np.all(np.abs(R_ - rv.BG[Y0:Y1, X0:X1]) < 1e-4, -1)
        uvify(R_); R_[bgm] = rv.BG[Y0:Y1, X0:X1][bgm] * 0.35 + hexc('#1a0f3a') * 0.65; F[Y0:Y1, X0:X1] = R_
        refl = ramp(t, cs(L_UV, 2) - 0.1, 0.6)
        for gx in range(30, 160, 22): glow(F, gx, GROUND - 3, 14, '#ffffff', 0.35 * refl)
        lichen(F, 88, GROUND - 1, uv=True)
        wx = lerp(200, 140, ramp(t, SEG[L_UV][0], 1.6)); draw_wolf(F, wx, uv=True, step=((t * 1.5) % 1) if wx > 141 else 0)
        viewfinder(F, t, ramp(t, SEG[L_UV][0], 0.4), rec=False); ctag(F, 'UV VISION', 200, px=7)
        if t >= cs(L_UV, 3) - 0.05:
            bk.label(F, 'FOOD', 470, 600, int(88 * S), int((GROUND - 4) * S), px=6)
            bk.label(F, 'WOLF', 790, 520, int(wx * S), int((GROUND - 34) * S), px=6)
    elif i == L_WOLF:                                            # they spot wolves first
        rv.island(F); lichen(F, 88, GROUND - 1, cover=0.0)
        spot, run = cs(L_WOLF, 1), cs(L_WOLF, 2)
        if t < run:
            hd = 1.0 - ramp(t, spot - 0.1, 0.3)
            nose, eye = draw_deer(F, 55, nose='black', eye_col='#3a8aff', head_down=hd)
            if t >= spot: bk.pixel_text(F, '!', int(eye[0] * S) - 10, int((eye[1] - 30) * S), px=12, colr=(255, 200, 58))
        else:
            rx = lerp(55, -45, ramp(t, run, 1.4)); draw_deer(F, rx, nose='black', eye_col='#3a8aff', flip=True, step=(t * 2.2) % 1)
            for k in range(8): put(F, rx + 34 + k * 3, GROUND + 1 - (k % 2), hexc('#eaf3ff'), 0.8 - k * 0.1)
        wx = lerp(205, 140, ramp(t, SEG[L_WOLF][0], 1.8)); draw_wolf(F, wx, step=((t * 1.2) % 1) if wx > 141 else 0)
        if t >= cs(L_WOLF, 3) - 0.05: bk.pixel_text(F, '?', int((wx - 8) * S), int((GROUND - 50) * S), px=10, colr=(255, 255, 255))
    elif i == L_SUM:                                             # a glowing nose and night vision
        rv.island(F)
        nose, eye = draw_deer(F, 90, nose='red', eye_col='#3a8aff'); nose_glow(F, nose, t)
        glow(F, eye[0], eye[1], 5, '#5aa0ff', 0.8)
        check_row(F, 'GLOWING NOSE', 260, ramp(t, cs(L_SUM, 0) + 0.2, 0.3))
        check_row(F, 'NIGHT VISION', 360, ramp(t, cs(L_SUM, 1) + 0.3, 0.3))
    else:                                                        # Santa didn't pick reindeer by accident
        rv.island(F)
        draw_santa(F, 52, bob=abs(math.sin(t * 3)) * 1.5)
        nose, eye = draw_deer(F, 122, nose='red', eye_col='#3a8aff'); nose_glow(F, nose, t)
        if t < cs(L_END, 2) - 0.05: ctag(F, "SANTA'S PICK", 300, px=7)
        else:
            ctag(F, 'MERRY CHRISTMAS', 300, px=7)
            for k in range(14):
                th = TAU * k / 14 + t; rv.sparkle(F, 90 + 62 * math.cos(th), 82 + 14 * math.sin(th), 0.9)

# ---------------- captions + frame ----------------
CAPS = [(c['t0'], c['t1'], rv.caption_sprite(c['text'], set(c['hl']))) for c in CAPJ]
def captions(F, t):
    for a, b, spr in CAPS:
        if a <= t < b:
            dy = int(6 * (1 - min(1.0, (t - a) / 0.06))); h_ = spr.shape[0]; A = spr[..., 3:4]
            F[rv.CAP_Y + dy:rv.CAP_Y + dy + h_] = F[rv.CAP_Y + dy:rv.CAP_Y + dy + h_] * (1 - A) + spr[..., :3] * A
    if t < SEG[1][1] + 0.4:
        y0 = rv.CAP_Y + 140; x0 = WF // 2 - 35
        for r_, row in enumerate(rv.HEADPHONES):
            for c_, bb in enumerate(row):
                if bb == '1': F[y0 + r_ * 7:y0 + r_ * 7 + 7, x0 + c_ * 7:x0 + c_ * 7 + 7] = 1.0
SHOUTS = [SEG[L_WHAT][0], cs(L_TWIST, 1)]
CUTS = (L_CAM, L_WHY, L_COLD, L_WHATIF, L_EVERY, L_TWIST, L_EYES, L_DARK, L_UV, L_WOLF, L_SUM, L_END)
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    if i not in (L_EVERY, L_EYES, L_WHY) and not (i == L_LIT and t > SEG[L_LIT][0] + 0.6): rv.snow(F, t)
    if i in CUTS and 0 <= t - SEG[i][0] < 0.12:
        m = rv.HR_BAYER < (1 - (t - SEG[i][0]) / 0.12) * 0.7; F[m] = F[m] * 0.4 + hexc('#f4fbff') * 0.6
    for st in SHOUTS:
        if 0 <= t - st < 0.35:
            A = 14 * math.exp(-(t - st) / 0.1); dx, dy = int(A * math.sin(t * 90)), int(A * math.cos(t * 70))
            F = np.roll(np.roll(F, dx, 1), dy, 0)
    captions(F, t)
    return (np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == '__main__':
    if sys.argv[1] == '--stills':
        for ts in sys.argv[3:]: Image.fromarray(frame(float(ts))).save(f'{sys.argv[2]}/still_{float(ts):06.2f}.png')
        sys.exit()
    out, wav = sys.argv[1], sys.argv[2]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WF}x{HF}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(int(round(END * FPS))):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 600 == 0: print('frame', f, flush=True)
    p.stdin.close(); p.wait(); print('done', out)
