"""Detailed props for the mom short + alignment helpers (all coordinates in GRID px, 1 grid px = 6 screen px).
phone(): proper phone with case, bezel, camera notch, gradient wallpaper, app icons, status bar, home bar,
side buttons and a screen shine. Anchored helpers put it exactly in an elf's hand or on the floor with a shadow.
Item icons for the memory grid are small detailed sprites, and every label is centred with real text widths."""
import math
import numpy as np
from characters import Layers, seg
from blueprint_kit import hexc, OUTLINE as NAVY
import blueprint_kit as bk

S = 6
def _blit(F, c, M, x0, y0):
    """pixel-exact blit (rounded to whole grid px so things line up)"""
    x0, y0 = int(round(x0)), int(round(y0)); h_, w_ = M.shape
    for yy in range(h_):
        Y = (y0 + yy) * S
        if Y < 0 or Y + S > F.shape[0]: continue
        row = M[yy]
        for xx in np.nonzero(row)[0]:
            X = (x0 + xx) * S
            if 0 <= X and X + S <= F.shape[1]: F[Y:Y + S, X:X + S] = c[yy, xx]

_cache = {}
def phone_sprite(case='#1b1428', big=False):
    key = (case, big)
    if key in _cache: return _cache[key]
    w_, h_ = (14, 24) if big else (10, 17)
    yy, xx = np.mgrid[0:h_, 0:w_ + 2].astype(np.float32); L = Layers(w_ + 2, h_)
    body = (xx >= 0) & (xx < w_) & (yy >= 0) & (yy < h_)
    body &= ~(((xx == 0) | (xx == w_ - 1)) & ((yy == 0) | (yy == h_ - 1)))          # rounded corners
    sx0, sy0, sx1, sy1 = 1, 2 if big else 1, w_ - 1, h_ - (3 if big else 2)            # screen rect
    def f(c, m):
        c[m] = hexc(case); c[m & (xx >= w_ - 2)] = hexc(case) * 0.8                        # case + side shade
        scr = (xx >= sx0) & (xx < sx1) & (yy >= sy0) & (yy < sy1)
        g = (yy - sy0) / max(1, sy1 - sy0)                                                  # wallpaper gradient (3 tones)
        c[scr] = hexc('#3a6ae8'); c[scr & (g > 0.4)] = hexc('#5a4ad8'); c[scr & (g > 0.75)] = hexc('#7a3ac8')
        c[scr & (yy == sy0)] = hexc('#1d2a5a')                                              # status bar
        if big:
            c[(yy == sy0) & (xx == sx1 - 2)] = hexc('#5ae07a'); c[(yy == sy0) & (xx == sx0 + 1)] = hexc('#ffffff')
            cols = ['#ffcc4a', '#5ae07a', '#ff5a64', '#ffffff', '#5ea6f2', '#ff9a3a']
            for k in range(6):                                                              # 2x3 app icons
                ax, ay = sx0 + 1 + (k % 3) * 4, sy0 + 3 + (k // 3) * 4
                c[(xx >= ax) & (xx < ax + 3) & (yy >= ay) & (yy < ay + 3)] = hexc(cols[k])
            c[(xx >= sx0 + 1) & (xx < sx1 - 1) & (yy == sy1 - 2)] = hexc('#cfe2f6') * 0.85     # dock line
        else:
            for k, col in enumerate(('#ffcc4a', '#5ae07a', '#ff5a64', '#ffffff')):
                ax, ay = sx0 + 1 + (k % 2) * 4, sy0 + 3 + (k // 2) * 4
                c[(xx >= ax) & (xx < ax + 2) & (yy >= ay) & (yy < ay + 2)] = hexc(col)
        shine = scr & (np.abs((xx - sx0) - (yy - sy0) * 0.6 - (sx1 - sx0) * 0.55) < 0.7)
        c[shine] = c[shine] * 0.5 + 0.5
        nx = w_ / 2 - 1.5                                                                    # camera notch
        c[(yy == (1 if big else 0)) & (xx >= nx) & (xx < nx + 3)] = hexc('#0a0a14') if big else hexc(case) * 0.6
        if big: c[(yy == h_ - 2) & (xx >= w_ / 2 - 2) & (xx < w_ / 2 + 2)] = hexc('#e8eef6')  # home bar
    L.add(body, f)
    L.add((xx == w_) & (yy >= 4) & (yy < (9 if big else 7)), hexc(case) * 0.7, outline=False)     # side button
    _cache[key] = L.out(); return _cache[key]

def draw_phone(F, cx, bottom, case='#1b1428', big=False, glint=0.0):
    """phone centred on cx with its bottom edge on `bottom`"""
    c, M = phone_sprite(case, big); h_, w_ = M.shape
    _blit(F, c, M, cx - (w_ - 2) / 2 - 1, bottom - h_ + 1)
    if glint > 0:
        from_x, from_y = cx + w_ / 2 - 1, bottom - h_ + 1
        for k in range(1, 4):
            for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)): _put(F, from_x + dx, from_y + dy, hexc('#fff6c0'), glint * (1 - k / 4))
        _put(F, from_x, from_y, hexc('#ffffff'), glint)
def _put(F, x, y, col, a=1.0):
    X, Y = int(round(x)) * S, int(round(y)) * S
    if 0 <= X < F.shape[1] - S and 0 <= Y < F.shape[0] - S: F[Y:Y + S, X:X + S] = F[Y:Y + S, X:X + S] * (1 - a) + col * a

