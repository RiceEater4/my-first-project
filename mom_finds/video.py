"""'What If Your Mom Has a Superpower?' - direct explainer (younger-sibling v2 order), Jett narration.
YOU = green elf, MOM = red elf. New clean callouts + cloud thought bubble (style_study/ui.py).
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study'))
import importlib.util
_s = importlib.util.spec_from_file_location('ysv', os.path.join(ROOT_, 'younger_sibling', 'video.py'))
ys = importlib.util.module_from_spec(_s); _s.loader.exec_module(ys)
fm, b1, sv, rv, pv, bk, ch = ys.fm, ys.b1, ys.sv, ys.rv, ys.pv, ys.bk, ys.ch
import ui
sys.path.insert(0, HERE)
import props

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
(L_HOOK, L_ALWAYS, L_LOOK, L_SCIENCE, L_NOTLOT, L_SUB, L_HALF, L_FRONT, L_NOBODY, L_MESSY, L_PUT, L_TIPS, L_YELL,
 L_CTA) = range(14)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))

_c = {}
def spr(key, fn):
    if key not in _c: _c[key] = fn()
    return _c[key]
def you(F, cx, mood='happy', **kw): return ys.you(F, cx, mood=mood, **kw)[1]
def mom(F, cx, mood='happy', **kw): return draw_elf(F, cx, 'holly', mood=mood, **kw)
def phone(F, x, y, case='#1b1428', glint=0.0):
    def mk():
        L = ch.Layers(9, 14); yy, xx = np.mgrid[0:14, 0:9].astype(np.float32)
        L.add((xx >= 0) & (xx < 9) & (yy >= 0) & (yy < 14), lambda c, m: (c.__setitem__(m, hexc(case)), c.__setitem__(m & (xx >= 1.5) & (xx < 7.5) & (yy >= 1.5) & (yy < 11.5), hexc('#5ea6f2')),
              c.__setitem__(m & (xx >= 2) & (xx < 4) & (yy >= 2) & (yy < 4), hexc('#cfe9ff'))))
        return L.out()
    c, M = spr(('phone', case), mk); pv.blit_hr(F, c, M, x - 4.5, y - 14, 1)
    if glint > 0: rv.sparkle(F, x + 5, y - 15, glint)
def pile(F, cx, feet=GROUND + 1):
    def mk():
        L = ch.Layers(46, 22); yy, xx = np.mgrid[0:22, 0:46].astype(np.float32)
        for k, (px_, py_, rx, ry, col) in enumerate(((14, 15, 13, 7, '#5a8ad8'), (31, 15, 13, 7, '#c8303a'), (22, 9, 12, 7, '#2f9a52'), (36, 9, 8, 5, '#ffcc4a'), (10, 9, 7, 5, '#e8eef6'))):
            m = ((xx - px_) / rx) ** 2 + ((yy - py_) / ry) ** 2 <= 1
            L.add(m, lambda c, mm, col=col: (c.__setitem__(mm, hexc(col)), c.__setitem__(mm & (yy > py_ + ry * 0.3), hexc(col) * 0.8)))
        return L.out()
    c, M = spr('pile', mk); shadow(F, cx, feet, 44); pv.blit_hr(F, c, M, cx - 23, feet - 21, 1)
def timer(F, secs, y=230, colr=(255, 255, 255)):
    m_, s_ = int(secs) // 60, int(secs) % 60; big_num(F, f'{m_:d}:{s_:02d}', y, px=12, colr=colr)
ICONS = ['PHONE', 'KEYS', 'SOCK', 'REMOTE', 'SHOE', 'CHARGER']
def memory_grid(F, t, t0):
    cw, chh = 46, 34                                         # card size (grid px)
    for k, name in enumerate(ICONS):
        cx, cy = 90 + (k % 3 - 1) * 54, 80 + (k // 3) * 40    # columns centred on the screen
        box = np.zeros((chh, cw, 3), np.float32) + hexc('#14234a'); M = np.ones((chh, cw), bool)
        box[:2] = hexc('#2a3f78'); box[-2:] = hexc('#0b1530')
        box, M = bk.outline(box, M); props._blit(F, box, M, cx - cw / 2 - 1, cy - chh / 2 - 1)
        c, Mi = props.icon(name); h_, w_ = Mi.shape
        props._blit(F, c, Mi, cx - w_ / 2, cy - h_ / 2 - 4)
        props.text_center(F, name, cx, cy + 8, px=4)
        if t >= t0 + k * 0.25:                               # check badge in the card corner
            bx_, by_ = cx + cw / 2 - 7, cy - chh / 2 + 3
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if dx * dx + dy * dy <= 10: props._put(F, bx_ + dx, by_ + dy, hexc('#5ae07a'))
            for j, (dx, dy) in enumerate(((-2, 0), (-1, 1), (0, 2), (1, 1), (2, 0), (3, -1))): props._put(F, bx_ + dx - 0.5, by_ + dy - 0.5, hexc('#0b1530'))
def bubble_item(F, bx, by, bw, bh, case, text, colr):
    """phone + label as one group, centred inside the cloud"""
    tw = props.text_w(text, 6) / S; gw = 14 + 4 + tw; cx, cy = bx + bw / 2, by + bh / 2 - 2
    x0 = cx - gw / 2
    props.draw_phone(F, x0 + 7, cy + 11, case=case, big=True)
    bk.pixel_text(F, text, int(round((x0 + 18) * S)), int(round((cy - 3.5) * S)), px=6, colr=colr)
def eye_scan(F, t, t0, x0, x1, y):
    f = ramp(t, t0, 1.2)
    for k in range(0, int((x1 - x0) * f), 3): put(F, x0 + k, y + math.sin(k * 0.3) * 2, hexc('#ffe27a'), 0.9)
def magnifier(F, x, y):
    for th in np.linspace(0, TAU, 40):
        for r in (6, 6.6): put(F, x + r * math.cos(th), y + r * math.sin(th), hexc('#c4ccd8'))
    for k in range(7): put(F, x + 5 + k * 0.8, y + 5 + k * 0.8, hexc('#8a5a36')); put(F, x + 6 + k * 0.8, y + 5 + k * 0.8, hexc('#8a5a36'))

def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t); a = t - SEG[i][0]
    if i == L_HOOK:
        you(F, 46, mood='shock'); pile(F, 130)
        for k in range(3): bk.pixel_text(F, '?', int((40 + k * 7) * S), int((GROUND - 70 - (k % 2) * 5) * S), px=7, colr=(255, 255, 255))
    elif i == L_ALWAYS:
        jump = 6 * abs(math.sin(a * 9)) * math.exp(-a * 1.2)
        mom(F, 120, mood='proud', arms='up', bob=jump); props.phone_in_hand(F, 120, GROUND + 1, 'up', 1, bob=jump, glint=1.0)
        you(F, 40, mood='shock'); sparkles(F, 120, 100, 26, 12, t, n=8)
        ctag(F, 'ALWAYS', 300, px=12)
    elif i == L_LOOK:                                            # 10 minutes searching... mom: 2 seconds
        pile(F, 112)
        mom_in = ramp(t, cs(L_LOOK, 3) - 0.1, 0.6); found = t >= cs(L_LOOK, 5) - 0.05
        you(F, 40, mood='happy' if found else ('sad' if t >= cs(L_LOOK, 2) else 'shock'), arms='hold' if (t * 3) % 2 < 1 else 'down')
        if mom_in < 0.02:
            timer(F, 600 * ramp(t, cs(L_LOOK, 1), max(0.5, cs(L_LOOK, 3) - cs(L_LOOK, 1))))
            if t < cs(L_LOOK, 1) - 0.05: ctag(F, 'LOOK AT YOU', 350, px=8)
        else:
            mom(F, lerp(210, 156, mom_in), mood='proud' if found else 'happy')
            timer(F, 2 * ramp(t, cs(L_LOOK, 4), 0.4), colr=(90, 224, 122))
            if found:
                k = ramp(t, cs(L_LOOK, 5) - 0.05, 0.3); props.draw_phone(F, 112, GROUND - 12 - 16 * math.sin(math.pi * min(1, k) * 0.5), glint=1.0)
                ui.callout(F, 'FOUND IT', 60, 74, 112, GROUND - 32, px=5)
    elif i == L_SCIENCE:                                         # superpower? scientists tested it... kind of yes: location memory
        if t < cs(L_SCIENCE, 3) - 0.05:
            mom(F, 90, mood='proud', arms='up'); glow(F, 90, 110, 34, '#ffe27a', 0.35); sparkles(F, 90, 104, 30, 12, t, n=10)
            ctag(F, 'SUPERPOWER?', 300, px=9)
        elif t < cs(L_SCIENCE, 5) - 0.05:
            draw_prof(F, 52); mom(F, 128, mood='proud')
            ctag(F, 'SCIENTISTS TESTED IT' if t < cs(L_SCIENCE, 4) - 0.05 else 'KIND OF... YES', 300, px=6 if t < cs(L_SCIENCE, 4) - 0.05 else 8)
        else:
            memory_grid(F, t, cs(L_SCIENCE, 5))
            ctag(F, 'WHERE THINGS ARE', 260, px=7)
    elif i == L_NOTLOT:                                          # not by a lot, but enough to beat you every time
        g = ramp(t, SEG[L_NOTLOT][0], 0.8)
        meter(F, 66, 'MOM', 0.1 + 0.74 * g, '#ff5a64', y_top=84, h_=62, w_=22); meter(F, 126, 'YOU', 0.1 + 0.68 * g, '#5ae07a', y_top=84, h_=62, w_=22)
        if t < cs(L_NOTLOT, 1) - 0.05: ctag(F, 'NOT BY A LOT', 230, px=8)
        else: big_num(F, 'MOM 47 - YOU 0', 220, px=9, colr=(255, 200, 58))
    elif i == L_SUB:
        b_ = abs(math.sin(t * 6)) * 3; mom(F, 60, mood='proud', arms='up', bob=b_); props.phone_in_hand(F, 60, GROUND + 1, 'up', 1, bob=b_, glint=0.6)
        if t >= cs(L_SUB, 2) - 0.05: sub_button(F, t, cs(L_SUB, 2) - 0.05, cs(L_SUB, 2) + 0.35)
        else: ctag(F, 'SUPERPOWER MOM?', 300, px=7)
    elif i in (L_HALF, L_FRONT):                                 # brain search template: imagined black phone, real one is pink
        top = you(F, 44, mood='shock' if i == L_FRONT else 'happy')
        pinkx = 92; props.phone_on_floor(F, pinkx, GROUND + 1, case='#ff6aa8', shadow_fn=shadow)
        if i == L_HALF and t < cs(L_HALF, 2) - 0.05: ctag(F, 'ONLY HALF', 300, px=9)
        else:
            bx, by = ui.thought_bubble(F, 76, 50, 112, 48, (52, top + 2), t)
            bubble_item(F, bx, by, 112, 48, '#1b1428', 'MY PHONE', (20, 40, 90))
            if i == L_HALF and t >= cs(L_HALF, 7) - 0.05: eye_scan(F, t, cs(L_HALF, 7), 56, 170, GROUND - 6)
            if i == L_FRONT or t >= cs(L_HALF, 5) - 0.05: ui.callout(F, "IT'S PINK" if i == L_HALF else 'RIGHT THERE', 116, 104, pinkx, GROUND - 12, px=5, accent='#ff6aa8')
    elif i == L_NOBODY:
        you(F, 60, mood='shock'); mom(F, 124, mood='proud')
        k = ramp(t, SEG[L_NOBODY][0], 0.4); F *= 1 - 0.55 * k
        glow(F, 90, 110, 46, '#ffcc4a', 0.25 * k); ctag(F, 'NOBODY TELLS YOU', 300, px=7)
    elif i == L_MESSY:                                           # you check empty spots, mom checks the messy ones
        pile(F, 132)
        if t < cs(L_MESSY, 2) - 0.05:
            you(F, 44, mood='sad')
            for k, sx in enumerate((22, 70)):
                if t >= cs(L_MESSY, 0) + k * 0.5: ui.callout(F, 'EMPTY', sx - 14, 70 + k * 12, sx, GROUND - 2, px=4, accent='#e8303a')
        else:
            mom(F, 92, mood='proud', arms='hold'); props.draw_phone(F, 132, GROUND - 12 - 10 * ramp(t, cs(L_MESSY, 3), 0.4), glint=ramp(t, cs(L_MESSY, 3), 0.3))
            ui.callout(F, 'MESSY = FOUND', 104, 60, 132, GROUND - 18, px=5)
    elif i == L_PUT:                                             # she probably put it there
        mom(F, 70, mood='proud'); pile(F, 132)
        if t >= cs(L_PUT, 1) - 0.05:
            ui.callout(F, 'SUSPICIOUS', 4, 66, 64, GROUND - 48, px=5, accent='#ff5a64')
            for k in range(3): put(F, 82 + k * 3, GROUND - 40 - k * 2 - (t * 6) % 3, hexc('#cfe2f6'))
        ctag(F, 'SHE PUT IT THERE' if t >= cs(L_PUT, 2) - 0.05 else 'OH...', 230, px=7)
    elif i == L_TIPS:                                            # picture it exactly, search the mess slowly
        top = you(F, 44, mood='proud'); pile(F, 132)
        if t < cs(L_TIPS, 3) - 0.05:
            bx, by = ui.thought_bubble(F, 80, 50, 120, 48, (52, top + 2), t)
            bubble_item(F, bx, by, 120, 48, '#ff6aa8', 'PINK PHONE', (200, 40, 110))
        else:
            f = ramp(t, cs(L_TIPS, 3), 1.6); magnifier(F, lerp(114, 150, f), GROUND - 14 + 3 * math.sin(t * 3))
            ctag(F, 'SEARCH SLOWLY', 230, px=8)
    elif i == L_YELL:                                            # or just yell MOM
        yell = t >= cs(L_YELL, 1) - 0.05
        you(F, 44, mood='angry' if yell else 'happy', arms='up' if yell else 'down')
        if yell:
            big_num(F, 'MOM!', 240, px=20, colr=(255, 90, 90))
            k = ramp(t, cs(L_YELL, 1) + 0.2, 0.4); mx = round(lerp(210, 134, k)); mom(F, mx, mood='proud', arms='up'); props.phone_in_hand(F, mx, GROUND + 1, 'up', 1, glint=k)
            if t >= cs(L_YELL, 2) - 0.05: ctag(F, 'WORKS EVERY TIME', 430, px=7)
    else:                                                        # CTA
        mom(F, 150, mood='happy')
        if t < cs(L_CTA, 2) - 0.05:
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(760 * pop), int(200 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 250
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    tx1, tx2 = 'SEND THIS TO', 'YOUR MOM'
                    bk.pixel_text(F, tx1, X + (bw - (len(tx1) * 42 - 7)) // 2, Y + 40, px=7, colr=(20, 24, 40))
                    bk.pixel_text(F, tx2, X + (bw - (len(tx2) * 42 - 7)) // 2, Y + 115, px=7, colr=(200, 40, 60))
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
SHOUTS = [SEG[L_ALWAYS][0], cs(L_SUB, 2), SEG[L_NOBODY][0], cs(L_YELL, 1)]
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    rv.snow(F, t)
    if i >= 2 and 0 <= t - SEG[i][0] < 0.12 and i not in (L_FRONT,):
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
