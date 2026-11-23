"""Chubby version of YOU (green elf): the torso + arms rows of the normal sprite are stretched sideways
around the centre (nearest-neighbour, so pixels stay crisp); head, hat and legs keep their width."""
import numpy as np
def widen(c, M, k, rows=(26, 45), pad=8):
    h_, w_ = M.shape; W2 = w_ + 2 * pad; cx = w_ / 2 - 0.5
    C2 = np.zeros((h_, W2, 3), np.float32); M2 = np.zeros((h_, W2), bool)
    C2[:, pad:pad + w_], M2[:, pad:pad + w_] = c, M
    r0, r1 = rows
    for y in range(r0, r1):
        f = k if y < r1 - 2 else 1 + (k - 1) * 0.5                     # hem rows taper back a little
        mid = (y - r0) / max(1, r1 - r0 - 1); f = 1 + (f - 1) * (0.55 + 0.45 * np.sin(np.pi * min(1, mid * 1.15)))  # roundest at the belly
        for X in range(W2):
            src = int(round(cx + (X - pad - cx) / f))
            if 0 <= src < w_ and M[y, src]: C2[y, X], M2[y, X] = c[y, src], True
            else: M2[y, X] = False
    return C2, M2