# elf hand anchors (from characters.elf geometry): sprite top-left = (cx - 19, feet - 53 - bob)
def hand(cx, feet, arms='up', side=1, bob=0.0):
    y0 = feet - 53 - bob
    if arms == 'up': return cx + side * 16.5, y0 + 18.5          # held a little outward so it never covers the head
    if arms == 'hold': return cx, y0 + 37
    return cx + side * 10.2, y0 + 39.5
def phone_in_hand(F, cx, feet, arms='up', side=1, bob=0.0, case='#1b1428', glint=0.0):
    hx, hy = hand(cx, feet, arms, side, bob)
    draw_phone(F, hx, hy + (4 if arms == 'hold' else 1), case=case, glint=glint)     # hand covers the bottom of the phone
def phone_on_floor(F, cx, feet, case='#1b1428', shadow_fn=None, glint=0.0, lift=0.0):
    if shadow_fn: shadow_fn(F, cx, feet, 14 * max(0.5, 1 - lift / 30))
    draw_phone(F, cx, feet - lift, case=case, glint=glint)

# ---------- detailed item icons (about 14x12 each) ----------
def icon(name):
    if name in _cache: return _cache[name]
    L = Layers(16, 14); yy, xx = np.mgrid[0:14, 0:16].astype(np.float32)
    if name == 'PHONE':
        c, M = phone_sprite('#1b1428'); _cache[name] = (c, M); return _cache[name]
    if name == 'KEYS':
        ring = (np.hypot(xx - 4.5, yy - 4.5) <= 3.4) & (np.hypot(xx - 4.5, yy - 4.5) >= 2.0)
        L.add(ring, hexc('#c4ccd8'))
        for (y_, col, teeth) in ((5, '#ffcc4a', (10, 12)), (9, '#e8a83a', (11, 13))):
            head = (np.hypot(xx - 7.5, yy - y_) <= 2.1)
            blade = (xx >= 8) & (xx < 14) & (np.abs(yy - y_) <= 0.6)
            tooth = np.zeros_like(blade)
            for tx in teeth: tooth |= (np.abs(xx - tx) < 0.6) & (yy > y_) & (yy <= y_ + 1.6)
            L.add(head | blade | tooth, lambda c, m, col=col, y_=y_: (c.__setitem__(m, hexc(col)), c.__setitem__(m & (np.hypot(xx - 7.5, yy - y_) <= 0.8), hexc('#1f4782'))))
    elif name == 'SOCK':
        leg = (xx >= 4) & (xx < 9) & (yy >= 0) & (yy < 9); foot = (((xx - 8) / 5) ** 2 + ((yy - 10) / 3) ** 2 <= 1) & (xx >= 4)
        L.add(leg | foot, lambda c, m: (c.__setitem__(m, hexc('#c8303a')), c.__setitem__(m & ((yy.astype(int) % 3) == 1) & (yy < 8) & (yy > 1), hexc('#ffffff')),
                                         c.__setitem__(m & (yy < 1.5), hexc('#ffffff')), c.__setitem__(m & (xx > 10.5) & (yy > 8), hexc('#a01828')),
                                         c.__setitem__(m & (xx < 6) & (yy > 9), hexc('#a01828'))))
    elif name == 'REMOTE':
        r = (xx >= 4) & (xx < 11) & (yy >= 0) & (yy < 14)
        def rf(c, m):
            c[m] = hexc('#3a4664'); c[m & (xx > 9)] = hexc('#2a3450')
            c[(np.hypot(xx - 7, yy - 2.5) <= 1.2)] = hexc('#ff4a4a')
            for k in range(6): bx, by = 5.5 + (k % 2) * 3, 5.5 + (k // 2) * 2.6; c[(np.abs(xx - bx) < 0.8) & (np.abs(yy - by) < 0.8)] = hexc('#cfe2f6')
        L.add(r, rf)
    elif name == 'SHOE':
        s_ = (((xx - 8) / 7) ** 2 + ((yy - 9) / 3.5) ** 2 <= 1) | ((xx >= 2) & (xx < 8) & (yy >= 3) & (yy < 10))
        L.add(s_, lambda c, m: (c.__setitem__(m, hexc('#8a5a36')), c.__setitem__(m & (yy >= 11), hexc('#f4f6fb')),
                                c.__setitem__(m & (np.abs(yy - 6) < 0.6) & (xx >= 3) & (xx < 7), hexc('#ffcc4a'))))
    elif name == 'CHARGER':
        blk = (xx >= 1) & (xx < 7) & (yy >= 3) & (yy < 10)
        L.add(blk, lambda c, m: (c.__setitem__(m, hexc('#f4f6fb')), c.__setitem__(m & (xx > 5), hexc('#d8dee8')), c.__setitem__(m & (np.hypot(xx - 4, yy - 6.5) < 0.9), hexc('#5ae07a'))))
        L.add(((np.abs(xx - 2.5) < 0.6) | (np.abs(xx - 5.5) < 0.6)) & (yy >= 1) & (yy < 3), hexc('#c4ccd8'), outline=False)
        cable = np.zeros_like(blk)
        for k in range(40):
            f = k / 39; px_, py_ = 7 + 7 * f, 8 + 3.5 * math.sin(f * math.pi)
            cable |= (np.abs(xx - round(px_)) < 0.6) & (np.abs(yy - round(py_)) < 0.6)
        L.add(cable, hexc('#e8eef6'))
    _cache[name] = L.out(); return _cache[name]

def text_w(text, px): return len(text) * 6 * px - px                      # screen px
def text_center(F, text, cx, y, px=5, colr=(225, 235, 255)):
    """text centred on grid x = cx, top at grid y"""
    bk.pixel_text(F, text, int(round(cx * S - text_w(text, px) / 2)), int(round(y * S)), px=px, colr=colr)
