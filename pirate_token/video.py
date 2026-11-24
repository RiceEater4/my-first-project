"""'Why You Can't Find The Pirate Token' - FLIP formula, 5 screams, ~40 s, Jett narration sped up 1.1x.
YOU = green elf digging snow chests for a gold token; a pixel pigeon mirrors you; a Skinner box with a peck
counter; a slot machine title; a mystery-box dopamine meter; the token spinning with its dollar value.
Our own art only (no Fortnite characters/map/items).
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess, re
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study')); sys.path.insert(0, os.path.join(ROOT_, 'mom_finds'))
import importlib.util
_s = importlib.util.spec_from_file_location('hussv', os.path.join(ROOT_, 'huss', 'video.py'))
hv = importlib.util.module_from_spec(_s); _s.loader.exec_module(hv)
lv, ys, fm, b1, sv, rv, pv, bk, ch = hv.lv, hv.ys, hv.fm, hv.b1, hv.sv, hv.rv, hv.pv, hv.bk, hv.ch
import ui, props, scenery

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
glow, ctag, big_num, disc = sv.glow, sv.ctag, sv.big_num, sv.disc
draw_santa, draw_prof, shadow, meter = b1.draw_santa, b1.draw_prof, b1.shadow, b1.meter
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
WORDS = json.load(open(os.path.join(HERE, 'words.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
def word_t(word, after_t):
    """start time of the first heard word containing `word` after `after_t` (for screams)"""
    for a, b, w in WORDS:
        if a >= after_t - 0.1 and word in re.sub(r'[^a-z]', '', w.lower()): return a
    return None
(L_HOOK, L_FLIP, L_NAME, L_PECK, L_SUB, L_YOU, L_MAYBE, L_TOKEN, L_STOP, L_CTA) = range(10)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))
def after(t, line, k): return t >= cs(line, k) - 0.05
you = hv.you
# ---------- BIG characters: the world layer (characters + props + shadows) is zoomed 1.5x around the ground
# centre, so 6-px pixels become crisp 9-px pixels. Text / meters / buttons are DEFERRED and drawn afterwards at
# normal size (shifted up a bit so they sit above the bigger characters). No platform: invisible floor + shadows.
Z, AX, AY = 1.5, 540, (GROUND + 1) * S
DROP = 300                                                                    # whole scene + captions moved down to fill the screen
_YX = np.clip(np.floor(AY + (np.arange(HF) - AY - DROP) / Z), 0, HF - 1).astype(int)
_XX = np.clip(np.floor(AX + (np.arange(WF) - AX) / Z), 0, WF - 1).astype(int)
def zoom_world(F):
    m = np.any(np.abs(F - rv.BG) > 1e-4, -1)
    Fz, mz = F[_YX][:, _XX], m[_YX][:, _XX]
    out = rv.BG.copy(); out[mz] = Fz[mz]; return out
def wx(x): return 90 + (x - 90) * Z                                            # world grid coords -> zoomed grid coords
def wy(y): return (GROUND + 1) + (y - (GROUND + 1)) * Z + DROP / S
def ty(y): return y + 200 if y < 700 else y + DROP                              # screen-y of text: top tags above the characters, low tags under the feet
UI = []
def ctag(F, text, y, px=6): UI.append(lambda F: sv.ctag(F, text, ty(y), px=px))
def big_num(F, text, y, px=12, colr=(255, 255, 255)): UI.append(lambda F: sv.big_num(F, text, ty(y), px=px, colr=colr))
def meter(F, x, label, val, colr, **kw): UI.append(lambda F: b1.meter(F, x, label, val, colr, **{**kw, 'y_top': kw.get('y_top', 62) + 60}))
def strike(F, y=294): UI.append(lambda F: hv.strike(F, ty(y)))
def ttext(F, text, x, y, px=5, colr=(225, 235, 255), world=False):
    X, Y = (wx(x), wy(y)) if world else (x, y)
    UI.append(lambda F: props.text_center(F, text, X, Y, px=px, colr=colr))
def callout(F, text, tx_, ty_, ax, ay, **kw): UI.append(lambda F: ui.callout(F, text, tx_, ty_ + 34, wx(ax), wy(ay), **kw))
def corner_sub(F, t, t0, press): UI.append(lambda F: lv.corner_sub(F, t, t0, press))
def dim(F, k): UI.append(lambda F: F.__imul__(1 - k))
SCREAMS = {}
def screams():
    if not SCREAMS:
        SCREAMS['bum'] = min(x for x in (word_t(w, cs(L_HOOK, 3)) for w in ('boom', 'bum', 'buu')) if x is not None)
        SCREAMS['pigeon'] = word_t('pigeon', cs(L_FLIP, 2)); SCREAMS['pecking'] = word_t('peck', cs(L_PECK, 1))
        SCREAMS['sub'] = word_t('subscrib', cs(L_SUB, 1)); SCREAMS['nothing'] = word_t('nothing', cs(L_SUB, 6))
    return SCREAMS

# ---------- props ----------
_C = {}
def spr(key, fn):
    if key not in _C: _C[key] = fn()
    return _C[key]
def pigeon_sprite(peck=False):
    W_, H_ = 28, 24; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = ch.Layers(W_, H_)
    hx, hy = (19, 9) if not peck else (22, 15)
    L.add((((xx - 3) / 4) ** 2 + ((yy - 13) / 2.2) ** 2 <= 1), hexc('#4a5262'))                        # tail
    for fx in (11, 15): L.add((np.abs(xx - fx) < 0.7) & (yy >= 18) & (yy < 22) | (np.abs(yy - 21.5) < 0.6) & (np.abs(xx - fx) < 2), hexc('#e87a8a'), outline=False)
    body = ((xx - 13) / 8.5) ** 2 + ((yy - 13.5) / 5.5) ** 2 <= 1
    L.add(body, lambda c, m: (c.__setitem__(m, hexc('#a8b0c0')), c.__setitem__(m & (yy > 15), hexc('#8a94a6')),
                              c.__setitem__(m & (((xx - 11) / 6) ** 2 + ((yy - 12.5) / 3) ** 2 <= 1), hexc('#7a8494')),
                              c.__setitem__(m & (np.abs(xx - 9) < 0.6) & (yy > 11) & (yy < 14), hexc('#3a4252')),
                              c.__setitem__(m & (np.abs(xx - 12) < 0.6) & (yy > 11) & (yy < 14), hexc('#3a4252'))))
    neck = ch.seg(xx, yy, 17, 12, hx, hy) <= 2.6
    L.add(neck, lambda c, m: (c.__setitem__(m, hexc('#5aa88a')), c.__setitem__(m & (xx + yy > hx + hy + 1), hexc('#8a5ab8'))))
    head = ((xx - hx) / 3.4) ** 2 + ((yy - hy) / 3.2) ** 2 <= 1
    L.add(head, lambda c, m: (c.__setitem__(m, hexc('#a8b0c0')), c.__setitem__(m & (np.hypot(xx - (hx + 0.8), yy - (hy - 0.6)) <= 1.2), hexc('#ff9a3a')),
                              c.__setitem__(m & (np.abs(xx - (hx + 0.8)) < 0.6) & (np.abs(yy - (hy - 0.6)) < 0.6), hexc('#1b1428'))))
    L.add((xx >= hx + 3) & (xx < hx + 6) & (np.abs(yy - (hy + 0.6)) < 0.9 - (xx - hx - 3) * 0.25), hexc('#e8c88a'))
    return L.out()
def pigeon(F, cx, t, peck_rate=0.0, flip=False, feet=GROUND + 1):
    peck = peck_rate > 0 and (t * peck_rate) % 1 < 0.35
    c, M = spr(('pg', peck), lambda: pigeon_sprite(peck))
    if flip: c, M = c[:, ::-1], M[:, ::-1]
    shadow(F, cx, feet, 22); pv.blit_hr(F, c, M, cx - 14, feet - 24, 1)
def chest(F, cx, open_=0.0, gold=False, feet=GROUND + 1):
    """wooden chest half-buried in snow; open_ 0..1 lifts the lid"""
    shadow(F, cx, feet, 34)
    x0, y0 = int(cx - 14), int(feet - 16)
    for y in range(y0, feet - 2):
        for x in range(x0, x0 + 28):
            edge = x in (x0, x0 + 27) or y in (y0, feet - 3)
            col = '#1b1428' if edge else ('#ffcc4a' if x in (x0 + 6, x0 + 21) else ('#8a5a36' if y < y0 + 7 else '#6a4226'))
            put(F, x, y, hexc(col))
    for x in range(x0 + 12, x0 + 16):
        for y in range(y0 + 5, y0 + 10): put(F, x, y, hexc('#ffcc4a') if (x, y) != (x0 + 13, y0 + 7) else hexc('#1b1428'))
    lift = 10 * open_
    for k in range(6):
        y = y0 - 6 + k - lift * (1 - k / 6) * 0.6
        for x in range(x0, x0 + 28): put(F, x, y, hexc('#1b1428') if k == 0 or x in (x0, x0 + 27) else hexc('#9a6a42'))
    if open_ > 0.3: glow(F, cx, y0 - 2, 20, '#ffe27a' if gold else '#cfe2f6', 0.35 * open_)
    for x in range(x0 - 6, x0 + 34):                                                       # snow drift
        hgt = 3 + 1.5 * math.sin(x * 0.7)
        for y in range(int(feet - hgt), feet + 1): put(F, x, y, hexc('#f4f8ff') if y < feet - 1 else hexc('#d8e4f4'))
def token(F, cx, cy, t, r=9, spin=True, a=1.0):
    sx = abs(math.cos(t * 3)) if spin else 1.0; rx = max(1.0, r * sx)
    glow(F, cx, cy, r * 3, '#ffd84a', 0.35 * a)
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / r) ** 2
            if d <= 1: put(F, x, y, hexc('#b8860e') if d > 0.72 else (hexc('#ffd84a') if d > 0.45 or (x - cx) * (y - cy) > 0 else hexc('#ffe98a')), a)
    if sx > 0.5:                                                                             # crossed swords mark
        for k in range(-4, 5): put(F, cx + k * sx * 0.9, cy + k * 0.9, hexc('#7a4a0a'), a); put(F, cx - k * sx * 0.9, cy + k * 0.9, hexc('#7a4a0a'), a)
def junk(F, kind, x, y):
    if kind == 'COAL': disc(F, x, y, 3.2, '#2a2a34', ring='#0b0b12', ringw=1)
    else:
        c, M = props.icon(kind); props._blit(F, c, M, x - 8, y - 7)
def fly_junk(F, t, t0, cx, kinds=('SOCK', 'COAL', 'SHOE')):
    for k, kind in enumerate(kinds):
        a = t - t0 - k * 0.18
        if 0 <= a < 1.2:
            x = cx + (k - 1) * 18 * a * 1.6; y = GROUND - 22 - 40 * a + 55 * a * a
            junk(F, kind, x, y)
def digger(F, cx, t, mood='angry', rate=3.0):
    """YOU digging frantically: body bobs, snow flies"""
    you(F, cx, mood=mood, arms='up' if (t * rate) % 1 < 0.5 else 'down', bob=abs(math.sin(t * rate * math.pi)) * 2)
    for k in range(5):
        ph = (t * 2.2 + k / 5) % 1
        put(F, cx + 16 + ph * 14 * (1 if k % 2 else -0.4), GROUND - 4 - 18 * ph + 22 * ph * ph, hexc('#f4f8ff'), 1 - ph)
def skinner_box(F, cx, t, pecks):
    x0, y0, w_, h_ = cx - 30, GROUND - 44, 60, 45
    for y in range(y0, y0 + h_):
        for x in range(x0, x0 + w_):
            edge = x in (x0, x0 + w_ - 1) or y in (y0, y0 + h_ - 1)
            if edge: put(F, x, y, hexc('#3a4664'))
            else: put(F, x, y, hexc('#cfe9ff'), 0.18)
    disc(F, x0 + w_ - 9, y0 + 14, 2.4, '#e8303a', ring='#7a0a10', ringw=1)               # pecking key
    for x in range(x0 + w_ - 14, x0 + w_ - 4): put(F, x, y0 + h_ - 5, hexc('#8a94a6'))    # empty food tray
    pigeon(F, cx + 6, t, peck_rate=4.0, feet=y0 + h_ - 1)
    ttext(F, f'PECKS: {pecks:,}', cx, y0 - 14, px=6, colr=(255, 226, 122), world=True)
def slot_machine(F, cx, cy, t, stop=False):
    x0, y0 = cx - 34, cy - 22
    F[int(y0 * S):int((y0 + 46) * S), int(x0 * S):int((x0 + 68) * S)] = hexc('#c8303a')
    for q in range(5):
        F[int(y0 * S) + q, int(x0 * S):int((x0 + 68) * S)] = NAVY; F[int((y0 + 46) * S) - 1 - q, int(x0 * S):int((x0 + 68) * S)] = NAVY
        F[int(y0 * S):int((y0 + 46) * S), int(x0 * S) + q] = NAVY; F[int(y0 * S):int((y0 + 46) * S), int((x0 + 68) * S) - 1 - q] = NAVY
    for k in range(3):
        wx = x0 + 6 + k * 20; F[int((y0 + 12) * S):int((y0 + 34) * S), int(wx * S):int((wx + 16) * S)] = hexc('#f4f6fb')
        sym = (int(t * 12) + k * 2) % 3 if not stop else 0
        if sym == 0: token(F, wx + 8, y0 + 23, 0, r=6, spin=False)
        elif sym == 1: junk(F, 'COAL', wx + 8, y0 + 23)
        else: junk(F, 'SOCK', wx + 8, y0 + 23)
    for y in range(int(y0 + 6), int(y0 + 30)): put(F, x0 + 70, y, hexc('#c4ccd8'))
    disc(F, x0 + 70, y0 + 6 + (10 if (t * 2) % 1 < 0.3 else 0), 3, '#e8303a', ring='#7a0a10', ringw=1)
def mystery_box(F, cx, t):
    b1.draw_gift(F, cx, 'neat', bob=abs(math.sin(t * 6)) * 2)
    ttext(F, '?', cx, GROUND - 46, px=12, colr=(255, 226, 122), world=True)
def snowfield(F):
    """thin snowy ground strip under the characters that fades out above the captions"""
    y0, y1 = (GROUND + 1) * S, (GROUND + 14) * S
    a = np.linspace(0.55, 0.0, y1 - y0)[:, None, None]
    F[y0:y1] = F[y0:y1] * (1 - a) + hexc('#cfe2f6') * a

def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t); sc = screams()
    if i == L_HOOK:                                              # digging chests -> STILL no token -> JOBLESS BUM
        if not after(t, L_HOOK, 3):
            op = (t * 1.3) % 1; chest(F, 120, open_=min(1, op * 3)); digger(F, 60, t)
            fly_junk(F, t, math.floor(t * 1.3) / 1.3, 120)
            if after(t, L_HOOK, 1): big_num(F, f'CHESTS: {int(1 + 480 * ramp(t, cs(L_HOOK, 1), 2.0))}', 220, px=9, colr=(255, 255, 255))
            if after(t, L_HOOK, 2): token(F, 118, 86, t, r=8)
        else:
            bum = t >= sc['bum'] - 0.05
            you(F, 60, mood='sad', bob=0); chest(F, 120, open_=1.0)
            big_num(F, 'JOBLESS', 220, px=13, colr=(255, 70, 80))
            if bum: big_num(F, 'BUM', 340, px=16, colr=(255, 70, 80))
    elif i == L_FLIP:                                            # not your skill -> trained you -> like a PIGEON
        if not after(t, L_FLIP, 1):
            you(F, 56, mood='sad'); ctag(F, 'SKILL ISSUE?', 260, px=9)
            if t >= cs(L_FLIP, 0) + 0.6: strike(F, 292)
        elif not after(t, L_FLIP, 2):
            you(F, 56, mood='shock'); ctag(F, 'TRAINED', 260, px=11)
            for k in range(3):
                ph = (t * 1.5 + k / 3) % 1; ttext(F, 'CLICK', 112 + k * 8, 100 - ph * 30, px=5, colr=(200, 215, 255), world=True)
        else:
            k = ramp(t, sc['pigeon'], 0.25)
            you(F, 56, mood='shock'); pigeon(F, 128, t, peck_rate=3.0)
            if t >= sc['pigeon'] - 0.05: big_num(F, 'PIGEON', 230, px=14, colr=(255, 226, 122)); glow(F, 128, GROUND - 12, 30, '#fff6a0', 0.3 * k)
    elif i == L_NAME:                                            # it's called a VARIABLE REWARD (slot machine)
        k = ramp(t, SEG[L_NAME][0], 0.3); dim(F, 0.35 * k)
        slot_machine(F, 90, 128, t, stop=False)
        ctag(F, "IT'S CALLED", 200, px=7)
        if after(t, L_NAME, 1): big_num(F, 'VARIABLE', 300, px=12, colr=(255, 200, 58)); big_num(F, 'REWARD', 400, px=12, colr=(255, 200, 58))
    elif i == L_PECK:                                            # you're not playing... you're PECKING (elf + pigeon in sync)
        chest(F, 90, open_=0.0)
        pk = (t * 3.0) % 1 < 0.35
        you(F, 54, mood='angry', bob=-2 if pk else 0); pigeon(F, 132, t, peck_rate=3.0, flip=True)
        if not after(t, L_PECK, 1): ctag(F, 'PLAYING?', 240, px=10)
        else: big_num(F, 'PECK PECK', 230, px=12, colr=(255, 226, 122))
    elif i == L_SUB:                                             # still hunting... SUBSCRIBE! 'cause a scientist... NOTHING
        if not after(t, L_SUB, 2):
            op = (t * 1.3) % 1; chest(F, 120, open_=min(1, op * 3)); digger(F, 60, t)
            if after(t, L_SUB, 1): corner_sub(F, t, sc['sub'] - 0.05, sc['sub'] + 0.3)
        else:
            draw_prof(F, 46);
            pecks = int(4800 * ramp(t, cs(L_SUB, 4), max(0.4, sc['nothing'] - cs(L_SUB, 4)))) if after(t, L_SUB, 4) else 0
            skinner_box(F, 112, t, pecks)
            if not after(t, L_SUB, 4): ctag(F, 'RANDOM FOOD', 230, px=8)
            if t >= sc['nothing'] - 0.05: big_num(F, 'FOOD: 0', 960, px=11, colr=(255, 70, 80))
    elif i == L_YOU:                                             # that's you. one more chest. one more drop.
        digger(F, 60, t, rate=4.0)
        if not after(t, L_YOU, 1):
            pigeon(F, 130, t, peck_rate=4.0, flip=True); callout(F, 'YOU', 14, 74, 60, GROUND - 40, px=6, accent='#5ae07a')
        else:
            t0 = cs(L_YOU, 1) if not after(t, L_YOU, 2) else cs(L_YOU, 2)
            chest(F, 122, open_=ramp(t, t0, 0.2)); fly_junk(F, t, t0 + 0.15, 122)
            ctag(F, 'ONE MORE CHEST' if not after(t, L_YOU, 2) else 'ONE MORE DROP', 240, px=8)
    elif i == L_MAYBE:                                           # the crazy part: biggest rush from MAYBE, not winning
        if not after(t, L_MAYBE, 2):
            you(F, 54, mood='shock'); k = ramp(t, SEG[L_MAYBE][0], 0.4); dim(F, 0.5 * k)
            glow(F, 54, 110, 46, '#ffcc4a', 0.25 * k); ctag(F, 'THE CRAZY PART', 300, px=7)
        else:
            you(F, 54, mood='happy' if not after(t, L_MAYBE, 5) else 'sad')
            top = GROUND + 1 - 53; hv.brain(F, 54, top - 10, t, 1.0)
            if not after(t, L_MAYBE, 5):
                mystery_box(F, 112, t); v = 0.85 + 0.1 * math.sin(t * 12)
                ctag(F, 'MAYBE = RUSH', 960, px=8)
            else:
                token(F, 112, GROUND - 22, t, r=10); v = 0.85 - 0.6 * ramp(t, cs(L_MAYBE, 5), 0.5)
                ctag(F, 'WIN = MEH', 960, px=8)
            meter(F, 160, 'DOPAMINE', v, '#ff4fa0', y_top=70, h_=60, w_=16)
    elif i == L_TOKEN:                                           # that token: $8,700 in skins; most will never find it
        dim(F, 0.25); token(F, 90, 118, t, r=18)
        if not after(t, L_TOKEN, 2): ctag(F, 'THAT TOKEN?', 240, px=10)
        elif not after(t, L_TOKEN, 4):
            big_num(F, '8,700', 230, px=16, colr=(90, 224, 122)); ctag(F, 'DOLLARS', 385, px=8) if not after(t, L_TOKEN, 3) else None
            if after(t, L_TOKEN, 3): ctag(F, 'DOLLARS IN SKINS', 385, px=8)
        else:
            ctag(F, 'MOST WILL', 165, px=9); big_num(F, 'NEVER', 310, px=15, colr=(255, 70, 80)); ctag(F, 'FIND IT', 480, px=9)
    elif i == L_STOP:                                            # that's exactly why you can't stop
        op = (t * 2.0) % 1; chest(F, 124, open_=min(1, op * 3)); digger(F, 60, t, rate=5.0)
        fly_junk(F, t, math.floor(t * 2.0) / 2.0, 124)
        ctag(F, "CAN'T STOP", 240, px=11)
    else:                                                        # CTA: send this to the grinder friend + naughty list
        you(F, 128, mood='happy')
        if not after(t, L_CTA, 3):
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25)
            def cta_box(F, pop=pop):
                bw, bh = int(820 * pop), int(200 * pop)
                if bw <= 20: return
                X, Y = (WF - bw) // 2, 480
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    for tx, yy_, col in (('SEND THIS TO', 40, (20, 24, 40)), ('YOUR GRINDER FRIEND', 115, (200, 40, 60))):
                        px = 7 if len(tx) < 14 else 6
                        bk.pixel_text(F, tx, X + (bw - (len(tx) * 6 * px - px)) // 2, Y + yy_, px=px, colr=col)
            UI.append(cta_box)
        else:
            sl = ramp(t, cs(L_CTA, 3) - 0.05, 0.5)
            draw_santa(F, lerp(-30, 48, sl), bob=abs(math.sin(t * 3)) * 1.2)
            if sl > 0.9: scenery.naughty_list(F, 86, GROUND + 1, shadow_fn=shadow); ctag(F, 'NAUGHTY LIST', 300, px=8)

CAP_Y = rv.CAP_Y + DROP
CAPS = [(c['t0'], c['t1'], rv.caption_sprite(c['text'], set(c['hl']))) for c in CAPJ]
def captions(F, t):
    for a, b, spr_ in CAPS:
        if a <= t < b:
            dy = int(6 * (1 - min(1.0, (t - a) / 0.06))); h_ = spr_.shape[0]; A = spr_[..., 3:4]
            F[CAP_Y + dy:CAP_Y + dy + h_] = F[CAP_Y + dy:CAP_Y + dy + h_] * (1 - A) + spr_[..., :3] * A
    if t < SEG[1][0] + 0.4:
        y0 = CAP_Y + 140; x0 = WF // 2 - 35
        for r_, row in enumerate(rv.HEADPHONES):
            for c_, bb in enumerate(row):
                if bb == '1': F[y0 + r_ * 7:y0 + r_ * 7 + 7, x0 + c_ * 7:x0 + c_ * 7 + 7] = 1.0
def scene_img(t):
    UI.clear(); F = rv.BG.copy(); scene(F, t)
    F = zoom_world(F); rv.snow(F, t)
    for op in UI: op(F)
    return F
XF = 0.22                                                                   # crossfade length (s)
def cut_times():
    if '_cuts' not in _C:
        ts = {c['t0'] for c in CAPJ} | {a for a, b in SEG} | set(screams().values())
        _C['_cuts'] = sorted(x for x in ts if x > 0.1)
    return _C['_cuts']
def frame(t):
    F = scene_img(t)
    for b in cut_times():                                                   # smooth every change: blend from the frame just before it
        if b - 0.05 <= t < b - 0.05 + XF:
            a = smooth((t - (b - 0.05)) / XF)
            F = scene_img(b - 0.07) * (1 - a) + F * a
            break
    for st in screams().values():                                           # screams still punch: short shake, eased out
        if 0 <= t - st < 0.35:
            A = 12 * math.exp(-(t - st) / 0.1); dx, dy = int(A * math.sin(t * 90)), int(A * math.cos(t * 70))
            F = np.roll(np.roll(F, dx, 1), dy, 0)
    captions(F, t)
    return (np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == '__main__':
    if sys.argv[1] == '--stills':
        for ts in sys.argv[3:]: Image.fromarray(frame(float(ts))).save(f'{sys.argv[2]}/still_{float(ts):06.2f}.png')
        sys.exit()
    if sys.argv[1] == '--screams': print(screams()); sys.exit()
    out, wav = sys.argv[1], sys.argv[2]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WF}x{HF}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:a', 'aac', '-b:a', '256k', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(int(round(END * FPS))):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 600 == 0: print('frame', f, flush=True)
    p.stdin.close(); p.wait(); print('done', out)
