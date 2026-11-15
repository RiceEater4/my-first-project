"""Santa, redone: simple but complete (arms + mittens), clean readable face, navy outline, chunky pixels.
Draws old vs new side by side on the blueprint background -> santa_redone.png"""
import os, sys, math
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from blueprint_kit import *

def santa_new():
    """layered: each part gets its own navy outline so arms read separately from the body; flat colours, no dither"""
    W_, H_ = 46, 52
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    cx = 23
    canvas = np.zeros((H_, W_, 3), np.float32); cm = np.zeros((H_, W_), bool)
    def layer(mask, colfn):
        nonlocal canvas, cm
        col = np.zeros((H_, W_, 3), np.float32); colfn(col, mask)
        p = np.pad(mask, 1); ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~mask
        canvas[ring] = OUTLINE; cm |= ring
        canvas[mask] = col[mask]; cm |= mask
    RED, RED_D, RED_L, WHITE, WHITE_S = hexc('#d22a38'), hexc('#a0182a'), hexc('#ee4a52'), hexc('#ffffff'), hexc('#dfe6f0')
    # boots + legs
    legs = (yy >= 40) & (yy < 46) & ((np.abs(xx - 17) <= 3) | (np.abs(xx - 29) <= 3))
    boots = (yy >= 45) & (yy < 50) & ((np.abs(xx - 16.5) <= 4) | (np.abs(xx - 29.5) <= 4))
    layer(legs | boots, lambda c, m: (c.__setitem__(m, RED_D), c.__setitem__(boots, hexc('#1b1418'))))
    # body (coat)
    body = ((xx - cx) / 12) ** 2 + ((yy - 32) / 11) ** 2 <= 1
    def body_col(c, m):
        c[m] = RED; c[m & (xx > cx + 5)] = RED_D; c[m & (xx < cx - 6) & (yy < 30)] = RED_L
        c[m & (np.abs(xx - cx) < 1.6)] = WHITE
        belt = m & (np.abs(yy - 34) < 1.6); c[belt] = hexc('#1b1418')
        c[belt & (np.abs(xx - cx) < 2.6)] = hexc('#ffcc4a'); c[belt & (np.abs(xx - cx) < 1.1) & (np.abs(yy - 34) < 0.6)] = hexc('#1b1418')
        c[m & (yy > 40.5)] = WHITE                                                  # coat hem
    layer(body, body_col)
    # head + beard
    head = ((xx - cx) / 7) ** 2 + ((yy - 15) / 6.5) ** 2 <= 1
    beard = (((xx - cx) / 8.5) ** 2 + ((yy - 21) / 6.5) ** 2 <= 1) & (yy >= 17)
    def head_col(c, m):
        c[m] = hexc('#f6c9a8'); c[m & (xx > cx + 4)] = hexc('#e8b090')
        c[beard] = WHITE; c[beard & (xx > cx + 4) & (yy > 21)] = WHITE_S
        for ex in (cx - 3, cx + 3):                                                 # eyes: 2x3 dark with a white highlight
            c[(xx >= ex - 1) & (xx < ex + 1) & (yy >= 14) & (yy < 17)] = hexc('#1b1428')
            c[(xx >= ex - 1) & (xx < ex) & (yy >= 14) & (yy < 15)] = WHITE
        must = (((xx - (cx - 2.5)) / 3) ** 2 + ((yy - 19.5) / 1.4) ** 2 <= 1) | (((xx - (cx + 2.5)) / 3) ** 2 + ((yy - 19.5) / 1.4) ** 2 <= 1)
        c[must] = WHITE
        c[((xx - cx) / 1.8) ** 2 + ((yy - 18) / 1.5) ** 2 <= 1] = hexc('#e8807a')      # nose
        for ck in (cx - 5, cx + 5): c[((xx - ck) / 1.2) ** 2 + ((yy - 17.6) / 0.9) ** 2 <= 1] = hexc('#f2a0a0')
        c[(yy >= 21.5) & (yy < 23) & (np.abs(xx - cx) < 2)] = hexc('#8a3a3a')                 # mouth
    layer(head | beard, head_col)
    # hat
    hat = (yy >= 1) & (yy < 10) & (np.abs(xx - cx - (10 - yy) * 0.5) <= 1.5 + (yy - 1) * 0.85)
    layer(hat, lambda c, m: (c.__setitem__(m, RED), c.__setitem__(m & (xx > cx + 3), RED_D)))
    brim = (yy >= 9) & (yy < 12) & (np.abs(xx - cx) <= 8)
    layer(brim, lambda c, m: (c.__setitem__(m, WHITE), c.__setitem__(m & (yy >= 11), WHITE_S)))
    pom = ((xx - (cx + 7.5)) / 2.4) ** 2 + ((yy - 2) / 2.4) ** 2 <= 1
    layer(pom, lambda c, m: c.__setitem__(m, WHITE))
    # arms on top, each with its own outline so they read clearly
    for side in (-1, 1):
        sx = cx + side * 11
        arm = (np.abs((xx - sx) - side * (yy - 26) * 0.3) <= 2.4) & (yy >= 25) & (yy <= 34)
        layer(arm, lambda c, m: (c.__setitem__(m, RED if side < 0 else RED_D), c.__setitem__(m & (yy >= 33), WHITE)))
        mit = ((xx - (sx + side * 3.2)) / 2.7) ** 2 + ((yy - 36.5) / 2.7) ** 2 <= 1
        layer(mit, lambda c, m: (c.__setitem__(m, hexc('#1f7a3e')), c.__setitem__(m & (yy < 36), hexc('#2f9a52'))))
    return canvas, cm

