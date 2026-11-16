"""'What If Santa Actually Flew That Fast?' - blueprint pixel short narrated by Jett (1080x1920, 60 fps).
Layout: visual in the middle or a bit higher, one-line captions right below, exact narration words timed to
the voice (captions.json). Clean layered characters (style_study/characters.py), never overlapping.
Ending: comment question + naughty-list subscribe CTA.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study')); sys.path.insert(0, os.path.join(ROOT_, 'penguin_gift'))
import importlib.util
_s = importlib.util.spec_from_file_location('reindeer_video', os.path.join(ROOT_, 'reindeer', 'video.py'))
rv = importlib.util.module_from_spec(_s); _s.loader.exec_module(rv)
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
(L_HOOK, L_WHAT, L_HOMES, L_HOURS, L_PERSEC, L_SPEED, L_SOUND, L_METEOR, L_FIRE, L_GFORCE, L_FLAT, L_BOOM,
 L_TWIST, L_TIME, L_SMART, L_CTA) = range(16)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))

# ---------------- sprites ----------------
_c = {}
def spr(name, fn):
    if name not in _c: _c[name] = fn()
    return _c[name]
SANTA = ch.santa()
def draw_santa(F, cx, feet=GROUND + 1, bob=0.0, soot=0.0, glasses=False, squash=1.0):
    c, M = SANTA
    if squash != 1.0:
        nh = max(4, int(round(52 * squash))); nw = int(round(46 * (1 + (1 - squash) * 0.9)))
        ri = np.minimum((np.arange(nh) / squash).astype(int), 51); ci = np.minimum((np.arange(nw) * 46 / nw).astype(int), 45)
        c, M = c[ri][:, ci], M[ri][:, ci]
    if soot > 0:
        c = c.copy(); keep = c.sum(-1) < 0.35; c = c * (1 - 0.55 * soot) + hexc('#2a2430') * 0.25 * soot; c[keep] = SANTA[0][keep] if squash == 1.0 else c[keep]
    h_, w_ = M.shape; x0, y0 = cx - w_ / 2, feet - h_ - bob
    pv.blit_hr(F, c, M, x0, y0, 1)
    if soot > 0 and squash == 1.0:
        for ex in (20, 26): put(F, x0 + ex - 1 + 0.5, y0 + 14, hexc('#ffffff'))
    if glasses and squash == 1.0:
        for ex in (-3, 3):
            for dx in (-2, -1, 0, 1):
                for dy in (-2, 1): put(F, x0 + 23 + ex + dx, y0 + 15 + dy, hexc('#1b1428'))
            for dy in (-1, 0): put(F, x0 + 23 + ex - 2, y0 + 15 + dy, hexc('#1b1428')); put(F, x0 + 23 + ex + 1, y0 + 15 + dy, hexc('#1b1428'))
        put(F, x0 + 23, y0 + 14, hexc('#1b1428'))
    return x0, y0
_dc = {}
def deer(**kw):
    key = tuple(sorted((k, round(v, 2) if isinstance(v, float) else v) for k, v in kw.items()))
    if key not in _dc: _dc[key] = ch.reindeer(**kw)
    return _dc[key]
def draw_deer(F, cx, feet=GROUND + 1, **kw):
    col, M, (nx, ny), (ex, ey) = deer(**kw); x0, y0 = cx - 33, feet - 56
    pv.blit_hr(F, col, M, x0, y0, 1); return (x0 + nx, y0 + ny), (x0 + ex, y0 + ey)
def draw_team(F, x, y, t, soot=0.0, deer_soot=0.0, show_deer=True):
    """Rudolph pulling the sleigh with Santa inside; (x, y) = sleigh top-left. Returns Rudolph's nose."""
    sc, sm = SANTA; crop_c, crop_m = sc[0:30, 9:37], sm[0:30, 9:37]
    if soot > 0:
        crop_c = crop_c.copy(); h_, w_ = crop_m.shape; yy, xx = np.mgrid[0:h_, 0:w_]
        d = (BAY[yy % 4, xx % 4] < soot * 0.75) & crop_m; crop_c[d] = crop_c[d] * 0.35 + hexc('#2a2430') * 0.65
    pv.blit_hr(F, crop_c, crop_m, x + 15, y - 8 + 0.8 * math.sin(t * 9), 1)
    c, M = spr('sleigh', ch.sleigh); pv.blit_hr(F, c, M, x, y, 1)
    nose = None
    if show_deer:
        for k in range(3): put(F, x + 47 + k * 2, y + 25 - k, hexc('#ffcc4a'))
        nose, _ = draw_deer(F, x + 86, feet=y + 46, nose='red', step=(t * 2.2) % 1)
        if deer_soot > 0:
            pass
    return nose
