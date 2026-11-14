"""Final soundtrack: Ethan's narration on top, a Jingle Bells bed (public domain) that ducks under the voice,
and sound effects on the story beats. usage: python3 mix.py out.wav"""
import sys, os, json, math, wave, subprocess
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
T = json.load(open(os.path.join(HERE, 'timing.json'))); SEG, END = T['lines'], T['total']
N = int(END * SR); rng = np.random.default_rng(5)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, 'narration.mp3'), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
voice = np.zeros(N); v = np.frombuffer(raw, np.float32); voice[:min(N, len(v))] = v[:N]
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def add(buf, t, sig):
    i = int(t * SR); e = min(N, i + len(sig))
    if 0 <= i < N: buf[i:e] += sig[:e - i]
def env(n, d): return np.exp(-np.arange(n) / SR / d)
def glock(m, v=1.0, dur=1.4):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    return v * (np.sin(2 * np.pi * f * t) * env(n, 0.8) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * env(n, 0.2)) * np.clip(t / 0.002, 0, 1)
def kick(v=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    return v * np.tanh(2 * np.sin(2 * np.pi * np.cumsum(50 + 160 * np.exp(-t / 0.03)) / SR)) * env(n, 0.15)
def bells(v=1.0):
    n = int(0.2 * SR); t = np.arange(n) / SR
    return v * sum(np.sin(2 * np.pi * f * t + f) for f in (3100, 4300, 5600, 7200)) / 4 * env(n, 0.05)
def clunk(v=1.0):
    n = int(0.3 * SR); t = np.arange(n) / SR
    wood = np.sin(2 * np.pi * 420 * t) * env(n, 0.04) + 0.6 * np.sin(2 * np.pi * 760 * t) * env(n, 0.02)
    return v * (wood + rng.standard_normal(n) * env(n, 0.01) * 0.4)
def boing(v=1.0):
    n = int(0.4 * SR); t = np.arange(n) / SR
    return v * np.sin(2 * np.pi * np.cumsum(180 + 220 * np.exp(-t / 0.08)) / SR) * env(n, 0.12)
def whoosh(dur=0.35, v=1.0):
    n = int(dur * SR); x = np.convolve(rng.standard_normal(n), np.ones(8) / 8, 'same')
    return v * x * np.sin(np.pi * np.arange(n) / n) ** 2
def sad_trombone(v=1.0):
    out = np.zeros(int(1.6 * SR))
    for k, m in enumerate((55, 54, 53, 52)):
        n = int(0.4 * SR if k < 3 else 0.8 * SR); t = np.arange(n) / SR; f = hz(m)
        s = sum(np.sin(2 * np.pi * f * h * t) / h for h in range(1, 6)) * np.clip(t / 0.02, 0, 1) * env(n, 0.5)
        i = int(k * 0.4 * SR); out[i:i + n] += s[:len(out) - i]
    return v * out
# ---- music bed: Jingle Bells chorus at 120 BPM, looped
music = np.zeros(N)
M = [(0, 71, 1), (1, 71, 1), (2, 71, 2), (4, 71, 1), (5, 71, 1), (6, 71, 2), (8, 71, 1), (9, 74, 1), (10, 67, 1.5), (11.5, 69, .5), (12, 71, 4),
     (16, 72, 1), (17, 72, 1), (18, 72, 1.5), (19.5, 72, .5), (20, 72, 1), (21, 71, 1), (22, 71, 1), (23, 71, .5), (23.5, 71, .5),
     (24, 74, 1), (25, 74, 1), (26, 72, 1), (27, 69, 1), (28, 67, 4)]
CH = [(55, 59, 62), (55, 59, 62), (55, 60, 64), (55, 59, 62), (55, 60, 64), (55, 59, 62), (54, 57, 62), (55, 59, 62)]
for rep in range(int(END / 16) + 1):
    t0 = rep * 16.0
    for b, m, d in M: add(music, t0 + b * 0.5, glock(m + 12, 0.55))
    for k in range(32): add(music, t0 + k * 0.5, kick(0.45 if k % 2 == 0 else 0.3))
    for k in range(64): add(music, t0 + k * 0.25, bells(0.25 if k % 2 else 0.4))
    for bar in range(8):
        n = int(2 * SR); t = np.arange(n) / SR
        pad = sum(np.sin(2 * np.pi * hz(m) * t) + 0.3 * np.sin(4 * np.pi * hz(m) * t) for m in CH[bar]) * 0.12
        pad *= np.clip(t / 0.05, 0, 1) * np.clip((2 - t) / 0.05, 0, 1); add(music, t0 + bar * 2, pad)
music /= np.max(np.abs(music)) + 1e-9
# duck the music under the voice
venv = np.convolve(np.abs(voice), np.ones(int(0.05 * SR)) / (0.05 * SR), 'same')
venv = np.convolve((venv > 0.02).astype(float), np.ones(int(0.25 * SR)) / (0.25 * SR), 'same')
music *= 0.42 - 0.27 * np.clip(venv, 0, 1)
music[int((END - 1.0) * SR):] *= np.linspace(1, 0, N - int((END - 1.0) * SR))
# ---- sound effects on the story beats
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location('rv', os.path.join(HERE, 'video.py')); rv = importlib.util.module_from_spec(spec); spec.loader.exec_module(rv)
fx = np.zeros(N)
add(fx, 0.0, bells(0.8)); add(fx, 0.0, glock(91, 0.4)); add(fx, 0.05, glock(95, 0.35))
d = rv.drop_time(); add(fx, d, whoosh(0.25, 0.4)); add(fx, d + 0.5, clunk(0.9)); add(fx, d + 0.75, clunk(0.4))
for k, pt in enumerate(rv.pop_times()): add(fx, pt, boing(0.5)); add(fx, pt + 0.55, clunk(0.35))
for bt in rv.bonk_times(): add(fx, bt, clunk(0.9)); add(fx, bt, kick(0.5))
add(fx, SEG[9][0] + 0.2, sad_trombone(0.5))
for i in (2, 4, 6, 8, 10, 11): add(fx, SEG[i][0], whoosh(0.3, 0.25))
add(fx, SEG[5][0] + 1.4, glock(98, 0.3)); add(fx, SEG[11][0] + 1.0, glock(91, 0.35)); add(fx, SEG[11][0] + 1.1, glock(98, 0.3))
for k in range(5): add(fx, SEG[11][1] + k * 0.08, glock(86 + k * 3, 0.25, 1.6))
mix = voice * 1.0 + music + fx * 0.55
mix = np.tanh(mix / (np.max(np.abs(mix)) + 1e-9) * 1.4) / np.tanh(1.4) * 0.95
st = np.stack([mix, mix], 1)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('mix ok', END)
