"""Layout reference: visual in the middle (or a bit higher), caption right below it."""
import sys, os, math
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'penguin_gift'))
from blueprint_kit import *
import importlib.util
_s = importlib.util.spec_from_file_location('penguin_model', os.path.join(HERE, '..', 'penguin_gift', 'video.py'))
pv = importlib.util.module_from_spec(_s); _s.loader.exec_module(pv); pv.INK = OUTLINE

def chunky_penguin(pose, bw=0.5):
    pose = dict(pose); pose['scale'] = bw / pv.FINE
    col, M, _ = pv.penguin(pose)
    ys, xs = np.nonzero(M); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return dither_seams(col[y0:y1, x0:x1], M[y0:y1, x0:x1]), M[y0:y1, x0:x1], (pv.OX - x0, pv.OY - y0)

UP = 190                                             # how far everything moved up vs the old layout
F = background(glow_xy=(540, 820 - UP))
soft_shadow(F, 540, 1150 - UP, 400, 60, 0.5)
tcol, tM = diorama(116, 44, 8, [hexc('#a9c8ea'), hexc('#cfe2f6'), hexc('#eaf3fd'), hexc('#ffffff')],
                   [hexc('#2c5d96'), hexc('#4a86c5'), hexc('#6fa6dd')], seed=3)
blit(F, tcol, tM, 540 - 58 * PX, 850 - UP)
for x, pose in ((420, dict(hat=True, eyes='happy', look=1, flipR=1.35, tilt=0.1)), (664, dict(bow=True, eyes='happy', look=-1, flipL=0.45))):
    col, M, (ox, oy) = chunky_penguin(pose); blit(F, col, M, x - ox * PX, 1000 - UP - oy * PX)
gm = np.array([[0, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 0]], bool); gp = np.zeros((4, 6, 3), np.float32)
gp[gm] = hexc('#dfe9f7'); gp[0:2, 1:3] = hexc('#ffffff'); gp[3, 1:5] = hexc('#a9b8cf'); gp, gm = outline(gp, gm); blit(F, gp, gm, 525, 790 - UP)
label(F, 'PEBBLE', 600, 560 - UP, 560, 786 - UP); tag(F, 'GENTOO', 742, 1150 - UP)
caption(F, ['HE', 'PROPOSED', 'WITH', 'A', 'ROCK.'], y=1040, size=66, highlight=('ROCK',))
# guide brackets
def bracket(y0, y1, text):
    c = np.array([1.0, 0.78, 0.23])
    F[y0:y1, 40:44] = c; F[y0:y0 + 4, 40:64] = c; F[y1 - 4:y1, 40:64] = c
    pixel_text(F, text, 40, y0 - 44, px=4, colr=(255, 200, 58))
bracket(360, 1000, 'VISUAL: MIDDLE OR A BIT HIGHER')
bracket(1030, 1140, '')
pixel_text(F, 'CAPTION: RIGHT BELOW', 40, 1160, px=4, colr=(255, 200, 58))
Image.fromarray((np.clip(F, 0, 1) * 255).astype(np.uint8)).save(os.path.join(HERE, 'layout_reference.png')); print('saved')
