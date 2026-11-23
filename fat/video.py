"""'Why Is It So Hard To Lose Weight?' - FLIP formula, roast hook with a bleep, Jett narration sped up 1.1x.
YOU = chubby green elf (torso widened, belly jiggles). Leptin meter, panicking brain, a weight-loss TV stage,
-500 CAL/DAY with a meal vanishing, hunter vs desk elf with the same calories, crash diet vs small changes.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT_, 'style_study')); sys.path.insert(0, os.path.join(ROOT_, 'mom_finds'))
import importlib.util
_s = importlib.util.spec_from_file_location('hussv', os.path.join(ROOT_, 'huss', 'video.py'))
hv = importlib.util.module_from_spec(_s); _s.loader.exec_module(hv)                 # shared props: brain, strike, thick...
lv, ys, fm, b1, sv, rv, pv, bk, ch = hv.lv, hv.ys, hv.fm, hv.b1, hv.sv, hv.rv, hv.pv, hv.bk, hv.ch
import ui, props, scenery
from chubby import widen

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
glow, ctag, big_num, disc = sv.glow, sv.ctag, sv.big_num, sv.disc
draw_santa, shadow, heart, meter = b1.draw_santa, b1.shadow, b1.heart, b1.meter
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
BEEP = json.load(open(os.path.join(HERE, 'beep.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
(L_HOOK, L_FLIP, L_HOW, L_WEAK, L_SUB, L_STUDY, L_MEAL, L_TWIST, L_FIX, L_CTA) = range(10)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))
def after(t, line, k): return t >= cs(line, k) - 0.05
def elf(F, cx, who='holly', **kw): return lv.draw_elf(F, cx, who, **kw)
strike, brain = hv.strike, hv.brain

_C = {}
def chubby(F, cx, t, k=1.45, mood='happy', jiggle=0.0, bob=0.0, outfit=('#2f9a52', '#1f7a3e')):
    """chubby elf; k = how wide the belly is, jiggle = wobble amount (belly width breathes in and out)"""
    kk = k + jiggle * 0.08 * math.sin(t * 22)
    key = (round(kk, 2), mood, outfit)
    if key not in _C:
        args = dict(b1.HOLLY); args.update(outfit=outfit[0], outfit_d=outfit[1], hat=outfit[0], mood=mood)
        c, M = ch.elf(**args); _C[key] = widen(c, M, kk)
    c, M = _C[key]; w_ = M.shape[1]
    shadow(F, cx, GROUND + 1, 30 * kk * max(0.6, 1 - bob / 30)); pv.blit_hr(F, c, M, cx - w_ / 2, GROUND + 1 - 53 - bob, 1)
    return GROUND + 1 - 53 - bob

# ---------- props ----------
def stage(F, cx, t):
    """TV studio stage: spotlights, a lit sign, a raised platform"""
    for k, sx in enumerate((cx - 50, cx + 50)):                            # two spotlights aimed at the middle
        glow(F, sx, 40, 10, '#fff6c0', 0.5)
        yy, xx = np.mgrid[40:GROUND + 2, 0:W].astype(np.float32)
        f = (yy - 40) / (GROUND + 1 - 40); lx = sx + (cx - sx) * f
        m = np.abs(xx - lx) < 3 + f * 12
        Y, X = np.nonzero(m)
        for y_, x_ in zip(Y[::3], X[::3]): put(F, x_, y_ + 40, hexc('#fff6c0'), 0.08)
    F[(GROUND + 1) * S:(GROUND + 5) * S, (cx - 60) * S:(cx + 60) * S] = hexc('#5a3a6a')     # platform
    F[(GROUND + 1) * S:(GROUND + 2) * S, (cx - 60) * S:(cx + 60) * S] = hexc('#ffcc4a')
    bw, bh = 600, 136; X0, Y0 = (WF - bw) // 2, 230                         # the show's sign with bulbs
    F[Y0:Y0 + bh, X0:X0 + bw] = hexc('#c8303a')
    for q in range(5): F[Y0 + q, X0:X0 + bw] = F[Y0 + bh - 1 - q, X0:X0 + bw] = NAVY; F[Y0:Y0 + bh, X0 + q] = F[Y0:Y0 + bh, X0 + bw - 1 - q] = NAVY
    for k in range(14):
        on = (int(t * 6) + k) % 2 == 0; bx = X0 + 20 + k * 43
        F[Y0 - 14:Y0 - 4, bx:bx + 10] = hexc('#fff6a0') if on else hexc('#8a7a40')
    for txt, yy_ in (('WEIGHT LOSS', 22), ('SHOW', 74)):
        bk.pixel_text(F, txt, X0 + (bw - (len(txt) * 36 - 6)) // 2, Y0 + yy_, px=6, colr=(255, 255, 255))
def plate(F, cx, cy, a, sc=2):
    """a plate with a roast drumstick, peas and a bun; a = 1 full, 0 gone (drawn at 2x)"""
    put_ = rv.put
    def put(F, x, y, col, al=1.0):
        X, Y = cx + (x - cx) * sc, cy + (y - cy) * sc
        for dx in range(sc):
            for dy in range(sc): put_(F, X + dx, Y + dy, col, al)
    def disc(F, x, y, r, col): [put(F, x + i, y + j, hexc(col)) for i in range(-2, 3) for j in range(-2, 3) if i * i + j * j <= r * r]
    for k in range(-14, 15):
        for j in range(-4, 5):
            if (k / 14) ** 2 + (j / 4.2) ** 2 <= 1: put(F, cx + k, cy + j, hexc('#f4f6fb') if (k / 11) ** 2 + (j / 3.2) ** 2 > 1 else hexc('#d8dee8'))
    if a <= 0: return
    for k in range(-6, 7):
        for j in range(-4, 4):
            if (k / 6.5) ** 2 + (j / 4) ** 2 <= 1: put(F, cx - 2 + k, cy - 3 + j, hexc('#a8582a') if j < 1 else hexc('#7a3a18'), a)
    for k in range(5): put(F, cx + 5 + k, cy - 5 - k * 0.5, hexc('#f4ecd8'), a)
    disc(F, cx + 10, cy - 8, 1.3, '#f4ecd8')
    for k, (px_, py_) in enumerate(((cx + 7, cy - 1), (cx + 9, cy), (cx + 8, cy + 1))): put(F, px_, py_, hexc('#5ae07a'), a)
    for k in range(-3, 4):
        for j in range(-2, 2): put(F, cx - 10 + k, cy - 2 + j, hexc('#e8a84a'), a)
def spear(F, x, y):
    for k in range(26): put(F, x + k * 0.15, y - k, hexc('#8a5a36'))
    for k in range(4): put(F, x + 3.9, y - 26 - k, hexc('#c4ccd8')); put(F, x + 3.9 - (3 - k) * 0.4, y - 26 - k, hexc('#c4ccd8'))
def desk(F, cx):
    F[(GROUND - 20) * S:(GROUND - 17) * S, (cx - 22) * S:(cx + 2) * S] = hexc('#8a5a36')                  # desk top
    for lx in (cx - 21, cx): F[(GROUND - 17) * S:(GROUND + 1) * S, lx * S:(lx + 2) * S] = hexc('#6a4226')
    F[(GROUND - 28) * S:(GROUND - 21) * S, (cx - 18) * S:(cx - 7) * S] = hexc('#3a4664')                  # laptop screen
    F[(GROUND - 27) * S:(GROUND - 22) * S, (cx - 17) * S:(cx - 8) * S] = hexc('#7ad8ff')
    F[(GROUND - 21) * S:(GROUND - 20) * S, (cx - 20) * S:(cx - 5) * S] = hexc('#c4ccd8')
def flex_glow(F, cx, t, k):
    if k > 0: glow(F, cx, GROUND - 26, 34, '#ff3a3a', (0.25 + 0.12 * math.sin(t * 14)) * k)

def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t)
    if i == L_HOOK:                                              # ever wondered why you're so... BEEP... FAAAAT
        fat = t >= BEEP['fat'] - 0.05
        chubby(F, 90, t, k=1.5 if fat else 1.4, mood='shock' if fat else 'happy', jiggle=1.0 if fat else 0.3)
        if BEEP['beep'] <= t < BEEP['beep'] + BEEP['len']:
            F[700:820, 260:820] = hexc('#1b1428'); big_num(F, 'BEEP!', 722, px=12, colr=(255, 60, 70))
        if fat: ui.callout(F, 'YOU', 14, 74, 72, GROUND - 40, px=6, accent='#ff5a64')
    elif i == L_FLIP:                                            # not lazy -> body FIGHTING you -> METABOLIC ADAPTATION
        if not after(t, L_FLIP, 2):
            chubby(F, 90, t, k=1.45, mood='sad'); ctag(F, 'LAZY?', 260, px=11)
            if t >= cs(L_FLIP, 1) + 0.3: strike(F, 292)
        elif not after(t, L_FLIP, 4):
            fight = after(t, L_FLIP, 3); flex_glow(F, 90, t, ramp(t, cs(L_FLIP, 3), 0.3))
            chubby(F, 90 + (2 * math.sin(t * 40) if fight else 0), t, k=1.45, mood='angry', jiggle=1.0 if fight else 0)
            ctag(F, 'YOUR BODY', 230, px=9)
            if fight: big_num(F, 'VS YOU', 360, px=10, colr=(255, 90, 100))
        else:
            chubby(F, 90, t, k=1.45, mood='shock'); k = ramp(t, cs(L_FLIP, 4), 0.4); F *= 1 - 0.45 * k
            glow(F, 90, 60, 60, '#ffcc4a', 0.3 * k); ctag(F, "IT'S CALLED", 220, px=7)
            if after(t, L_FLIP, 5):
                big_num(F, 'METABOLIC', 320, px=11, colr=(255, 200, 58)); big_num(F, 'ADAPTATION', 420, px=11, colr=(255, 200, 58))
    elif i == L_HOW:                                             # lose weight -> less leptin -> brain panics -> hunger up, energy down
        kk = 1.45 - 0.25 * ramp(t, SEG[L_HOW][0], 1.2)
        top = chubby(F, 64, t, k=kk, mood='shock' if after(t, L_HOW, 4) else 'happy')
        if not after(t, L_HOW, 1): ctag(F, 'LOSE WEIGHT', 260, px=9)
        elif not after(t, L_HOW, 4):
            meter(F, 140, 'LEPTIN', 0.9 - 0.75 * ramp(t, cs(L_HOW, 1), 1.5), '#ffcc4a', y_top=70, h_=60, w_=18)
            if after(t, L_HOW, 3): ctag(F, 'LEPTIN', 260, px=10)
        elif not after(t, L_HOW, 6):
            brain(F, 64, top - 10, t, ramp(t, cs(L_HOW, 4), 0.3))
            if after(t, L_HOW, 5):
                if (t * 6) % 1 < 0.5: glow(F, 64, top - 10, 30, '#ff3a3a', 0.4)
                ctag(F, 'PANIC!', 260, px=11)
        else:
            meter(F, 116, 'HUNGER', 0.2 + 0.75 * ramp(t, cs(L_HOW, 6), 0.6), '#ff5a64', y_top=70, h_=60, w_=16)
            if after(t, L_HOW, 7): meter(F, 158, 'ENERGY', 0.9 - 0.75 * ramp(t, cs(L_HOW, 7), 0.6), '#5ae07a', y_top=70, h_=60, w_=16)
    elif i == L_WEAK:                                            # not weak - your body thinks you're starving
        top = chubby(F, 90, t, k=1.3, mood='sad' if after(t, L_WEAK, 1) else 'happy')
        if not after(t, L_WEAK, 1):
            ctag(F, 'WEAK?', 260, px=11)
            if t >= cs(L_WEAK, 0) + 0.45: strike(F, 292)
        else:
            if (t * 5) % 1 < 0.55: glow(F, 90, top + 10, 40, '#ff3a3a', 0.3)
            hv.fm.bubble(F, 90, 48, 'STARVING!', px=8)
    elif i == L_SUB:                                             # tried every diet? SUBSCRIBE! the study's insane
        chubby(F, 90, t, k=1.4, mood='happy', jiggle=0.6 if after(t, L_SUB, 1) else 0)
        if not after(t, L_SUB, 1): ctag(F, 'EVERY DIET', 260, px=9)
        if after(t, L_SUB, 1): lv.corner_sub(F, t, cs(L_SUB, 1) - 0.05, cs(L_SUB, 1) + 0.3)
        if after(t, L_SUB, 2): ctag(F, 'THE STUDY', 520, px=9)
    elif i == L_STUDY:                                           # weight-loss TV show, 6 years, lost a ton, then -500 cal/day
        stage(F, 90, t)
        if not after(t, L_STUDY, 3):
            chubby(F, 90, t, k=1.5, outfit=('#d22a38', '#a0182a'))
            if after(t, L_STUDY, 2): big_num(F, f'YEAR {1 + int(5 * ramp(t, cs(L_STUDY, 2), 0.9))}', 420, px=9, colr=(255, 226, 122))
        elif not after(t, L_STUDY, 5):
            kk = 1.5 - 0.5 * ramp(t, cs(L_STUDY, 3), 0.9); chubby(F, 90, t, k=kk, mood='proud', outfit=('#d22a38', '#a0182a'))
            if after(t, L_STUDY, 4): ctag(F, 'LOST A TON', 420, px=9); b1.sparkles(F, 90, 110, 30, 28, t)
        else:
            chubby(F, 90, t, k=1.0 + 0.35 * ramp(t, cs(L_STUDY, 6), 2.0), mood='shock', outfit=('#d22a38', '#a0182a'))
            if not after(t, L_STUDY, 6): ctag(F, '6 YEARS LATER...', 420, px=8)
            if after(t, L_STUDY, 7): big_num(F, '-500 CAL', 400, px=12, colr=(255, 70, 80))
            if after(t, L_STUDY, 8): ctag(F, 'EVERY DAY', 500, px=8)
    elif i == L_MEAL:                                            # a whole meal your body refuses to burn, every day
        chubby(F, 52, t, k=1.4, mood='sad')
        a = 1.0 - ramp(t, cs(L_MEAL, 1), 0.8) if not after(t, L_MEAL, 2) else ((t * 1.2) % 1 < 0.6) * 1.0
        plate(F, 124, GROUND - 26, a); ctag(F, 'A WHOLE MEAL', 260, px=9)
        if after(t, L_MEAL, 2): big_num(F, f'DAY {1 + int(364 * ramp(t, cs(L_MEAL, 2), 1.2))}', 520, px=9, colr=(255, 226, 122))
    elif i == L_TWIST:                                           # can't outrun it: hunter-gatherers = desk workers
        if not after(t, L_TWIST, 2):
            chubby(F, 90, t, k=1.4, mood='shock'); k = ramp(t, SEG[L_TWIST][0], 0.4); F *= 1 - 0.5 * k
            glow(F, 90, 110, 46, '#ffcc4a', 0.25 * k); ctag(F, 'NOBODY TELLS YOU', 300, px=7)
        elif not after(t, L_TWIST, 3):
            chubby(F, 90, t, k=1.4, mood='angry', bob=abs(math.sin(t * 14)) * 3, jiggle=1.0)
            ctag(F, "CAN'T OUTRUN IT", 260, px=8)
        else:
            hx = 46 + 4 * math.sin(t * 2.5)
            elf(F, hx, 'tinsel', bob=abs(math.sin(t * 8)) * 1.5, outfit='#c8823a', outfit_d='#9a5a22', hat='#c8823a'); spear(F, hx + 12, GROUND - 6)
            ctag(F, 'HUNTER', 230, px=7) if not after(t, L_TWIST, 5) else None
            if after(t, L_TWIST, 5):
                desk(F, 146); elf(F, 128, 'tinsel', outfit='#7a4ac8', outfit_d='#5a2ea0', hat='#7a4ac8')
                props.text_center(F, 'WALKS ALL DAY', 46, 74, px=5, colr=(255, 226, 122)); props.text_center(F, 'SITS ALL DAY', 132, 74, px=5, colr=(200, 215, 255))
                if after(t, L_TWIST, 6): big_num(F, '=', 600, px=14, colr=(255, 255, 255)); ctag(F, 'SAME CALORIES', 260, px=8)
    elif i == L_FIX:                                             # forget crazy diets; small changes kept forever win
        crash = 0.9 * (1 - ramp(t, SEG[L_FIX][0] + 0.4, 0.5)) + 0.1 * ramp(t, SEG[L_FIX][0] + 0.9, 0.3)
        meter(F, 26, 'CRASH', crash, '#ff5a64', y_top=70, h_=60, w_=16)
        if after(t, L_FIX, 1): meter(F, 154, 'SMALL', 0.1 + 0.85 * ramp(t, cs(L_FIX, 1), 2.0), '#5ae07a', y_top=70, h_=60, w_=16)
        kk = 1.4 - 0.25 * ramp(t, cs(L_FIX, 1), 2.4)
        chubby(F, 90, t, k=kk, mood='proud' if after(t, L_FIX, 3) else 'happy', bob=abs(math.sin(t * 6)) * 2 if after(t, L_FIX, 3) else 0)
        if not after(t, L_FIX, 1): ctag(F, 'CRAZY DIETS', 260, px=9); strike(F, 292) if t >= SEG[L_FIX][0] + 0.5 else None
        elif after(t, L_FIX, 3): ctag(F, 'WIN', 260, px=12); b1.sparkles(F, 90, 110, 34, 30, t)
        else: ctag(F, 'SMALL CHANGES', 260, px=8)
    else:                                                        # CTA: send this to your diet friend + naughty list
        chubby(F, 150, t, k=1.25, mood='happy')
        if not after(t, L_CTA, 3):
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(820 * pop), int(200 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 250
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    for tx, yy_, col in (('SEND THIS TO', 40, (20, 24, 40)), ('YOUR DIET FRIEND', 115, (200, 40, 60))):
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
    if t < SEG[1][0] + 0.4:
        y0 = rv.CAP_Y + 140; x0 = WF // 2 - 35
        for r_, row in enumerate(rv.HEADPHONES):
            for c_, bb in enumerate(row):
                if bb == '1': F[y0 + r_ * 7:y0 + r_ * 7 + 7, x0 + c_ * 7:x0 + c_ * 7 + 7] = 1.0
SHOUTS = [BEEP['beep'], BEEP['fat'], cs(L_FLIP, 3), cs(L_SUB, 1), SEG[L_TWIST][0]]
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    rv.snow(F, t)
    if i >= 1 and 0 <= t - SEG[i][0] < 0.12 and i not in (L_SUB,):
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
