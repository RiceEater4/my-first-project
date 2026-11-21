"""'What If Everyone Could See Your Fake Smile?' - straight-to-camera explainer, Jett narration (1080x1920, 60 fps).
Tinsel = YOU. Screamed hook (FURIOUS), screamed mid-video SUBSCRIBE (~22 s), comment + naughty-list ending.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study'))
import importlib.util
_s = importlib.util.spec_from_file_location('bw1', os.path.join(ROOT_, 'bad_wrapping', 'video.py'))
b1 = importlib.util.module_from_spec(_s); _s.loader.exec_module(b1)
sv, rv, pv, bk, ch = b1.sv, b1.rv, b1.pv, b1.bk, b1.ch

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
glow, ctag, ctext, big_num, draw_cursor = sv.glow, sv.ctag, sv.ctext, sv.big_num, sv.draw_cursor
draw_elf, draw_gift, draw_santa, draw_prof = b1.draw_elf, b1.draw_gift, b1.draw_santa, b1.draw_prof
shadow, heart, sparkles, meter, thought = b1.shadow, b1.heart, b1.sparkles, b1.meter, b1.thought
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
(L_HOOK, L_FURIOUS, L_AUNT, L_FACE, L_TELL, L_SUB, L_SMILE, L_NOBODY, L_SURPRISE, L_ASKED, L_UNGRATEFUL, L_WISH,
 L_EYES, L_CTA) = range(14)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))

_c = {}
def spr(key, fn):
    if key not in _c: _c[key] = fn()
    return _c[key]
def candle(F, cx, feet=GROUND + 1, lift=0.0, flick=0.0):
    c, M = spr('cat', ch.cat_candle); h_, w_ = M.shape
    shadow(F, cx, feet, 22 * max(0.5, 1 - lift / 40)); pv.blit_hr(F, c, M, cx - w_ / 2, feet - h_ - lift, 1)
    glow(F, cx, feet - h_ - lift + 5, 6 + flick, '#ffcc4a', 0.5)
def bubble(F, cx, y, text, px=6):
    tw = len(text) * 6 * px - px; X, Y = int(cx * S - tw / 2) - 30, int(y * S); Wd, Hd = tw + 60, 7 * px + 50
    X = max(20, min(WF - Wd - 20, X))
    F[Y:Y + Hd, X:X + Wd] = 1.0
    for q in range(5): F[Y + q, X:X + Wd] = F[Y + Hd - 1 - q, X:X + Wd] = NAVY; F[Y:Y + Hd, X + q] = F[Y:Y + Hd, X + Wd - 1 - q] = NAVY
    tail_x = int(cx * S)
    for k in range(5): F[Y + Hd + k * 6:Y + Hd + k * 6 + 6, tail_x - 15 + k * 3:tail_x + 15 - k * 3] = 1.0
    bk.pixel_text(F, text, X + 30, Y + 25, px=px, colr=(20, 24, 40))
def steam(F, x, y, t):
    for k in range(4):
        ph = (t * 1.6 + k / 4) % 1; r_ = 1 + ph * 3
        for dx in range(-int(r_), int(r_) + 1):
            for dy in range(-int(r_), int(r_) + 1):
                if dx * dx + dy * dy <= r_ * r_: put(F, x + dx + 3 * math.sin(k + t * 4), y - ph * 22 + dy, hexc('#f4f8ff'), (1 - ph) * 0.9)
def eye_icon(F, cx, cy, t):
    yy, xx = np.mgrid[-5:6, -9:10]; M = (xx / 9) ** 2 + (yy / 5) ** 2 <= 1
    col = np.zeros(M.shape + (3,), np.float32); col[M] = 1.0
    px_ = int(2 * math.sin(t * 2)); col[((xx - px_) / 3) ** 2 + (yy / 3) ** 2 <= 1] = hexc('#1b1428')
    col, M = bk.outline(col, M); pv.blit_hr(F, col, M, cx - 10, cy - 6, 1)
def bigface(F, cx, top, mood):
    """zoomed-in head (2x) of Tinsel for the real-vs-fake comparison"""
    c, M = spr(('elf', mood), lambda: ch.elf(messy=True, mood=mood))
    c, M = c[0:31, 2:36], M[0:31, 2:36]
    c, M = np.repeat(np.repeat(c, 2, 0), 2, 1), np.repeat(np.repeat(M, 2, 0), 2, 1)
    pv.blit_hr(F, c, M, cx - 34, top, 1)
def envelope(F, x, y):
    col = np.zeros((9, 13, 3), np.float32) + 1.0; M = np.ones((9, 13), bool); yy, xx = np.mgrid[0:9, 0:13]
    col[np.abs(yy - np.abs(xx - 6) * 0.7) < 0.7] = hexc('#c8303a')
    col, M = bk.outline(col, M); pv.blit_hr(F, col, M, x - 7, y - 5, 1)
def sub_button(F, t, t0, pressed_at):
    pop = ramp(t, t0, 0.18); bw, bh = int(720 * (0.6 + 0.4 * pop)), int(170 * (0.6 + 0.4 * pop)); X, Y = (WF - bw) // 2, 250
    pressed = t >= pressed_at; sq = 6 if pressed_at - 0.1 <= t < pressed_at + 0.1 else 0
    F[Y + sq:Y + bh - sq, X + sq:X + bw - sq] = hexc('#5a6070') if pressed else hexc('#e8202e')
    for q in range(5):
        F[Y + sq + q, X + sq:X + bw - sq] = F[Y + bh - sq - 1 - q, X + sq:X + bw - sq] = NAVY
        F[Y + sq:Y + bh - sq, X + sq + q] = F[Y + sq:Y + bh - sq, X + bw - sq - 1 - q] = NAVY
    txt = 'SUBSCRIBED' if pressed else 'SUBSCRIBE'; px = 10 if pop > 0.9 else 8; tw = len(txt) * 6 * px - px
    bk.pixel_text(F, txt, (WF - tw) // 2, Y + (bh - 7 * px) // 2, px=px, colr=(255, 255, 255))
    draw_cursor(F, int(lerp(WF * 0.85, WF * 0.62, ramp(t, t0 + 0.1, 0.3))), Y + bh - 30)
    if pressed:
        for k in range(10): rv.sparkle(F, 90 + 62 * math.cos(TAU * k / 10), 62 + 20 * math.sin(TAU * k / 10), 1 - ramp(t, pressed_at, 0.9))

def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t); a = t - SEG[i][0]
    if i == L_HOOK:                                              # the gift opens: a cat candle. Fake smile.
        opened = t >= cs(L_HOOK, 0) + 0.5
        mood = 'fake' if t >= cs(L_HOOK, 2) - 0.05 else ('shock' if opened else 'happy')
        draw_elf(F, 48, 'tinsel', mood=mood, arms='hold')
        if not opened: draw_gift(F, 122, 'neat', bob=abs(math.sin(t * 6)) * 2)
        else:
            k = ramp(t, cs(L_HOOK, 0) + 0.5, 0.35); candle(F, 122, lift=14 * math.sin(math.pi * min(1, k)), flick=math.sin(t * 9))
            if t < cs(L_HOOK, 2) - 0.05: bk.pixel_text(F, '?', int(60 * S), int((GROUND - 70) * S), px=10, colr=(255, 255, 255))
    elif i == L_FURIOUS:                                         # FURIOUS
        jump = 6 * abs(math.sin(a * 9)) * math.exp(-a * 1.2)
        _, top = draw_elf(F, 64, 'tinsel', mood='angry', bob=jump); candle(F, 130, flick=math.sin(t * 9))
        steam(F, 52, top + 18, t); steam(F, 77, top + 18, t + 0.3)
        glow(F, 64, top + 22, 26, '#ff3a3a', 0.35)
        ctag(F, 'FURIOUS', 300, px=12)
    elif i == L_AUNT:                                            # Christmas morning: the aunt hands you a gift and stares
        aunt_in = ramp(t, cs(L_AUNT, 2) - 0.1, 0.5); handed = ramp(t, cs(L_AUNT, 3), 0.6)
        opened = t >= cs(L_AUNT, 8) - 0.1
        draw_elf(F, 40, 'tinsel', mood='shock' if opened else ('happy' if handed < 1 else 'happy'), arms='hold' if handed > 0.5 else 'down')
        if aunt_in > 0:
            draw_elf(F, lerp(210, 142, aunt_in), 'holly', mood='happy')
            if aunt_in > 0.95: bk.label(F, 'AUNT', 870, 450, int(142 * S), int((GROUND - 56) * S), px=6)
        if t < cs(L_AUNT, 2) - 0.05: ctag(F, 'CHRISTMAS MORNING', 300, px=7)
        if aunt_in > 0.5 and not opened:
            gx = lerp(122, 80, handed); draw_gift(F, gx, 'neat', bob=6 * math.sin(math.pi * handed))
        if t >= cs(L_AUNT, 4) - 0.05 and not opened:
            for k in range(3):
                y_ = GROUND - 38; put(F, 128 - k * 10 - (t * 20) % 10, y_, hexc('#ffffff'), 0.7)
            ctag(F, 'STARING', 300, px=8)
        if t >= cs(L_AUNT, 6) - 0.05:
            for k, ex in enumerate((50, 90, 130)): eye_icon(F, ex, 76 + 3 * math.sin(t * 2 + k), t + k)
        if opened:
            k = ramp(t, cs(L_AUNT, 8) - 0.1, 0.3); candle(F, 84, lift=12 * math.sin(math.pi * min(1, k)), flick=math.sin(t * 9))
            if t >= cs(L_AUNT, 9) - 0.05: ctag(F, 'CAT CANDLE', 190, px=8)
    elif i in (L_FACE, L_TELL):                                  # the face: "wow I love it"... everyone can tell
        draw_elf(F, 40, 'tinsel', mood='fake', arms='up' if i == L_FACE and t >= cs(L_FACE, 1) else 'down')
        candle(F, 90, flick=math.sin(t * 9))
        tell = i == L_TELL and t >= cs(L_TELL, 1) - 0.05
        draw_elf(F, 142, 'holly', mood='sad' if tell else 'proud')
        if i == L_FACE and t >= cs(L_FACE, 2) - 0.05: bubble(F, 48, 52, 'WOW I LOVE IT!', px=7)
        if tell:
            ctag(F, 'EVERYONE CAN TELL', 280, px=7)
            for k in range(3): bk.pixel_text(F, '?', int((136 + k * 8) * S), int((GROUND - 72 - (k % 2) * 6) * S), px=7, colr=(255, 255, 255))
    elif i == L_SUB:                                             # screamed mid-video SUBSCRIBE
        draw_elf(F, 54, 'tinsel', mood='fake', arms='up', bob=abs(math.sin(t * 6)) * 3); candle(F, 126, flick=math.sin(t * 9))
        if t >= cs(L_SUB, 2) - 0.05: sub_button(F, t, cs(L_SUB, 2) - 0.05, cs(L_SUB, 2) + 0.35)
        else: ctag(F, 'BEEN THERE?', 300, px=8)
    elif i == L_SMILE:                                           # real smile crinkles the eyes, fake only the mouth
        bigface(F, 46, 72, 'real'); bigface(F, 134, 72, 'fake')
        bk.pixel_text(F, 'REAL', int(46 * S) - 70, int(62 * S), px=7, colr=(90, 224, 122))
        bk.pixel_text(F, 'FAKE', int(134 * S) - 70, int(62 * S), px=7, colr=(255, 90, 90))
        if t >= cs(L_SMILE, 1) - 0.05: bk.label(F, 'EYES CRINKLE', 40, 930, int(40 * S), int(112 * S), px=6)
        if t >= cs(L_SMILE, 3) - 0.05: bk.label(F, 'MOUTH ONLY', 640, 930, int(134 * S), int(124 * S), px=6)
        if t >= cs(L_SMILE, 4) - 0.05: ctag(F, 'PEOPLE CAN TELL', 240, px=7)
    elif i == L_NOBODY:                                          # re-hook
        draw_elf(F, 90, 'tinsel', mood='shock')
        k = ramp(t, SEG[L_NOBODY][0], 0.4); F *= 1 - 0.55 * k
        glow(F, 90, 110, 40, '#ffcc4a', 0.25 * k)
        if t < cs(L_NOBODY, 2) - 0.05: ctag(F, 'NOBODY TELLS YOU', 300, px=7)
        else: ctag(F, 'NOT YOUR FAULT', 300, px=8)
    elif i == L_SURPRISE:                                        # givers pick surprises, think they look thoughtful
        draw_elf(F, 50, 'holly', mood='proud', arms='hold'); draw_gift(F, 110, 'neat')
        bk.pixel_text(F, '?', int(108 * S), int((GROUND - 46) * S), px=10, colr=(255, 200, 58))
        bk.label(F, 'SURPRISE', 700, 470, int(110 * S), int((GROUND - 30) * S), px=6)
        if t >= cs(L_SURPRISE, 3) - 0.05:
            thought(F, 52, 52, 72, 30); bk.pixel_text(F, 'THOUGHTFUL!', int((52 - 33) * S) + 6, int(62 * S), px=5, colr=(200, 40, 60))
    elif i == L_ASKED:                                           # but asked-for gifts are loved way more
        draw_gift(F, 40, 'neat'); bk.pixel_text(F, '?', int(38 * S), int((GROUND - 46) * S), px=8, colr=(255, 200, 58))
        c, M = sv.spr('scroll', ch.scroll); shadow(F, 92, GROUND + 1, 24); pv.blit_hr(F, c, M, 92 - 13, GROUND + 1 - 38, 1)
        bk.pixel_text(F, 'WISH', int(84 * S) + 6, int((GROUND - 30) * S), px=3, colr=(30, 36, 60))
        meter(F, 122, 'SURPRISE', 0.35, '#ffcc4a', y_top=70); meter(F, 162, 'ASKED', 0.35 + 0.6 * ramp(t, cs(L_ASKED, 1), 1.0), '#5ae07a', y_top=70)
        if t >= cs(L_ASKED, 2) - 0.05:
            ctag(F, 'LOVED WAY MORE', 260, px=7)
            for k in range(4):
                ph = (t * 0.8 + k / 4) % 1; heart(F, 84 + k * 6, 100 - ph * 26, 1 - ph)
    elif i == L_UNGRATEFUL:                                      # not ungrateful - it's a cat candle
        draw_elf(F, 54, 'tinsel', mood='happy'); candle(F, 126, flick=math.sin(t * 9))
        if t < cs(L_UNGRATEFUL, 1) - 0.05:
            ctag(F, 'UNGRATEFUL', 300, px=9)
            for k in range(-200, 200, 2): F[int(330 + k * 0.1):int(338 + k * 0.1), 540 + k:542 + k] = hexc('#e8303a')
        else:
            bk.label(F, 'MEOW', 760, 470, int(126 * S), int((GROUND - 30) * S), px=7)
    elif i == L_WISH:                                            # make a wish list, send it to everyone
        draw_elf(F, 40, 'tinsel', mood='proud', arms='hold', cap=True)
        c, M = sv.spr('scroll', ch.scroll); pv.blit_hr(F, c, M, 52, GROUND - 46, 1)
        bk.pixel_text(F, 'WISH', int(54.5 * S), int((GROUND - 38) * S), px=3, colr=(30, 36, 60))
        if t < cs(L_WISH, 1) - 0.05: ctag(F, 'GENIUS MOVE', 300, px=8)
        else: ctag(F, 'WISH LIST', 300, px=8)
        if t >= cs(L_WISH, 2) - 0.05:
            for k in range(6):
                f = ((t - cs(L_WISH, 2)) * 0.8 + k / 6) % 1
                envelope(F, lerp(80, 190, f), 112 - 50 * math.sin(math.pi * f) + (k % 3) * 8)
    elif i == L_EYES:                                            # the cat candle still shows up: smile with your eyes
        k = ramp(t, SEG[L_EYES][0] + 0.2, 0.5); land = SEG[L_EYES][0] + 0.7
        candle(F, 126, lift=max(0.0, 120 * (1 - k)), flick=math.sin(t * 9))
        real = t >= cs(L_EYES, 2) - 0.05
        draw_elf(F, 54, 'tinsel', mood='real' if real else 'shock', arms='up' if real else 'down', bob=abs(math.sin(t * 5)) * 2 if real else 0)
        if real: ctag(F, 'SMILE WITH YOUR EYES', 280, px=6); sparkles(F, 54, 100, 28, 12, t, n=8)
    else:                                                        # CTA: comment the worst gift + naughty list
        draw_elf(F, 146, 'tinsel', mood='happy'); candle(F, 116, flick=math.sin(t * 9))
        if t < cs(L_CTA, 2) - 0.05:
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(720 * pop), int(200 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 250
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    tx1, tx2 = 'COMMENT YOUR', 'WORST GIFT EVER'
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
SHOUTS = [SEG[L_FURIOUS][0], cs(L_SUB, 2), SEG[L_NOBODY][0]]
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    rv.snow(F, t)
    if i >= 2 and 0 <= t - SEG[i][0] < 0.12 and i not in (L_TELL, L_ASKED):
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
