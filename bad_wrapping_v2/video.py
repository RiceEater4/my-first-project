"""'What If Bad Gift Wrapping Made You a Genius?' v2 - straight-to-camera explainer, Jett narration (1080x1920, 60 fps).
One elf stands in for YOU and acts out each line; no plot. Invisible floor with soft shadows.
usage: python3 video.py out.mp4 audio.wav  |  python3 video.py --stills DIR t1 t2 ...
"""
import sys, os, math, json, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT_ = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT_, 'style_study'))
import importlib.util
_s = importlib.util.spec_from_file_location('bw1', os.path.join(ROOT_, 'bad_wrapping', 'video.py'))
b1 = importlib.util.module_from_spec(_s); _s.loader.exec_module(b1)          # helpers from v1 (elves, gifts, shadows, meters)
sv, rv, pv, bk, ch = b1.sv, b1.rv, b1.pv, b1.bk, b1.ch

W, H, S, FPS = 180, 320, 6, 60
WF, HF = W * S, H * S
TAU = 2 * math.pi
hexc, put, smooth, lerp, NAVY, BAY = rv.hexc, rv.put, rv.smooth, rv.lerp, rv.NAVY, rv.BAY
glow, ctag, ctext, big_num, draw_cursor = sv.glow, sv.ctag, sv.ctext, sv.big_num, sv.draw_cursor
draw_elf, draw_gift, draw_santa, draw_deer, draw_prof = b1.draw_elf, b1.draw_gift, b1.draw_santa, b1.draw_deer, b1.draw_prof
shadow, heart, sparkles, meter, thought, paper_bits = b1.shadow, b1.heart, b1.sparkles, b1.meter, b1.thought, b1.paper_bits
T_ = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T_['lines'], T_['total']
CAPJ = json.load(open(os.path.join(HERE, 'captions.json')))
def cs(line, k):
    c_ = [c for c in CAPJ if c['line'] == line]; return c_[min(k, len(c_) - 1)]['t0']
(L_HOOK, L_GENIUS, L_CORNERS, L_TRASH, L_MESSY, L_PROVED, L_MORE, L_WHY, L_FLOOR, L_LAZY, L_CATCH, L_BOSS,
 L_SHINE, L_CTA) = range(14)
GROUND = rv.GROUND
def ramp(t, t0, d=0.5): return smooth(min(1.0, max(0.0, (t - t0) / d)))

# ---------------- extra sprites ----------------
_c = {}
def spr(key, fn):
    if key not in _c: _c[key] = fn()
    return _c[key]
def trash_can():
    W_, H_ = 30, 36; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = ch.Layers(W_, H_)
    L.add((yy >= 8) & (yy < 35) & (np.abs(xx - 15) <= 11 - (yy - 8) * 0.08), lambda c, m: (c.__setitem__(m, hexc('#8a94a8')), c.__setitem__(m & (xx > 19), hexc('#6a7488')),
          c.__setitem__(m & (np.abs(((xx - 3) % 6) - 3) < 0.7) & (yy > 11) & (yy < 32), hexc('#5a6478'))))
    L.add((yy >= 4) & (yy < 8) & (np.abs(xx - 15) <= 13), hexc('#a8b2c4'))
    L.add((yy >= 1) & (yy < 4) & (np.abs(xx - 15) <= 3), hexc('#a8b2c4'))
    return L.out()
