"""'What If Being Late to School Made You a Genius?' - direct explainer (younger-sibling v2 order), Jett narration.
YOU = green elf, TEACHER = red elf. Detailed props + aligned anchors, clean callouts/bubbles (style_study/ui.py).
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study')); sys.path.insert(0, os.path.join(ROOT_, 'mom_finds'))
import importlib.util
_s = importlib.util.spec_from_file_location('ysv', os.path.join(ROOT_, 'younger_sibling', 'video.py'))
ys = importlib.util.module_from_spec(_s); _s.loader.exec_module(ys)
fm, b1, sv, rv, pv, bk, ch = ys.fm, ys.b1, ys.sv, ys.rv, ys.pv, ys.bk, ys.ch
import ui, props, scenery

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
glow, ctag, big_num = sv.glow, sv.ctag, sv.big_num
draw_elf, draw_santa, draw_prof, shadow, heart, sparkles, meter = b1.draw_elf, b1.draw_santa, b1.draw_prof, b1.shadow, b1.heart, b1.sparkles, b1.meter
sub_button = fm.sub_button
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
(L_HOOK, L_GENIUS, L_SNOOZE, L_SCIENCE, L_SEVEN, L_SUB, L_SEATTLE, L_DOCTORS, L_LAZY, L_NOBODY, L_TEACHER, L_TIPS,
 L_CTA) = range(13)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))

_c = {}
def spr(key, fn):
    if key not in _c: _c[key] = fn()
    return _c[key]
def you(F, cx, mood='happy', one_shoe=False, **kw):
    x, top = ys.you(F, cx, mood=mood, **kw)
    if one_shoe:                                             # left foot in a white sock instead of a brown shoe
        bob = kw.get('bob', 0.0); y0 = GROUND + 1 - 53 - bob; x0 = cx - 19
        for dx in range(-4, 5):
            for dy in range(-2, 3):
                if (dx / 4.2) ** 2 + (dy / 2) ** 2 <= 1: props._put(F, x0 + 13 + dx, y0 + 50 + dy, hexc('#f4f6fb') if dy < 1 else hexc('#d8dee8'))
    return top
def teacher(F, cx, mood='angry', **kw): return draw_elf(F, cx, 'holly', mood=mood, **kw)[1]
def alarm_clock(F, cx, feet, t, ringing=False):
    def mk():
        L = ch.Layers(30, 30); yy, xx = np.mgrid[0:30, 0:30].astype(np.float32)
        for bx in (8, 22): L.add(np.hypot(xx - bx, yy - 5) <= 4, hexc('#ffcc4a'))
        L.add((np.abs(xx - 8) < 1.5) & (yy >= 23) & (yy < 28) | (np.abs(xx - 22) < 1.5) & (yy >= 23) & (yy < 28), hexc('#3a4664'))
        body = np.hypot(xx - 15, yy - 15) <= 11
        def bf(c, m):
            c[m] = hexc('#e8303a'); c[m & (xx > 19)] = hexc('#b81e2a')
            face = np.hypot(xx - 15, yy - 15) <= 8; c[face] = hexc('#f4f6fb'); c[face & (yy > 19)] = hexc('#d8dee8')
            for k in range(12):
                th = TAU * k / 12; c[(np.abs(xx - (15 + 6.5 * math.sin(th))) < 0.6) & (np.abs(yy - (15 - 6.5 * math.cos(th))) < 0.6)] = hexc('#3a4664')
            c[seg_(xx, yy, 15, 15, 15, 10)] = hexc('#1b1428'); c[seg_(xx, yy, 15, 15, 19, 15)] = hexc('#1b1428')
            c[(np.abs(xx - 15) < 0.6) & (np.abs(yy - 15) < 0.6)] = hexc('#e8303a')
        L.add(body, bf)
        return L.out()
    c, M = spr('alarm', mk); jx = (math.sin(t * 60) * 1.2) if ringing else 0
    shadow(F, cx, feet, 26); props._blit(F, c, M, cx - 15 + jx, feet - 29)
    if ringing:
        for sd in (-1, 1):
            for k in range(3): props._put(F, cx + sd * (19 + k * 2), feet - 22 - k * 3 + (t * 20 % 2), hexc('#ffffff'), 0.9)
def seg_(xx, yy, ax, ay, bx, by): return ch.seg(xx, yy, ax, ay, bx, by) <= 0.8
def clock_face(F, cx, cy, r, hours, label, colr=(255, 255, 255)):
    sv.disc(F, cx, cy, r, '#f4f6fb', ring='#c8d0e0')
    for k in range(12):
        th = TAU * k / 12; props._put(F, cx + (r - 3) * math.sin(th), cy - (r - 3) * math.cos(th), hexc('#3a4664'))
    sv.hand(F, cx, cy, TAU * (hours % 12) / 12, r * 0.5, w=2); sv.hand(F, cx, cy, 0, r * 0.78, '#e8303a'); props._put(F, cx, cy, hexc('#1b1428'))
    props.text_center(F, label, cx, cy + r + 4, px=5, colr=colr)
def school(F, cx, feet=GROUND + 1): scenery.school(F, cx, feet, shadow_fn=shadow)
def sun(F, cx, cy, t, k=1.0):
    if k <= 0: return
    glow(F, cx, cy, 30 * k, '#ffe27a', 0.5 * k); sv.disc(F, cx, cy, 9 * k + 1, '#ffcc4a', ring='#ff9a3a')
    for j in range(10):
        th = TAU * j / 10 + t * 0.6
        for r in range(13, 18): props._put(F, cx + r * k * math.cos(th), cy + r * k * math.sin(th), hexc('#ffe27a'), 0.9)
def moon(F, cx, cy):
    sv.disc(F, cx, cy, 8, '#f4f0d0', ring='#d8d0a0'); sv.disc(F, cx + 4, cy - 2, 6, '#1f4782')
def zzz(F, x, y, t):
    for k in range(3):
        ph = (t * 0.7 + k / 3) % 1; bk.pixel_text(F, 'Z', int((x + ph * 12) * S), int((y - ph * 22) * S), px=4 + k, colr=(225, 235, 255))

def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t); a = t - SEG[i][0]
    if i == L_HOOK:
        you(F, 60, mood='shock', one_shoe=True); school(F, 136)
        ui.callout(F, 'LATE AGAIN', 4, 72, 52, GROUND - 50, px=5, accent='#ff5a64')
    elif i == L_GENIUS:
        jump = 8 * abs(math.sin(a * 7)) * math.exp(-a * 1.3)
        you(F, 90, mood='proud', arms='up', cap=True, bob=jump); sparkles(F, 90, 100, 32, 12, t)
        ctag(F, 'GENIUS', 300, px=12)
    elif i == L_SNOOZE:                                          # snooze x3, then running in with one shoe
        run = cs(L_SNOOZE, 4) - 0.05
        if t < run:
            n = sum(1 for k in (1, 2, 3) if t >= cs(L_SNOOZE, k) - 0.05)
            you(F, 52, mood='sad' if n else 'happy'); zzz(F, 62, 96, t)
            alarm_clock(F, 122, GROUND + 1, t, ringing=(n == 0) or ((t - cs(L_SNOOZE, max(1, n))) % 1.0 > 0.6))
            if n: big_num(F, 'SNOOZE' + ' X' + str(n), 230, px=9, colr=(255, 200, 58))
            else: ctag(F, 'LOOK AT YOU', 300, px=8)
        else:
            f = ramp(t, run, 1.6); school(F, 140)
            x = lerp(-20, 78, f); you(F, x, mood='shock', one_shoe=True, bob=abs(math.sin(t * 14)) * 3 * (1 - f ** 4))
            for k in range(6): put(F, x - 22 - k * 4, GROUND - 2 - (k % 2) * 2, hexc('#eaf3ff'), 0.8 - k * 0.12)
            if t >= cs(L_SNOOZE, 5) - 0.05: ui.callout(F, 'ONE SHOE', max(4, int(x) - 50), 76, x - 6, GROUND - 1, px=5, accent='#ffcc4a')
    elif i in (L_SCIENCE, L_SEVEN):                              # actually smart? scientists: body clock shifts later
        if i == L_SCIENCE and t < cs(L_SCIENCE, 2) - 0.05:
            you(F, 90, mood='shock'); ctag(F, 'ACTUALLY SMART?', 300, px=8)
        elif i == L_SCIENCE and t < cs(L_SCIENCE, 4) - 0.05:
            draw_prof(F, 52); you(F, 128, mood='happy')
            ctag(F, 'SCIENTISTS TESTED IT' if t < cs(L_SCIENCE, 3) - 0.05 else 'KIND OF... YES', 300, px=6 if t < cs(L_SCIENCE, 3) - 0.05 else 8)
        elif i == L_SCIENCE:
            k = ramp(t, cs(L_SCIENCE, 5), 1.0)
            clock_face(F, 90, 104, 34, 7 - 2 * k, 'YOUR BODY CLOCK', (255, 200, 58))
            ctag(F, 'UP TO 2 HRS LATER', 230, px=7)
        else:
            clock_face(F, 48, 100, 26, 7, 'REAL: 7 AM'); clock_face(F, 132, 100, 26, 5, 'FEELS: 5 AM', (255, 200, 58))
            if t >= cs(L_SEVEN, 1) - 0.05: zzz(F, 150, 70, t)
            bk.pixel_text(F, '=', int(86 * S), int(94 * S), px=8, colr=(255, 255, 255))
    elif i == L_SUB:
        you(F, 60, mood='proud', arms='up', one_shoe=True, bob=abs(math.sin(t * 6)) * 3)
        if t >= cs(L_SUB, 2) - 0.05: sub_button(F, t, cs(L_SUB, 2) - 0.05, cs(L_SUB, 2) + 0.35)
        else: ctag(F, 'LATE TO 1ST PERIOD?', 300, px=6)
    elif i == L_SEATTLE:                                         # Seattle: school later -> +34 min sleep, grades up
        school(F, 50)
        moved = ramp(t, cs(L_SEATTLE, 1), 0.8)
        big_num(F, '7:50' if moved < 0.5 else '8:45', 220, px=11, colr=(255, 255, 255) if moved < 0.5 else (90, 224, 122))
        if t >= cs(L_SEATTLE, 3) - 0.05:
            meter(F, 118, 'SLEEP', 0.45 + 0.3 * ramp(t, cs(L_SEATTLE, 3), 0.8), '#5ea6f2', y_top=86, h_=56, w_=18)
            props.text_center(F, '+34 MIN', 118, 64, px=6, colr=(120, 200, 255))
        if t >= cs(L_SEATTLE, 5) - 0.05:
            meter(F, 156, 'GRADES', 0.5 + 0.2 * ramp(t, cs(L_SEATTLE, 5), 0.8), '#5ae07a', y_top=86, h_=56, w_=18)
            props.text_center(F, 'UP!', 156, 64, px=6, colr=(120, 240, 150))
    elif i == L_DOCTORS:                                         # doctors: not before 8:30
        draw_prof(F, 56); school(F, 136)
        if t >= cs(L_DOCTORS, 1) - 0.05: ui.callout(F, 'NOT BEFORE 8:30', 14, 64, 136, GROUND - 42, px=5, accent='#5ae07a')
        ctag(F, 'DOCTORS SAY', 230, px=8)
    elif i == L_LAZY:                                            # not lazy: different clock
        top = you(F, 50, mood='proud')
        if t < cs(L_LAZY, 1) - 0.05:
            ctag(F, 'LAZY', 300, px=11)
            for k in range(-140, 140, 2): F[int(334 + k * 0.1):int(342 + k * 0.1), 540 + k:542 + k] = hexc('#e8303a')
        else:
            bx, by = ui.thought_bubble(F, 108, 54, 110, 48, (62, top + 2), t)
            clock_face(F, bx + 30, by + 24, 12, 5, ''); bk.pixel_text(F, 'MY TIME', int((bx + 48) * S), int((by + 20) * S), px=6, colr=(20, 40, 90))
            if t >= cs(L_LAZY, 2) - 0.05: ctag(F, 'DIFFERENT CLOCK', 960, px=7)
    elif i == L_NOBODY:
        you(F, 60, mood='shock'); teacher(F, 124, mood='angry')
        k = ramp(t, SEG[L_NOBODY][0], 0.4); F *= 1 - 0.55 * k
        glow(F, 90, 110, 46, '#ffcc4a', 0.25 * k); ctag(F, 'NOBODY TELLS YOU', 300, px=7)
    elif i == L_TEACHER:                                         # the teacher does not care
        you(F, 44, mood='sad', one_shoe=True); teacher(F, 136, mood='angry')
        ui.callout(F, 'TEACHER', 108, 72, 136, GROUND - 54, px=5, accent='#ff5a64')
        if t >= cs(L_TEACHER, 1) - 0.05: big_num(F, 'LATE!', 220, px=14, colr=(255, 90, 90))
    elif i == L_TIPS:                                            # phone down an hour before bed; sunlight when you wake
        if t < cs(L_TIPS, 2) - 0.05:
            down = t >= cs(L_TIPS, 1) - 0.05
            F *= 0.72; moon(F, 146, 92)
            you(F, 54, mood='happy' if not down else 'proud', arms='hold' if not down else 'down')
            if not down:
                props.phone_in_hand(F, 54, GROUND + 1, 'hold'); glow(F, 54, GROUND - 22, 12, '#5ea6f2', 0.4)
                ctag(F, 'PHONE DOWN', 300, px=8)
            else:
                zzz(F, 64, 96, t); ctag(F, '1 HR BEFORE BED', 300, px=7)
        else:
            sk = ramp(t, cs(L_TIPS, 2), 0.8); sun(F, 136, 66, t, sk)
            you(F, 54, mood='proud', arms='up'); glow(F, 54, 120, 30, '#ffe27a', 0.3 * sk)
            for j in range(6): props._put(F, lerp(128, 66, ((t * 0.8 + j / 6) % 1)), lerp(72, 112, ((t * 0.8 + j / 6) % 1)), hexc('#ffe27a'))
            ctag(F, 'MORNING SUN' if t < cs(L_TIPS, 4) - 0.05 else 'CLOCK: EARLIER', 300, px=8)
    else:                                                        # CTA
        you(F, 150, mood='happy', one_shoe=True)
        if t < cs(L_CTA, 2) - 0.05:
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(760 * pop), int(200 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 250
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    tx1, tx2 = 'SEND THIS TO', 'YOUR LATE FRIEND'
                    bk.pixel_text(F, tx1, X + (bw - (len(tx1) * 42 - 7)) // 2, Y + 40, px=7, colr=(20, 24, 40))
                    bk.pixel_text(F, tx2, X + (bw - (len(tx2) * 42 - 7)) // 2, Y + 115, px=7, colr=(200, 40, 60))
        else:
            sl = ramp(t, cs(L_CTA, 2) - 0.05, 0.5)
            draw_santa(F, lerp(-30, 40, sl), bob=abs(math.sin(t * 3)) * 1.2)
            if sl > 0.9:
                scenery.naughty_list(F, 86, GROUND + 1, shadow_fn=shadow)
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
SHOUTS = [SEG[L_GENIUS][0], cs(L_SUB, 2), SEG[L_NOBODY][0], cs(L_TEACHER, 1)]
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    rv.snow(F, t)
    if i >= 2 and 0 <= t - SEG[i][0] < 0.12 and i not in (L_SEVEN,):
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
