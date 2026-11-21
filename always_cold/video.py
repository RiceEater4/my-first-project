"""'What If Being Always Cold Made You a Genius?' - straight-to-camera explainer, Jett narration (1080x1920, 60 fps).
Talks to YOU (the elf in hoodies + blanket acts it out). Screamed hook + screamed mid-video SUBSCRIBE, re-hook,
catch, tag + naughty-list ending. Invisible floor with soft shadows.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study'))
import importlib.util
_s = importlib.util.spec_from_file_location('fsm', os.path.join(ROOT_, 'fake_smile', 'video.py'))
fm = importlib.util.module_from_spec(_s); _s.loader.exec_module(fm)            # helpers (elves, bubbles, subscribe button...)
b1, sv, rv, pv, bk, ch = fm.b1, fm.sv, fm.rv, fm.pv, fm.bk, fm.ch

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
glow, ctag, ctext, big_num = sv.glow, sv.ctag, sv.ctext, sv.big_num
draw_elf, draw_santa = b1.draw_elf, b1.draw_santa
shadow, heart, sparkles, meter = b1.shadow, b1.heart, b1.sparkles, b1.meter
bubble, sub_button, eye_icon = fm.bubble, fm.sub_button, fm.eye_icon
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
(L_HOOK, L_GENIUS, L_ROOM, L_DRAMA, L_SUB, L_FORMULA, L_WOMEN, L_NOBODY, L_STUDY, L_CRANK, L_CATCH, L_CTA) = range(12)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))

_c = {}
def spr(key, fn):
    if key not in _c: _c[key] = fn()
    return _c[key]
HOOD = dict(outfit='#8a94a8', outfit_d='#6a7488')
def you(F, cx, mood='happy', shiver=0.0, blanket=True, t=0.0, cap=False, arms='down', bob=0.0, warm=0.0):
    """the viewer: an elf in a grey hoodie wrapped in a red plaid blanket, shivering"""
    jx = shiver * math.sin(t * 60) * 0.8
    _, top = draw_elf(F, cx + jx, 'tinsel', mood=mood, cap=cap, arms=arms, bob=bob, **HOOD)
    if blanket:
        def bl():
            Wb, Hb = 34, 24; yy, xx = np.mgrid[0:Hb, 0:Wb].astype(np.float32); L = ch.Layers(Wb, Hb)
            m = (np.abs(xx - 17) <= 11 + yy * 0.25) & (yy >= 1)
            L.add(m, lambda c, mm: (c.__setitem__(mm, hexc('#c8303a')), c.__setitem__(mm & ((xx.astype(int) % 6) < 2), hexc('#8a1a2a')),
                                     c.__setitem__(mm & ((yy.astype(int) % 6) < 2), hexc('#e85a5a')), c.__setitem__(mm & ((xx.astype(int) % 6) < 2) & ((yy.astype(int) % 6) < 2), hexc('#5a1020'))))
            return L.out()
        c, M = spr('blanket', bl); pv.blit_hr(F, c, M, cx + jx - 17, top + 27, 1)
    if shiver > 0:
        for sd in (-1, 1):
            for k in range(3): put(F, cx + sd * (20 + k % 2), top + 22 + k * 5, hexc('#cfe9ff'), 0.8 * shiver)
    if warm > 0: glow(F, cx, top + 30, 30, '#ff9a3a', 0.35 * warm)
    return top
def tree(F, cx, feet=GROUND + 1, t=0.0):
    def mk():
        L = ch.Layers(40, 56); yy, xx = np.mgrid[0:56, 0:40].astype(np.float32)
        L.add((np.abs(xx - 19.5) <= 2.5) & (yy >= 46) & (yy < 54), hexc('#6a4226'))
        for (ty, hgt, wd) in ((24, 24, 18), (12, 20, 14), (3, 16, 9)):
            m = (yy >= ty) & (yy < ty + hgt) & (np.abs(xx - 19.5) <= (yy - ty + 1) / hgt * wd)
            L.add(m, lambda c, m_: (c.__setitem__(m_, hexc('#2f8f4a')), c.__setitem__(m_ & (xx > 19.5), hexc('#1d6a3a'))))
        L.add((np.abs(xx - 19.5) + np.abs(yy - 3) * 0.8 <= 2.6), hexc('#ffcc4a'))
        return L.out()
    c, M = spr('tree', mk); shadow(F, cx, feet, 34); pv.blit_hr(F, c, M, cx - 20, feet - 55, 1)
    for k, (ox, oy, col) in enumerate(((-8, 40, '#e8303a'), (6, 34, '#3a8aff'), (-4, 26, '#ffcc4a'), (8, 46, '#ff5ad0'), (0, 18, '#5ae07a'), (-11, 47, '#ffcc4a'))):
        on = (int(t * 3) + k) % 3 != 0; put(F, cx - 0.5 + ox, feet - 55 + oy, hexc(col) if on else hexc(col) * 0.5)
def thermostat(F, cx, cy, temp_txt, sub_txt=None, dial=0.0):
    w_, h_ = 70, 46; x0, y0 = int(cx - w_ / 2), int(cy - h_ / 2)
    col = np.zeros((h_, w_, 3), np.float32) + hexc('#e8ecf4'); M = np.ones((h_, w_), bool)
    yy, xx = np.mgrid[0:h_, 0:w_]
    M &= ~(((xx < 3) | (xx >= w_ - 3)) & ((yy < 3) | (yy >= h_ - 3)))
    col[(xx > 5) & (xx < w_ - 22) & (yy > 6) & (yy < h_ - 8)] = hexc('#1d3a2a')
    d = np.hypot(xx - (w_ - 12), yy - h_ / 2); col[d < 8] = hexc('#a8b2c4'); col[d < 6] = hexc('#d8dee8')
    col, M = bk.outline(col, M); pv.blit_hr(F, col, M, x0, y0, 1)
    for j in range(10): put(F, x0 + w_ - 12 + j * 0.6 * math.cos(-math.pi / 2 + dial), y0 + h_ / 2 + j * 0.6 * math.sin(-math.pi / 2 + dial), hexc('#e8303a'))
    tw = len(temp_txt) * 6 * 8 - 8; bk.pixel_text(F, temp_txt, int((x0 + 5 + (w_ - 27) / 2) * S - tw / 2), int((y0 + 12) * S), px=8, colr=(120, 255, 150))
    if sub_txt:
        tw = len(sub_txt) * 6 * 3 - 3; bk.pixel_text(F, sub_txt, int((x0 + 5 + (w_ - 27) / 2) * S - tw / 2), int((y0 + 30) * S), px=3, colr=(120, 255, 150))
def suit_man(F, cx, feet=GROUND + 1):
    """a quick 'average 1960s office man' in a grey suit (front view), simple parts"""
    def mk():
        W_, H_ = 34, 54; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = ch.Layers(W_, H_); c0 = 17
        L.add((yy >= 42) & (yy < 52) & ((np.abs(xx - 13.5) <= 2.2) | (np.abs(xx - 20.5) <= 2.2)), lambda c, m: (c.__setitem__(m, hexc('#3a4664')), c.__setitem__(m & (yy >= 49), hexc('#1b1418'))))
        body = (yy >= 22) & (yy < 44) & (np.abs(xx - c0) <= 8)
        L.add(body, lambda c, m: (c.__setitem__(m, hexc('#5a6478')), c.__setitem__(m & (np.abs(xx - c0) < 2.5) & (yy < 32), hexc('#ffffff')),
                                  c.__setitem__(m & (np.abs(xx - c0) < 0.8) & (yy < 34), hexc('#c8303a'))))
        for sd in (-1, 1):
            L.add((np.abs(xx - (c0 + sd * 10)) <= 2) & (yy >= 23) & (yy < 37), hexc('#4a5468'))
            L.add(((xx - (c0 + sd * 10)) / 2.2) ** 2 + ((yy - 38) / 2.2) ** 2 <= 1, hexc('#f6c9a8'))
        head = ((xx - c0) / 7) ** 2 + ((yy - 13) / 8) ** 2 <= 1
        def hf(c, m):
            c[m] = hexc('#f6c9a8'); c[m & (yy < 9)] = hexc('#5a3a28')
            for ex in (c0 - 3, c0 + 3): c[(xx >= ex - 1) & (xx < ex + 1) & (yy >= 12) & (yy < 15)] = hexc('#1b1428'); c[(xx >= ex - 1) & (xx < ex) & (yy >= 12) & (yy < 13)] = hexc('#ffffff')
            c[(yy >= 17.5) & (yy < 18.5) & (np.abs(xx - c0) < 2.5)] = hexc('#8a3a3a')
        L.add(head, hf)
        return L.out()
    c, M = spr('suit', mk); shadow(F, cx, feet, 28); pv.blit_hr(F, c, M, cx - 17, feet - 53, 1)
def score_bar(F, x, label, val, colr, top=78, h_=60):
    meter(F, x, label, val, colr, y_top=top, h_=h_, w_=18)
def sweat(F, x, y, t):
    for k in range(3):
        ph = (t * 1.2 + k / 3) % 1; put(F, x + k * 4 - 4, y + ph * 10, hexc('#9fd8ff'), 1 - ph); put(F, x + k * 4 - 4, y + ph * 10 + 1, hexc('#9fd8ff'), 1 - ph)

def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t); a = t - SEG[i][0]
    if i == L_HOOK:
        you(F, 90, mood='sad', shiver=1.0, t=t); bk.label(F, 'ALWAYS COLD', 90, 470, int(78 * S), int((GROUND - 46) * S), px=6)
    elif i == L_GENIUS:
        jump = 8 * abs(math.sin(a * 7)) * math.exp(-a * 1.3)
        you(F, 90, mood='proud', cap=True, arms='up', bob=jump, t=t, blanket=False)
        sparkles(F, 90, 100, 34, 12, t); ctag(F, 'GENIUS', 300, px=12)
    elif i == L_ROOM:                                            # look around: T-shirts vs you in hoodies + blanket
        tree(F, 24, t=t)
        if t >= cs(L_ROOM, 1) - 0.05:
            draw_elf(F, 154, 'holly', mood='happy'); bk.label(F, 'T-SHIRT', 830, 440, int(154 * S), int((GROUND - 34) * S), px=5)
        else: ctag(F, 'LOOK AROUND', 300, px=8)
        if t >= cs(L_ROOM, 2) - 0.05:
            you(F, 92, mood='sad', shiver=1.0 if t >= cs(L_ROOM, 5) - 0.05 else 0.3, blanket=t >= cs(L_ROOM, 4) - 0.05, t=t)
            if t >= cs(L_ROOM, 3) - 0.05: bk.label(F, '2 HOODIES', 300, 560, int(92 * S), int((GROUND - 30) * S), px=5)
            if t >= cs(L_ROOM, 5) - 0.05: ctag(F, 'STILL SHAKING', 300, px=7)
    elif i == L_DRAMA:                                           # called dramatic -> ignore -> your body isn't broken, the room is
        tree(F, 22, t=t); draw_elf(F, 152, 'holly', mood='proud')
        ign = t >= cs(L_DRAMA, 2) - 0.05
        you(F, 88, mood='proud' if ign else 'angry', shiver=0.6, t=t)
        if not ign: bubble(F, 148, 52, 'SO DRAMATIC!', px=6)
        elif t < cs(L_DRAMA, 3) - 0.05: ctag(F, 'IGNORE', 300, px=10)
        elif t < cs(L_DRAMA, 5) - 0.05: ctag(F, 'BODY: FINE', 300, px=9)
        else: ctag(F, 'ROOM: BROKEN', 300, px=9)
    elif i == L_SUB:
        you(F, 60, mood='proud', arms='up', bob=abs(math.sin(t * 6)) * 3, t=t)
        if t >= cs(L_SUB, 1) - 0.05: sub_button(F, t, cs(L_SUB, 1) - 0.05, cs(L_SUB, 1) + 0.35)
        else: ctag(F, 'BLANKET THIEVES', 300, px=7)
    elif i == L_FORMULA:                                         # walk to the thermostat: formula built around a 40-y/o man
        walk = ramp(t, SEG[L_FORMULA][0], 1.0)
        you(F, lerp(26, 32, walk), mood='happy', shiver=0.4, t=t, blanket=True)
        thermostat(F, 86, 92, '21 C', 'OLD FORMULA' if t >= cs(L_FORMULA, 3) - 0.05 else None)
        if t >= cs(L_FORMULA, 5) - 0.05:
            suit_man(F, 152); bk.label(F, '40 Y/O MAN', 770, 450, int(152 * S), int((GROUND - 56) * S), px=5)
        if t >= cs(L_FORMULA, 7) - 0.05 and t < cs(L_FORMULA, 8) - 0.05: ctag(F, 'NOT YOU', 280, px=10)
        elif t >= cs(L_FORMULA, 8) - 0.05: ctag(F, 'HIM', 280, px=12)
    elif i == L_WOMEN:                                           # women burn less heat -> normal room is freezing
        suit_man(F, 40); you(F, 90, mood='sad', shiver=1.0, t=t, blanket=False); draw_elf(F, 146, 'holly', mood='sad')
        meter(F, 40, 'HIM', 0.9, '#ff9a3a', y_top=62, h_=32, w_=14); meter(F, 146, 'HER', 0.62 * ramp(t, SEG[L_WOMEN][0], 0.6), '#ff9a3a', y_top=62, h_=32, w_=14)
        if t < cs(L_WOMEN, 2) - 0.05: ctag(F, 'BODY HEAT', 190, px=8)
        else: ctag(F, 'FREEZING', 190, px=9)
    elif i == L_NOBODY:                                          # re-hook
        you(F, 90, mood='shock', t=t)
        k = ramp(t, SEG[L_NOBODY][0], 0.4); F *= 1 - 0.55 * k
        glow(F, 90, 110, 40, '#ffcc4a', 0.25 * k); ctag(F, 'THE GENIUS PART', 300, px=7)
    elif i == L_STUDY:                                           # turn the heat up; women did better in warmer rooms
        up_ = ramp(t, SEG[L_STUDY][0] + 0.2, 0.8)
        thermostat(F, 52, 86, f'{int(17 + 10 * up_)} C', dial=up_ * 2.4)
        bk.pixel_text(F, '+ - = ?', 120, 760, px=8, colr=(225, 235, 255))
        score_bar(F, 124, 'COLD', 0.4, '#5ea6f2'); score_bar(F, 160, 'WARM', 0.4 + 0.45 * ramp(t, cs(L_STUDY, 4), 0.8), '#5ae07a')
        if t < cs(L_STUDY, 1) - 0.05: ctag(F, 'HEAT UP', 230, px=9)
        elif t < cs(L_STUDY, 4) - 0.05: ctag(F, 'MATH + WORDS', 230, px=7)
        else: ctag(F, 'BETTER WARM', 230, px=8)
    elif i == L_CRANK:                                           # crank it, grab the blanket, own the thermostat, think better
        k = ramp(t, SEG[L_CRANK][0], 0.6)
        thermostat(F, 134, 92, f'{int(21 + 6 * k)} C', 'MINE' if t >= cs(L_CRANK, 2) - 0.05 else None, dial=k * 2.4)
        smart = t >= cs(L_CRANK, 4) - 0.05
        you(F, 56, mood='proud', shiver=0.0, t=t, warm=k, blanket=t >= cs(L_CRANK, 1) - 0.05, cap=smart, arms='up' if smart else 'down',
            bob=abs(math.sin(t * 5)) * 2 if smart else 0)
        if t < cs(L_CRANK, 1) - 0.05: ctag(F, 'CRANK IT', 280, px=10)
        elif t < cs(L_CRANK, 3) - 0.05: ctag(F, 'OWN IT', 280, px=10)
        elif not smart: ctag(F, 'NOT DRAMATIC', 280, px=8)
        else: ctag(F, 'BRAIN MODE', 280, px=9); sparkles(F, 56, 96, 26, 10, t, n=8)
    elif i == L_CATCH:                                           # the catch: everyone else sweating. Not your problem.
        you(F, 32, mood='proud', t=t, blanket=True); thermostat(F, 90, 86, '27 C')
        top = draw_elf(F, 148, 'holly', mood='shock')[1]
        if t >= cs(L_CATCH, 1) - 0.05: sweat(F, 148, top + 8, t)
        glow(F, 90, 120, 70, '#ff8a3a', 0.2)
        if t < cs(L_CATCH, 1) - 0.05: ctag(F, 'THE CATCH', 230, px=8)
        elif t < cs(L_CATCH, 3) - 0.05: ctag(F, 'EVERYONE ELSE: SWEATING', 230, px=6)
        else: ctag(F, 'NOT YOUR PROBLEM', 230, px=7)
    else:                                                        # CTA: tag the blanket thief + naughty list
        you(F, 146, mood='happy', t=t)
        if t < cs(L_CTA, 2) - 0.05:
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(720 * pop), int(200 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 250
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    tx1, tx2 = 'TAG THE', 'BLANKET THIEF'
                    bk.pixel_text(F, tx1, X + (bw - (len(tx1) * 42 - 7)) // 2, Y + 40, px=7, colr=(20, 24, 40))
                    bk.pixel_text(F, tx2, X + (bw - (len(tx2) * 42 - 7)) // 2, Y + 115, px=7, colr=(200, 40, 60))
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
SHOUTS = [SEG[L_GENIUS][0], cs(L_SUB, 1), SEG[L_NOBODY][0]]
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    rv.snow(F, t)
    if i >= 2 and 0 <= t - SEG[i][0] < 0.12 and i not in (L_DRAMA,):
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
