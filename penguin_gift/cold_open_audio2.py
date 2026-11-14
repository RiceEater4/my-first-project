"""Builds the final soundtrack: cold open (the theft) -> tape-rewind -> the story from its first downbeat.
usage: python3 cold_open_audio.py story.wav final.wav   (story.wav comes from audio.py)"""
import sys, wave
import numpy as np
from score2 import *

SNATCH_T0, COLD_LEN, REW = THIEF_FALL + 0.3, 1.6, 0.8
STORY0 = 0.0
with wave.open(sys.argv[1]) as w:
    SR = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), '<i2').reshape(-1, 2).astype(np.float32) / 32767
def seg(t0, t1): return a[int(t0 * K * SR):int(t1 * K * SR)]
cold = seg(SNATCH_T0, SNATCH_T0 + COLD_LEN).copy()
cold[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))[:, None]
# rewind: the last moments played backwards, speeding up, plus a rising whoosh
src = seg(SNATCH_T0 + COLD_LEN - 1.6, SNATCH_T0 + COLD_LEN)[::-1]
n = int(REW * K * SR); idx = (np.cumsum(np.linspace(1.2, 3.2, n)) % len(src)).astype(int)
rew = src[idx] * 0.55
rng = np.random.default_rng(3); tt = np.arange(n) / SR / K
noise = np.convolve(rng.standard_normal(n), np.ones(5) / 5, 'same') * (tt / REW) ** 2 * 0.35
rew = rew + noise[:, None]
rew[:int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))[:, None]
story = seg(STORY0, LOOP)
out = np.concatenate([cold, rew, story])
out /= max(1.0, np.max(np.abs(out)) / 0.93)
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype('<i2').tobytes())
print('final audio', round(len(out) / SR, 2), 's')
