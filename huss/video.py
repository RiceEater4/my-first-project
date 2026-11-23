"""'Huss Huss Huss' - FLIP formula, roast hook, Jett narration sped up 1.15x.
YOU = green elf dribbling a basketball alone under a streetlight while the town parties in a glowing house.
Study scene: violin elves (the best vs the future music teacher) with hour counters. Open-loop corner subscribe.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study')); sys.path.insert(0, os.path.join(ROOT_, 'mom_finds'))
import importlib.util
_s = importlib.util.spec_from_file_location('lsv', os.path.join(ROOT_, 'late_school', 'video.py'))
lv = importlib.util.module_from_spec(_s); _s.loader.exec_module(lv)
ys, fm, b1, sv, rv, pv, bk, ch = lv.ys, lv.fm, lv.b1, lv.sv, lv.rv, lv.pv, lv.bk, lv.ch
import ui, props, scenery

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
glow, ctag, big_num, disc = sv.glow, sv.ctag, sv.big_num, sv.disc
draw_santa, shadow, heart, meter = b1.draw_santa, b1.shadow, b1.heart, b1.meter
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
(L_HOOK, L_HUSS, L_FLIP, L_HOW, L_REEL, L_SUB, L_STUDY, L_ALONE, L_NIGHTS, L_NOBODY, L_GO, L_CTA) = range(12)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))
def after(t, line, k): return t >= cs(line, k) - 0.05
def you(F, cx, mood='happy', **kw): return lv.you(F, cx, mood=mood, **kw)
def elf(F, cx, who='holly', **kw): return lv.draw_elf(F, cx, who, **kw)
def strike(F, y=294):
    for k in range(-170, 170, 2): F[int(y + k * 0.1):int(y + 8 + k * 0.1), 540 + k:542 + k] = hexc('#e8303a')

# ---------- props ----------
def ball(F, cx, cy):
    disc(F, cx, cy, 4.2, '#ff8a2a', ring='#b8520e', ringw=1)
    for k in range(-4, 5): put(F, cx + k * 0.9, cy, hexc('#6a2a08')); put(F, cx, cy + k * 0.9, hexc('#6a2a08'))
def dribble(F, cx, t, rate=1.6, side=1):
    """ball bouncing between the elf's hand and the floor; returns True on the frame window of a floor hit"""
    ph = (t * rate) % 1; h_ = abs(math.cos(math.pi * ph))
    bx, by = cx + side * 15, GROUND - 4 - 20 * h_
    shadow(F, bx, GROUND + 1, 9 * (0.6 + 0.4 * (1 - h_))); ball(F, bx, by)
def puff(F, x, y, t, t0, side=1):
    a = t - t0
    if not 0 <= a < 0.7: return
    for k in range(3):
        r = 1.5 + a * 7 + k; cx_, cy_ = x + side * (a * 16 + k * 3), y - a * 6 - k
        yy, xx = np.mgrid[int(cy_ - r) - 1:int(cy_ + r) + 2, int(cx_ - r) - 1:int(cx_ + r) + 2]
        for Y, X in zip(*np.nonzero(np.hypot(xx - cx_, yy - cy_) <= r)):
            put(F, xx[Y, X], yy[Y, X], hexc('#f4f8ff'), 0.55 * (1 - a / 0.7))
def streetlight(F, x):
    glow(F, x + 8, 80, 46, '#ffd86a', 0.22)
    yy, xx = np.mgrid[0:H, 0:W]; cone = (yy > 82) & (yy < GROUND + 2) & (np.abs(xx - (x + 8)) < (yy - 80) * 0.45)
    m = cone & (BAY[yy % 4, xx % 4] < 0.25); A = np.repeat(np.repeat(m.astype(np.float32), S, 0), S, 1)[..., None] * 0.35
    F[:] = F * (1 - A) + hexc('#ffe9a0') * A
    for yv in range(74, GROUND + 1): put(F, x, yv, hexc('#3a4664')); put(F, x + 1, yv, hexc('#2a3450'))
    for xv in range(x, x + 10): put(F, xv, 74, hexc('#3a4664'))
    for xv in range(x + 5, x + 12): put(F, xv, 76, hexc('#ffe27a')); put(F, xv, 77, hexc('#fff6c0'))
_c = {}
def big_house():
    if 'bh' not in _c:
        c, M = ch.house(lit=True); _c['bh'] = (np.repeat(np.repeat(c, 2, 0), 2, 1), np.repeat(np.repeat(M, 2, 0), 2, 1))
    return _c['bh']