def draw_house(F, cx, feet=GROUND + 1, broken=False):
    c, M = spr(('house', broken), lambda: ch.house(broken=broken)); pv.blit_hr(F, c, M, cx - 21, feet - 39, 1)

# ---------------- effects ----------------
def glow(F, x, y, r, colr, a=1.0):
    if a <= 0: return
    x0, y0 = int(math.floor(x - r)), int(math.floor(y - r)); n = int(2 * r) + 2
    yy, xx = np.mgrid[y0:y0 + n, x0:x0 + n]
    lv = np.clip(1 - np.hypot(xx + 0.5 - x, yy + 0.5 - y) / r, 0, 1) ** 1.4
    q = np.floor(lv * 4 + BAY[yy % 4, xx % 4] * 0.99) / 4 * a * 0.75
    ya, yb, xa, xb = max(0, y0), min(H, y0 + n), max(0, x0), min(W, x0 + n)
    if yb <= ya or xb <= xa: return
    A = np.repeat(np.repeat(q[ya - y0:yb - y0, xa - x0:xb - x0], S, 0), S, 1)[..., None]
    reg = F[ya * S:yb * S, xa * S:xb * S]; F[ya * S:yb * S, xa * S:xb * S] = reg * (1 - A) + hexc(colr) * A
FLAME = [hexc('#fff6a0'), hexc('#ffcc4a'), hexc('#ff8a2a'), hexc('#e8303a')]
def flames(F, x0, x1, ybase, t, hmax=10, a=1.0):
    if a <= 0: return
    for x in range(int(x0), int(x1)):
        h_ = hmax * a * (0.55 + 0.45 * math.sin(x * 1.7 + t * 13) * math.sin(x * 0.6 - t * 7))
        for k in range(int(max(0, h_))):
            f = k / max(1, h_); put(F, x, ybase - k, FLAME[min(3, int(f * 4))])
def smoke(F, x, y, t, a=1.0):
    for k in range(5):
        ph = (t * 0.7 + k / 5) % 1; r_ = 1 + ph * 4
        cx, cy = x + 3 * math.sin(k * 2 + t), y - ph * 26
        for dx in range(-int(r_), int(r_) + 1):
            for dy in range(-int(r_), int(r_) + 1):
                if dx * dx + dy * dy <= r_ * r_: put(F, cx + dx, cy + dy, hexc('#8a90a0'), a * (1 - ph) * 0.8)
def explosion(F, x, y, k):
    """k 0->1"""
    if k <= 0 or k >= 1: return
    a_ = 1 - k ** 1.5
    glow(F, x, y, 20 + 50 * k, '#ff8a2a', a_); glow(F, x, y, 12 + 30 * k, '#ffcc4a', a_); glow(F, x, y, 6 + 14 * k, '#fff6a0', a_)
    for j in range(36):
        th = TAU * j / 36 + j * 0.37; r_ = 6 + 60 * k * (0.6 + 0.4 * ((j * 7) % 5) / 4)
        for q in range(3):
            put(F, x + (r_ - q * 2) * math.cos(th), y + (r_ - q * 2) * math.sin(th), FLAME[(j + q) % 4], a_ * (1 - q * 0.25))
def speed_lines(F, t, y0, y1, n=14, sp=300, colr='#cfe2f6', a=0.8):
    for k in range(n):
        y = y0 + (y1 - y0) * ((k * 0.618) % 1); x = W - ((t * sp + k * 53) % (W + 60))
        for j in range(18): put(F, x + j, y, hexc(colr), a * (1 - j / 18))
