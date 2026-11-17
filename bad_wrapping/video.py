"""'What If Bad Gift Wrapping Made You a Genius?' - blueprint pixel short narrated by Jett (1080x1920, 60 fps).
A story, not a fact list: Tinsel (messy wrapper, the viewer) vs Holly (perfect wrapper). Study = the turn,
re-hook around 30 s, friends-vs-boss twist, tag + naughty-list subscribe CTA.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study'))
import importlib.util
_s = importlib.util.spec_from_file_location('santa_video', os.path.join(ROOT_, 'santa_speed', 'video.py'))
sv = importlib.util.module_from_spec(_s); _s.loader.exec_module(sv)          # shared helpers
rv, pv, bk, ch = sv.rv, sv.pv, sv.bk, sv.ch

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
glow, ctag, ctext, big_num, draw_cursor = sv.glow, sv.ctag, sv.ctext, sv.big_num, sv.draw_cursor
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
(L_HOOK, L_GENIUS, L_TINSEL, L_MESS, L_HOLLY, L_WINS, L_TEST, L_MORE, L_WHY, L_MUG, L_MESSY, L_SANTA, L_NOBODY,
 L_FRIENDS, L_BOSS, L_BOTH, L_CTA) = range(17)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))

# ---------------- invisible floor: soft pixel shadows instead of a platform ----------------
def shadow(F, cx, feet, w_, a=0.42):
    """dithered oval shadow on the invisible floor (grid coords), two soft bands"""
    rx, ry = w_ * 0.5, max(2.2, w_ * 0.09)
    x0, x1, y0, y1 = int(cx - rx - 1), int(cx + rx + 2), int(feet - ry - 1), int(feet + ry + 2)
    yy, xx = np.mgrid[y0:y1, x0:x1]; d = ((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - feet) / ry) ** 2
    k = np.where(d <= 0.45, a, np.where(d <= 1.0, a * 0.55, 0.0)) * (BAY[yy % 4, xx % 4] < 0.92)
    ya, yb, xa, xb = max(0, y0), min(H, y1), max(0, x0), min(W, x1)
    K = np.repeat(np.repeat(k[ya - y0:yb - y0, xa - x0:xb - x0], S, 0), S, 1)[..., None]
    F[ya * S:yb * S, xa * S:xb * S] *= (1 - K) + K * np.array([0.35, 0.4, 0.6])
def floor(F): pass                                           # no platform: characters stand on an invisible floor
def draw_santa(F, cx, feet=GROUND + 1, **kw):
    if kw.get('bob', 0) < 30: shadow(F, cx, feet, 40 * max(0.6, 1 - kw.get('bob', 0) / 40))
    return sv.draw_santa(F, cx, feet, **kw)
def draw_deer(F, cx, feet=GROUND + 1, **kw):
    shadow(F, cx, feet, 56); return sv.draw_deer(F, cx, feet, **kw)
def draw_prof(F, cx, feet=GROUND + 1, bob=0.0):
    shadow(F, cx, feet, 28); c, M = sv.spr('prof', ch.professor); pv.blit_hr(F, c, M, cx - 17, feet - 54 - bob, 1)

# ---------------- sprites ----------------
_c = {}
def spr(key, fn):
    if key not in _c: _c[key] = fn()
    return _c[key]
TINSEL = dict(messy=True)
HOLLY = dict(outfit='#d22a38', outfit_d='#a0182a', hat='#d22a38')
def draw_elf(F, cx, who, feet=GROUND + 1, bob=0.0, **kw):
    args = dict(TINSEL if who == 'tinsel' else HOLLY); args.update(kw)
    c, M = spr(('elf', who, tuple(sorted(kw.items()))), lambda: ch.elf(**args))
    shadow(F, cx, feet, 30 * max(0.6, 1 - bob / 30)); pv.blit_hr(F, c, M, cx - 19, feet - 53 - bob, 1); return cx, feet - 53 - bob
def draw_gift(F, cx, kind, feet=GROUND + 1, big=False, bob=0.0, scale_open=0.0):
    if kind == 'neat': c, M = spr(('gn', big), lambda: ch.gift_neat(w=60, h=48) if big else ch.gift_neat())
    else: c, M = spr(('gm', big), lambda: ch.gift_messy(w=64, h=52, seed=4) if big else ch.gift_messy())
    h_, w_ = M.shape; shadow(F, cx, feet, w_ * 0.9 * max(0.6, 1 - bob / 30)); pv.blit_hr(F, c, M, cx - w_ / 2, feet - h_ - bob, 1); return cx - w_ / 2, feet - h_ - bob, w_, h_
def draw_mug(F, cx, bottom):
    c, M = spr('mug', ch.mug); shadow(F, cx - 2, GROUND + 1, 18 * max(0.5, 1 - (GROUND + 1 - bottom) / 30)); pv.blit_hr(F, c, M, cx - 11, bottom - 20, 1)
HEART = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
def heart(F, x, y, a=1.0, colr='#ff4f7a'):
    for r_, row in enumerate(HEART):
        for c_, b in enumerate(row):
            if b == '1': put(F, x + c_ - 3, y + r_ - 3, hexc(colr), a)
def sparkles(F, cx, cy, rx, ry, t, n=10):
    for k in range(n):
        th = TAU * k / n + t; rv.sparkle(F, cx + rx * math.cos(th), cy + ry * math.sin(th), 0.9)
def meter(F, x, label, val, colr, y_top=62, h_=56, w_=14):
    """vertical meter (grid coords), val 0..1, label under it in screen px"""
    frame_ = np.zeros((h_, w_, 3), np.float32) + hexc('#0f1a34'); M = np.ones((h_, w_), bool)
    fill = int(h_ * max(0, min(1, val)))
    if fill > 0: frame_[h_ - fill:, 2:w_ - 2] = hexc(colr)
    frame_, M = bk.outline(frame_, M); pv.blit_hr(F, frame_, M, x - w_ / 2, y_top, 1)
    tw = len(label) * 6 * 5 - 5; bk.pixel_text(F, label, int(x * S - tw / 2), int((y_top - 9) * S), px=5, colr=(225, 235, 255))
def thought(F, x, y, w_, h_):
    X, Y = int((x - w_ / 2) * S), int(y * S); Wd, Hd = int(w_ * S), int(h_ * S)
    F[Y:Y + Hd, X:X + Wd] = 1.0
    for q in range(5): F[Y + q, X:X + Wd] = F[Y + Hd - 1 - q, X:X + Wd] = NAVY; F[Y:Y + Hd, X + q] = F[Y:Y + Hd, X + Wd - 1 - q] = NAVY
    for k, (dx, dy, r_) in enumerate(((0, h_ + 3, 2.2), (-3, h_ + 8, 1.4))):
        sv.disc(F, x + dx, y + dy, r_, '#ffffff')
def paper_bits(F, cx, cy, t, n=14, spread=40):
    cols = ['#e8303a', '#ff5a64', '#ffcc4a', '#f4f8ff', '#5ae07a']
    for k in range(n):
        ph = (t * 1.3 + k * 0.137) % 1; ang = k * 2.4
        x = cx + math.cos(ang) * spread * ph; y = cy - 30 * math.sin(math.pi * ph) + math.sin(ang) * 8 * ph
        for dx, dy in ((0, 0), (1, 0), (0, 1)): put(F, x + dx, y + dy, hexc(cols[k % 5]), 1 - ph * 0.5)

# ---------------- scenes ----------------
def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t); a = t - SEG[i][0]
    if i == L_HOOK:                                              # Tinsel and her terrible gift
        floor(F); draw_elf(F, 58, 'tinsel', bob=abs(math.sin(t * 3)))
        draw_gift(F, 122, 'messy')
        bk.label(F, 'BAD WRAPPING', 560, 470, int(122 * S), int((GROUND - 34) * S), px=6)
    elif i == L_GENIUS:                                          # ...are GENIUSES!
        floor(F); jump = 8 * abs(math.sin(a * 7)) * math.exp(-a * 1.3)
        draw_elf(F, 58, 'tinsel', bob=jump, cap=True, mood='proud', arms='up'); draw_gift(F, 122, 'messy')
        sparkles(F, 58, 100, 30, 12, t); ctag(F, 'GENIUS', 300, px=12)
    elif i == L_TINSEL:                                          # wraps like a raccoon in a hurry
        floor(F); draw_elf(F, 50, 'tinsel', mood='shock' if (t * 4) % 2 < 1 else 'happy', arms='up' if (t * 6) % 2 < 1 else 'hold')
        bx = draw_gift(F, 124, 'messy', bob=abs(math.sin(t * 14)) * 2)
        paper_bits(F, 124, 116, t, n=18)
        bk.label(F, 'TINSEL', 60, 440, int(50 * S), int((GROUND - 56) * S), px=6)
        if t >= cs(L_TINSEL, 2) - 0.05: ctag(F, 'RACCOON MODE', 260, px=7)
    elif i == L_MESS:                                            # close-up: tape, ripped, the bow?
        gx, gy, gw, gh = draw_gift(F, 90, 'messy', feet=150, big=True)
        notes = [(cs(L_MESS, 0), 'TAPE', 60, 330, gx + 14, gy + 26), (cs(L_MESS, 1), 'RIPPED', 690, 330, gx + gw / 2 + 64 * 0.28, gy + 10 + 26 + 52 * 0.22),
                 (cs(L_MESS, 2), 'BOW?', 820, 520, gx + gw - 6, gy + 10)]
        for ts, txt, lx, ly, ax, ay in notes:
            if t >= ts - 0.05: bk.label(F, txt, lx, ly, int(ax * S), int(ay * S), px=7)
        if t >= cs(L_MESS, 3) - 0.05: bk.pixel_text(F, '?', 900, 700, px=12, colr=(255, 200, 58))
    elif i == L_HOLLY:                                           # Holly: fancy-store gifts
        floor(F); draw_elf(F, 58, 'holly', mood='proud', arms='hold'); draw_gift(F, 122, 'neat')
        if t >= cs(L_HOLLY, 1) - 0.05: bk.label(F, 'HOLLY', 60, 440, int(58 * S), int((GROUND - 56) * S), px=6)
        if t >= cs(L_HOLLY, 4) - 0.05: sparkles(F, 122, 128, 22, 10, t, n=8); ctag(F, 'FANCY', 280, px=8)
    elif i == L_WINS:                                            # everyone thinks Holly wins
        floor(F); draw_elf(F, 40, 'tinsel', mood='sad'); draw_elf(F, 140, 'holly', mood='proud', arms='up', bob=abs(math.sin(t * 4)) * 2)
        for k in range(5):
            ph = (t * 0.8 + k / 5) % 1; heart(F, 128 + k * 6, 92 - ph * 30, 1 - ph)
        ctag(F, 'WINNER?', 300, px=8)
    elif i in (L_TEST, L_MORE):                                  # scientists tested it: same gift, neat vs sloppy
        floor(F); draw_prof(F, 30)
        draw_gift(F, 92, 'neat'); draw_gift(F, 144, 'messy')
        if t >= cs(L_TEST, 2) - 0.05 or i == L_MORE: ctag(F, 'SAME GIFT', 260, px=7)
        if t >= cs(L_TEST, 3) - 0.05 or i == L_MORE: bk.pixel_text(F, 'NEAT', int(80 * S), int((GROUND + 6) * S) - 230, px=5)
        if t >= cs(L_TEST, 4) - 0.05 or i == L_MORE: bk.pixel_text(F, 'SLOPPY', int(126 * S), int((GROUND + 6) * S) - 230, px=5)
        if i == L_MORE:
            n_h = min(5, int(1 + (t - SEG[L_MORE][0]) * 3))
            heart(F, 92, 98); heart(F, 92 - 9, 98)
            for k in range(n_h): heart(F, 144 - 18 + k * 9, 92 - (k % 2) * 4)
            if t >= cs(L_MORE, 1) - 0.05: ctag(F, 'LIKED MORE', 380, px=7)
    elif i in (L_WHY, L_MUG):                                    # perfect wrap -> sky-high expectations -> just a mug
        floor(F)
        opened = i == L_MUG and t >= cs(L_MUG, 1) - 0.1
        if not opened: draw_gift(F, 60, 'neat', bob=abs(math.sin(t * 3)))
        else:
            k = ramp(t, cs(L_MUG, 1) - 0.1, 0.3); draw_mug(F, 60, GROUND + 1 - 10 * math.sin(math.pi * min(1, k)))
            for j in range(6): put(F, 50 + j * 4, GROUND - 4 - (t - cs(L_MUG, 1)) * 30 * (j % 3 + 1) % 20, hexc('#3a8aff'))
        if t >= cs(L_WHY, 2) - 0.05 or i == L_MUG:
            thought(F, 56, 58, 62, 30)
            bk.pixel_text(F, 'AMAZING!', int((56 - 27) * S) + 8, int(68 * S), px=6, colr=(230, 150, 20)); sparkles(F, 56, 73, 36, 18, t, n=8)
        exp_v = ramp(t, cs(L_WHY, 2), 1.0)
        meter(F, 118, 'EXPECTED', exp_v, '#ffcc4a')
        if i == L_MUG:
            meter(F, 158, 'GOT', 0.3 * ramp(t, cs(L_MUG, 1), 0.5), '#e8303a')
            if t >= cs(L_MUG, 2) - 0.05: ctag(F, 'DISAPPOINTED', 200, px=7)
        else: meter(F, 158, 'GOT', 0, '#e8303a')
    elif i == L_MESSY:                                           # messy wrap -> low expectations -> better!
        floor(F)
        opened = t >= cs(L_MESSY, 2) - 0.1
        if not opened: draw_gift(F, 60, 'messy')
        else:
            k = ramp(t, cs(L_MESSY, 2) - 0.1, 0.3); draw_mug(F, 60, GROUND + 1 - 10 * math.sin(math.pi * min(1, k)))
            paper_bits(F, 60, 140, t, n=10, spread=24)
        meter(F, 118, 'EXPECTED', 0.15 * ramp(t, cs(L_MESSY, 1), 0.6), '#ffcc4a')
        meter(F, 158, 'GOT', 0.3 * ramp(t, cs(L_MESSY, 3), 0.5), '#5ae07a')
        if t >= cs(L_MESSY, 3) - 0.05: ctag(F, 'BETTER!', 200, px=9)
    elif i == L_SANTA:                                           # what if Santa found out?
        floor(F); draw_santa(F, 46, bob=abs(math.sin(t * 3)) * 1.2)
        c, M = spr('scrl', ch.scroll); pv.blit_hr(F, c, M, 70, GROUND - 46, 1)
        bk.pixel_text(F, 'STUDY', int(72.5 * S), int((GROUND - 38) * S), px=3, colr=(30, 36, 60))
        promo = t >= cs(L_SANTA, 2) - 0.05
        draw_elf(F, 140, 'tinsel', cap=promo, mood='proud' if promo else 'shock', arms='up' if promo else 'down', bob=abs(math.sin(t * 5)) * 2 if promo else 0)
        if not promo: ctag(F, 'WHAT IF', 300, px=8)
        else: ctag(F, 'HEAD WRAPPER', 300, px=7); sparkles(F, 140, 104, 24, 10, t, n=8)
    elif i == L_NOBODY:                                          # re-hook
        floor(F); draw_elf(F, 90, 'tinsel', cap=True, mood='shock')
        k = ramp(t, SEG[L_NOBODY][0], 0.4); F *= 1 - 0.55 * k
        glow(F, 90, 110, 40, '#ffcc4a', 0.25 * k)
        ctag(F, 'NOBODY TELLS YOU', 300, px=7); bk.pixel_text(F, '!', 680, 520, px=12, colr=(255, 200, 58))
    elif i == L_FRIENDS:                                         # only with friends and family
        floor(F); draw_elf(F, 38, 'tinsel', mood='happy', arms='hold'); draw_gift(F, 82, 'messy')
        draw_deer(F, 142, nose='red', flip=True)
        for k in range(4):
            ph = (t * 0.8 + k / 4) % 1; heart(F, 132 + k * 6, 86 - ph * 26, 1 - ph)
        if t >= cs(L_FRIENDS, 1) - 0.05: ctag(F, 'FRIENDS + FAMILY', 300, px=7)
    elif i == L_BOSS:                                            # boss: wrap it perfect
        floor(F); draw_santa(F, 142); bk.label(F, 'BOSS', 900, 520, int(142 * S), int((GROUND - 54) * S), px=6)
        neat = t >= cs(L_BOSS, 2) - 0.05
        if not neat:
            draw_elf(F, 38, 'tinsel', mood='shock'); draw_gift(F, 88, 'messy')
            bk.pixel_text(F, '?', int(150 * S), int((GROUND - 70) * S), px=10, colr=(255, 255, 255))
        else:
            draw_elf(F, 38, 'holly', mood='proud', arms='hold'); draw_gift(F, 88, 'neat')
            sparkles(F, 88, 132, 18, 8, t, n=6)
            for k in range(3):
                ph = (t * 0.8 + k / 3) % 1; heart(F, 136 + k * 7, 92 - ph * 24, 1 - ph)
            if t >= cs(L_BOSS, 4) - 0.05: ctag(F, 'NEAT = YOU CARE', 300, px=7)
    elif i == L_BOTH:                                            # everybody wins
        floor(F); fam = t >= cs(L_BOTH, 1) - 0.05; boss = t >= cs(L_BOTH, 3) - 0.05; win = t >= cs(L_BOTH, 4) - 0.05
        draw_elf(F, 50, 'tinsel', cap=True, mood='proud', arms='up' if win else 'down', bob=abs(math.sin(t * 5)) * 3 if win else 0)
        draw_elf(F, 130, 'holly', mood='proud', arms='up' if win else 'down', bob=abs(math.sin(t * 5 + 1)) * 3 if win else 0)
        if fam: bk.pixel_text(F, 'FAMILY', int(50 * S) - 105, int((GROUND - 64) * S), px=6, colr=(90, 224, 122))
        if boss: bk.pixel_text(F, 'BOSS', int(130 * S) - 70, int((GROUND - 64) * S), px=6, colr=(255, 200, 58))
        if win: ctag(F, 'EVERYBODY WINS', 280, px=7); sparkles(F, 90, 96, 70, 14, t, n=14)
    else:                                                        # CTA: tag the worst wrapper + subscribe or naughty list
        floor(F)
        sl = ramp(t, SEG[L_CTA][0], 0.6)
        draw_santa(F, lerp(-30, 44, sl), bob=abs(math.sin(t * 3)) * 1.2)
        draw_elf(F, 146, 'tinsel', mood='happy'); draw_gift(F, 112, 'messy')
        if t < cs(L_CTA, 2) - 0.05:
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(720 * pop), int(200 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 250
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    tx1 = 'TAG THE WORST'; tx2 = 'WRAPPER YOU KNOW'
                    bk.pixel_text(F, tx1, X + (bw - (len(tx1) * 42 - 7)) // 2, Y + 40, px=7, colr=(20, 24, 40))
                    bk.pixel_text(F, tx2, X + (bw - (len(tx2) * 42 - 7)) // 2, Y + 115, px=7, colr=(200, 40, 60))
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
            draw_cursor(F, int(lerp(WF * 0.8, WF * 0.6, ramp(t, cs(L_CTA, 2), 0.35))), Y + bh - 30)
            if pressed:
                for k in range(8): rv.sparkle(F, 90 + 50 * math.cos(TAU * k / 8), 62 + 18 * math.sin(TAU * k / 8), 1 - ramp(t, press, 0.8))
            if t >= cs(L_CTA, 3) - 0.05:
                c, M = sv.spr('scroll', ch.scroll); sx = lerp(44, 60, ramp(t, cs(L_CTA, 3), 0.3))
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
SHOUTS = [SEG[L_GENIUS][0], cs(L_MORE, 1), SEG[L_NOBODY][0]]
NO_SNOW = (L_MESS,)
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    if i not in NO_SNOW: rv.snow(F, t)
    if i >= 2 and 0 <= t - SEG[i][0] < 0.12 and i not in (L_MORE, L_MUG):
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
