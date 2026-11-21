"""Blueprint-style remake of 'What If Penguins Gave Christmas Gifts?' - 1080x1920, 60 fps, ~86 s.

Story: meet Pip and Penny -> he wants to give her a perfect pebble -> the search -> a thief (set up
behind an iceberg) steals it -> an even better pebble across the ice -> belly-slide -> the gift ->
plot twist: gentoo penguins really do this -> the nest -> the thief had a crush too -> a few weeks
later, the egg hatches. Cold open on the theft, then a rewind.

Style (studied from reference shorts): navy blueprint grid background, chunky navy-outlined pixel
art, a floating ice diorama, unboxed bold captions with yellow key words, pixel labels and tags.

usage: python3 video2.py out.mp4 audio.wav | python3 video2.py --stills DIR t1 t2 ...  (video seconds)
"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'style_study'))
os.chdir(HERE)
import video as pv                       # the penguin character, pebbles, hearts, bubble, egg sprite
import blueprint_kit as bk
from score2 import *

W, H, S = pv.W, pv.H, pv.S               # 180 x 320 pixel grid, 6 screen px per pixel
WF, HF = W * S, H * S
TAU = 2 * math.pi
GY = 172                                  # where feet stand on the ice tile
WW = 700                                  # world width (pixels)
hexc = pv.hexc
NAVY = bk.OUTLINE
pv.INK = NAVY
pv.BODY, pv.BODY_L = hexc('#26304c'), hexc('#45537c')
smooth, put, up = pv.smooth, pv.put, pv.up
def last_age(hits, t): return pv.last_age(hits, t)

# ================================================================ background (screen space, smooth blueprint)
def build_bg():
    yy, xx = np.mgrid[0:HF, 0:WF].astype(np.float32)
    top, mid, low = hexc('#0f2a55'), hexc('#1f4782'), hexc('#162f5c')
    f = yy / HF
    base = np.where((f < 0.45)[..., None], top + (mid - top) * (f / 0.45)[..., None], mid + (low - mid) * ((f - 0.45) / 0.55)[..., None])
    glow = np.exp(-(((xx - 540) / 560) ** 2 + ((yy - 760) / 640) ** 2))
    base = base + glow[..., None] * hexc('#123a70') * 0.55
    vig = np.clip(1 - 0.35 * ((np.abs(xx - WF / 2) / (WF / 2)) ** 2 + (np.abs(yy - HF / 2) / (HF / 2)) ** 2) / 2, 0, 1)
    base = base * vig[..., None]
    rows = (yy.astype(int) % 60) == 0
    base[rows] = base[rows] * 1.12 + 0.012
    return np.clip(base, 0, 1).astype(np.float32)
BG = build_bg()

# ================================================================ the floating ice tile (world space)
BAY = pv.BAYER
def build_world():
    yy, xx = np.mgrid[0:H, 0:WW]
    col = np.zeros((H, WW, 3), np.float32); A = np.zeros((H, WW), np.float32)
    t0, t1, depth, rad = 142, 196, 10, 14
    def rr(y0, y1):
        cx = np.clip(xx, 6 + rad, WW - 7 - rad); cy = np.clip(yy, y0 + rad, y1 - rad)
        return ((xx - cx) ** 2 + (yy - cy) ** 2) <= rad ** 2
    top = rr(t0, t1); side = rr(t0 + depth, t1 + depth) & ~top
    snow = np.stack([hexc('#a9c8ea'), hexc('#cfe2f6'), hexc('#eaf3fd'), hexc('#ffffff')])
    v = 0.9 + 2.4 * (1 - (yy - t0) / (t1 - t0)) + 0.35 * np.sin(xx / 23.0) * np.sin(yy / 9.0)
    idx = np.clip(np.floor(v + BAY[yy % 4, xx % 4] - 0.5), 0, 3).astype(int)
    col[top] = snow[idx][top]
    r = np.random.default_rng(3)
    sp = top & (r.random((H, WW)) < 0.05); col[sp] = snow[np.clip(idx[sp] - 1, 0, 3)]
    sdy = (yy - (t0 + depth)) / (t1 - t0)
    sidec = np.where((yy > t1 + depth * 0.55)[..., None], hexc('#2c5d96'), hexc('#4a86c5'))
    col[side] = sidec[side]
    ice = top & (xx >= 145) & (xx < 300) & (yy >= t0 + 12 + np.round(2 * np.sin(xx / 11))) & (yy < t1 - 5 - np.round(2 * np.sin(xx / 13 + 1)))
    iceP = np.stack([hexc('#93cdf0'), hexc('#a9daf6'), hexc('#bfe6fb'), hexc('#d4f1ff')])
    vi = 1.0 + 2.2 * (1 - (yy - t0) / (t1 - t0))
    col[ice] = iceP[np.clip(np.floor(vi + BAY[yy % 4, xx % 4] - 0.5), 0, 3).astype(int)][ice]
    streak = ice & (((xx + 2 * yy) % 23) < 2) & (((xx - yy) % 37) < 18)
    col[streak] = hexc('#ffffff')
    p = np.pad(ice, 1); iedge = ice & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    col[iedge] = hexc('#6aa8d6')
    rim = top & ~np.roll(top, 1, 0); col[rim] = hexc('#ffffff')
    M = top | side
    p = np.pad(M, 1); ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~M
    col[ring] = NAVY; M = M | ring; A[M] = 1
    sh = (yy > t1 + depth + 1) & (yy < t1 + depth + 22) & (xx > 10) & (xx < WW - 10) & ~M
    A[sh] = 0.42 * (1 - (yy[sh] - (t1 + depth + 1)) / 21.0); col[sh] = hexc('#050a18')
    for _ in range(26):                                        # little rocks frozen into the snow
        x, y = int(r.uniform(12, WW - 12)), int(r.uniform(t0 + 8, t1 - 4))
        if 140 < x < 330 or 360 < x < 510: continue
        col[y, x:x + 2] = hexc('#8e95a4'); col[y - 1, x] = hexc('#c3c9d4'); col[y + 1, x:x + 2] = hexc('#5d6270')
    return col, A
WCOL, WA = build_world()
WCOL_HR, WA_HR = up(WCOL), up(WA[..., None])

def build_iceberg():
    """a tall chunk of ice the thief hides behind (chunky 6-px pixels)"""
    w_, h_ = 42, 132
    yy, xx = np.mgrid[0:h_, 0:w_]
    topline = 18 + 10 * np.abs(np.sin(xx / 6.5 + 0.8)) + 6 * (xx < 9) + 4 * (xx > 33)
    M = (yy >= topline) & (np.abs(xx - w_ / 2 + 0.5) <= w_ / 2 - 1 - 3 * (yy < 30) * (1 - (yy - topline).clip(0, 12) / 12))
    pal_ = np.stack([hexc('#7fb3df'), hexc('#a7d0f0'), hexc('#cfe7fa'), hexc('#f4fbff')])
    v = 1.2 + 2.0 * (1 - xx / w_) + 0.5 * ((xx + yy // 3) % 9 < 2)
    col = pal_[np.clip(np.floor(v + BAY[yy % 4, xx % 4] - 0.5), 0, 3).astype(int)].astype(np.float32)
    facet = M & (np.abs(xx - (12 + yy * 0.12)) < 0.8); col[facet] = hexc('#ffffff')
    facet2 = M & (np.abs(xx - (28 - yy * 0.06)) < 0.8) & (yy > 40); col[facet2] = hexc('#7fb3df')
    p = np.pad(M, 1); ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~M
    col[ring] = NAVY
    return col, M | ring
ICEBERG = build_iceberg(); ICEBERG_X, ICEBERG_Y = 13, GY + 4 - 132

# ================================================================ camera
CAMK = [(0, 'pip'), (3.6, 'pip'), (5.0, 380), (7.4, 380), (8.9, 'pip'), (24.6, 'pip'), (25.4, ('pip', -100)),
        (31.0, ('pip', -100)), (32.0, 'pip'), (36.0, 'pip'), (37.2, 170), (38.6, 170), (39.8, ('pip', -50)),
        (43.3, ('pip', -50)), (46.5, ('pip', -20)), (48.6, ('pip', -60)), (52.6, ('pip', -60)), (53.8, 344),
        (71.8, 344), (72.8, 520), (75.8, 520), (77.0, 344), (LOOP + 1, 344)]
def cam_val(spec, T):
    if spec == 'pip': return pip_x(T) - 72
    if isinstance(spec, tuple): return pip_x(T) + spec[1]
    return spec
def cam_x(T):
    for (t0, a), (t1, b) in zip(CAMK, CAMK[1:]):
        if t0 <= T < t1:
            s = smooth((T - t0) / (t1 - t0)) if a != b else 0.0
            c = cam_val(a, T) * (1 - s) + cam_val(b, T) * s
            return min(max(c, 0), WW - W)
    return 344

# ================================================================ Pip
def pip_x(T):
    if SLIDE[0] <= T < SLIDE[1]:
        s = (T - SLIDE[0]) / (SLIDE[1] - SLIDE[0]); return SLIDE[2] + (SLIDE[3] - SLIDE[2]) * (1 - (1 - s) ** 2.2)
    if T >= SLIDE[1] and T < WALKS[4][0]: return SLIDE[3]
    x = PIP0
    for t0, t1, x0, x1 in WALKS:
        if T >= t1: x = x1
        elif T >= t0:
            s = (T - t0) / (t1 - t0); return x0 + (x1 - x0) * (s * s * (3 - 2 * s) * 0.3 + s * 0.7)
    if T >= SLIDE[1]: x = max(x, SLIDE[3]) if T < WALKS[4][0] else x
    return x
def walking(T):
    for t0, t1, x0, x1 in WALKS:
        if t0 <= T < t1: return (T - t0) / 0.32
    return None
def blinking(T, ph): return ((T + ph) % 3.1) < 0.12
def beat_hop(T, hits, k=3.0): return k * math.exp(-last_age(hits, T) / 0.12)

def pip(T):
    x = pip_x(T); ph = walking(T)
    pose = dict(hat=True, look=0, eyes='open', flop=1.2 * math.sin(T * 5), sq=1 + 0.018 * math.sin(T * 2.4))
    if ph is not None:
        pose['dy'] = 2.2 * abs(math.sin(math.pi * ph)); pose['tilt'] = 0.13 * math.sin(math.pi * ph)
        pose['liftL'] = 2 * max(0, math.sin(math.pi * ph)); pose['liftR'] = 2 * max(0, -math.sin(math.pi * ph))
        pose['flipL'] = 0.35 + 0.15 * math.sin(math.pi * ph); pose['flipR'] = 0.35 - 0.15 * math.sin(math.pi * ph)
        pose['look'] = 1
    holding = None
    if 0.6 <= T < 2.8: pose['flipR'] = 2.0 + 0.35 * math.sin(T * 9); pose['eyes'] = 'happy'          # waves hi
    if 3.6 <= T < 7.5: pose['look'] = 1
    if 7.5 <= T < 12.0: pose['eyes'] = 'happy'; pose['look'] = 1; pose['tilt'] = 0.07 * math.sin(T * 2.2)   # dreamy
    if 12.0 <= T < 17.0: pose['eyes'] = 'happy'; pose['look'] = 0.4
    for k, tp in PICKS.items():
        end = {'dull1': TOSSES['dull1'], 'dull2': TOSSES['dull2'], 'shiny': PLACE_SHINY, 'best': GIVE}[k]
        if tp - 0.4 <= T < tp and k != 'best':
            pose['sq'] = 1 - 0.14 * math.sin(math.pi * (T - (tp - 0.4)) / 0.4); pose['flipR'] = 0.6
        if tp <= T < end: holding = k
    if holding in ('dull1', 'dull2'):
        a = T - PICKS[holding]
        pose['flipR'] = 1.55; pose['look'] = 1; pose['tilt'] = 0.05 * math.sin(a * 3)
        if a > 0.9: pose['brows'] = True                         # unimpressed
    for k, tt in TOSSES.items():
        a = T - tt
        if -0.3 <= a < 0: pose['flipR'] = 1.55 - 0.7 * math.sin(math.pi * (a + 0.3) / 0.6); pose['tilt'] = 0.08 * (a + 0.3) / 0.3
        if 0 <= a < 0.25: pose['flipR'] = 1.55 + 0.9 * math.sin(math.pi * a / 0.25); pose['tilt'] = -0.1 * math.sin(math.pi * a / 0.25)
    if holding == 'shiny':
        pose['flipR'] = 1.85; pose['eyes'] = 'happy' if T > PICKS['shiny'] + 0.25 else 'open'
    if PLACE_SHINY - 0.4 <= T < PLACE_SHINY:                     # puts it down to admire it
        pose['sq'] = 1 - 0.14 * math.sin(math.pi * (T - PLACE_SHINY + 0.4) / 0.4); pose['flipR'] = 0.7
    if PLACE_SHINY + 0.2 <= T < SNATCH:                          # happy dance next to his pebble
        pose['eyes'] = 'happy'; pose['look'] = 0.6
        pose['dy'] = beat_hop(T, KICKS + STABS, 4); pose['flipL'] = 1.0 + 0.6 * math.sin(T * 10); pose['flipR'] = 1.0 + 0.6 * math.sin(T * 10 + 1.5)
        pose['tilt'] = 0.12 * math.sin(T * 5)
    if SNATCH <= T < SAD:                                        # WAIT-- HEY!!
        a = T - SNATCH
        pose['eyes'] = 'wide'; pose['look'] = 1; pose['flipL'] = 2.0 + 0.3 * math.sin(a * 30); pose['flipR'] = 2.0 + 0.3 * math.sin(a * 30 + 1)
        pose['sq'] = 1 + 0.08 * math.exp(-a / 0.1)
        if a < 0.45: pose['dy'] = 12 * math.sin(math.pi * a / 0.45)
    if SAD <= T < SIGH:                                          # robbed...
        pose['flipL'] = pose['flipR'] = 0.05; pose['sq'] = 0.94; pose['look'] = 0; pose['dy'] = -1
    if SIGH <= T < DETERMINED:
        pose['flipL'] = pose['flipR'] = 0.05; pose['sq'] = 0.94 - 0.05 * math.sin(math.pi * (T - SIGH) / 0.6); pose['eyes'] = 'blink'
    if DETERMINED <= T < 39.0:                                   # fine. an even better one.
        a = T - DETERMINED
        pose['brows'] = True; pose['look'] = 1; pose['flipL'] = pose['flipR'] = 0.8
        if a < 0.4: pose['dy'] = 7 * math.sin(math.pi * a / 0.4)
    if SLIP <= T < FALL:
        a = T - SLIP
        pose['eyes'] = 'wide'; pose['flipL'] = 1.3 + 0.7 * math.sin(a * 20); pose['flipR'] = 1.3 + 0.7 * math.sin(a * 20 + 2)
        pose['tilt'] = 0.16 * math.sin(a * 14); pose['liftL'] = 3 * max(0, math.sin(a * 22)); pose['liftR'] = 3 * max(0, -math.sin(a * 22))
    if FALL <= T < SLIDE[0]:
        k_ = smooth((T - FALL) / (SLIDE[0] - FALL)); pose['tilt'] = 1.45 * k_; pose['dy'] = 27 * k_; pose['eyes'] = 'wide'
        pose['flipL'] = pose['flipR'] = 1.8 * (1 - k_) + 0.25 * k_
    if SLIDE[0] <= T < GETUP:
        a = T - SLIDE[0]
        pose['tilt'] = 1.45 + 0.03 * math.sin(a * 20); pose['dy'] = 27 + 2.5 * math.exp(-a / 0.08) * math.cos(a * 30)
        pose['flipL'] = pose['flipR'] = 0.25 + 0.12 * math.sin(a * 14); pose['eyes'] = 'happy' if T < SLIDE[1] else 'open'; pose['sq'] = 1.0
    if GETUP <= T < GETUP + 0.7:
        k_ = smooth((T - GETUP) / 0.7); pose['tilt'] = 1.45 * (1 - k_); pose['dy'] = 27 * (1 - k_) + 8 * math.sin(math.pi * k_)
    if GETUP + 0.7 <= T < GETUP + 1.3:
        a = T - GETUP - 0.7; pose['tilt'] = 0.14 * math.sin(a * 40) * math.exp(-a * 5); pose['eyes'] = 'happy'
    if holding == 'best':
        pose['flipR'] = 1.85 if T < OFFER else 1.35; pose['look'] = 1
        if T >= OFFER: pose['tilt'] = 0.16 * smooth((T - OFFER) / 0.5); pose['sq'] = 0.96
    if T >= GIVE:
        a = T - GIVE
        pose['eyes'] = 'happy'; pose['look'] = 1
        pose['flipL'] = pose['flipR'] = 0.4 + 0.5 * max(0, math.sin(a * 9)) * math.exp(-a / 1.5)
        if a < 0.5: pose['dy'] = 7 * math.sin(math.pi * a / 0.5)
    if T >= NEST_T: pose['dy'] = pose.get('dy', 0) + beat_hop(T, KICKS)
    if CRACKS[0] <= T < HATCH: pose['eyes'] = 'wide'; pose['look'] = 1
    if HATCH <= T < HATCH + 0.6: pose['dy'] = 9 * math.sin(math.pi * (T - HATCH) / 0.6); pose['flipL'] = pose['flipR'] = 2.0
    pose['flop'] = pose['flop'] - 9 * pose.get('tilt', 0) + 0.25 * pose.get('dy', 0)
    if pose['eyes'] == 'open' and blinking(T, 0.0): pose['eyes'] = 'blink'
    return x, pose, holding

def penny(T):
    pose = dict(bow=True, look=0, eyes='open', sq=1 + 0.018 * math.sin(T * 2.2 + 1), tilt=0.04 * math.sin(T * 1.6))
    holding = None
    if 3.6 <= T < 7.4:                                           # preening
        pose['flipL'] = 1.7 + 0.3 * math.sin(T * 9); pose['look'] = -0.3
        if T > 5.4: pose['eyes'] = 'happy'
    if T >= 50.6: pose['look'] = -1 * smooth((T - 50.6) / 0.8)
    if PONDER[0] <= T < PONDER[1]:                               # ...hmm
        pose['look'] = -0.4; pose['tilt'] = -0.08 + 0.03 * math.sin(T * 3)
    if GIVE <= T < NEST_T - 0.2: holding = 'best'; pose['flipL'] = 1.1
    if T >= GIVE:
        pose['eyes'] = 'happy'
        if T < GIVE + 0.45: pose['dy'] = 9 * math.sin(math.pi * (T - GIVE) / 0.45)
    if T >= NEST_T: pose['dy'] = pose.get('dy', 0) + beat_hop(T, [k + 0.5 for k in KICKS])
    if CRACKS[0] <= T < HATCH: pose['eyes'] = 'wide'; pose['look'] = -1
    if HATCH <= T < HATCH + 0.6: pose['dy'] = 9 * math.sin(math.pi * (T - HATCH) / 0.6); pose['flipL'] = pose['flipR'] = 2.0
    if pose['eyes'] == 'open' and blinking(T, 1.3): pose['eyes'] = 'blink'
    return pose, holding

def thief_x(T):
    if T < THIEF_FALL + 0.3: return THIEF_X0
    if T < SNATCH: return THIEF_X0 + (THIEF_XS - THIEF_X0) * (T - THIEF_FALL - 0.3) / (SNATCH - THIEF_FALL - 0.3)
    a = T - SNATCH; return THIEF_XS + 70 * a + 60 * a * a
def thief(T):
    """returns (x, pose, mode) mode: 'hidden','peek','slide','gone','scene'"""
    if T < PEEK[0] or (THIEF_GONE <= T < THIEF_SCENE - 0.5) or T >= FLURRY + 0.6: return None
    if T >= THIEF_SCENE - 0.5:
        pose = dict(look=1, eyes='open', sq=1 + 0.02 * math.sin(T * 2.5), flipR=1.5, tilt=0.05)
        if T >= THIEF_GIVE: pose['eyes'] = 'happy'; pose['flipR'] = 0.4; pose['dy'] = 6 * math.sin(math.pi * min(1, (T - THIEF_GIVE) / 0.45))
        elif blinking(T, 0.6): pose['eyes'] = 'blink'
        return 585, pose, 'scene'
    if T < THIEF_FALL:                                           # peeking out from behind the iceberg
        a = T - PEEK[0]
        lean = 0.42 * smooth(a / 0.5) - 0.18 * smooth((a - 1.1) / 0.3) + 0.18 * smooth((a - 1.7) / 0.3)
        return THIEF_X0, dict(tilt=lean, brows=True, look=1, eyes='open', flipL=0.2, flipR=0.2), 'peek'
    if T < THIEF_FALL + 0.3:
        k_ = smooth((T - THIEF_FALL) / 0.3)
        return THIEF_X0, dict(tilt=0.42 + (1.45 - 0.42) * k_, dy=27 * k_, brows=True, look=1, flipL=2.6 * k_, flipR=2.6 * k_), 'slide'
    return thief_x(T), dict(tilt=1.45, dy=27 + 1.2 * abs(math.sin(T * 22)), brows=True, look=1, eyes='open', flipL=2.6, flipR=2.6), 'slide'

def crush(T):
    pose = dict(look=-1, eyes='open', sq=1 + 0.018 * math.sin(T * 2.1 + 2), tilt=0.04 * math.sin(T * 1.4 + 1))
    holding = None
    if T >= THIEF_GIVE:
        holding = 'shiny'; pose['flipL'] = 1.1; pose['eyes'] = 'happy'
        if T < THIEF_GIVE + 0.45: pose['dy'] = 9 * math.sin(math.pi * (T - THIEF_GIVE) / 0.45)
    elif blinking(T, 2.0): pose['eyes'] = 'blink'
    return pose, holding

# ================================================================ captions (unboxed, bold, yellow key words)
FONT = ImageFont.truetype(bk.FONT_BOLD, 76)
HEADPHONES = ["0011111100", "0100000010", "1000000001", "1000000001", "1110000111", "1110000111", "1110000111", "0110000110"]
def caption_sprite(text, highlight, icon=False):
    lines = text.split('\n'); lh = 92
    img = Image.new('RGBA', (WF, lh * len(lines) + 40 + (90 if icon else 0)), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for li, line in enumerate(lines):
        words = line.split(' '); sp = 20
        wd = [d.textlength(w_, font=FONT) for w_ in words]; x = (WF - (sum(wd) + sp * (len(words) - 1))) / 2; y = 10 + li * lh
        for w_, ww in zip(words, wd):
            key = w_.strip('.,!?:-').upper()
            colr = bk.YELLOW if key in highlight else bk.WHITE
            d.text((x + 5, y + 7), w_, font=FONT, fill=(6, 10, 24, 255), stroke_width=7, stroke_fill=(6, 10, 24, 255))
            d.text((x, y), w_, font=FONT, fill=colr + (255,), stroke_width=7, stroke_fill=(8, 14, 30, 255))
            x += ww + sp
    a = np.asarray(img).astype(np.float32) / 255
    if icon:
        y0 = lh * len(lines) + 24; x0 = WF // 2 - 5 * 7
        for r_, row in enumerate(HEADPHONES):
            for c_, b in enumerate(row):
                if b == '1': a[y0 + r_ * 7:y0 + r_ * 7 + 7, x0 + c_ * 7:x0 + c_ * 7 + 7] = [1, 1, 1, 1]
    return a
CAP_Y = 1278
CAPS = []                    # (video t_in, t_out, sprite)
def cap(text, a, b, hl=(), icon=False, story=True):
    off = 2.4 if story else 0.0
    CAPS.append((a + off, b + off, caption_sprite(text, set(hl), icon)))
cap("HE GOT\nROBBED!!", 0.0, 1.55, ('ROBBED',), icon=True, story=False)
cap("OK WAIT.\nLET ME EXPLAIN.", 1.62, 2.75, ('WAIT',), story=False)
for text, a, b, hl in [
    ("THIS IS PIP.", 0.4, 3.3, ('PIP',)), ("THIS IS PENNY.", 5.1, 7.4, ('PENNY',)),
    ("HE HAS A CRUSH\nON HER.", 9.0, 11.8, ('CRUSH',)), ("HE WANTS TO GIVE\nHER A GIFT.", 12.2, 14.8, ('GIFT',)),
    ("THE PERFECT\nPEBBLE.", 15.0, 16.9, ('PERFECT',)), ("NOPE.\nTOO DULL.", 18.7, 20.2, ('NOPE',)),
    ("NOPE.\nTOO SMALL.", 22.1, 23.6, ('NOPE',)), ("THIS ONE.\nPERFECT.", 25.4, 28.4, ('PERFECT',)),
    ("WAIT--\nHEY!!", 29.6, 31.0, ('HEY',)), ("HE GOT\nROBBED.", 31.2, 33.2, ('ROBBED',)),
    ("FINE. AN EVEN\nBETTER ONE.", 33.6, 35.8, ('BETTER',)), ("BUT IT'S\nACROSS THE ICE.", 36.4, 38.8, ('ICE',)),
    ("HOW HARD\nCAN IT BE?", 40.4, 42.8, ()), ("WHEEEE!!", 43.4, 46.2, ('WHEEEE',)), ("GOT IT.", 46.5, 48.2, ('GOT',)),
    ("NOW THE\nIMPORTANT PART.", 49.4, 52.6, ('IMPORTANT',)), ("...", 54.6, 56.2, ()), ("SHE SAID\nYES!!", 56.4, 59.6, ('YES',)),
    ("PLOT TWIST:\nPENGUINS REALLY\nDO THIS.", 60.2, 63.4, ('REALLY',)), ("THEY GIVE PEBBLES\nTO THE ONE\nTHEY LIKE.", 63.6, 67.0, ('PEBBLES',)),
    ("AND BUILD A\nNEST TOGETHER.", 67.2, 71.6, ('NEST',)), ("AND THE\nTHIEF?", 72.4, 74.2, ('THIEF',)),
    ("HE HAD A\nCRUSH TOO.", 74.4, 76.4, ('CRUSH',)), ("A FEW WEEKS\nLATER...", 77.2, 79.2, ()),
    ("WAIT... IS IT\nMOVING??", 79.4, 81.3, ('MOVING',)), ("BEST CHRISTMAS\nGIFT EVER.", 81.7, 83.8, ('CHRISTMAS',))]:
    cap(text, a, b, hl)
def draw_captions(F, v):
    for a, b, spr in CAPS:
        if a <= v < b:
            al = min(1.0, (v - a) / 0.1, (b - v) / 0.1)
            dy = int(10 * (1 - min(1.0, (v - a) / 0.12)))
            h_ = spr.shape[0]; y0 = CAP_Y + dy
            A = spr[..., 3:4] * al
            F[y0:y0 + h_] = F[y0:y0 + h_] * (1 - A) + spr[..., :3] * A

# ================================================================ labels and tags (anchored to the world)
def head_of(x): return x, GY - 128
LABELS = [('PIP', 0.5, 3.4, lambda T: head_of(pip_x(T))), ('PENNY', 5.0, 7.4, lambda T: head_of(PENNY_X)),
          ('???', 26.4, 28.5, lambda T: (THIEF_X0 + 34, GY - 92)), ('BETTER ONE', 34.2, 38.8, lambda T: (PEBBLE_X['best'], GY - 6)), ('THE THIEF', 72.4, 74.3, lambda T: head_of(585)),
          ('HIS CRUSH', 74.5, 76.3, lambda T: head_of(CRUSH_X))]
TAGS = [('SLIPPERY', 36.4, 38.8, (196, 30)), ('GENTOO', 60.4, 63.4, (404, 26))]
def draw_labels(F, T, cam):
    for text, a, b, anchor in LABELS:
        if a <= T < b:
            wx, wy = anchor(T); ax, ay = int((wx - cam) * S), int(wy * S)
            tw = len(text) * 6 * 5 - 5
            tx = min(max(ax - tw // 2, 30), WF - tw - 30); ty = max(min(ay - 150, 640), 60)
            bk.label(F, text, tx, ty, ax, ay - 6, px=5)
    for text, a, b, (wx, wy) in TAGS:
        if a <= T < b:
            x = int((wx - cam) * S); bk.tag(F, text, min(max(x, 40), WF - 300), int(wy * S), px=5)

# ================================================================ the egg and the chick
def draw_egg(OUT, x, y, T):
    a_in = T - EGG_IN
    grow = 1 - math.exp(-a_in / 0.08) * math.cos(a_in * 18) if a_in < 0.6 else 1.0
    if T < HATCH:
        amp = 0.05 + 0.2 * smooth((T - (EGG_IN + 1.0)) / (HATCH - EGG_IN - 1.0))
        kk = last_age(KICKS, T); idx = int(np.searchsorted(KICKS, T, side='right'))
        ang = amp * math.exp(-kk / 0.18) * math.sin(kk * 25) * (1 if idx % 2 else -1) if T > EGG_IN + 1.0 else 0
        col, M = pv.egg_sprite(ang, 'all', sum(1 for c in CRACKS if T >= c))
        if grow < 1:
            sc = max(0.05, grow); n = col.shape[0]; yy, xx = np.mgrid[0:n, 0:n]
            sy = np.clip(((yy - (n - 6)) / sc + (n - 6)).astype(int), 0, n - 1); sx = np.clip(((xx - n / 2) / sc + n / 2).astype(int), 0, n - 1)
            col, M = col[sy, sx], M[sy, sx] & (np.abs(yy - (n - 6)) <= (n - 6) * sc) & (np.abs(xx - n / 2) <= n / 2 * sc)
        pv.blit_hr(OUT, col, M, x - 24, y - 45, pv.FINE); return
    a = T - HATCH
    pop_ = min(1.0, a / 0.3); rise = 22 * (1 - (1 - pop_) ** 3) + (3 * math.exp(-a / 0.1) * math.sin(a * 30) if a > 0.3 else 0)
    bob = 2.5 * math.exp(-last_age(KICKS, T) / 0.12) if a > 0.6 else 0
    cp = dict(scale=0.36, hat=True, eyes='happy' if a > 0.5 else 'wide', flipL=0.9 + 0.6 * math.sin(a * 12) * math.exp(-a / 1.0),
              flipR=0.9 + 0.6 * math.sin(a * 12 + 1) * math.exp(-a / 1.0), flop=1.5 * math.sin(T * 6), sq=1 - 0.05 * math.exp(-last_age(KICKS, T) / 0.08))
    if cp['eyes'] == 'happy' and ((T + 0.7) % 2.3) < 0.12: cp['eyes'] = 'blink'
    col, M, _ = pv.penguin(cp)
    pv.blit_hr(OUT, col, M, x - pv.OX / pv.FINE, y + 14 - rise * 20 / 22 - bob - pv.OY / pv.FINE, pv.FINE)
    col, M = pv.egg_sprite(0.0, 'bottom', 0); pv.blit_hr(OUT, col, M, x - 24, y - 45, pv.FINE)
    if a < 1.2:
        col, M = pv.egg_sprite(a * 9, 'top', 0); pv.blit_hr(OUT, col, M, x - 24 + 30 * a, y - 45 - 40 * a + 60 * a * a, pv.FINE)

# ================================================================ render one story moment
rng = np.random.default_rng(41)
FLAKES = [(rng.uniform(0, W), rng.uniform(0, 1), rng.uniform(10, 22), rng.uniform(0, 6.28)) for _ in range(46)]
NEST_POS = [(NEST_CX + 64 * math.cos(math.pi + TAU * i / len(NEST) * 0.999), GY + 11 + 10 * math.sin(math.pi + TAU * i / len(NEST) * 0.999)) for i in range(len(NEST))]
HEARTS = [(t, 'pip') for t in (7.6, 8.2, 8.8, 9.6, 10.4)] + [(t, 'couple') for t in (GIVE + 0.15, GIVE + 0.5, GIVE + 0.9, 61.0, 64.0, 67.0)] + \
         [(t, 'thief') for t in (THIEF_GIVE + 0.15, THIEF_GIVE + 0.5, THIEF_GIVE + 0.9)] + [(t, 'egg') for t in (HATCH + 0.2, HATCH + 0.5, HATCH + 0.9, HATCH + 1.6)]
HR_BAYER = up(BAY[np.arange(H)[:, None] % 4, np.arange(W)[None, :] % 4][..., None])[..., 0]
def onscreen(x, cam): return -70 < x - cam < W + 70
def pebble(OUT, x, y, kind, T, shine=0.0, small=False):
    pb = pv.PB
    if small: pv.PB = 2
    pv.draw_pebble(OUT, x, y, kind, T, shine); pv.PB = pb

def render(T):
    cam = cam_x(T); X = int(round(cam * S))
    F = BG.copy()
    off = int(round(cam * S * 0.35)) % 60
    cols = np.arange((60 - off) % 60, WF, 60); F[:, cols] = F[:, cols] * 1.12 + 0.012
    for x0, ph0, sp, ph in FLAKES:                                  # snow drifting behind the tile
        y = ((T * sp / H + ph0) % 1.0) * (H + 10) - 5
        put(F, (x0 + 4 * math.sin(T * 0.8 + ph)) % W, y, np.array([0.85, 0.92, 1.0]), 0.35)
    A = WA_HR[:, X:X + WF]; F = F * (1 - A) + WCOL_HR[:, X:X + WF] * A
    # pebbles waiting on the tile
    for k, tp in PICKS.items():
        if T < tp:
            sh = 0.6 if (k == 'shiny' and T > 23.8) else (1.0 if (k == 'best' and T > 33.6) else 0.0)
            pebble(F, PEBBLE_X[k] - cam, GY + 1, k, T, sh, small=(k == 'dull2'))
    if PLACE_SHINY <= T < SNATCH: pebble(F, SHINY_GROUND_X - cam, GY + 2, 'shiny', T, 0.8)
    for i, (nt, n, d) in enumerate(NEST):                           # the nest: one pebble per note
        a = T - nt
        if a >= 0 and onscreen(NEST_CX, cam):
            x, y = NEST_POS[i]
            yy = y - 30 * (1 - min(1, a / 0.18)) ** 2 - (3 * math.sin(math.pi * (a - 0.18) / 0.14) if 0.18 < a < 0.32 else 0)
            pebble(F, x - cam, yy, 'best' if i == 0 else 'nest', T, 0.6 * math.exp(-a / 0.3) if a < 1 else 0)
    th = thief(T)
    if th and th[2] == 'peek': pv.draw_penguin(F, th[0], GY - th[1].get('dy', 0), th[1], cam)
    pv.blit_hr(F, ICEBERG[0], ICEBERG[1], ICEBERG_X - cam, ICEBERG_Y, 1)
    hx, hpose, hheld = pv.eased(pip, T)
    ppose, pheld = pv.eased(penny, T)
    if onscreen(PENNY_X, cam):
        ptips = pv.draw_penguin(F, PENNY_X, GY - ppose.get('dy', 0), ppose, cam)
        if pheld: tx, ty = ptips[-1]; pebble(F, tx, ty - 1, pheld, T, 1.0)
    if onscreen(hx, cam):
        htips = pv.draw_penguin(F, hx, GY - hpose.get('dy', 0), hpose, cam)
        if hheld: tx, ty = htips[1]; pebble(F, tx, ty - 1, hheld, T, 1.0 if hheld in ('shiny', 'best') else 0, small=(hheld == 'dull2'))
    for k, tt in TOSSES.items():
        a = T - tt
        if 0 <= a < 0.6: pebble(F, PEBBLE_X[k] + 8 - 60 * a / 0.6 - cam, GY - 66 + 180 * (a - 0.25) ** 2 - 10, k, T, small=(k == 'dull2'))
    if th and th[2] in ('slide', 'scene'):
        tp = pv.eased(lambda t_: (thief(t_)[1] if thief(t_) else th[1], None), T)[0] if th[2] == 'scene' else th[1]
        ttips = pv.draw_penguin(F, th[0], GY - tp.get('dy', 0), tp, cam)
        if th[2] == 'slide':
            for k in range(1, 9): put(F, th[0] - 8 - k * 5 - cam, GY - 1 - (k % 3), np.array([1.0, 1.0, 1.0]), 0.8 - k * 0.08)
            if T >= SNATCH: pebble(F, th[0] + 92 - cam, GY - 14, 'shiny', T, 0.8)
        elif T < THIEF_GIVE: tx, ty = ttips[1]; pebble(F, tx, ty - 1, 'shiny', T, 1.0)
    if onscreen(CRUSH_X, cam) and T >= THIEF_SCENE - 0.5 and T < FLURRY + 0.6:
        cpose, cheld = pv.eased(crush, T)
        ctips = pv.draw_penguin(F, CRUSH_X, GY - cpose.get('dy', 0), cpose, cam)
        if cheld: tx, ty = ctips[-1]; pebble(F, tx, ty - 1, cheld, T, 1.0)
    if 0 <= T - SNATCH < 0.3:                                       # snatch puff
        a = T - SNATCH
        for q in range(10):
            ang = TAU * q / 10; d = 4 + 14 * a / 0.3
            put(F, SHINY_GROUND_X + d * math.cos(ang) - cam, GY - 6 + d * math.sin(ang) * 0.6, np.array([1.0, 1.0, 1.0]), 1 - a / 0.3)
    if SLIDE[0] <= T < SLIDE[1]:                                    # Pip's slide spray
        sp_ = 1 - (T - SLIDE[0]) / (SLIDE[1] - SLIDE[0])
        for k in range(1, 9): put(F, hx - 8 - k * 5 - cam, GY - 1 - (k % 3) - 2 * math.sin(T * 30 + k), np.array([1.0, 1.0, 1.0]), (0.85 - k * 0.09) * (0.3 + 0.7 * sp_))
    if 33.6 <= T < PICKS['best']:                                  # the better pebble twinkles so you can't miss it
        k = 0.5 + 0.5 * math.sin(T * 6)
        for q in range(3):
            ang = q * TAU / 3 + T * 0.8; d = 9 + 2 * k
            sx_, sy_ = PEBBLE_X['best'] + d * math.cos(ang) - cam, GY - 6 + d * math.sin(ang) * 0.7
            tw_ = 0.5 + 0.5 * math.sin(T * 7 + q * 2)
            put(F, sx_, sy_, hexc('#ffc83a'), 1.0)
            for dx_, dy_ in ((1, 0), (-1, 0), (0, 1), (0, -1)): put(F, sx_ + dx_, sy_ + dy_, hexc('#ffc83a'), tw_)
    if 0 <= T - PICKS['best'] < 0.45:
        a = T - PICKS['best']
        for q in range(12):
            ang = TAU * q / 12; d = 3 + 16 * a / 0.45
            put(F, PEBBLE_X['best'] + d * math.cos(ang) - cam, GY - 4 + d * math.sin(ang), hexc('#fff6c0'), 1 - a / 0.45)
    if T >= EGG_IN and onscreen(NEST_CX, cam): draw_egg(F, NEST_CX - cam, GY + 16, T)
    if 12.0 <= T < 17.0:                                            # thought bubble: the perfect pebble for Penny
        popk = 0 if T < 16.6 else (T - 16.6) / 0.3
        grow = min(1.0, (T - 12.0) / 0.25)
        if popk < 1 and grow > 0.3: pv.draw_bubble(F, pip_x(T) + 34 - cam, GY - 122 + 1.5 * math.sin(T * 4), T, 1.0, popk)
    for ht, who in HEARTS:
        a = T - ht
        if 0 <= a < 1.4:
            mx = {'pip': pip_x(T) + 6, 'couple': (pip_x(T) + PENNY_X) / 2, 'thief': (585 + CRUSH_X) / 2, 'egg': NEST_CX}[who]
            sc = 1.0 + 0.25 * math.exp(-a / 0.12) * math.cos(a * 25)
            pv.draw_heart(F, mx - cam + (int(ht * 7) % 3 - 1) * 8, GY - 140 - 26 * a, max(0.0, 1 - (a / 1.4) ** 2), sc * 2.0)
    if FLURRY <= T < FLURRY + 1.0:                                  # "a few weeks later..." snow flurry
        k = math.sin(math.pi * (T - FLURRY) / 1.0) * 0.9
        m = HR_BAYER < k; F[m] = F[m] * 0.15 + hexc('#f4fbff') * 0.85
    draw_labels(F, T, cam)
    return F

# ================================================================ video time -> story time (cold open, rewind)
COLD0, COLD_LEN, REW = THIEF_FALL + 0.3, 1.6, 0.8
VLOOP = COLD_LEN + REW + LOOP
def story_time(v):
    if v < COLD_LEN: return COLD0 + v
    if v < COLD_LEN + REW: return (COLD0 + COLD_LEN) * (1 - smooth((v - COLD_LEN) / REW))
    return v - COLD_LEN - REW
REWIND_ICON = ["1000100", "1100110", "1110111", "1111111", "1110111", "1100110", "1000100"]
def frame(v):
    F = render(story_time(v))
    if COLD_LEN <= v < COLD_LEN + REW:
        for j, row in enumerate(REWIND_ICON):
            for i, ch in enumerate(row[::-1]):
                if ch == '1': F[120 + j * 10:130 + j * 10, 900 + i * 10:910 + i * 10] = 1.0
        sl = (np.arange(HF) // 3) % 4 == 0; F[sl] = F[sl] * 0.85
    if v > VLOOP - 0.4:
        G = render(story_time(0.0)); m = HR_BAYER < smooth((v - (VLOOP - 0.4)) / 0.4); F[m] = G[m]
    draw_captions(F, v)
    return (np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8)

if __name__ == '__main__':
    if sys.argv[1] == '--stills':
        for ts in sys.argv[3:]: Image.fromarray(frame(float(ts))).save(f'{sys.argv[2]}/still_{float(ts):06.2f}.png')
        sys.exit()
    out, wav = sys.argv[1], sys.argv[2]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WF}x{HF}', '-r', str(FPS),
                          '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    for f in range(int(round(VLOOP * FPS))):
        p.stdin.write(frame(f / FPS).tobytes())
        if f % 600 == 0: print('frame', f, flush=True)
    p.stdin.close(); p.wait(); print('done', out)