def ctag(F, text, y, px=6):
    w_ = len(text) * 6 * px - px; bk.tag(F, text, (WF - w_) // 2, y, px)
def ctext(F, text, y, px=7, colr=(255, 200, 58)):
    w_ = len(text) * 6 * px - px; bk.pixel_text(F, text, (WF - w_) // 2, y, px=px, colr=colr)
def big_num(F, text, y, px=12, colr=(255, 255, 255)):
    w_ = len(text) * 6 * px - px; x = (WF - w_) // 2
    bk.pixel_text(F, text, x + px // 2, y + px // 2, px=px, colr=(6, 10, 24)); bk.pixel_text(F, text, x, y, px=px, colr=colr)
def disc(F, cx, cy, r, colr, ring=None, ringw=2):
    yy, xx = np.mgrid[int(cy - r) - 1:int(cy + r) + 2, int(cx - r) - 1:int(cx + r) + 2]
    d = np.hypot(xx + 0.5 - cx, yy + 0.5 - cy); M = d <= r
    col = np.zeros(M.shape + (3,), np.float32); col[M] = hexc(colr)
    if ring: col[M & (d > r - ringw)] = hexc(ring)
    col, M = bk.outline(col, M); pv.blit_hr(F, col, M, int(cx - r) - 1, int(cy - r) - 1, 1)
def hand(F, cx, cy, ang, ln, colr='#1b1428', w=1):
    for k in range(int(ln * 2)):
        f = k / 2; put(F, cx + f * math.sin(ang), cy - f * math.cos(ang), hexc(colr))
        if w > 1: put(F, cx + f * math.sin(ang) + 0.6, cy - f * math.cos(ang), hexc(colr))
def clock(F, cx, cy, r, ang_m, ang_h):
    disc(F, cx, cy, r, '#f4f6fb', ring='#c8d0e0')
    for k in range(12):
        th = TAU * k / 12; put(F, cx + (r - 3) * math.sin(th), cy - (r - 3) * math.cos(th), hexc('#3a4664'))
    hand(F, cx, cy, ang_h, r * 0.5, w=2); hand(F, cx, cy, ang_m, r * 0.78, '#e8303a'); put(F, cx, cy, hexc('#1b1428'))

HAND = ["001100000000", "010010000000", "010010000000", "010011011000", "010010100110", "110010100101", "100010100101",
        "100000000001", "100000000001", "010000000001", "010000000010", "001000000010", "000100000100", "000111111100"]
def draw_cursor(F, x, y, px=7):
    for r_, row in enumerate(HAND):
        ones = [k for k, ch_ in enumerate(row) if ch_ == '1']
        for k in range(len(row)):
            if row[k] == '1': colr = NAVY
            elif ones and ones[0] < k < ones[-1] and (r_ >= 1): colr = np.array([1.0, 1.0, 1.0])
            else: continue
            F[y + r_ * px:y + r_ * px + px, x + k * px:x + k * px + px] = colr

# ---------------- globe (from the penguins short) ----------------
_ly, _lx = np.mgrid[0:64, 0:128]
LAT = (0.5 - (_ly + 0.5) / 64) * math.pi; LON = (_lx + 0.5) / 128 * TAU
LAND = (np.sin(LON * 2 + 0.5) * np.cos(LAT * 3) + 0.6 * np.sin(LON * 5 + LAT * 4) + 0.35 * np.cos(LON * 3 - LAT * 6)) > 0.55
rng0 = np.random.default_rng(11)
HOME_PTS = [(la, lo) for la, lo in zip(rng0.uniform(-0.9, 1.1, 900), rng0.uniform(0, TAU, 900))
            if LAND[int((0.5 - la / math.pi) * 64) % 64, int(lo / TAU * 128) % 128]][:260]
def globe(F, t, cx=90, cy=108, R=50, homes=0.0, night=False):
    yy, xx = np.mgrid[-R - 1:R + 2, -R - 1:R + 2]
    nx, ny = (xx + 0.5) / R, (yy + 0.5) / R; d2 = nx ** 2 + ny ** 2; M = d2 <= 1
    nz = np.sqrt(np.clip(1 - d2, 0, 1)); lat = np.arcsin(np.clip(-ny, -1, 1)); rot = t * 0.25
    lon = (np.arctan2(nx, nz + 1e-6) + rot) % TAU
    land = LAND[np.clip(((0.5 - lat / math.pi) * 64).astype(int), 0, 63), (lon / TAU * 128).astype(int) % 128]
    light = np.clip(nx * -0.5 + ny * -0.45 + nz * 0.7, 0, 1); lvl = np.clip(np.floor(light * 3.2 + BAY[yy % 4, xx % 4] * 0.9), 0, 3).astype(int)
    OCE = np.stack([hexc('#123f8a'), hexc('#1d5bb8'), hexc('#2f7ddf'), hexc('#5ea6f2')])
    LND = np.stack([hexc('#1d6a3a'), hexc('#2f8f4a'), hexc('#4fb860'), hexc('#8fe08a')])
    ICE_ = np.stack([hexc('#8fb3dd'), hexc('#c4dcf4'), hexc('#eaf4ff'), hexc('#ffffff')])
    col = np.where(land[..., None], LND[lvl], OCE[lvl]); col = np.where((np.abs(lat) > 1.15)[..., None], ICE_[lvl], col)
    if night:
        nside = ((lon - rot + 1.2) % TAU) < math.pi; col[nside] = col[nside] * 0.45 + hexc('#0b1430') * 0.55
    col, M2 = bk.outline(col.astype(np.float32), M); pv.blit_hr(F, col, M2, cx - R - 1, cy - R - 1, 1)
    n_on = int(len(HOME_PTS) * homes)
    for la, lo in HOME_PTS[:n_on]:
        l2 = (lo - rot) % TAU; x3 = math.sin(l2) * math.cos(la); z3 = math.cos(l2) * math.cos(la)
        if z3 > 0.1: put(F, cx + x3 * R, cy - math.sin(la) * R, hexc('#ffe27a'))

# ---------------- scenes ----------------
def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t); a = t - SEG[i][0]
    if i == L_HOOK:                                              # sleigh races in... and explodes
        rv.island(F); boom_t = cs(L_HOOK, 3)
        speed_lines(F, t, 50, 140, sp=260)
        if t < boom_t:
            x = lerp(-120, 22, ramp(t, 0, 1.2)); draw_team(F, x, 64 + 3 * math.sin(t * 4), t)
            heat = ramp(t, cs(L_HOOK, 2), max(0.3, boom_t - cs(L_HOOK, 2)))
            if heat > 0: flames(F, x + 4, x + 120, 106, t, hmax=8, a=heat)
        else:
            k = ramp(t, boom_t, 0.9); explosion(F, 80, 88, k)
            if k > 0.25:
                c, M = SANTA; hat_c, hat_m = c[0:13, 12:36], M[0:13, 12:36]
                hy = 88 - 80 * math.sin(math.pi * min(1, (t - boom_t) / 1.6)) ; pv.blit_hr(F, hat_c, hat_m, 70 + (t - boom_t) * 14, hy, 1)
                smoke(F, 80, 100, t, a=1 - k * 0.5)
    elif i == L_WHAT:                                            # sooty Santa: WHAAAAT?!
        rv.island(F); jump = 8 * abs(math.sin(a * 8)) * math.exp(-a * 1.2)
        draw_santa(F, 90, GROUND + 1 - jump, soot=1.0); smoke(F, 84, 92, t); smoke(F, 98, 94, t + 0.4)
        ctext(F, '!?', 330, px=14)
    elif i == L_HOMES:                                           # 200 million homes
        globe(F, t, cy=118, homes=ramp(t, cs(L_HOMES, 1), 2.0), night=False)
        n = int(200_000_000 * ramp(t, cs(L_HOMES, 1), 2.4)); ctext(F, f'{n:,}', 210, px=9, colr=(255, 226, 122))
        ctag(F, 'HOMES', 330, px=6)
    elif i == L_HOURS:                                           # time zones: 31 hours
        globe(F, t * 3, cx=56, cy=110, R=36, homes=1.0, night=True)
        clock(F, 132, 110, 28, a * TAU * 3, a * TAU * 0.25)
        bk.label(F, 'TIME ZONES', 60, 300, int(56 * S), int(74 * S), px=6)
        if t >= cs(L_HOURS, 1) - 0.05: big_num(F, '31 HOURS', 880, px=10, colr=(255, 200, 58))
    elif i == L_PERSEC:                                          # 1,800 houses every second
        rv.island(F); sp = 260
        for k in range(6):
            hx = 200 - ((a * sp + k * 48) % 288); draw_house(F, hx)
        speed_lines(F, t, 60, 150, n=10, sp=500)
        draw_team(F, 26, 58 + 2 * math.sin(t * 6), t)
        if t >= cs(L_PERSEC, 1) - 0.05:
            n = min(1800, int(1800 * ramp(t, cs(L_PERSEC, 1), 1.0))); ctext(F, f'{n:,} / SECOND', 230, px=8)
    elif i == L_SPEED:                                           # speedometer to 1,000 km/s
        cx, cy, R = 90, 128, 58; k = ramp(t, cs(L_SPEED, 2) - 0.6, 1.4)
        yy, xx = np.mgrid[cy - R - 2:cy + 3, cx - R - 2:cx + R + 3]; d = np.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
        M = (d <= R) & (yy <= cy); col = np.zeros(M.shape + (3,), np.float32); col[M] = hexc('#0f1a34')
        ang = np.arctan2(-(yy + 0.5 - cy), xx + 0.5 - cx)
        band = M & (d > R - 7); col[band] = np.where((ang < math.pi * 0.33)[band][:, None], hexc('#e8303a'), np.where((ang < math.pi * 0.66)[band][:, None], hexc('#ffcc4a'), hexc('#5ae07a')))
        col, M = bk.outline(col, M); pv.blit_hr(F, col, M, cx - R - 2, cy - R - 2, 1)
        th = math.pi * (1 - k) + 0.04 * math.sin(t * 40) * k
        for j in range(0, int((R - 10) * 2)): put(F, cx + j / 2 * math.cos(th), cy - j / 2 * math.sin(th), hexc('#ffffff'))
        disc(F, cx, cy, 4, '#e8303a')
        big_num(F, f'{int(1000 * k):,} KM/S', 220, px=9, colr=(255, 200, 58) if k > 0.98 else (255, 255, 255))
        if k > 0.98: flames(F, cx - R, cx + R, cy + 4, t, hmax=5)
    elif i == L_SOUND:                                           # 3,000x the speed of sound
        k = ramp(t, SEG[L_SOUND][0] + 0.2, 1.6)
        rows = (('SOUND', 0.012, '#5ea6f2'), ('SANTA', k, '#e8303a'))
        for j, (lbl, f, colr) in enumerate(rows):
            y = 76 + j * 50; bk.pixel_text(F, lbl, 84, int((y - 14) * S), px=8, colr=(225, 235, 255))
            w_ = max(3, int(150 * f)); bar = np.zeros((24, w_, 3), np.float32) + hexc(colr); M = np.ones((24, w_), bool)
            bar[:4] = bar[:4] * 0.6 + 0.4; bar, M = bk.outline(bar, M); pv.blit_hr(F, bar, M, 14, y, 1)
            if j == 1 and k > 0.95: flames(F, 14 + w_ - 12, 14 + w_ + 2, y + 23, t, hmax=12)
            if j == 1 and k > 0.2: draw_team(F, 14 + w_ - 128, y - 52, t) if False else None
        if t >= cs(L_SOUND, 0) + 0.4: big_num(F, 'X3,000', 950, px=11, colr=(255, 200, 58))
    elif i == L_METEOR:                                          # meteors burn up at 20 km/s; Santa is 50x faster
        f1 = (a * 0.4) % 1; mx = lerp(200, -30, f1); my = lerp(58, 96, f1)
        for j in range(60):
            for w in range(-3, 4):
                if abs(w) <= 3 - j / 20: put(F, mx + j * 1.5, my - j * 0.25 + w, FLAME[min(3, j // 15)], 1 - j / 60)
        disc(F, mx, my, 7, '#8a7a6a', ring='#6a5a4a'); glow(F, mx, my, 14, '#ffcc4a', 0.5)
        ctext(F, 'METEOR: 20 KM/S', 230, px=7, colr=(255, 200, 120))
        if t >= cs(L_METEOR, 3) - 0.05:
            sx = lerp(220, -150, ((t - cs(L_METEOR, 3)) * 0.9) % 1)
            for j in range(80): put(F, sx + 120 + j, 128 + 6 * math.sin(j * 0.5 + t * 30), FLAME[min(3, j // 20)], 1 - j / 80)
            flames(F, sx, sx + 125, 152, t, hmax=12); draw_team(F, sx, 108, t)
            big_num(F, 'X50', 940, px=11, colr=(255, 120, 60))
    elif i == L_FIRE:                                            # the reindeer catch fire
        rv.island(F); burnt = ramp(t, cs(L_FIRE, 2), 1.2)
        nose, eye = draw_deer(F, 90, nose='red')
        if burnt > 0:
            col, M, _, _ = deer(nose='red'); yy, xx = np.mgrid[0:M.shape[0], 0:M.shape[1]]
            m = M & (BAY[yy % 4, xx % 4] < burnt) & (col.sum(-1) > 0.3)
            c2 = np.where(m[..., None], col * 0.15 + hexc('#241e28') * 0.85, col); pv.blit_hr(F, c2, M, 57, GROUND + 1 - 56, 1)
            put(F, eye[0], eye[1], hexc('#ffffff')); put(F, eye[0] - 1, eye[1], hexc('#ffffff'))
            smoke(F, 84, 110, t, a=burnt); smoke(F, 100, 104, t + 0.5, a=burnt)
        flames(F, 64, 116, 116, t, hmax=12, a=ramp(t, cs(L_FIRE, 1) - 0.1, 0.4) * (1 - burnt))
    elif i in (L_GFORCE, L_FLAT):                                # millions of g's, squished flat
        rv.island(F)
        if i == L_GFORCE:
            k = ramp(t, cs(L_GFORCE, 2), 1.0); sq = 1 - 0.15 * k
            draw_santa(F, 90, squash=sq)
            for j in range(5):
                ay = 52 + ((t * 120 + j * 9) % 30); put(F, 82 + j * 4, ay, hexc('#cfe2f6')); put(F, 82 + j * 4, ay + 1, hexc('#cfe2f6'))
            if t < cs(L_GFORCE, 3) - 0.05:
                n = int(3_000_000 * k); ctext(F, f'{n:,} G', 230, px=8, colr=(255, 120, 60))
            else:
                ctext(F, 'PILOTS: 9 G', 230, px=8, colr=(225, 235, 255)); ctext(F, 'SANTA: MILLIONS', 310, px=8, colr=(255, 120, 60))
        else:
            k = ramp(t, cs(L_FLAT, 1) - 0.1, 0.25); wob = 0.04 * math.sin((t - cs(L_FLAT, 1)) * 30) * math.exp(-(t - cs(L_FLAT, 1)) * 3) if k > 0 else 0
            draw_santa(F, 90, squash=max(0.18, 1 - 0.82 * k + wob))
            if t >= cs(L_FLAT, 2) - 0.05: ctag(F, 'PANCAKE', 380, px=8)
    elif i == L_BOOM:                                            # sonic boom shatters the windows
        rv.island(F); shat = cs(L_BOOM, 2)
        for hx in (48, 132): draw_house(F, hx, broken=t >= shat)
        pass_t = cs(L_BOOM, 1); f = (t - pass_t + 0.4) / 1.0
        if 0 < f < 1.2: draw_team(F, lerp(-130, 200, f / 1.2), 52, t)
        if t >= pass_t:
            for r_ in range(3):
                rr = ((t - pass_t) * 70 + r_ * 22) % 90
                for j in range(60):
                    th = TAU * j / 60; al = max(0, 1 - rr / 90)
                    put(F, 90 + rr * math.cos(th), 74 + rr * 0.7 * math.sin(th), hexc('#ffffff'), al); put(F, 90 + (rr + 1) * math.cos(th), 74 + (rr + 1) * 0.7 * math.sin(th), hexc('#9fd8ff'), al)
            if t < shat + 0.2: ctag(F, 'BOOM', 250, px=10)
        if t >= shat:
            for hx in (48, 132):
                for j in range(10):
                    dt_ = t - shat; ox = (j - 5) * 3 * dt_ * 4; oy = -6 * dt_ + 30 * dt_ * dt_
                    put(F, hx - 9 + (j % 2) * 17 + ox * 0.3, GROUND - 14 + oy, hexc('#cfe9ff'))
    elif i == L_TWIST:                                           # plot twist: a real professor
        rv.island(F)
        board = np.zeros((40, 66, 3), np.float32) + hexc('#1d3a2a'); bm = np.ones((40, 66), bool)
        board[:3] = hexc('#8a5a36'); board[-3:] = hexc('#8a5a36'); board[:, :3] = hexc('#8a5a36'); board[:, -3:] = hexc('#8a5a36')
        board, bm = bk.outline(board, bm); pv.blit_hr(F, board, bm, 22, 88, 1)
        bk.pixel_text(F, 'E=MC2', int(31 * S), int(98 * S), px=6, colr=(240, 240, 230))
        if t >= cs(L_TWIST, 1) - 0.05:
            c, M = spr('prof', ch.professor); pv.blit_hr(F, c, M, 112 - 17, GROUND + 1 - 54 - abs(math.sin(t * 3)), 1)
            bk.label(F, 'PROFESSOR', 780, 520, int(118 * S), int(102 * S), px=5)
        ctag(F, 'PLOT TWIST', 250, px=8)
        if t >= cs(L_TWIST, 2) - 0.05: ctext(F, 'POSSIBLE!', 400, px=9, colr=(90, 224, 122))
    elif i == L_TIME:                                            # relativity: time stretches in a bubble
        rv.island(F)
        bub = ramp(t, cs(L_TIME, 1) - 0.1, 0.6)
        if bub > 0:
            yy, xx = np.mgrid[0:H, 0:W]; d = np.hypot((xx - 90) / 1.25, yy - 110)
            m = (np.abs(d - 46 * bub) < 1.2) & (BAY[yy % 4, xx % 4] < 0.8)
            A = np.repeat(np.repeat(m.astype(np.float32), S, 0), S, 1)[..., None] * 0.8
            F[:] = F * (1 - A) + hexc('#9fd8ff') * A
            glow(F, 90, 110, 46 * bub, '#5aa0ff', 0.25)
        draw_team(F, 32, 92 + 2 * math.sin(t * 2), t, show_deer=True)
        if t >= cs(L_TIME, 3) - 0.05:
            clock(F, 26, 50, 13, (t - cs(L_TIME, 3)) * 0.4, 0); bk.pixel_text(F, 'US: 1 NIGHT', 40, int(68 * S), px=5, colr=(225, 235, 255))
        if t >= cs(L_TIME, 5) - 0.05:
            months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT']
            m_ = months[min(9, int((t - cs(L_TIME, 5)) * 5))]
            rv.calendar(F, m_, x=600, y=200); bk.pixel_text(F, 'SANTA: MONTHS', 640, 345, px=5, colr=(255, 200, 58))
    elif i == L_SMART:                                           # not just magic: a genius
        rv.island(F)
        c, M = spr('board', lambda: None) if False else (None, None)
        draw_santa(F, 90, bob=abs(math.sin(t * 3)) * 1.5, glasses=t >= cs(L_SMART, 2) - 0.05)
        if t < cs(L_SMART, 2) - 0.05: ctag(F, 'MAGIC?', 300, px=8)
        else:
            ctag(F, 'GENIUS', 300, px=8)
            for k in range(10):
                th = TAU * k / 10 + t; rv.sparkle(F, 90 + 40 * math.cos(th), 98 + 12 * math.sin(th), 0.9)
    else:                                                        # CTA: comment + subscribe or naughty list
        rv.island(F)
        sl = ramp(t, SEG[L_CTA][0], 0.6)
        draw_santa(F, lerp(-30, 48, sl), bob=abs(math.sin(t * 3)) * 1.2)
        nose, _ = draw_deer(F, 138, nose='red', flip=True)
        # comment bubble with the two answers
        if t < cs(L_CTA, 2) - 0.05:
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(760 * pop), int(230 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 240
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    bk.pixel_text(F, 'HOW DOES HE DO IT?', X + 70, Y + 40, px=6, colr=(20, 24, 40))
                    bk.pixel_text(F, 'MAGIC', X + 80, Y + 130, px=7, colr=(200, 40, 60)); bk.pixel_text(F, 'OR', X + 330, Y + 130, px=7, colr=(20, 24, 40))
                    bk.pixel_text(F, 'SCIENCE', X + 440, Y + 130, px=7, colr=(30, 120, 220))
        else:
            press = cs(L_CTA, 2) + 0.35; pressed = t >= press
            bw, bh = 640, 150; X, Y = (WF - bw) // 2, 260
            sq = 6 if press - 0.1 <= t < press + 0.1 else 0
            F[Y + sq:Y + bh - sq, X + sq:X + bw - sq] = hexc('#5a6070') if pressed else hexc('#e8202e')
            for q in range(5):
                F[Y + sq + q, X + sq:X + bw - sq] = F[Y + bh - sq - 1 - q, X + sq:X + bw - sq] = NAVY
                F[Y + sq:Y + bh - sq, X + sq + q] = F[Y + sq:Y + bh - sq, X + bw - sq - 1 - q] = NAVY
            txt = 'SUBSCRIBED' if pressed else 'SUBSCRIBE'; tw = len(txt) * 6 * 9 - 9
            bk.pixel_text(F, txt, (WF - tw) // 2, Y + 44, px=9, colr=(255, 255, 255))
            cx_, cy_ = lerp(WF * 0.8, WF * 0.6, ramp(t, cs(L_CTA, 2), 0.35)), Y + bh - 30          # pointer hand
            draw_cursor(F, int(cx_), int(cy_))
            if pressed:
                for k in range(8): rv.sparkle(F, 90 + 50 * math.cos(TAU * k / 8), 62 + 18 * math.sin(TAU * k / 8), 1 - ramp(t, press, 0.8))
            if t >= cs(L_CTA, 3) - 0.05:
                c, M = spr('scroll', ch.scroll); sx = lerp(48, 64, ramp(t, cs(L_CTA, 3), 0.3))
                pv.blit_hr(F, c, M, sx + 6, GROUND - 46, 1)
                bk.pixel_text(F, 'NAUGHTY', int((sx + 8) * S) + 2, int((GROUND - 38) * S), px=3, colr=(200, 30, 40))

# ---------------- captions + frame ----------------
CAPS = [(c['t0'], c['t1'], rv.caption_sprite(c['text'], set(c['hl']))) for c in CAPJ]
def captions(F, t):
    for a, b, spr_ in CAPS:
        if a <= t < b:
            dy = int(6 * (1 - min(1.0, (t - a) / 0.06))); h_ = spr_.shape[0]; A = spr_[..., 3:4]
            F[rv.CAP_Y + dy:rv.CAP_Y + dy + h_] = F[rv.CAP_Y + dy:rv.CAP_Y + dy + h_] * (1 - A) + spr_[..., :3] * A
    if t < SEG[1][1] + 0.4:
        y0 = rv.CAP_Y + 140; x0 = WF // 2 - 35
        for r_, row in enumerate(rv.HEADPHONES):
            for c_, bb in enumerate(row):
                if bb == '1': F[y0 + r_ * 7:y0 + r_ * 7 + 7, x0 + c_ * 7:x0 + c_ * 7 + 7] = 1.0
SHOUTS = [cs(L_HOOK, 3), SEG[L_WHAT][0], cs(L_FLAT, 1), cs(L_BOOM, 2)]
NO_SNOW = (L_HOMES, L_HOURS, L_SPEED, L_SOUND, L_METEOR)
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    if i not in NO_SNOW: rv.snow(F, min(t, cs(L_TIME, 1)) if i == L_TIME else t)       # snow freezes in the time bubble
    if i >= 2 and 0 <= t - SEG[i][0] < 0.12:
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