def santa_old():
    n = 40; yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    body = ((xx - 20) / 11) ** 2 + ((yy - 26) / 10) ** 2 <= 1
    face = ((xx - 20) / 6) ** 2 + ((yy - 11) / 5.5) ** 2 <= 1
    beard = ((xx - 20) / 7.5) ** 2 + ((yy - 16) / 5.5) ** 2 <= 1
    hat = ((yy >= 0) & (yy < 7) & (np.abs(xx - 20 - (7 - yy) * 0.6) <= 2 + yy * 0.9)) | (((xx - 26) / 2.2) ** 2 + ((yy - 1) / 2.2) ** 2 <= 1)
    brim = (yy >= 6) & (yy < 8.5) & (np.abs(xx - 20) <= 7.5)
    boots = (yy >= 35) & (yy < 39) & ((np.abs(xx - 14) < 3.5) | (np.abs(xx - 26) < 3.5))
    M = body | face | beard | hat | brim | boots
    col = np.zeros((n, n, 3), np.float32)
    col[body] = hexc('#c81e2e'); col[face] = hexc('#f2c2a0'); col[beard & ~(face & (yy < 13))] = hexc('#ffffff')
    for ex in (17.5, 22.5): col[(np.abs(xx - ex) < 0.8) & (np.abs(yy - 10.5) < 0.8)] = hexc('#14101a')
    col[hat] = hexc('#c81e2e'); col[brim] = hexc('#ffffff'); col[boots] = hexc('#1b1418')
    return outline(col, M)

F = background(glow_xy=(540, 760))
tcol, tM = diorama(140, 30, 8, [hexc('#a9c8ea'), hexc('#cfe2f6'), hexc('#eaf3fd'), hexc('#ffffff')],
                   [hexc('#2c5d96'), hexc('#4a86c5'), hexc('#6fa6dd')], seed=5)
blit(F, tcol, tM, 540 - 70 * PX, 900)
old, oM = santa_old(); blit(F, old, oM, 230 - 20 * PX * 1.0, 900 - 38 * PX + 30)
new, nM = santa_new(); blit(F, new, nM, 700 - 23 * PX, 900 - 50 * PX + 30)
label(F, 'BEFORE', 120, 380, 230, 640)
label(F, 'AFTER', 820, 300, 720, 560)
caption(F, ['SANTA,', 'REDONE.'], y=1180, size=78, highlight=('REDONE',))
pixel_text(F, 'ARMS + MITTENS', 330, 1330, px=5, colr=(225, 235, 255))
pixel_text(F, 'CLEAR EYES + NOSE', 330, 1380, px=5, colr=(225, 235, 255))
Image.fromarray((np.clip(F, 0, 1) * 255).astype(np.uint8)).save(os.path.join(HERE, 'santa_redone.png'))
big = np.ones((54, 48, 3), np.float32) * hexc('#1f4782'); m2 = None
c2, m_ = santa_new(); big[1:1 + c2.shape[0], 1:1 + c2.shape[1]][m_] = c2[m_]
Image.fromarray((np.repeat(np.repeat(big, 16, 0), 16, 1) * 255).astype(np.uint8)).save(os.path.join(HERE, 'santa_redone_closeup.png'))
print('saved')
