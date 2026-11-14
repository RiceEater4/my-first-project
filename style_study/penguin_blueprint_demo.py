"""Demo frame: the penguin gift scene in the blueprint pixel-art style."""
import sys, os, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blueprint_kit import *
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'penguin_gift'))
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'penguin_gift'))
import video as pv                                         # reuse the penguin character
pv.INK = OUTLINE

def chunky_penguin(pose, bw=1.0):
    """render the penguin on the chunky 6-px grid, navy outline, dithered shade seams"""
    pose = dict(pose); pose['scale'] = pose.get('scale', 1.0) / pv.FINE * bw
    col, M, tips = pv.penguin(pose)
    ys, xs = np.nonzero(M); y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    col, M = col[y0:y1, x0:x1], M[y0:y1, x0:x1]
    col = dither_seams(col, M)
    return col, M, (pv.OX - x0, pv.OY - y0)

F = background(glow_xy=(540, 820))
soft_shadow(F, 540, 1150, 400, 60, 0.5)
tcol, tM = diorama(116, 44, 8, [hexc('#a9c8ea'), hexc('#cfe2f6'), hexc('#eaf3fd'), hexc('#ffffff')],
                   [hexc('#2c5d96'), hexc('#4a86c5'), hexc('#6fa6dd')], seed=3)
blit(F, tcol, tM, 540 - 58 * PX, 850)
r = np.random.default_rng(5)                                  # pebbles scattered on the tile
for _ in range(9):
    px_, py_ = r.uniform(-48, 48), r.uniform(6, 38)
    pc = np.zeros((3, 4, 3), np.float32); pm = np.array([[0, 1, 1, 0], [1, 1, 1, 1], [0, 1, 1, 0]], bool)
    pc[pm] = hexc('#8e95a4'); pc[0, 1:3] = hexc('#c3c9d4'); pc, pm = outline(pc, pm)
    blit(F, pc, pm, 540 + px_ * PX, 850 + py_ * PX)
tips = {}
for x, pose in ((420, dict(hat=True, eyes='happy', look=1, flipR=1.35, tilt=0.1)),
                (664, dict(bow=True, eyes='happy', look=-1, flipL=0.45))):
    col, M, (ox, oy) = chunky_penguin(pose, bw=0.5)
    blit(F, col, M, x - ox * PX, 1000 - oy * PX)
gp = np.zeros((4, 6, 3), np.float32); gm = np.array([[0, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 0]], bool)
gp[gm] = hexc('#dfe9f7'); gp[0:2, 1:3] = hexc('#ffffff'); gp[3, 1:5] = hexc('#a9b8cf'); gp, gm = outline(gp, gm)
blit(F, gp, gm, 525, 790)                                     # the gift pebble

label(F, 'PEBBLE', 600, 560, 560, 786)
tag(F, 'GENTOO', 742, 1150)
caption(F, ['SHE', 'SAID', 'YES.'], y=1290, highlight=('YES',))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'penguin_blueprint_demo.png')
Image.fromarray((np.clip(F, 0, 1) * 255).astype(np.uint8)).save(out); print('saved', out)