PARTY = ['#ff4fa0', '#5ae07a', '#5ea6f2', '#ffcc4a', '#c86aff']
def note(F, x, y, a, colr):
    disc(F, x, y, 1.6, colr); [put(F, x + 1.4, y - k, hexc(colr), a) for k in range(6)]; put(F, x + 2.4, y - 5, hexc(colr), a)
def party_house(F, cx, t, flash=False):
    c, M = big_house(); h_, w_ = M.shape; x0, y0 = cx - w_ / 2, GROUND + 1 - h_
    glow(F, cx, y0 + 50, 60, PARTY[int(t * 4) % 5], 0.18)
    shadow(F, cx, GROUND + 1, w_ * 0.9); props._blit(F, c, M, x0, y0)
    for k, wx in enumerate((9, 26)):                                       # disco windows + dancing silhouettes
        col = hexc('#ffffff') if flash else hexc(PARTY[(int(t * 5) + k * 2) % 5])
        X0, Y0 = int(x0 + wx * 2), int(y0 + 21 * 2)
        for yy in range(Y0 + 1, Y0 + 13):
            for xx in range(X0 + 1, X0 + 13):
                if abs(xx - (X0 + 6.5)) > 0.8 and abs(yy - (Y0 + 6.5)) > 0.8: put(F, xx, yy, col, 0.75)
        hx = X0 + 6.5 + 2.5 * math.sin(t * 9 + k * 2); hy = Y0 + 8 + abs(math.sin(t * 9 + k)) * -2
        for dy in range(-2, 5):
            for dx in range(-1, 2): put(F, hx + dx, hy + dy, hexc('#1b1428'), 0.9)
        disc(F, hx, hy - 3.5, 1.6, '#1b1428')
    for k in range(4):                                                     # music notes floating out of the chimney side
        ph = (t * 0.6 + k / 4) % 1
        note(F, cx - 30 + k * 18 + 4 * math.sin(t * 3 + k), y0 + 8 - ph * 30, 1 - ph, PARTY[k])
def night(F, k=1.0):
    F *= 1 - 0.35 * k
    lv.moon(F, 150, 30)
def town_scene(F, t, cx_you=40, mood='happy', huss_t=None):
    night(F); party_house(F, 128, t); streetlight(F, 14)
    you(F, cx_you, mood=mood, bob=abs(math.sin(t * 3.2 * math.pi)) * 1.2)
    dribble(F, cx_you, t)
    if huss_t is not None: puff(F, cx_you + 6, GROUND - 40, t, huss_t)
def counter(F, label, n, y, px=8, colr=(255, 255, 255)): big_num(F, f'{label}{n:,}', y, px=px, colr=colr)
def violin(F, x, y):
    """bigger violin tucked under the chin: two-lobed body, f-holes, neck + scroll, and a bow across it"""
    for k in range(-7, 8):
        for j in range(-5, 6):
            w_ = 4.6 if abs(k) > 2 else 3.6
            if (k / 7.2) ** 2 + (j / w_) ** 2 <= 1:
                put(F, x + k * 0.8 + j * 0.6, y + j * 0.8 - k * 0.6, hexc('#c8642a') if j < 2 else hexc('#a04a1e'))
    for k in (-1.5, 1.5): put(F, x + k, y - 0.5, hexc('#3a2418')); put(F, x + k, y + 0.5, hexc('#3a2418'))
    for k in range(5, 15): put(F, x + k * 0.8, y - k * 0.6, hexc('#2a1a10'))
    disc(F, x + 12.5, y - 9.5, 1.4, '#3a2418')
    for k in range(-10, 11): put(F, x - 2 + k, y + 4 - k * 0.55, hexc('#f0e4c0'))
def brain(F, cx, cy, t, k):
    if k <= 0: return
    glow(F, cx, cy, 22, '#ff9ad0', 0.3 * k)
    disc(F, cx - 4, cy, 7, '#ffb0d8', ring='#d86aa8'); disc(F, cx + 4, cy, 7, '#ffb0d8', ring='#d86aa8')
    nodes = [(cx - 7, cy - 3), (cx - 2, cy + 3), (cx + 3, cy - 4), (cx + 7, cy + 2), (cx, cy - 1)]
    for a_ in range(len(nodes)):
        for b_ in range(a_ + 1, len(nodes)):
            if (a_ + b_ + int(t * 4)) % 3 == 0 and k > 0.3:
                (x1, y1), (x2, y2) = nodes[a_], nodes[b_]
                for f in np.linspace(0, 1, 12): put(F, lerp(x1, x2, f), lerp(y1, y2, f), hexc('#fff6a0'), 0.9 * k)
    for x_, y_ in nodes: put(F, x_, y_, hexc('#ffffff'))
