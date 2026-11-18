"""'What If Your Younger Sibling Really Is Dumber?' - direct explainer, Jett narration (1080x1920, 60 fps).
YOU = green elf (older), younger sibling = short blue elf. Santa plays the parent. Screamed hook + mid SUBSCRIBE.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study'))
import importlib.util
_s = importlib.util.spec_from_file_location('fsm', os.path.join(ROOT_, 'fake_smile', 'video.py'))
fm = importlib.util.module_from_spec(_s); _s.loader.exec_module(fm)
b1, sv, rv, pv, bk, ch = fm.b1, fm.sv, fm.rv, fm.pv, fm.bk, fm.ch

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
glow, ctag, ctext, big_num = sv.glow, sv.ctag, sv.ctext, sv.big_num
draw_elf, draw_santa, draw_prof = b1.draw_elf, b1.draw_santa, b1.draw_prof
shadow, heart, sparkles, meter, thought = b1.shadow, b1.heart, b1.sparkles, b1.meter, b1.thought
bubble, sub_button = fm.bubble, fm.sub_button
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
(L_HOOK, L_DUMB, L_LOOK, L_CHECKED, L_TWO, L_SUB, L_STUDY, L_THEORY, L_SMARTER, L_NOBODY, L_STRICT, L_FOUR,
 L_NICE, L_CTA) = range(14)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))

_c = {}
def spr(key, fn):
    if key not in _c: _c[key] = fn()
    return _c[key]
def you(F, cx, mood='happy', **kw):
    return draw_elf(F, cx, 'holly', mood=mood, outfit='#2f9a52', outfit_d='#1f7a3e', hat='#2f9a52', **kw)
def kid(F, cx, mood='happy', arms='down', bob=0.0, cap=False):
    """younger sibling: a shorter blue elf (legs shortened, big head) with messy hair"""
    def mk():
        c, M = ch.elf(outfit='#3a8aff', outfit_d='#1d5bb8', hat='#3a8aff', messy=True, mood=mood, arms=arms, cap=cap)
        keep = np.r_[0:41, 46:c.shape[0]]
        return c[keep], M[keep]
    c, M = spr(('kid', mood, arms, cap), mk); h_ = M.shape[0]
    shadow(F, cx, GROUND + 1, 26 * max(0.6, 1 - bob / 30)); pv.blit_hr(F, c, M, cx - 19, GROUND + 1 - h_ - bob, 1)
    return GROUND + 1 - h_ - bob
def bowl(F, cx, y):
    def mk():
        L = ch.Layers(18, 11); yy, xx = np.mgrid[0:11, 0:18].astype(np.float32)
        L.add((yy >= 2) & (np.abs(xx - 8.5) <= 8 - (yy - 2) * 0.55), lambda c, m: (c.__setitem__(m, hexc('#f4f6fb')), c.__setitem__(m & (np.abs(yy - 5) < 1), hexc('#3a8aff'))))
        for k, (dx, dy) in enumerate(((4, 1), (7, 0), (10, 1), (13, 1), (6, 2), (11, 2))): L.add((np.abs(xx - dx) < 1.1) & (np.abs(yy - dy) < 0.8), hexc(('#ffcc4a', '#e8903a', '#e8303a')[k % 3]), outline=False)
        return L.out()
    c, M = spr('bowl', mk); pv.blit_hr(F, c, M, cx - 9, y, 1)
def fork(F, x, y, t):
    a = 0.3 * math.sin(t * 6)
    for j in range(12): put(F, x + j * math.sin(a) * 0.4, y - j, hexc('#c4ccd8'))
    for dx in (-1.5, 0, 1.5):
        for j in range(4): put(F, x + dx + 12 * math.sin(a) * 0.4, y - 12 - j, hexc('#c4ccd8'))
def fish(F, x, y):
    for dx in range(-5, 6):
        for dy in range(-3, 4):
            if (dx / 5) ** 2 + (dy / 3) ** 2 <= 1: put(F, x + dx, y + dy, hexc('#ff9a3a'))
    for k in range(4): put(F, x + 6 + k, y - k * 0.8, hexc('#ff9a3a')); put(F, x + 6 + k, y + k * 0.8, hexc('#ff9a3a'))
    put(F, x - 3, y - 1, hexc('#1b1428'))
def iq_bars(F, you_v, them_v, x0=40, x1=140, top=60, h_=70, label_px=5):
    meter(F, x0, 'YOU', you_v, '#5ae07a', y_top=top, h_=h_, w_=22); meter(F, x1, 'THEM', them_v, '#3a8aff', y_top=top, h_=h_, w_=22)
def board(F, x, y, txt):
    b = np.zeros((34, 62, 3), np.float32) + hexc('#1d3a2a'); bm = np.ones((34, 62), bool)
    b[:3] = hexc('#8a5a36'); b[-3:] = hexc('#8a5a36'); b[:, :3] = hexc('#8a5a36'); b[:, -3:] = hexc('#8a5a36')
    b, bm = bk.outline(b, bm); pv.blit_hr(F, b, bm, x, y, 1)
    bk.pixel_text(F, txt, int((x + 8) * S), int((y + 12) * S), px=6, colr=(240, 240, 230))
def card(F, cx, y, grade, stamp=None):
    w_, h_ = 24, 30; col = np.zeros((h_, w_, 3), np.float32) + 1.0; M = np.ones((h_, w_), bool)
    yy, xx = np.mgrid[0:h_, 0:w_]; col[(yy % 5 == 0) & (yy > 4) & (xx > 3) & (xx < w_ - 4)] = hexc('#c4ccd8')
    col, M = bk.outline(col, M); pv.blit_hr(F, col, M, cx - w_ / 2, y, 1)
    bk.pixel_text(F, grade, int((cx - 4) * S), int((y + 9) * S), px=9, colr=(200, 40, 60) if grade != 'A' else (30, 140, 60))
    if stamp: ctag(F, stamp, 0, px=6) if False else bk.tag(F, stamp, int((cx - len(stamp) * 3.2) * S), int((y + 34) * S), px=5)
def cookie(F, x, y):
    for dx in range(-6, 7):
        for dy in range(-6, 7):
            if dx * dx + dy * dy <= 36: put(F, x + dx, y + dy, hexc('#c8904a') if dx * dx + dy * dy < 30 else hexc('#8a5a2a'))
    for dx, dy in ((-2, -2), (2, 1), (-1, 3), (3, -3)): put(F, x + dx, y + dy, hexc('#3a2010'))

def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t); a = t - SEG[i][0]
    if i == L_HOOK:
        you(F, 50, mood='happy'); kid(F, 130, mood='happy')
        if t >= cs(L_HOOK, 1) - 0.05: bk.label(F, 'YOUNGER SIBLING', 470, 470, int(130 * S), int((GROUND - 46) * S), px=5)
    elif i == L_DUMB:
        jump = 6 * abs(math.sin(a * 9)) * math.exp(-a * 1.2)
        you(F, 50, mood='angry', bob=jump); top = kid(F, 130, mood='happy', bob=abs(math.sin(t * 4)) * 2)
        for k in range(3): bk.pixel_text(F, '?', int((124 + k * 7) * S), int((top - 14 - (k % 2) * 5) * S), px=7, colr=(255, 255, 255))
        ctag(F, 'DUMB?!', 300, px=12)
    elif i == L_LOOK:                                            # cereal with a fork; do fish get thirsty?
        you(F, 40, mood='shock'); top = kid(F, 112, mood='happy', arms='hold')
        bowl(F, 112, GROUND - 22); fork(F, 120, GROUND - 22, t)
        if t >= cs(L_LOOK, 2) - 0.05 and t < cs(L_LOOK, 3) - 0.05: bk.label(F, 'A FORK', 760, 520, int(122 * S), int((GROUND - 34) * S), px=6)
        if t >= cs(L_LOOK, 3) - 0.05:
            thought(F, 110, 42, 96, 34); fish(F, 76, 59); bk.pixel_text(F, 'THIRSTY?', int(86 * S), int(54 * S), px=6, colr=(30, 90, 200))
        elif t < cs(L_LOOK, 1) - 0.05: ctag(F, 'LOOK AT THEM', 300, px=7)
    elif i in (L_CHECKED, L_TWO):                                # science checked: about 2 IQ points
        g = ramp(t, SEG[L_CHECKED][0] + 0.3, 1.0)
        iq_bars(F, 0.10 + 0.72 * g, 0.10 + 0.69 * g, x0=66, x1=126, top=84, h_=62)
        if i == L_CHECKED:
            draw_prof(F, 22)
            if t < cs(L_CHECKED, 1) - 0.05: ctag(F, 'SCIENCE CHECKED', 260, px=7)
            elif t < cs(L_CHECKED, 2) - 0.05: ctag(F, 'THEY ARE...', 260, px=8)
            else: big_num(F, '2 IQ POINTS', 230, px=10, colr=(255, 200, 58))
        else:
            big_num(F, '2', 210, px=22, colr=(255, 200, 58))
            if t >= cs(L_TWO, 2) - 0.05: ctag(F, 'BARELY ANYTHING', 920, px=7)
    elif i == L_SUB:
        you(F, 60, mood='proud', arms='up', cap=True, bob=abs(math.sin(t * 6)) * 3)
        if t >= cs(L_SUB, 2) - 0.05: sub_button(F, t, cs(L_SUB, 2) - 0.05, cs(L_SUB, 2) + 0.35)
        else: ctag(F, 'THE SMART ONE?', 300, px=7)
    elif i == L_STUDY:                                           # 240,000 brothers: oldest a little higher
        n = int(240000 * ramp(t, cs(L_STUDY, 1) - 0.2, 1.2)); big_num(F, f'{n:,}', 210, px=10, colr=(255, 226, 122))
        bk.pixel_text(F, 'BROTHERS', 400, 300, px=6, colr=(225, 235, 255))
        for k in range(24):
            x = 20 + (k % 12) * 13; y = 66 + (k // 12) * 16
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx * dx + dy * dy <= 5: put(F, x + dx, y + dy, hexc('#f6c9a8'))
            for dy in range(3, 9): put(F, x, y + dy, hexc('#5a8ad8')); put(F, x - 1, y + dy, hexc('#5a8ad8')); put(F, x + 1, y + dy, hexc('#5a8ad8'))
        if t >= cs(L_STUDY, 2) - 0.05:
            ctag(F, 'OLDEST: A BIT HIGHER', 640, px=6)
            for k in range(24):
                if k % 4 == 0:
                    x = 20 + (k % 12) * 13; y = 66 + (k // 12) * 16
                    for dx in (-3, 0, 3): put(F, x + dx, y - 5, hexc('#ffcc4a'))
    elif i in (L_THEORY, L_SMARTER):                             # you taught them everything -> teaching made YOU smarter
        board(F, 58, 58, '1+1=2')
        you(F, 40, mood='happy' if i == L_THEORY else 'proud', arms='up' if (t * 2) % 2 < 1 else 'down', cap=i == L_SMARTER)
        kid(F, 144, mood='shock' if i == L_THEORY else 'happy')
        if i == L_THEORY:
            if t < cs(L_THEORY, 1) - 0.05: ctag(F, 'ONE THEORY', 260, px=8)
            elif t < cs(L_THEORY, 4) - 0.05: ctag(F, 'YEARS OF EXPLAINING', 260, px=6)
            else:
                k = ramp(t, cs(L_THEORY, 4), 0.6); glow(F, 40, 104, 26, '#ffe27a', 0.45 * k); sparkles(F, 40, 104, 22, 9, t, n=8)
                ctag(F, 'BRAIN: STRONGER', 260, px=7)
        else:
            glow(F, 40, 104, 26, '#ffe27a', 0.4); sparkles(F, 40, 104, 22, 9, t, n=8)
            if t >= cs(L_SMARTER, 2) - 0.05: ctag(F, 'THEY MADE YOU SMARTER', 260, px=6)
            else: ctag(F, 'NOT DUMB', 260, px=9)
    elif i == L_NOBODY:
        you(F, 60, mood='shock'); kid(F, 124, mood='proud')
        k = ramp(t, SEG[L_NOBODY][0], 0.4); F *= 1 - 0.55 * k
        glow(F, 90, 110, 46, '#ffcc4a', 0.25 * k); ctag(F, 'NOBODY TELLS YOU', 300, px=7)
    elif i == L_STRICT:                                          # parents less strict: grounded for a B, cookie for a C
        draw_santa(F, 90); bk.label(F, 'DAD', 470, 440, int(90 * S), int((GROUND - 52) * S), px=6)
        if t < cs(L_STRICT, 2) - 0.05: ctag(F, 'LESS STRICT EACH KID', 260, px=6)
        if t >= cs(L_STRICT, 2) - 0.05:
            you(F, 30, mood='sad'); card(F, 30, 56, 'B', 'GROUNDED' if t >= cs(L_STRICT, 3) - 0.05 else None)
        if t >= cs(L_STRICT, 4) - 0.05:
            kid(F, 150, mood='proud'); card(F, 150, 56, 'C')
            cookie(F, 150, GROUND - 52 - 6 * abs(math.sin(t * 4)))
            for k in range(3):
                ph = (t * 0.8 + k / 3) % 1; heart(F, 140 + k * 8, GROUND - 60 - ph * 20, 1 - ph)
    elif i == L_FOUR:                                            # 4 out of 10 families: the younger one is smarter
        for k in range(10):
            x = 22 + (k % 5) * 34; y = 72 + (k // 5) * 30; win = k < 4 and t >= cs(L_FOUR, 2) - 0.05
            col = '#3a8aff' if win else '#5a6478'
            for dx in range(-8, 9):
                for dy in range(-8, 9):
                    if dx * dx + dy * dy <= 64: put(F, x + dx, y + dy, hexc(col))
            if win:
                for dx in range(-4, 5): put(F, x + dx, y - 11, hexc('#ffcc4a'))
                for dx in (-4, 0, 4): put(F, x + dx, y - 12, hexc('#ffcc4a')); put(F, x + dx, y - 13, hexc('#ffcc4a'))
            bk.pixel_text(F, 'KID' if win else '', int((x - 7) * S), int((y - 3) * S), px=3, colr=(255, 255, 255))
        big_num(F, '4 / 10', 200, px=12, colr=(255, 200, 58) if t >= cs(L_FOUR, 1) - 0.05 else (150, 160, 190))
        if t >= cs(L_FOUR, 3) - 0.05: ctag(F, 'YOUNGER = SMARTER', 1000 - 60 - 200 + 30, px=6)
    elif i == L_NICE:                                            # be nice: one day they might be the genius
        you(F, 52, mood='shock' if t >= cs(L_NICE, 1) - 0.05 else 'happy')
        gen = t >= cs(L_NICE, 2) - 0.05
        kid(F, 128, mood='proud', cap=gen, arms='up' if gen else 'down', bob=abs(math.sin(t * 5)) * 2 if gen else 0)
        if not gen: ctag(F, 'BE NICE', 300, px=10)
        else: ctag(F, 'FUTURE GENIUS', 300, px=8); sparkles(F, 128, 110, 24, 10, t, n=8)
    else:                                                        # CTA: send this to your younger sibling + naughty list
        kid(F, 150, mood='happy')
        if t < cs(L_CTA, 2) - 0.05:
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(760 * pop), int(200 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 250
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    tx1, tx2 = 'SEND THIS TO', 'YOUR SIBLING'
                    bk.pixel_text(F, tx1, X + (bw - (len(tx1) * 42 - 7)) // 2, Y + 40, px=7, colr=(20, 24, 40))
                    bk.pixel_text(F, tx2, X + (bw - (len(tx2) * 42 - 7)) // 2, Y + 115, px=7, colr=(30, 90, 200))
            you(F, 40, mood='proud')
        else:
            sl = ramp(t, cs(L_CTA, 2) - 0.05, 0.5)
            draw_santa(F, lerp(-30, 40, sl), bob=abs(math.sin(t * 3)) * 1.2)
            if sl > 0.9:
                c, M = sv.spr('scroll', ch.scroll); pv.blit_hr(F, c, M, 66, GROUND - 46, 1)
                bk.pixel_text(F, 'NAUGHTY', int(68 * S) + 2, int((GROUND - 38) * S), px=3, colr=(200, 30, 40))
                ctag(F, 'NAUGHTY LIST', 300, px=8)

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
SHOUTS = [SEG[L_DUMB][0], cs(L_SUB, 2), SEG[L_NOBODY][0]]
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    rv.snow(F, t)
    if i >= 2 and 0 <= t - SEG[i][0] < 0.12 and i not in (L_TWO, L_SMARTER):
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