def socks():
    W_, H_ = 26, 26; yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32); L = ch.Layers(W_, H_)
    for ox in (0, 11):
        leg = (xx >= 2 + ox) & (xx < 9 + ox) & (yy >= 1) & (yy < 18)
        foot = (((xx - (8 + ox)) / 5.5) ** 2 + ((yy - 19) / 4) ** 2 <= 1) & (xx >= 2 + ox)
        L.add(leg | foot, lambda c, m: (c.__setitem__(m, hexc('#d22a38')), c.__setitem__(m & (((yy.astype(int) // 3) % 2) == 0) & (yy < 16), hexc('#ffffff')),
                                         c.__setitem__(m & (yy < 3), hexc('#ffffff'))))
    return L.out()
def draw_obj(F, key, fn, cx, feet=GROUND + 1, lift=0.0, shadow_w=None):
    c, M = spr(key, fn); h_, w_ = M.shape
    shadow(F, cx, feet, (shadow_w or w_ * 0.9) * max(0.5, 1 - lift / 30)); pv.blit_hr(F, c, M, cx - w_ / 2, feet - h_ - lift, 1)
def timer(F, secs, y=230, colr=(255, 255, 255)):
    m_, s_ = int(secs) // 60, int(secs) % 60; big_num(F, f'{m_:d}:{s_:02d}', y, px=12, colr=colr)

# ---------------- scenes ----------------
def seg_of(t):
    i = 0
    for k, (a, b) in enumerate(SEG):
        if t >= a - 0.05: i = k
    return i
def scene(F, t):
    i = seg_of(t); a = t - SEG[i][0]
    if i == L_HOOK:
        draw_elf(F, 58, 'tinsel', bob=abs(math.sin(t * 3))); draw_gift(F, 122, 'messy')
        bk.label(F, 'BAD WRAPPING', 560, 470, int(122 * S), int((GROUND - 34) * S), px=6)
    elif i == L_GENIUS:
        jump = 8 * abs(math.sin(a * 7)) * math.exp(-a * 1.3)
        draw_elf(F, 58, 'tinsel', bob=jump, cap=True, mood='proud', arms='up'); draw_gift(F, 122, 'messy')
        sparkles(F, 58, 100, 30, 12, t); ctag(F, 'GENIUS', 300, px=12)
    elif i == L_CORNERS:                                         # 20 minutes of corners... ripped in 2 seconds
        rip = cs(L_CORNERS, 4) - 0.05
        if t < rip:
            k = ramp(t, cs(L_CORNERS, 1), max(0.5, rip - cs(L_CORNERS, 1)))
            draw_elf(F, 52, 'tinsel', mood='sad' if k > 0.6 else 'happy', arms='hold', bob=abs(math.sin(t * 9)) * 0.8)
            draw_gift(F, 124, 'neat'); timer(F, 1200 * k)
            if t >= cs(L_CORNERS, 2) - 0.05:
                for j in range(4): rv.sparkle(F, 124 + (-13, 13, -13, 13)[j], 128 + (-1, -1, 9, 9)[j] * 1.0, 0.6 + 0.4 * math.sin(t * 8 + j))
        else:
            k = ramp(t, rip, 0.25)
            draw_elf(F, 52, 'tinsel', mood='shock')
            if k < 1: draw_gift(F, 124, 'neat', bob=6 * k)
            paper_bits(F, 124, 130, t - rip, n=24, spread=50)
            big_num(F, '0:02', 230, px=12, colr=(255, 120, 60)); ctag(F, 'RIIIP!', 420, px=9)
    elif i == L_TRASH:                                           # gone, straight in the trash
        draw_elf(F, 40, 'tinsel', mood='sad'); draw_obj(F, 'trash', trash_can, 128)
        for j in range(14):
            f = ((t - SEG[L_TRASH][0]) * 0.9 + j * 0.07) % 1
            x, y = lerp(70, 128, f), lerp(100, GROUND - 32, f) - 30 * math.sin(math.pi * f)
            put(F, x, y, hexc(('#3a8aff', '#ffcc4a', '#f4f8ff')[j % 3])); put(F, x + 1, y, hexc(('#3a8aff', '#ffcc4a', '#f4f8ff')[j % 3]))
        big_num(F, '20:00', 230, px=12, colr=(150, 160, 190))
        if t >= cs(L_TRASH, 1) - 0.05:
            for k in range(-160, 160, 2): F[int(230 + 42 + k * 0.18):int(230 + 50 + k * 0.18), 540 + k:542 + k] = hexc('#e8303a')
        if t >= cs(L_TRASH, 2) - 0.05: bk.label(F, 'TRASH', 760, 480, int(128 * S), int((GROUND - 38) * S), px=6)
    elif i == L_MESSY:                                           # 30 seconds, same gift, same smile
        k = ramp(t, cs(L_MESSY, 1), 0.6)
        draw_elf(F, 40, 'tinsel', mood='proud', arms='up' if (t * 6) % 2 < 1 else 'hold')
        draw_gift(F, 86, 'messy', bob=abs(math.sin(t * 12)) * 2 * (1 - k)); timer(F, 30 * k, colr=(90, 224, 122))
        if k < 1: paper_bits(F, 86, 120, t, n=10, spread=26)
        if t >= cs(L_MESSY, 2) - 0.05:
            draw_deer(F, 146, nose='red', flip=True)
            if t >= cs(L_MESSY, 3) - 0.05:
                for j in range(4):
                    ph = (t * 0.8 + j / 4) % 1; heart(F, 136 + j * 6, 88 - ph * 26, 1 - ph)
    elif i in (L_PROVED, L_MORE):                                # the study: neat vs sloppy, sloppy liked more
        draw_prof(F, 30); draw_gift(F, 92, 'neat'); draw_gift(F, 144, 'messy')
        if t >= cs(L_PROVED, 1) - 0.05 or i == L_MORE: ctag(F, 'PROVED', 260, px=8)
        if t >= cs(L_PROVED, 4) - 0.05 or i == L_MORE: bk.pixel_text(F, 'NEAT', int(80 * S), int((GROUND + 6) * S) - 230, px=5)
        if t >= cs(L_PROVED, 5) - 0.05 or i == L_MORE: bk.pixel_text(F, 'SLOPPY', int(126 * S), int((GROUND + 6) * S) - 230, px=5)
        if i == L_MORE:
            n_h = min(5, int(1 + (t - SEG[L_MORE][0]) * 3))
            heart(F, 92, 98); heart(F, 92 - 9, 98)
            for k in range(n_h): heart(F, 144 - 18 + k * 9, 92 - (k % 2) * 4)
            if t >= cs(L_MORE, 1) - 0.05: ctag(F, 'LIKED MORE', 380, px=7)
    elif i == L_WHY:                                             # perfect wrap -> AMAZING -> just socks
        opened = t >= cs(L_WHY, 4) - 0.1
        if not opened: draw_gift(F, 60, 'neat', bob=abs(math.sin(t * 3)))
        else:
            k = ramp(t, cs(L_WHY, 4) - 0.1, 0.3); draw_obj(F, 'socks', socks, 60, lift=10 * math.sin(math.pi * min(1, k)))
        if t < cs(L_WHY, 4) - 0.1 or True:
            thought(F, 56, 58, 62, 30)
            bk.pixel_text(F, 'AMAZING!', int((56 - 27) * S) + 8, int(68 * S), px=6, colr=(230, 150, 20)); sparkles(F, 56, 73, 36, 18, t, n=8)
        meter(F, 118, 'EXPECTED', ramp(t, cs(L_WHY, 1), 1.0), '#ffcc4a')
        meter(F, 158, 'GOT', 0.3 * ramp(t, cs(L_WHY, 5), 0.5), '#e8303a')
        if t >= cs(L_WHY, 6) - 0.05: ctag(F, 'DISAPPOINTED', 200, px=7)
    elif i == L_FLOOR:                                           # messy wrap: expectations hit the floor, gift feels better
        opened = t >= cs(L_FLOOR, 3) - 0.1
        if not opened: draw_gift(F, 60, 'messy')
        else:
            k = ramp(t, cs(L_FLOOR, 3) - 0.1, 0.3); draw_obj(F, 'socks', socks, 60, lift=10 * math.sin(math.pi * min(1, k)))
            paper_bits(F, 60, 140, t, n=10, spread=24)
        drop = ramp(t, cs(L_FLOOR, 2) - 0.1, 0.5)
        meter(F, 118, 'EXPECTED', 0.85 - 0.75 * drop, '#ffcc4a')
        meter(F, 158, 'GOT', 0.3 * ramp(t, cs(L_FLOOR, 4), 0.5), '#5ae07a')
        if t >= cs(L_FLOOR, 4) - 0.05: ctag(F, 'BETTER!', 200, px=9)
    elif i == L_LAZY:                                            # not lazy: managing expectations, a business skill
        biz = t >= cs(L_LAZY, 3) - 0.05
        draw_elf(F, 64, 'tinsel', cap=biz, mood='proud', arms='up' if biz else 'down', bob=abs(math.sin(t * 5)) * 2 if biz else 0)
        if t < cs(L_LAZY, 1) - 0.05:
            ctag(F, 'LAZY', 300, px=10)
            for k in range(-120, 120, 2): F[int(330 + k * 0.12):int(338 + k * 0.12), 540 + k:542 + k] = hexc('#e8303a')
        elif not biz: ctag(F, 'EXPECTATION MANAGER', 300, px=6)
        else:
            ctag(F, 'BUSINESS SKILL', 300, px=7); sparkles(F, 64, 100, 28, 12, t, n=8)
            pts = [(108, 140), (122, 126), (134, 132), (150, 104), (162, 90)]
            k = ramp(t, cs(L_LAZY, 3), 0.8); n_ = int(1 + k * (len(pts) - 1) * 10)
            for j in range(min(n_, (len(pts) - 1) * 10)):
                s_, f = j // 10, (j % 10) / 10; x0, y0 = pts[s_]; x1, y1 = pts[s_ + 1]
                put(F, lerp(x0, x1, f), lerp(y0, y1, f), hexc('#5ae07a')); put(F, lerp(x0, x1, f), lerp(y0, y1, f) + 1, hexc('#5ae07a'))
            if k > 0.95:
                for dx, dy in ((0, 0), (-2, 0), (-1, -1), (0, 2), (-1, 1)): put(F, 163 + dx, 89 + dy, hexc('#5ae07a'))
    elif i == L_CATCH:                                           # re-hook
        draw_elf(F, 90, 'tinsel', cap=True, mood='shock')
        k = ramp(t, SEG[L_CATCH][0], 0.4); F *= 1 - 0.55 * k
        glow(F, 90, 110, 40, '#ffcc4a', 0.25 * k)
        ctag(F, 'THE CATCH', 300, px=8); bk.pixel_text(F, '!', 680, 520, px=12, colr=(255, 200, 58))
    elif i == L_BOSS:                                            # friends & family vs the boss
        boss = t >= cs(L_BOSS, 3) - 0.05
        if not boss:
            draw_elf(F, 38, 'tinsel', mood='happy', arms='hold'); draw_gift(F, 82, 'messy'); draw_deer(F, 142, nose='red', flip=True)
            for k in range(4):
                ph = (t * 0.8 + k / 4) % 1; heart(F, 132 + k * 6, 86 - ph * 26, 1 - ph)
            if t >= cs(L_BOSS, 1) - 0.05: ctag(F, 'FRIENDS + FAMILY', 300, px=7)
        else:
            draw_elf(F, 38, 'tinsel', mood='happy', arms='hold'); draw_gift(F, 88, 'neat'); draw_santa(F, 142)
            bk.label(F, 'BOSS', 880, 470, int(142 * S), int((GROUND - 54) * S), px=6)
            sparkles(F, 88, 132, 18, 8, t, n=6)
            if t >= cs(L_BOSS, 6) - 0.05:
                ctag(F, 'NEAT = YOU CARE', 300, px=7)
                for k in range(3):
                    ph = (t * 0.8 + k / 3) % 1; heart(F, 136 + k * 7, 92 - ph * 24, 1 - ph)
    elif i == L_SHINE:                                           # grab the tape, skip the corners, shine
        shine = t >= cs(L_SHINE, 3) - 0.05
        draw_elf(F, 90, 'tinsel', cap=True, mood='proud', arms='up', bob=abs(math.sin(t * 5)) * 3)
        if t >= cs(L_SHINE, 1) - 0.05:
            sv.disc(F, 60, 128, 7, '#d8dee8', ring='#a8b2c4', ringw=3); sv.disc(F, 60, 128, 3, '#1f4782')
            bk.label(F, 'TAPE', 100, 520, int(60 * S), int(120 * S), px=6)
        if t >= cs(L_SHINE, 2) - 0.05: draw_gift(F, 128, 'messy')
        if shine:
            glow(F, 90, 110, 46, '#ffe27a', 0.35); sparkles(F, 90, 104, 52, 18, t, n=14); ctag(F, 'GENIUS', 300, px=12)
    else:                                                        # CTA
        sl = ramp(t, SEG[L_CTA][0], 0.6)
        draw_santa(F, lerp(-30, 44, sl), bob=abs(math.sin(t * 3)) * 1.2)
        draw_elf(F, 146, 'tinsel', mood='happy'); draw_gift(F, 112, 'messy')
        if t < cs(L_CTA, 2) - 0.05:
            pop = ramp(t, SEG[L_CTA][0] + 0.1, 0.25); bw, bh = int(720 * pop), int(200 * pop)
            if bw > 20:
                X, Y = (WF - bw) // 2, 250
                F[Y:Y + bh, X:X + bw] = 1.0
                for q in range(5): F[Y + q, X:X + bw] = F[Y + bh - 1 - q, X:X + bw] = NAVY; F[Y:Y + bh, X + q] = F[Y:Y + bh, X + bw - 1 - q] = NAVY
                if pop > 0.95:
                    tx1 = 'TAG THE WORST'; tx2 = 'WRAPPER YOU KNOW'
                    bk.pixel_text(F, tx1, X + (bw - (len(tx1) * 42 - 7)) // 2, Y + 40, px=7, colr=(20, 24, 40))
                    bk.pixel_text(F, tx2, X + (bw - (len(tx2) * 42 - 7)) // 2, Y + 115, px=7, colr=(200, 40, 60))
        else:
            press = cs(L_CTA, 2) + 0.35; pressed = t >= press
            bw, bh = 640, 150; X, Y = (WF - bw) // 2, 260
            sq = 6 if press - 0.1 <= t < press + 0.1 else 0
            F[Y + sq:Y + bh - sq, X + sq:X + bw - sq] = hexc('#5a6070') if pressed else hexc('#e8202e')
            for q in range(5):
                F[Y + sq + q, X + sq:X + bw - sq] = F[Y + bh - sq - 1 - q, X + sq:X + bw - sq] = NAVY
                F[Y + sq:Y + bh - sq, X + sq + q] = F[Y + sq:Y + bh - sq, X + bw - sq - 1 - q] = NAVY
            txt = 'SUBSCRIBED' if pressed else 'SUBSCRIBE'; tw = len(txt) * 6 * 9 - 9
            bk.pixel_text(F, txt, (WF - tw) // 2, Y + 44, px=9, colr=(255, 255, 255))
            draw_cursor(F, int(lerp(WF * 0.8, WF * 0.6, ramp(t, cs(L_CTA, 2), 0.35))), Y + bh - 30)
            if pressed:
                for k in range(8): rv.sparkle(F, 90 + 50 * math.cos(TAU * k / 8), 62 + 18 * math.sin(TAU * k / 8), 1 - ramp(t, press, 0.8))
            if t >= cs(L_CTA, 3) - 0.05:
                c, M = sv.spr('scroll', ch.scroll); sx = lerp(44, 60, ramp(t, cs(L_CTA, 3), 0.3))
                pv.blit_hr(F, c, M, sx + 6, GROUND - 46, 1)
                bk.pixel_text(F, 'NAUGHTY', int((sx + 8) * S) + 2, int((GROUND - 38) * S), px=3, colr=(200, 30, 40))

# ---------------- captions + frame ----------------
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
SHOUTS = [SEG[L_GENIUS][0], cs(L_CORNERS, 4), cs(L_MORE, 1), SEG[L_CATCH][0]]
def frame(t):
    F = rv.BG.copy()
    scene(F, t)
    i = seg_of(t)
    rv.snow(F, t)
    if i >= 2 and 0 <= t - SEG[i][0] < 0.12 and i not in (L_MORE, L_TRASH):
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