def two_bars(F, t, t_easy, t_hard):
    meter(F, 56, 'EASY', 0.08, '#c4ccd8', y_top=70, h_=60, w_=18)
    meter(F, 124, 'HARD', 0.08 + 0.87 * ramp(t, t_hard, 1.0) if t >= t_hard else 0.08, '#5ae07a', y_top=70, h_=60, w_=18)

def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
HUSS_T = []
def scene(F, t):
    i = seg_of(t)
    if i == L_HOOK:                                              # everybody parties... except you, no friends
        town_scene(F, t, mood='happy' if not after(t, L_HOOK, 2) else 'sad')
        if not after(t, L_HOOK, 2): ctag(F, 'PARTY TONIGHT', 230, px=7)
        elif not after(t, L_HOOK, 4): ui.callout(F, 'YOU', 8, 70, 40, GROUND - 52, px=6, accent='#5ae07a')
        else: big_num(F, 'FRIENDS: 0', 220, px=10, colr=(255, 90, 100))
    elif i == L_HUSS:                                            # HUSS! HUSS! HUUUSSS! - breath puffs + big text
        k = sum(1 for j in range(3) if after(t, L_HUSS, j)) - 1; t0 = cs(L_HUSS, max(0, k))
        town_scene(F, t, mood='proud', huss_t=t0)
        txt = 'HUUUSSS!' if k >= 2 else 'HUSS!'; px = 13 if k >= 2 else 12
        if t - t0 < 0.9: big_num(F, txt, 200 + 40 * k, px=px, colr=(255, 226, 122))
    elif i == L_FLIP:                                            # not a loser -> what the best did -> DELIBERATE PRACTICE
        if not after(t, L_FLIP, 2):
            night(F); streetlight(F, 60); you(F, 74, mood='sad'); dribble(F, 74, t, rate=1.0)
            ctag(F, 'LOSER?', 270, px=10)
            if after(t, L_FLIP, 1) and t >= cs(L_FLIP, 1) + 0.35: strike(F, 300)
        elif not after(t, L_FLIP, 5):
            night(F); streetlight(F, 60); you(F, 74, mood='proud', bob=abs(math.sin(t * 6)) * 2); dribble(F, 74, t)
            b1.sparkles(F, 80, 110, 34, 30, t); ctag(F, 'WHAT THE BEST DID', 270, px=7)
        else:
            night(F); you(F, 90, mood='proud'); dribble(F, 90, t)
            k = ramp(t, cs(L_FLIP, 5), 0.4); F *= 1 - 0.45 * k; glow(F, 90, 60, 60, '#ffcc4a', 0.3 * k)
            ctag(F, "IT'S CALLED", 220, px=7)
            if after(t, L_FLIP, 6):
                big_num(F, 'DELIBERATE', 320, px=12, colr=(255, 200, 58)); big_num(F, 'PRACTICE', 420, px=12, colr=(255, 200, 58))
    elif i == L_HOW:                                             # not for fun; the stuff you're BAD at; alone; reps; brain rewires
        night(F); streetlight(F, 30)
        if not after(t, L_HOW, 1):
            you(F, 60, mood='happy'); dribble(F, 60, t); ctag(F, 'FOR FUN', 270, px=10)
            if t >= cs(L_HOW, 0) + 0.5: strike(F, 300)
        elif not after(t, L_HOW, 3):
            you(F, 60, mood='angry'); dribble(F, 60, t, rate=2.2)
            ui.callout(F, 'WEAK SPOT', 100, 70, 76, GROUND - 22, px=5, accent='#ff5a64')
        elif not after(t, L_HOW, 5):
            you(F, 60, mood='proud'); dribble(F, 60, t, rate=2.2)
            if not after(t, L_HOW, 4): ctag(F, 'ALONE', 270, px=10)
            else: counter(F, 'REPS: ', int(1 + 999 * ramp(t, cs(L_HOW, 4), 1.4)), 240, px=9, colr=(255, 226, 122))
        else:
            you(F, 60, mood='proud'); dribble(F, 60, t, rate=2.2)
            k = ramp(t, cs(L_HOW, 5), 0.5); brain(F, 60, 62, t, k)
            meter(F, 140, 'SKILL', 0.15 + 0.8 * ramp(t, cs(L_HOW, 6), 1.0), '#5ae07a', y_top=70, h_=60, w_=18)
            if after(t, L_HOW, 6): ctag(F, 'REWIRED', 230, px=9)
    elif i == L_REEL:                                            # they make memories; you make a highlight reel
        night(F)
        if not after(t, L_REEL, 1):
            party_house(F, 90, t, flash=(t * 3) % 1 < 0.12); ctag(F, 'MEMORIES', 240, px=10)
        else:
            streetlight(F, 30); you(F, 90, mood='proud', arms='up', bob=abs(math.sin(t * 6)) * 3)
            b1.sparkles(F, 90, 110, 36, 32, t); ctag(F, 'HIGHLIGHT REEL', 240, px=8)
            for k in range(3):
                ph = (t * 0.8 + k / 3) % 1; rv.sparkle(F, 60 + k * 30, 70 - ph * 20, 1 - ph)
    elif i == L_SUB:                                             # grinding alone? SUBSCRIBE! HUSS HUSS - corner button
        night(F); streetlight(F, 30); you(F, 70, mood='proud'); dribble(F, 70, t, rate=2.0)
        if after(t, L_SUB, 1): lv.corner_sub(F, t, cs(L_SUB, 1) - 0.05, cs(L_SUB, 1) + 0.3)
        if after(t, L_SUB, 2) and not after(t, L_SUB, 3):
            puff(F, 76, GROUND - 40, t, cs(L_SUB, 2)); big_num(F, 'HUSS! HUSS!', 520, px=10, colr=(255, 226, 122))
        if after(t, L_SUB, 3): ctag(F, 'THE PROOF', 520, px=9)
    elif i == L_STUDY:                                           # 1993 Berlin violinists: best ~10,000 h vs teachers ~half
        if not after(t, L_STUDY, 1):
            big_num(F, '1993', 300, px=16, colr=(255, 200, 58))
        elif not after(t, L_STUDY, 5):
            elf(F, 90, 'holly', arms='hold'); violin(F, 100, GROUND - 25)
            if after(t, L_STUDY, 2): ctag(F, 'VIOLIN STUDENTS', 230, px=7)
            if after(t, L_STUDY, 4): ui.callout(F, 'BERLIN', 124, 70, 104, GROUND - 44, px=6, accent='#ffcc4a')
        else:
            best = after(t, L_STUDY, 9)
            elf(F, 50, 'holly', arms='hold', bob=abs(math.sin(t * 5)) * 1.5); violin(F, 60, GROUND - 25)
            n1 = int(10000 * ramp(t, cs(L_STUDY, 6), max(0.5, cs(L_STUDY, 9) - cs(L_STUDY, 6) - 0.2)))
            props.text_center(F, f'{n1:,} H', 50, 60, px=6, colr=(90, 224, 122)); props.text_center(F, 'THE BEST', 50, 50, px=5, colr=(255, 226, 122))
            if best:
                elf(F, 130, 'tinsel', arms='hold', mood='sad', outfit='#7a4ac8', outfit_d='#5a2ea0', hat='#7a4ac8'); violin(F, 140, GROUND - 25)
                n2 = int(5000 * ramp(t, cs(L_STUDY, 9), 0.9))
                props.text_center(F, f'{n2:,} H', 130, 60, px=6, colr=(255, 120, 120))
                if after(t, L_STUDY, 11): props.text_center(F, 'TEACHER', 130, 50, px=5, colr=(200, 215, 255))
                if after(t, L_STUDY, 9) and t >= cs(L_STUDY, 9) + 0.4: ctag(F, '2X MORE PRACTICE', 960, px=7)
    elif i == L_ALONE:                                           # what helped the most? PRACTICING ALONE
        if not after(t, L_ALONE, 3):
            elf(F, 50, 'holly', arms='hold'); violin(F, 60, GROUND - 25); elf(F, 130, 'tinsel', outfit='#7a4ac8', outfit_d='#5a2ea0', hat='#7a4ac8'); ctag(F, 'THE SECRET?', 260, px=9)
        else:
            k = ramp(t, cs(L_ALONE, 3), 0.4); F *= 1 - 0.55 * k; glow(F, 90, 110, 40, '#ffe27a', 0.35 * k)
            elf(F, 90, 'holly', arms='hold', bob=abs(math.sin(t * 5)) * 1.5); violin(F, 100, GROUND - 25)
            big_num(F, 'PRACTICING', 250, px=11, colr=(255, 255, 255)); big_num(F, 'ALONE', 340, px=13, colr=(255, 200, 58))
    elif i == L_NIGHTS:                                          # every night you stayed in -> hours they never get back
        night(F); party_house(F, 128, t); streetlight(F, 14); you(F, 40, mood='proud'); dribble(F, 40, t, rate=2.0)
        if not after(t, L_NIGHTS, 3):
            counter(F, 'NIGHTS: ', int(1 + 364 * ramp(t, SEG[L_NIGHTS][0], 2.2)), 220, px=9, colr=(200, 215, 255))
        else:
            counter(F, 'YOUR HOURS: ', int(1500 * ramp(t, cs(L_NIGHTS, 3), 1.0)), 220, px=8, colr=(90, 224, 122))
            if after(t, L_NIGHTS, 4): ctag(F, 'THEY NEVER GET BACK', 960, px=6)
    elif i == L_NOBODY:                                          # twist: only counts if it's HARD; easy stuff does nothing
        if not after(t, L_NOBODY, 2):
            night(F); you(F, 90, mood='shock'); k = ramp(t, SEG[L_NOBODY][0], 0.4); F *= 1 - 0.5 * k
            glow(F, 90, 110, 46, '#ffcc4a', 0.25 * k); ctag(F, 'NOBODY TELLS YOU', 300, px=7)
        else:
            night(F); you(F, 90, mood='angry' if after(t, L_NOBODY, 2) else 'happy')
            if not after(t, L_NOBODY, 4): ctag(F, "ONLY IF IT'S HARD", 260, px=7)
            else:
                two_bars(F, t, cs(L_NOBODY, 4), cs(L_NOBODY, 4) + 0.2)
                ctag(F, 'EASY = NOTHING', 260, px=8)
    elif i == L_GO:                                              # next time they go out: pick the thing you suck at. go. huss.
        night(F)
        if not after(t, L_GO, 2):
            party_house(F, 128, t); streetlight(F, 14); you(F, 40, mood='happy'); dribble(F, 40, t, rate=1.2)
            ctag(F, 'NEXT PARTY...', 240, px=8)
        elif not after(t, L_GO, 4):
            streetlight(F, 30); you(F, 70, mood='angry'); dribble(F, 70, t, rate=2.0)
            ui.callout(F, 'YOUR WEAK SPOT', 100, 70, 86, GROUND - 22, px=5, accent='#ff5a64')
        else:
            streetlight(F, 30); you(F, 70, mood='proud', bob=abs(math.sin(t * 6)) * 2); dribble(F, 70, t, rate=2.4)
            if not after(t, L_GO, 5): big_num(F, 'GO.', 260, px=16, colr=(255, 200, 58))
            else:
                k = sum(1 for j in range(3) if t >= cs(L_GO, 5) + j * 0.55)
                puff(F, 76, GROUND - 40, t, cs(L_GO, 5) + (k - 1) * 0.55)
                props.text_center(F, ' '.join(['HUSS.'] * k), 90, 44, px=6, colr=(200, 215, 255))
    else:                                                        # CTA: send this to the friend who never comes out + naughty list
        you(F, 150, mood='happy'); dribble(F, 150, t, rate=1.4, side=-1)
        if not after(t, L_CTA, 3):
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(820 * pop), int(200 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 250
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    for tx, yy_, col in (('SEND THIS TO', 40, (20, 24, 40)), ('YOUR HERMIT FRIEND', 115, (200, 40, 60))):
                        px = 7 if len(tx) < 14 else 6
                        bk.pixel_text(F, tx, X + (bw - (len(tx) * 6 * px - px)) // 2, Y + yy_, px=px, colr=col)
        else:
            sl = ramp(t, cs(L_CTA, 3) - 0.05, 0.5)
            draw_santa(F, lerp(-30, 40, sl), bob=abs(math.sin(t * 3)) * 1.2)
            if sl > 0.9: scenery.naughty_list(F, 86, GROUND + 1, shadow_fn=shadow); ctag(F, 'NAUGHTY LIST', 300, px=8)

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
SHOUTS = [cs(L_HUSS, 0), cs(L_HUSS, 1), cs(L_HUSS, 2), cs(L_SUB, 1), SEG[L_NOBODY][0]]
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    rv.snow(F, t)
    if i >= 2 and 0 <= t - SEG[i][0] < 0.12 and i not in (L_HUSS, L_SUB, L_ALONE):
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
                          '-i', '-', '-i', wav, '-c:a', 'aac', '-b:a', '256k', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(int(round(END * FPS))):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 600 == 0: print('frame', f, flush=True)
    p.stdin.close(); p.wait(); print('done', out)
