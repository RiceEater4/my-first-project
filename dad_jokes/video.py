"""'What If Dad Jokes Were Bad On Purpose?' - direct explainer (younger-sibling v2 order), Jett narration.
YOU = green elf, DAD = Santa, your future kid = short blue elf. Open-loop corner subscribe, clean callouts/bubbles.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study')); sys.path.insert(0, os.path.join(ROOT_, 'mom_finds'))
import importlib.util
_s = importlib.util.spec_from_file_location('lsv', os.path.join(ROOT_, 'late_school', 'video.py'))
lv = importlib.util.module_from_spec(_s); _s.loader.exec_module(lv)            # helpers: corner_sub, you(), etc.
ys, fm, b1, sv, rv, pv, bk, ch = lv.ys, lv.fm, lv.b1, lv.sv, lv.rv, lv.pv, lv.bk, lv.ch
import ui, props, scenery

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
glow, ctag, big_num = sv.glow, sv.ctag, sv.big_num
draw_santa, draw_prof, shadow, heart, sparkles, meter = b1.draw_santa, b1.draw_prof, b1.shadow, b1.heart, b1.sparkles, b1.meter
bubble = fm.bubble
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
(L_HOOK, L_WORST, L_JOKE, L_PURPOSE, L_TROLL, L_SUB, L_WHY, L_EYEROLL, L_NOBODY, L_FUTURE, L_CTA) = range(11)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))
def you(F, cx, mood='happy', **kw): return lv.you(F, cx, mood=mood, **kw)
def kid(F, cx, mood='happy', **kw): return ys.kid(F, cx, mood=mood, **kw)
def dad(F, cx, bob=0.0): draw_santa(F, cx, bob=bob)
def corner_sub(F, t, t0, press): lv.corner_sub(F, t, t0, press)
def laugh(F, x, y, t):
    for k, (dx, dy) in enumerate(((0, 0), (14, -6))):
        if (t * 3 + k) % 2 < 1.4: bk.pixel_text(F, 'HA', int((x + dx) * S), int((y + dy) * S), px=6, colr=(255, 226, 122))
def groan_meter(F, val, x=150, top=60, h_=70):
    meter(F, x, 'GROAN', val, '#ff5a64', y_top=top, h_=h_, w_=18)
def drum_hit(F, t, t0):
    k = ramp(t, t0, 0.15)
    if t >= t0 and t < t0 + 1.2: big_num(F, 'BA-DUM-TSS!', 220, px=9, colr=(255, 200, 58))
def tally(F, n, cx=90, y=60):
    for k in range(min(n, 20)):
        gx = cx - 40 + (k % 10) * 9 + (k // 10) * 0; gy = y + (k // 10) * 14
        for j in range(8): props._put(F, gx + (3 if (k % 5) == 4 else 0) * (j / 8), gy + j, hexc('#f4f6fb'))
def shield(F, cx, cy, r, t, k):
    if k <= 0: return
    yy, xx = np.mgrid[0:H, 0:W]; d = np.hypot((xx - cx) / 1.0, (yy - cy) / 1.25)
    m = (np.abs(d - r) < 1.2) & (BAY[yy % 4, xx % 4] < 0.85 * k)
    A = np.repeat(np.repeat(m.astype(np.float32), S, 0), S, 1)[..., None] * 0.85
    F[:] = F * (1 - A) + hexc('#7ad8ff') * A
    glow(F, cx, cy, r, '#5aa0ff', 0.22 * k)

def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t); a = t - SEG[i][0]
    if i == L_HOOK:
        you(F, 44, mood='happy'); dad(F, 130)
        if t >= cs(L_HOOK, 1) - 0.05: ui.callout(F, 'DAD', 150, 58, 140, GROUND - 46, px=6, accent='#ff5a64')
    elif i == L_WORST:
        jump = 6 * abs(math.sin(a * 9)) * math.exp(-a * 1.2)
        you(F, 44, mood='angry', bob=jump); dad(F, 130, bob=abs(math.sin(t * 5)) * 2)
        ctag(F, 'WORST JOKES', 300, px=10)
    elif i == L_JOKE:                                            # "Hi hungry, I'm Dad" -> groan -> he laughs -> every time
        groan = t >= cs(L_JOKE, 2) - 0.05; laughs = t >= cs(L_JOKE, 3) - 0.05; every = t >= cs(L_JOKE, 4) - 0.05
        you(F, 44, mood='sad' if groan else 'happy'); dad(F, 132, bob=abs(math.sin(t * 7)) * 2 if laughs else 0)
        if not groan: bubble(F, 122, 52, "HI HUNGRY, I'M DAD!", px=6)
        else:
            if not every: drum_hit(F, t, cs(L_JOKE, 2) - 0.05)
            bk.pixel_text(F, 'UGH', int(34 * S), int((GROUND - 72) * S), px=7, colr=(200, 215, 255))
        if laughs: laugh(F, 140, GROUND - 70, t)
        if every:
            n = int(1 + 846 * ramp(t, cs(L_JOKE, 4), max(0.4, SEG[L_JOKE][1] - cs(L_JOKE, 4))))
            big_num(F, f'JOKES TOLD: {n}', 200, px=9, colr=(255, 200, 58)); ctag(F, 'EVERY SINGLE TIME', 330, px=6)
    elif i in (L_PURPOSE, L_TROLL, L_SUB):                       # just bad? researcher: on purpose, the groan IS the joke
        if i == L_PURPOSE and t < cs(L_PURPOSE, 2) - 0.05:
            dad(F, 90); ctag(F, 'JUST BAD AT JOKES?', 300, px=7)
        elif i == L_PURPOSE and t < cs(L_PURPOSE, 4) - 0.05:
            draw_prof(F, 52); dad(F, 128); ctag(F, 'A RESEARCHER', 300, px=8)
        else:
            you(F, 40, mood='angry' if i != L_SUB else 'sad'); dad(F, 104, bob=abs(math.sin(t * 6)) * 2)
            g = ramp(t, cs(L_PURPOSE, 6) if i == L_PURPOSE else SEG[L_PURPOSE][0], 0.8) if i == L_PURPOSE else 1.0
            groan_meter(F, 0.15 + 0.8 * g, x=156, top=70, h_=60)
            if i == L_PURPOSE:
                if t < cs(L_PURPOSE, 6) - 0.05: ctag(F, 'NOPE. ON PURPOSE', 260, px=7)
                elif t < cs(L_PURPOSE, 7) - 0.05: ctag(F, 'GROAN = THE JOKE', 260, px=7)
                else: ctag(F, 'WEAPONIZED ANTI-HUMOR', 260, px=6)
            elif i == L_TROLL:
                if t < cs(L_TROLL, 1) - 0.05:
                    ctag(F, 'FAILING', 260, px=10)
                    for k in range(-150, 150, 2): F[int(294 + k * 0.1):int(302 + k * 0.1), 540 + k:542 + k] = hexc('#e8303a')
                else:
                    ctag(F, 'TROLLING YOU', 260, px=9); laugh(F, 112, GROUND - 70, t)
            else:
                laugh(F, 112, GROUND - 70, t)
                if t >= cs(L_SUB, 2) - 0.05: corner_sub(F, t, cs(L_SUB, 2) - 0.05, cs(L_SUB, 2) + 0.3)
                if t >= cs(L_SUB, 3) - 0.05:
                    ctag(F, 'KIND OF SWEET', 960, px=7)
                    for k in range(3):
                        ph = (t * 0.8 + k / 3) % 1; heart(F, 96 + k * 8, 96 - ph * 24, 1 - ph)
    elif i == L_WHY:                                             # teasing = a little safe embarrassment -> handle cringe
        you(F, 52, mood='sad' if t < cs(L_WHY, 6) - 0.05 else 'proud'); dad(F, 132, bob=abs(math.sin(t * 5)) * 1.5)
        if t < cs(L_WHY, 2) - 0.05: ctag(F, 'TEASING', 280, px=10)
        elif t < cs(L_WHY, 5) - 0.05:
            meter(F, 92, 'CRINGE', 0.3, '#ffcc4a', y_top=66, h_=50, w_=16)
            ui.callout(F, 'SAFE ZONE', 104, 64, 100, 108, px=5, accent='#5ae07a')
            ctag(F, 'A LITTLE EMBARRASSMENT', 960, px=6)
        else:
            k = ramp(t, cs(L_WHY, 6), 0.8); shield(F, 52, 118, 30, t, k)
            ctag(F, 'CRINGE SHIELD', 280, px=9)
    elif i == L_EYEROLL:                                         # every eye roll = training
        you(F, 60, mood='proud', arms='up', bob=abs(math.sin(t * 5)) * 2); shield(F, 60, 118, 30, t, 1.0)
        n = int(1 + 8 * ramp(t, SEG[L_EYEROLL][0], 1.2)); big_num(F, f'EYE ROLLS: {n}', 220, px=8, colr=(200, 215, 255))
        if t >= cs(L_EYEROLL, 1) - 0.05:
            meter(F, 140, 'POWER', 0.2 + 0.75 * ramp(t, cs(L_EYEROLL, 1), 0.8), '#5ae07a', y_top=84, h_=50, w_=18)
            ctag(F, "THAT'S TRAINING", 330, px=8)
    elif i == L_NOBODY:
        you(F, 60, mood='shock'); dad(F, 124)
        k = ramp(t, SEG[L_NOBODY][0], 0.4); F *= 1 - 0.55 * k
        glow(F, 90, 110, 46, '#ffcc4a', 0.25 * k); ctag(F, 'NOBODY TELLS YOU', 300, px=7)
    elif i == L_FUTURE:                                          # one day YOU do it too; your kid groans; you get it
        if t < cs(L_FUTURE, 1) - 0.05:
            you(F, 90, mood='shock'); ctag(F, 'ONE DAY...', 300, px=10)
        else:
            you(F, 58, mood='proud', bob=abs(math.sin(t * 6)) * 1.5); kid(F, 132, mood='sad' if t >= cs(L_FUTURE, 2) - 0.05 else 'happy')
            ui.callout(F, 'YOU (DAD)', 4, 84, 48, GROUND - 52, px=5, accent='#5ae07a')
            if t < cs(L_FUTURE, 2) - 0.05: bubble(F, 64, 52, "HI HUNGRY, I'M DAD!", px=6)
            else:
                bk.pixel_text(F, 'UGH', int(140 * S), int((GROUND - 62) * S), px=7, colr=(200, 215, 255))
                if t >= cs(L_FUTURE, 3) - 0.05:
                    ctag(F, "YOU'LL GET IT", 300, px=9)
                    for k in range(4):
                        ph = (t * 0.8 + k / 4) % 1; heart(F, 80 + k * 8, 96 - ph * 26, 1 - ph)
    else:                                                        # CTA: send this to your dad + naughty list
        you(F, 150, mood='happy')
        if t < cs(L_CTA, 2) - 0.05:
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(760 * pop), int(200 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 250
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    tx1, tx2 = 'SEND THIS TO', 'YOUR DAD'
                    bk.pixel_text(F, tx1, X + (bw - (len(tx1) * 42 - 7)) // 2, Y + 40, px=7, colr=(20, 24, 40))
                    bk.pixel_text(F, tx2, X + (bw - (len(tx2) * 42 - 7)) // 2, Y + 115, px=7, colr=(200, 40, 60))
        else:
            sl = ramp(t, cs(L_CTA, 2) - 0.05, 0.5)
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
SHOUTS = [SEG[L_WORST][0], cs(L_SUB, 2), SEG[L_NOBODY][0]]
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    rv.snow(F, t)
    if i >= 2 and 0 <= t - SEG[i][0] < 0.12 and i not in (L_TROLL, L_SUB, L_EYEROLL):
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
